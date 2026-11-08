
import argparse
import os
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch

from fraudshield.pytorch.model import FraudMLP
from scripts.evaluate_pytorch import (
    evaluate_checkpoint,
    load_checkpoint,
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Registra o experimento PyTorch "
            "do FraudShield AI no MLflow."
        )
    )

    parser.add_argument(
        "--checkpoint",
        default="artifacts/pytorch/best_model.pt",
        help="Caminho do checkpoint PyTorch.",
    )

    parser.add_argument(
        "--dataset",
        default="data/raw/creditcard.csv",
        help="Caminho do dataset utilizado.",
    )

    parser.add_argument(
        "--allow-legacy-checkpoint",
        action="store_true",
        help=(
            "Permite carregar checkpoints antigos "
            "com objetos NumPy. Utilize somente "
            "com arquivos confiáveis."
        ),
    )

    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint)

    if not checkpoint_path.is_file():
        raise FileNotFoundError(
            f"Checkpoint não encontrado: {checkpoint_path}"
        )

    # Carrega o checkpoint experimental.
    checkpoint = load_checkpoint(
        checkpoint_path,
        allow_legacy=args.allow_legacy_checkpoint,
    )

    # Avalia o modelo no conjunto de teste.
    metrics = evaluate_checkpoint(
        checkpoint_path=str(checkpoint_path),
        dataset_path=args.dataset,
        allow_legacy=args.allow_legacy_checkpoint,
    )

    # Configura o servidor MLflow.
    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )

    mlflow.set_tracking_uri(tracking_uri)

    experiment_name = "FraudShield-PyTorch-Experiments"

    mlflow.set_experiment(experiment_name)

    # Reconstrói a arquitetura da rede neural.
    model = FraudMLP(
        input_dim=int(checkpoint["input_dim"]),
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    # Exemplo de entrada necessário para a
    # serialização pt2 do MLflow.
    input_example = torch.zeros(
        1,
        int(checkpoint["input_dim"]),
        dtype=torch.float32,
    )

    config = checkpoint["config"]

    print("\n=== REGISTRO NO MLFLOW ===")
    print("Tracking URI:", tracking_uri)
    print("Experimento:", experiment_name)
    print("Modelo:", "FraudMLP")
    print("Melhor época:", checkpoint["best_epoch"])

    with mlflow.start_run(
        run_name="pytorch-mlp-experiment"
    ) as run:

        # Identifica o modelo como experimental.
        mlflow.set_tags({
            "framework": "pytorch",
            "model_type": "MLP",
            "role": "experimental",
            "production_candidate": "false",
            "project": "FraudShield AI",
        })

        # Registra hiperparâmetros.
        mlflow.log_params({
            "input_dim": int(
                checkpoint["input_dim"]
            ),
            "batch_size": int(
                config["batch_size"]
            ),
            "learning_rate": float(
                config["learning_rate"]
            ),
            "max_epochs": int(
                config["epochs"]
            ),
            "patience": int(
                config["patience"]
            ),
            "random_state": int(
                config["random_state"]
            ),
            "threshold": 0.5,
        })

        # Registra as métricas de teste.
        mlflow.log_metrics({
            **metrics,
            "best_val_ap": float(
                checkpoint["best_val_ap"]
            ),
            "best_epoch": int(
                checkpoint["best_epoch"]
            ),
        })

        # Preserva o checkpoint original.
        mlflow.log_artifact(
            str(checkpoint_path),
            artifact_path="checkpoints",
        )

       
        mlflow.pytorch.log_model(
    pytorch_model=model,
    name="pytorch_model",
    serialization_format="pickle",
)

        print("\nMflow:")
        print("Experimento registrado com sucesso.")
        print("Run ID:", run.info.run_id)
        print("Tracking URI:", tracking_uri)
        print("Experimento:", experiment_name)


if __name__ == "__main__":
    main()
