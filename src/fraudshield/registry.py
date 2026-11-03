
import mlflow

from mlflow import MlflowClient


REGISTERED_MODEL_NAME = "FraudShield-FraudDetector"


def register_model_from_run(
    run_id: str,
    model_name: str = REGISTERED_MODEL_NAME
) -> int:
    """
    Registra no Model Registry o modelo
    associado a uma execução do MLflow.
    """

    client = MlflowClient()

    # Recupera a execução para identificar
    # a qual experimento ela pertence.
    run = client.get_run(run_id)

    experiment_id = run.info.experiment_id

    # Procura os modelos registrados
    # durante essa execução.
    logged_models = client.search_logged_models(
        experiment_ids=[experiment_id],
        filter_string=f"source_run_id = '{run_id}'"
    )

    if not logged_models:
        raise ValueError(
            "Nenhum modelo encontrado para "
            f"o run_id={run_id}."
        )

    model = next(
        (
            item
            for item in logged_models
            if item.name == "model"
        ),
        None
    )

    if model is None:
        raise ValueError(
            "Nenhum modelo com o nome 'model' "
            "foi encontrado nessa execução."
        )

    model_uri = f"models:/{model.model_id}"

    print(f"Modelo encontrado: {model_uri}")

    registered = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
        await_registration_for=60
    )

    return int(registered.version)


def set_champion_alias(
    version: int,
    model_name: str = REGISTERED_MODEL_NAME
) -> None:
    """
    Associa o alias champion a uma versão.
    """

    client = MlflowClient()

    client.set_registered_model_alias(
        name=model_name,
        alias="champion",
        version=str(version)
    )


def get_champion_version(
    model_name: str = REGISTERED_MODEL_NAME
):
    """
    Recupera a versão associada ao
    alias champion.
    """

    client = MlflowClient()

    return client.get_model_version_by_alias(
        name=model_name,
        alias="champion"
    )
