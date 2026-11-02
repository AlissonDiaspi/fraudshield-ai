
import numpy as np
import pandas as pd
import pytest

from fraudshield.inference import predict_fraud


class FakeModel:
    """
    Simula um modelo treinado para testar
    a lógica de inferência sem usar XGBoost real.
    """

    def get_booster(self):
        return self

    @property
    def feature_names(self):
        return ["V1", "V2", "Amount"]

    def predict_proba(self, X):
        scores = np.array([0.1, 0.9])

        return np.column_stack([
            1 - scores,
            scores
        ])[:len(X)]


@pytest.fixture
def model():
    return FakeModel()


@pytest.fixture
def transactions():
    return pd.DataFrame({
        "V1": [0.5, -1.2],
        "V2": [1.0, 0.3],
        "Amount": [100.0, 250.0]
    })


def test_predict_fraud_returns_predictions(
    model,
    transactions
):
    result = predict_fraud(
        model,
        transactions,
        threshold=0.5
    )

    assert len(result) == 2
    assert result["prediction"].tolist() == [0, 1]
    assert "fraud_score" in result.columns


def test_predict_fraud_invalid_threshold(
    model,
    transactions
):
    with pytest.raises(ValueError):
        predict_fraud(
            model,
            transactions,
            threshold=1.5
        )


def test_predict_fraud_empty_dataframe(model):
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError):
        predict_fraud(
            model,
            empty_df
        )


def test_predict_fraud_missing_feature(
    model,
    transactions
):
    invalid_df = transactions.drop(columns=["V2"])

    with pytest.raises(ValueError):
        predict_fraud(
            model,
            invalid_df
        )


def test_predict_fraud_extra_feature(
    model,
    transactions
):
    invalid_df = transactions.copy()
    invalid_df["Unexpected"] = 10

    with pytest.raises(ValueError):
        predict_fraud(
            model,
            invalid_df
        )


def test_predict_fraud_nan_values(
    model,
    transactions
):
    invalid_df = transactions.copy()
    invalid_df.loc[0, "V1"] = np.nan

    with pytest.raises(ValueError):
        predict_fraud(
            model,
            invalid_df
        )
