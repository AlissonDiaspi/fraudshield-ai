
from unittest.mock import MagicMock, patch

import pytest
from xgboost import XGBClassifier

from fraudshield.registry_loader import (
    load_registered_model_info,
    load_registered_model
)


@patch("fraudshield.registry_loader.mlflow.xgboost.load_model")
@patch("fraudshield.registry_loader.MlflowClient")
def test_load_registered_model_info(
    mock_client_class,
    mock_load_model
):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_version = MagicMock()
    mock_version.version = "1"

    mock_client.get_model_version_by_alias.return_value = (
        mock_version
    )

    mock_model = XGBClassifier()
    mock_load_model.return_value = mock_model

    result = load_registered_model_info()

    assert result.model is mock_model
    assert result.version == "1"
    assert result.alias == "champion"

    mock_load_model.assert_called_once_with(
        "models:/FraudShield-FraudDetector/1"
    )


@patch("fraudshield.registry_loader.mlflow.xgboost.load_model")
@patch("fraudshield.registry_loader.MlflowClient")
def test_load_registered_model_invalid_type(
    mock_client_class,
    mock_load_model
):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_version = MagicMock()
    mock_version.version = "1"

    mock_client.get_model_version_by_alias.return_value = (
        mock_version
    )

    mock_load_model.return_value = object()

    with pytest.raises(TypeError):
        load_registered_model_info()


@patch("fraudshield.registry_loader.mlflow.xgboost.load_model")
@patch("fraudshield.registry_loader.MlflowClient")
def test_load_registered_model_returns_classifier(
    mock_client_class,
    mock_load_model
):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_version = MagicMock()
    mock_version.version = "1"

    mock_client.get_model_version_by_alias.return_value = (
        mock_version
    )

    mock_model = XGBClassifier()
    mock_load_model.return_value = mock_model

    result = load_registered_model()

    assert result is mock_model


@patch("fraudshield.registry_loader.MlflowClient")
def test_registry_unavailable(
    mock_client_class
):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.get_model_version_by_alias.side_effect = (
        ConnectionError("MLflow indisponível")
    )

    with pytest.raises(
        ConnectionError,
        match="MLflow indisponível"
    ):
        load_registered_model_info()
