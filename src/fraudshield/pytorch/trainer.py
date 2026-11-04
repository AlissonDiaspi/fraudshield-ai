
from dataclasses import asdict, dataclass
from pathlib import Path
import copy
import random

import numpy as np
import torch
from sklearn.metrics import average_precision_score
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from fraudshield.pytorch.data import prepare_pytorch_data
from fraudshield.pytorch.model import FraudMLP


@dataclass
class TrainingConfig:
    dataset_path: str = "data/raw/creditcard.csv"
    batch_size: int = 512
    epochs: int = 30
    learning_rate: float = 0.001
    patience: int = 5
    random_state: int = 42
    checkpoint_path: str = (
        "artifacts/pytorch/best_model.pt"
    )


def set_seed(seed: int) -> None:
    """
    Define sementes para melhorar a reprodutibilidade.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """
    Utiliza CUDA quando disponível; caso contrário, CPU.
    """
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def train_one_epoch(
    model: FraudMLP,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: Adam,
    device: torch.device,
) -> float:
    """
    Executa uma época de treinamento.
    """
    model.train()

    total_loss = 0.0
    total_samples = 0

    for features, labels in loader:
        features = features.to(device)
        labels = labels.to(device)

        optimizer.zero_grad(set_to_none=True)

        logits = model(features)
        loss = criterion(logits, labels)

        loss.backward()
        optimizer.step()

        batch_size = features.size(0)

        total_loss += loss.item() * batch_size
        total_samples += batch_size

    return total_loss / total_samples


@torch.no_grad()
def evaluate_validation(
    model: FraudMLP,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    """
    Avalia o modelo no conjunto de validação.
    """
    model.eval()

    total_loss = 0.0
    total_samples = 0

    probabilities = []
    targets = []

    for features, labels in loader:
        features = features.to(device)
        labels = labels.to(device)

        logits = model(features)
        loss = criterion(logits, labels)

        probs = torch.sigmoid(logits)

        batch_size = features.size(0)

        total_loss += loss.item() * batch_size
        total_samples += batch_size

        probabilities.append(
            probs.cpu().numpy().ravel()
        )

        targets.append(
            labels.cpu().numpy().ravel()
        )

    y_prob = np.concatenate(probabilities)
    y_true = np.concatenate(targets)

    average_precision = average_precision_score(
        y_true,
        y_prob,
    )

    average_loss = total_loss / total_samples

    return average_loss, float(average_precision)


def train_pytorch_model(
    config: TrainingConfig | None = None,
) -> dict:
    """
    Treina a rede neural, aplica early stopping
    e salva o melhor checkpoint.
    """
    if config is None:
        config = TrainingConfig()

    if config.epochs <= 0:
        raise ValueError("epochs deve ser positivo.")

    if config.patience <= 0:
        raise ValueError("patience deve ser positivo.")

    if config.learning_rate <= 0:
        raise ValueError(
            "learning_rate deve ser positivo."
        )

    set_seed(config.random_state)

    device = get_device()

    print("\n=== FRAUDSHIELD AI — PYTORCH ===")
    print("Dispositivo:", device)

    data = prepare_pytorch_data(
        dataset_path=config.dataset_path,
        batch_size=config.batch_size,
        random_state=config.random_state,
    )

    model = FraudMLP(
        input_dim=data.input_dim,
    ).to(device)

    pos_weight_value = (
        data.negative_count / data.positive_count
    )

    pos_weight = torch.tensor(
        [pos_weight_value],
        dtype=torch.float32,
        device=device,
    )

    criterion = nn.BCEWithLogitsLoss(
        pos_weight=pos_weight
    )

    optimizer = Adam(
        model.parameters(),
        lr=config.learning_rate,
    )

    best_ap = -1.0
    best_epoch = 0
    best_state = None
    epochs_without_improvement = 0

    history = []

    for epoch in range(1, config.epochs + 1):
        train_loss = train_one_epoch(
            model,
            data.train_loader,
            criterion,
            optimizer,
            device,
        )

        val_loss, val_ap = evaluate_validation(
            model,
            data.val_loader,
            criterion,
            device,
        )

        history.append({
            "epoch": epoch,
            "train_loss": float(train_loss),
            "val_loss": float(val_loss),
            "val_average_precision": float(val_ap),
        })

        print(
            f"Epoch {epoch:02d}/{config.epochs} | "
            f"Train Loss: {train_loss:.5f} | "
            f"Val Loss: {val_loss:.5f} | "
            f"Val AP: {val_ap:.5f}"
        )

        if val_ap > best_ap + 1e-5:
            best_ap = float(val_ap)
            best_epoch = epoch

            best_state = copy.deepcopy(
                model.state_dict()
            )

            epochs_without_improvement = 0

        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= config.patience:
            print("\nEarly stopping acionado.")
            break

    if best_state is None:
        raise RuntimeError(
            "Nenhum checkpoint válido foi produzido."
        )

    model.load_state_dict(best_state)
    model.eval()

    checkpoint_path = Path(
        config.checkpoint_path
    )

    checkpoint_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Somente tensores e tipos Python simples.
    # Compatível com torch.load(weights_only=True).
    checkpoint = {
        "checkpoint_format_version": 2,
        "model_state_dict": {
            key: value.detach().cpu()
            for key, value in model.state_dict().items()
        },
        "input_dim": int(data.input_dim),
        "best_epoch": int(best_epoch),
        "best_val_ap": float(best_ap),
        "config": asdict(config),
        "scaler_mean": (
            data.scaler.mean_.tolist()
        ),
        "scaler_scale": (
            data.scaler.scale_.tolist()
        ),
        "feature_names": list(
            data.scaler.feature_names_in_
        ),
    }

    torch.save(
        checkpoint,
        checkpoint_path,
    )

    print("\n=== TREINAMENTO CONCLUÍDO ===")
    print("Melhor época:", best_epoch)
    print("Melhor Val AP:", round(best_ap, 5))
    print("Checkpoint:", checkpoint_path)

    return {
        "model": model,
        "device": device,
        "data": data,
        "history": history,
        "best_epoch": best_epoch,
        "best_val_ap": best_ap,
        "checkpoint_path": str(checkpoint_path),
    }
