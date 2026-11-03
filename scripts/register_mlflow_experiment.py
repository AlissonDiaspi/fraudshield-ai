
from pathlib import Path

from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from fraudshield.config import (
    MODEL_CONFIG,
    PROJECT_ROOT
)

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)

from fraudshield.model_io import load_model

from fraudshield.tracking import (
    configure_tracking,
    log_model_experiment
)


def main():
    print(
        "=== FRAUDSHIELD AI — MLFLOW EXPERIMENT ==="
    )

    dataset_path = (
        PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
    )

    print("\nCarregando dataset...")

    df = load_dataset(dataset_path)

    X, y = split_features_target(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(
        X,
        y,
        random_state=MODEL_CONFIG.random_state
    )

    print("Carregando modelo salvo...")

    model = load_model(
        MODEL_CONFIG.model_path
    )

    print("Calculando métricas de validação...")

    probabilities = model.predict_proba(
        X_val
    )[:, 1]

    predictions = (
        probabilities >= MODEL_CONFIG.threshold
    ).astype(int)

    metrics = {
        "validation_average_precision": float(
            average_precision_score(
                y_val,
                probabilities
            )
        ),

        "validation_precision": float(
            precision_score(
                y_val,
                predictions,
                zero_division=0
            )
        ),

        "validation_recall": float(
            recall_score(
                y_val,
                predictions,
                zero_division=0
            )
        ),

        "validation_f1": float(
            f1_score(
                y_val,
                predictions,
                zero_division=0
            )
        ),

        "validation_roc_auc": float(
            roc_auc_score(
                y_val,
                probabilities
            )
        )
    }

    configure_tracking()

    print("\nRegistrando experimento no MLflow...")

    run_id = log_model_experiment(
        model=model,
        metrics=metrics,
        model_path=MODEL_CONFIG.model_path,
        threshold=MODEL_CONFIG.threshold
    )

    print("\nExperimento registrado!")

    print(f"Run ID: {run_id}")

    print("\nMétricas:")

    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")

    print(
        "\nAcesse: http://127.0.0.1:5000"
    )


if __name__ == "__main__":
    main()
