
from unittest.mock import patch

import pytest

from fraudshield.monitoring.service import MonitoringService


def test_record_legitimate_prediction():
    monitoring = MonitoringService()

    with (
        patch(
            "fraudshield.monitoring.service.TRANSACTIONS_PROCESSED"
        ) as transactions,
        patch(
            "fraudshield.monitoring.service.PREDICTIONS_TOTAL"
        ) as predictions,
    ):
        monitoring.record_prediction(0)

        transactions.inc.assert_called_once()

        predictions.labels.assert_called_once_with(
            prediction="0"
        )

        predictions.labels.return_value.inc.assert_called_once()


def test_record_fraud_prediction():
    monitoring = MonitoringService()

    with (
        patch(
            "fraudshield.monitoring.service.TRANSACTIONS_PROCESSED"
        ) as transactions,
        patch(
            "fraudshield.monitoring.service.PREDICTIONS_TOTAL"
        ) as predictions,
    ):
        monitoring.record_prediction(1)

        transactions.inc.assert_called_once()

        predictions.labels.assert_called_once_with(
            prediction="1"
        )


@pytest.mark.parametrize("prediction", [-1, 2, 10])
def test_invalid_prediction(prediction):
    monitoring = MonitoringService()

    with pytest.raises(ValueError):
        monitoring.record_prediction(prediction)


def test_inference_duration_and_gauge():
    monitoring = MonitoringService()

    with (
        patch(
            "fraudshield.monitoring.service.INFERENCE_DURATION"
        ) as duration,
        patch(
            "fraudshield.monitoring.service.INFERENCE_IN_PROGRESS"
        ) as gauge,
    ):
        with monitoring.track_inference():
            result = 2 + 2

        assert result == 4

        gauge.inc.assert_called_once()
        gauge.dec.assert_called_once()

        duration.observe.assert_called_once()

        recorded_duration = duration.observe.call_args.args[0]

        assert recorded_duration >= 0


def test_inference_error():
    monitoring = MonitoringService()

    with (
        patch(
            "fraudshield.monitoring.service.INFERENCE_ERRORS"
        ) as errors,
        patch(
            "fraudshield.monitoring.service.INFERENCE_IN_PROGRESS"
        ) as gauge,
        patch(
            "fraudshield.monitoring.service.INFERENCE_DURATION"
        ) as duration,
    ):
        with pytest.raises(
            RuntimeError,
            match="Erro simulado",
        ):
            with monitoring.track_inference():
                raise RuntimeError("Erro simulado")

        errors.inc.assert_called_once()
        gauge.inc.assert_called_once()
        gauge.dec.assert_called_once()
        duration.observe.assert_called_once()
