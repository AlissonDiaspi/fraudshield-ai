
from pathlib import Path

import httpx

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
)

API_URL = "http://127.0.0.1:8000/predict"


def main():
    print("Teste da API")

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

    # Seleciona uma fraude do conjunto de validação.
    fraud_index = y_val[y_val == 1].index[0]

    transaction = X_val.loc[fraud_index]

    payload = {
        "features": {
            column: float(value)
            for column, value in transaction.items()
        }
    }

    print(f"\nTransação selecionada: {fraud_index}")
    print("Classe real: fraude")

    print("\nEnviando transação para a API...")

    response = httpx.post(
        API_URL,
        json=payload,
        timeout=30.0
    )

    print(f"\nStatus HTTP: {response.status_code}")

    print("\nResposta da API:")
    print(response.json())

    response.raise_for_status()


if __name__ == "__main__":
    main()
