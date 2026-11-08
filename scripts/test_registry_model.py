
import numpy as np

from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
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

from fraudshield.registry_loader import (
    load_registered_model
)

from fraudshield.inference import predict_fraud


def main():
    print(
        "Registry model test"
    )

    print("\n1. Carregando modelo do Registry...")

    model = load_registered_model()

    print("\n2. Carregando dataset...")

    dataset_path = (
        PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
    )

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

    print("\n3. Realizando inferência...")

    results = predict_fraud(
        model=model,
        transactions=X_val,
        threshold=MODEL_CONFIG.threshold
    )

    scores = results["fraud_score"].to_numpy()
    predictions = results["prediction"].to_numpy()

    metrics = {
        "average_precision": average_precision_score(
            y_val,
            scores
        ),
        "precision": precision_score(
            y_val,
            predictions,
            zero_division=0
        ),
        "recall": recall_score(
            y_val,
            predictions,
            zero_division=0
        ),
        "f1": f1_score(
            y_val,
            predictions,
            zero_division=0
        )
    }

    print("\n4. Métricas de validação:")

    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")

    print("\n5. Exemplo de previsão:")

    fraud_indices = np.flatnonzero(
        y_val.to_numpy() == 1
    )

    example_position = fraud_indices[0]

    print(
        results.iloc[[example_position]].to_string()
    )

    print("\nTeste concluído!")


if __name__ == "__main__":
    main()
