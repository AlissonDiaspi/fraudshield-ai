
import argparse
import os

import mlflow

from fraudshield.registry import (
    REGISTERED_MODEL_NAME,
    get_champion_version,
    register_model_from_run,
    set_champion_alias,
)

from scripts.train_model import main as train_main


def configure_mlflow() -> None:
    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )

    mlflow.set_tracking_uri(tracking_uri)

    print(f"MLflow Tracking URI: {tracking_uri}")


def champion_exists() -> bool:
    client = mlflow.MlflowClient()

    try:
        client.get_model_version_by_alias(
            name=REGISTERED_MODEL_NAME,
            alias="champion",
        )
        return True

    except mlflow.exceptions.RestException as exc:
        if exc.error_code == "RESOURCE_DOES_NOT_EXIST":
            return False
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepara o modelo champion do FraudShield AI."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Treina e registra uma nova versão mesmo se já existir um champion.",
    )

    args = parser.parse_args()

    print("=== FRAUDSHIELD AI — MODEL BOOTSTRAP ===")

    configure_mlflow()

    if not args.force and champion_exists():
        champion = get_champion_version()

        print(
            f"Champion já existe: versão {champion.version}"
        )
        print("Nenhuma alteração realizada.")
        return

    

    run_id = train_main()

    if not isinstance(run_id, str) or not run_id:
        raise RuntimeError(
            "O treinamento não retornou um run_id válido."
        )

    print(f"\nRegistrando modelo do run {run_id}...")

    version = register_model_from_run(
        run_id=run_id
    )

    set_champion_alias(
        version=version
    )

    champion = get_champion_version()

    print("\nBootstrap concluído")
    print(f"Modelo: {REGISTERED_MODEL_NAME}")
    print(f"Versão champion: {champion.version}")
    print(f"Run ID: {champion.run_id}")


if __name__ == "__main__":
    main()
