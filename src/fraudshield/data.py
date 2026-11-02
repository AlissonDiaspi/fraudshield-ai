from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    """
    Carrega o dataset de transações financeiras.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("O dataset está vazio.")

    if "Class" not in df.columns:
        raise ValueError(
            "O dataset precisa conter a coluna 'Class'."
        )

    return df


def split_features_target(
    df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separa as variáveis de entrada da variável alvo.
    """

    X = df.drop(columns=["Class"])
    y = df["Class"]

    return X, y

def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42
) -> tuple:
    """
    Divide o dataset em treino, validação e teste.

    Proporções:
    - Treino: 70%
    - Validação: 15%
    - Teste: 15%

    A estratificação preserva aproximadamente
    a proporção de fraudes em cada conjunto.
    """

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=random_state,
        stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=random_state,
        stratify=y_temp
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    )