
import argparse

import mlflow
import os

from fraudshield.registry import (
    REGISTERED_MODEL_NAME,
    register_model_from_run,
    set_champion_alias,
    get_champion_version
)


TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Registra uma execução do FraudShield "
            "no MLflow Model Registry."
        )
    )

    parser.add_argument(
        "--run-id",
        required=True,
        help="ID da execução que contém o modelo."
    )

    args = parser.parse_args()

    print(
        "=== FRAUDSHIELD AI — MODEL REGISTRY ==="
    )

    mlflow.set_tracking_uri(TRACKING_URI)

    print("\nRegistrando modelo...")

    version = register_model_from_run(
        run_id=args.run_id
    )

    print(
        f"Modelo registrado: {REGISTERED_MODEL_NAME}"
    )

    print(f"Versão criada: {version}")

    # Nesta etapa, estamos promovendo
    # explicitamente nossa versão inicial.
    print("\nDefinindo alias champion...")

    set_champion_alias(
        version=version
    )

    champion = get_champion_version()

    print("\nRegistro concluído!")

    print(
        f"Champion: versão {champion.version}"
    )

    print(
        f"Run ID: {champion.run_id}"
    )

    print(
        "\nURI do modelo:"
    )

    print(
        f"models:/{REGISTERED_MODEL_NAME}@champion"
    )


if __name__ == "__main__":
    main()
