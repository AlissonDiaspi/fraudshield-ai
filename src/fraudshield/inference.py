
import numpy as np
import pandas as pd

from xgboost import XGBClassifier


def predict_fraud(
    model: XGBClassifier,
    transactions: pd.DataFrame,
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Recebe transações e retorna os scores
    e as classificações de fraude.
    """

    if not 0 <= threshold <= 1:
        raise ValueError(
            "O threshold deve estar entre 0 e 1."
        )

    if transactions.empty:
        raise ValueError(
            "Nenhuma transação foi fornecida."
        )

    expected_features = model.get_booster().feature_names

    if expected_features is None:
        raise ValueError(
            "O modelo não possui nomes de features registrados."
        )

    missing_features = [
        feature
        for feature in expected_features
        if feature not in transactions.columns
    ]

    extra_features = [
        feature
        for feature in transactions.columns
        if feature not in expected_features
    ]

    if missing_features or extra_features:
        raise ValueError(
            f"Features ausentes: {missing_features}. "
            f"Features extras: {extra_features}."
        )

    # Garante a mesma ordem usada no treinamento.
    X = transactions.loc[:, expected_features].copy()

    # Nesta primeira versão, exigimos valores numéricos válidos.
    if not all(pd.api.types.is_numeric_dtype(X[col]) for col in X):
        raise ValueError(
            "Todas as features devem ser numéricas."
        )

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError(
            "As features não podem conter NaN ou infinito."
        )

    probabilities = model.predict_proba(X)[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    return pd.DataFrame(
        {
            "fraud_score": probabilities,
            "prediction": predictions
        },
        index=transactions.index
    )
