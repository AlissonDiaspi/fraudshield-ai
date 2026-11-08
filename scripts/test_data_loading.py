from pathlib import Path

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"


def main():
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

    print("Divisão do dataset:")

    for name, features, target in [
        ("Treino", X_train, y_train),
        ("Validação", X_val, y_val),
        ("Teste", X_test, y_test)
    ]:
        print(f"\n{name}:")
        print(f"Transações: {len(features)}")
        print(f"Fraudes: {target.sum()}")
        print(f"Taxa de fraude: {target.mean() * 100:.4f}%")

    assert len(X_train) + len(X_val) + len(X_test) == len(df)

    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)

    print("\nTodos os testes passaram!")


if __name__ == "__main__":
    main()