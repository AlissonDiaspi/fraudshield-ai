
from pathlib import Path

import mlflow
import mlflow.xgboost

from xgboost import XGBClassifier
import os


EXPERIMENT_NAME = "fraudshield-xgboost"


def configure_tracking(
    tracking_uri: str | None = None
) -> None:
    uri = tracking_uri or os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000"
    )

    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(EXPERIMENT_NAME)


def log_model_experiment(
    model: XGBClassifier,
    metrics: dict[str, float],
    model_path: Path,
    threshold: float,
    run_name: str = "xgboost-optimized-v1"
) -> str:

    with mlflow.start_run(
        run_name=run_name
    ) as run:

        # Registra hiperparâmetros do modelo.
        mlflow.log_params(
            model.get_params()
        )

        # Registra o threshold utilizado.
        mlflow.log_param(
            "decision_threshold",
            threshold
        )

        # Registra as métricas calculadas.
        mlflow.log_metrics(metrics)

        # Guarda o JSON original como artefato.
        mlflow.log_artifact(
            str(model_path),
            artifact_path="original_model"
        )

        # Registra o modelo no formato MLflow.
        mlflow.xgboost.log_model(
            xgb_model=model,
            name="model"
        )

        return run.info.run_id
