
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

from fraudshield.training import (
    build_model,
    train_model
)

from fraudshield.model_io import save_model

from fraudshield.tracking import (
    configure_tracking,
    log_model_experiment
)


def main():
    print("=== FRAUDSHIELD AI — TRAINING PIPELINE ===")

    dataset_path = (
        PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
    )

    print("\n1. Carregando dataset...")

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

    print("\n2. Construindo modelo...")

    model = build_model(y_train)

    print("\n3. Treinando XGBoost...")

    model = train_model(
        model,
        X_train,
        y_train
    )

    print("\n4. Avaliando na validação...")

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

    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")

    print("\n5. Salvando modelo...")

    save_model(
        model,
        MODEL_CONFIG.model_path
    )

    print(
        f"Modelo salvo em: {MODEL_CONFIG.model_path}"
    )

    print("\n6. Registrando no MLflow...")

    configure_tracking()

    run_id = log_model_experiment(
        model=model,
        metrics=metrics,
        model_path=MODEL_CONFIG.model_path,
        threshold=MODEL_CONFIG.threshold,
        run_name="xgboost-training-pipeline-v1"
    )

    print("\nTreinamento concluído!")
    print(f"MLflow Run ID: {run_id}")
    print("Tracking UI: http://127.0.0.1:5000")


if __name__ == "__main__":
    main()
