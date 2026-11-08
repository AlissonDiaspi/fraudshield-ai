
import argparse
from pathlib import Path

import numpy as np
import torch

from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from fraudshield.pytorch.data import prepare_pytorch_data
from fraudshield.pytorch.model import FraudMLP


def load_checkpoint(
    checkpoint_path: Path,
    allow_legacy: bool = False,
) -> dict:
    """
    Carrega um checkpoint de forma segura por padrão.

    Checkpoints antigos com arrays NumPy podem
    exigir desserialização Python completa.

    Use allow_legacy somente para arquivos
    locais e de origem confiável.
    """
    try:
        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True,
        )

    except Exception as error:
        if not allow_legacy:
            raise RuntimeError(
                "Não foi possível carregar o checkpoint "
                "com weights_only=True. "
                "Se ele foi gerado localmente pelo "
                "treinamento anterior, execute novamente "
                "com --allow-legacy-checkpoint. "
                "Nunca utilize essa opção com arquivos "
                "de origem desconhecida."
            ) from error

        print(
            "\nAVISO: carregando checkpoint legado "
            "com weights_only=False."
        )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=False,
        )

    if not isinstance(checkpoint, dict):
        raise ValueError(
            "Formato de checkpoint inválido."
        )

    required_keys = {
        "model_state_dict",
        "input_dim",
        "best_epoch",
        "best_val_ap",
        "config",
        "scaler_mean",
        "scaler_scale",
        "feature_names",
    }

    missing = required_keys - checkpoint.keys()

    if missing:
        raise ValueError(
            f"Checkpoint incompleto: {sorted(missing)}"
        )

    return checkpoint


@torch.no_grad()
def evaluate_checkpoint(
    checkpoint_path: str,
    dataset_path: str,
    batch_size: int = 512,
    threshold: float = 0.5,
    allow_legacy: bool = False,
) -> dict:
    """
    Avalia o melhor checkpoint no conjunto de teste.

    Não ajusta threshold nem parâmetros usando
    os dados de teste.
    """
    if not 0 <= threshold <= 1:
        raise ValueError(
            "threshold deve estar entre 0 e 1."
        )

    if batch_size <= 0:
        raise ValueError(
            "batch_size deve ser positivo."
        )

    checkpoint_file = Path(checkpoint_path)

    if not checkpoint_file.is_file():
        raise FileNotFoundError(
            f"Checkpoint não encontrado: {checkpoint_file}"
        )

    checkpoint = load_checkpoint(
        checkpoint_file,
        allow_legacy=allow_legacy,
    )

    config = checkpoint["config"]

    data = prepare_pytorch_data(
        dataset_path=dataset_path,
        batch_size=batch_size,
        random_state=config["random_state"],
    )

    expected_features = list(
        checkpoint["feature_names"]
    )

    current_features = list(
        data.scaler.feature_names_in_
    )

    if expected_features != current_features:
        raise ValueError(
            "As features não correspondem "
            "às utilizadas no treinamento."
        )

    if checkpoint["input_dim"] != data.input_dim:
        raise ValueError(
            "Dimensão de entrada incompatível."
        )

    saved_mean = np.asarray(
        checkpoint["scaler_mean"],
        dtype=np.float64,
    )

    saved_scale = np.asarray(
        checkpoint["scaler_scale"],
        dtype=np.float64,
    )

    if not np.allclose(
        saved_mean,
        data.scaler.mean_,
        rtol=1e-10,
        atol=1e-10,
    ):
        raise ValueError(
            "A média do scaler não corresponde "
            "ao checkpoint."
        )

    if not np.allclose(
        saved_scale,
        data.scaler.scale_,
        rtol=1e-10,
        atol=1e-10,
    ):
        raise ValueError(
            "A escala do scaler não corresponde "
            "ao checkpoint."
        )

    model = FraudMLP(
        input_dim=checkpoint["input_dim"],
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    probabilities = []
    targets = []

    for features, labels in data.test_loader:
        logits = model(features)

        probs = torch.sigmoid(logits)

        probabilities.append(
            probs.cpu().numpy().ravel()
        )

        targets.append(
            labels.cpu().numpy().ravel()
        )

    y_prob = np.concatenate(probabilities)

    y_true = np.concatenate(
        targets
    ).astype(int)

    y_pred = (
        y_prob >= threshold
    ).astype(int)

    metrics = {
        "average_precision": float(
            average_precision_score(
                y_true,
                y_prob,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                y_prob,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
    }

    print("\nPytorch Test")

    print("Checkpoint:", checkpoint_file)
    print("Melhor época:", checkpoint["best_epoch"])
    print(
        "Melhor Val AP:",
        round(float(checkpoint["best_val_ap"]), 5),
    )
    print("Threshold:", threshold)
    print("Amostras de teste:", len(y_true))

    print("\n classification report:")

    print(
        classification_report(
            y_true,
            y_pred,
            digits=4,
            zero_division=0,
        )
    )

    print("\n Matriz de Confusão:")

    print(
        confusion_matrix(
            y_true,
            y_pred,
            labels=[0, 1],
        )
    )

    print("\nMétricas:")

    for name, value in metrics.items():
        print(f"{name}: {value:.5f}")

    return metrics


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Avalia o checkpoint experimental "
            "PyTorch do FraudShield AI."
        )
    )

    parser.add_argument(
        "--checkpoint",
        default="artifacts/pytorch/best_model.pt",
    )

    parser.add_argument(
        "--dataset",
        default="data/raw/creditcard.csv",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=512,
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
    )

    parser.add_argument(
        "--allow-legacy-checkpoint",
        action="store_true",
        help=(
            "Permite carregar checkpoints antigos "
            "com objetos NumPy. Use somente com "
            "arquivos de origem confiável."
        ),
    )

    args = parser.parse_args()

    evaluate_checkpoint(
        checkpoint_path=args.checkpoint,
        dataset_path=args.dataset,
        batch_size=args.batch_size,
        threshold=args.threshold,
        allow_legacy=args.allow_legacy_checkpoint,
    )


if __name__ == "__main__":
    main()
