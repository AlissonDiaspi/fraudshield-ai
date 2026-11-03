
import os
from dataclasses import dataclass

import mlflow
import mlflow.xgboost

from mlflow import MlflowClient
from xgboost import XGBClassifier

from fraudshield.registry import REGISTERED_MODEL_NAME


@dataclass(frozen=True)
class LoadedRegisteredModel:
    model: XGBClassifier
    version: str
    model_name: str
    alias: str


def load_registered_model_info(
    model_name: str = REGISTERED_MODEL_NAME,
    alias: str = "champion"
) -> LoadedRegisteredModel:

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000"
    )

    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    # Resolve o alias para uma versão específica.
    model_version = client.get_model_version_by_alias(
        name=model_name,
        alias=alias
    )

    version = str(model_version.version)

    # Carrega a versão fixa, evitando que uma
    # mudança de alias entre as duas chamadas
    # carregue uma versão diferente.
    model_uri = f"models:/{model_name}/{version}"

    print(f"Carregando modelo: {model_uri}")

    model = mlflow.xgboost.load_model(model_uri)

    if not isinstance(model, XGBClassifier):
        raise TypeError(
            "O modelo carregado não é um XGBClassifier."
        )

    print(f"Modelo carregado! Versão: {version}")

    return LoadedRegisteredModel(
        model=model,
        version=version,
        model_name=model_name,
        alias=alias
    )


def load_registered_model(
    model_name: str = REGISTERED_MODEL_NAME,
    alias: str = "champion"
) -> XGBClassifier:
    """
    Mantém compatibilidade com os scripts
    existentes que esperam apenas o modelo.
    """

    return load_registered_model_info(
        model_name=model_name,
        alias=alias
    ).model
