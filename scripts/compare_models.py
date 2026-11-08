
import os

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import mlflow.xgboost

import numpy as np

from mlflow.models import Model

from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset,
)


DATASET_PATH = "data/raw/creditcard.csv"

MODEL_URI = "models:/FraudShield-FraudDetector/1"

THRESHOLD = 0.5

RANDOM_STATE = 42


PYTORCH_METRICS = {
    "average_precision": 0.728076399504229,
    "roc_auc": 0.971361414875765,
    "precision": 0.08301404853128991,
    "recall": 0.8783783783783784,
    "f1": 0.1516919486581097,
}


def load_registered_model(model_uri: str):
    """
    Identifica o flavor do modelo registrado
    e utiliza o carregador correspondente.
    """
    model_info = Model.load(model_uri)

    flavors = model_info.flavors

    print("\nFlavors disponíveis:")
    print(list(flavors.keys()))

    if "xgboost" in flavors:
        print("Carregando modelo com mlflow.xgboost")

        model = mlflow.xgboost.load_model(
            model_uri
        )

        return model, "xgboost"

    if "sklearn" in flavors:
        print("Carregando modelo com mlflow.sklearn")

        model = mlflow.sklearn.load_model(
            model_uri
        )

        return model, "sklearn"

    if "python_function" in flavors:
        print("Carregando modelo com mlflow.pyfunc")

        model = mlflow.pyfunc.load_model(
            model_uri
        )

        return model, "pyfunc"

    raise ValueError(
        "Nenhum flavor compatível foi encontrado. "
        f"Flavors: {list(flavors.keys())}"
    )


def predict_probabilities(
    model,
    model_type: str,
    features,
) -> np.ndarray:
    """
    Obtém probabilidades da classe fraude.
    """
    if model_type in ("xgboost", "sklearn"):
        probabilities = model.predict_proba(
            features
        )

        probabilities = np.asarray(
            probabilities
        )

        if probabilities.ndim == 2:
            if probabilities.shape[1] != 2:
                raise ValueError(
                    "Saída de probabilidades inesperada."
                )

            return probabilities[:, 1]

        if probabilities.ndim == 1:
            return probabilities

        raise ValueError(
            "Formato de probabilidades inválido."
        )

    if model_type == "pyfunc":
        predictions = model.predict(
            features
        )

        predictions = np.asarray(
            predictions
        )

        if predictions.ndim == 2:
            if predictions.shape[1] != 2:
                raise ValueError(
                    "Saída pyfunc com formato inesperado."
                )

            return predictions[:, 1]

        if predictions.ndim == 1:
            return predictions

        raise ValueError(
            "Formato de saída pyfunc inválido."
        )

    raise ValueError(
        f"Tipo de modelo não suportado: {model_type}"
    )


def calculate_metrics(
    y_true,
    y_prob,
    threshold: float = 0.5,
) -> tuple[dict, np.ndarray]:
    """
    Calcula as métricas de classificação binária.
    """
    y_prob = np.asarray(
        y_prob,
        dtype=float,
    ).ravel()

    if not np.all(np.isfinite(y_prob)):
        raise ValueError(
            "O modelo retornou valores não finitos."
        )

    if np.any((y_prob < 0) | (y_prob > 1)):
        raise ValueError(
            "A saída do modelo não contém "
            "probabilidades entre 0 e 1."
        )

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

    return metrics, y_pred


def print_comparison(
    xgboost_metrics: dict,
    pytorch_metrics: dict,
) -> None:
    """
    Exibe a comparação das métricas.
    """
    print("\n=== COMPARAÇÃO FINAL ===")

    print(
        f"{'Métrica':<22}"
        f"{'XGBoost':>12}"
        f"{'PyTorch':>12}"
        f"{'Maior valor':>16}"
    )

    print("-" * 62)

    for metric, xgboost_value in xgboost_metrics.items():
        pytorch_value = pytorch_metrics[metric]

        if np.isclose(
            xgboost_value,
            pytorch_value,
            atol=1e-8,
        ):
            winner = "Empate"

        elif xgboost_value > pytorch_value:
            winner = "XGBoost"

        else:
            winner = "PyTorch"

        print(
            f"{metric:<22}"
            f"{xgboost_value:>12.5f}"
            f"{pytorch_value:>12.5f}"
            f"{winner:>16}"
        )


def main():
    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )

    mlflow.set_tracking_uri(
        tracking_uri
    )

    print("\n=== FRAUDSHIELD AI ===")
    print("Comparação XGBoost vs PyTorch")
    print("Tracking URI:", tracking_uri)
    print("Modelo:", MODEL_URI)

    # Carrega os dados e utiliza a mesma
    # divisão de teste da rede neural.
    df = load_dataset(
        DATASET_PATH
    )

    X, y = split_features_target(
        df
    )

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(
        X,
        y,
        random_state=RANDOM_STATE,
    )

    print("\n=== DATASET ===")
    print("Amostras de treino:", len(X_train))
    print("Amostras de validação:", len(X_val))
    print("Amostras de teste:", len(X_test))
    print("Fraudes no teste:", int(y_test.sum()))

    # Carrega o modelo XGBoost registrado.
    model, model_type = load_registered_model(
        MODEL_URI
    )

    # Obtém as probabilidades da classe fraude.
    y_prob = predict_probabilities(
        model,
        model_type,
        X_test,
    )

    # Calcula métricas.
    metrics, y_pred = calculate_metrics(
        y_test,
        y_prob,
        threshold=THRESHOLD,
    )

    print("\n=== XGBOOST — TESTE ===")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            digits=4,
            zero_division=0,
        )
    )

    print("\nMatriz de confusão:")

    print(
        confusion_matrix(
            y_test,
            y_pred,
            labels=[0, 1],
        )
    )

    print("\nMétricas:")

    for name, value in metrics.items():
        print(
            f"{name}: {value:.5f}"
        )

    print("\n=== PYTORCH — TESTE ===")

    for name, value in PYTORCH_METRICS.items():
        print(
            f"{name}: {value:.5f}"
        )

    print_comparison(
        metrics,
        PYTORCH_METRICS,
    )

    


if __name__ == "__main__":
    main()
