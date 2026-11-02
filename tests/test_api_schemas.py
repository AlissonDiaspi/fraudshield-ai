
import pytest
from pydantic import ValidationError

from fraudshield.api.schemas import PredictionRequest


@pytest.fixture
def valid_features():
    features = {
        f"V{i}": float(i)
        for i in range(1, 29)
    }

    features["Time"] = 100.0
    features["Amount"] = 50.0

    return features


def test_valid_transaction(valid_features):
    payload = PredictionRequest(
        features=valid_features
    )

    assert len(payload.features) == 30


def test_missing_feature(valid_features):
    del valid_features["V1"]

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_extra_feature(valid_features):
    valid_features["V29"] = 10.0

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_negative_amount(valid_features):
    valid_features["Amount"] = -100.0

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_negative_time(valid_features):
    valid_features["Time"] = -1.0

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_nan_value(valid_features):
    valid_features["V1"] = float("nan")

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_infinite_value(valid_features):
    valid_features["V1"] = float("inf")

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)


def test_string_value(valid_features):
    valid_features["Amount"] = "100"

    with pytest.raises(ValidationError):
        PredictionRequest(features=valid_features)
