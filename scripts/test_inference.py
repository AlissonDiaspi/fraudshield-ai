
from pathlib import Path

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)

from fraudshield.model_io import load_model
from fraudshield.inference import predict_fraud
import pandas as pd
from fraudshield.config import MODEL_CONFIG


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
)

MODEL_PATH = MODEL_CONFIG.model_path


def main():
    print("Inferência")

    print("\n[1/3] Carregando modelo...")

    model = load_model(MODEL_PATH)

    print("Modelo carregado com sucesso!")

    print("\n[2/3] Preparando transações...")

    df = load_dataset(DATA_PATH)

    X, y = split_features_target(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(X, y)

    # Seleciona exemplos da validação:
    # 3 transações legítimas e 3 fraudulentas.
    legitimate_samples = X_val.loc[
        y_val[y_val == 0].index
    ].head(3)

    fraud_samples = X_val.loc[
        y_val[y_val == 1].index
    ].head(3)

    samples = pd.concat(
    [legitimate_samples, fraud_samples],
    axis=0
)

    print(f"Transações selecionadas: {len(samples)}")

    print("\n[3/3] Realizando previsões...")

    results = predict_fraud(
    model=model,
    transactions=samples,
    threshold=MODEL_CONFIG.threshold
)

    results["actual_class"] = y_val.loc[results.index]

    print("\nResultados:")
    print(results.to_string())

    print("\nInferência concluída com sucesso!")


if __name__ == "__main__":
    main()
