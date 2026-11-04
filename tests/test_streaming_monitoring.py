
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from fraudshield.streaming.persistence_service import (
    StreamingPersistenceService,
)
from fraudshield.streaming.schemas import (
    PredictionEvent,
    TransactionEvent,
)


def make_transaction():
    return TransactionEvent.model_construct(
        event_id=uuid4(),
        features={"V1": 0.5},
    )


def make_prediction(event_id):
    return PredictionEvent(
        event_id=event_id,
        fraud_score=0.85,
        prediction=1,
        model_version="1",
    )


def make_database_context(db):
    context = MagicMock()
    context.__enter__.return_value = db
    context.__exit__.return_value = False
    return context


def test_successful_prediction_records_metrics():
    event = make_transaction()
    result = make_prediction(event.event_id)

    inference = MagicMock()
    inference.predict.return_value = result

    monitoring = MagicMock()

    db = MagicMock()
    context = make_database_context(db)

    with (
        patch(
            "fraudshield.streaming.persistence_service.SessionLocal",
            return_value=context,
        ),
        patch(
            "fraudshield.streaming.persistence_service.PredictionRepository"
        ) as prediction_repository_class,
        patch(
            "fraudshield.streaming.persistence_service.OutboxRepository"
        ),
    ):
        prediction_repository = (
            prediction_repository_class.return_value
        )
        prediction_repository.get_by_event_id.return_value = None

        service = StreamingPersistenceService(
            inference_service=inference,
            monitoring_service=monitoring,
        )

        returned = service.process(event)

    assert returned == result

    inference.predict.assert_called_once_with(event)

    monitoring.track_inference.assert_called_once()
    monitoring.record_prediction.assert_called_once_with(1)

    db.commit.assert_called_once()


def test_duplicate_event_does_not_record_metrics():
    event = make_transaction()

    existing = SimpleNamespace(
        event_id=event.event_id,
        fraud_score=0.10,
        prediction=0,
        model_version="1",
    )

    inference = MagicMock()
    monitoring = MagicMock()

    db = MagicMock()
    context = make_database_context(db)

    with (
        patch(
            "fraudshield.streaming.persistence_service.SessionLocal",
            return_value=context,
        ),
        patch(
            "fraudshield.streaming.persistence_service.PredictionRepository"
        ) as prediction_repository_class,
        patch(
            "fraudshield.streaming.persistence_service.OutboxRepository"
        ) as outbox_repository_class,
    ):
        prediction_repository_class.return_value.get_by_event_id.return_value = (
            existing
        )

        outbox_repository_class.return_value.get_by_event_and_topic.return_value = (
            SimpleNamespace(id=uuid4())
        )

        service = StreamingPersistenceService(
            inference_service=inference,
            monitoring_service=monitoring,
        )

        returned = service.process(event)

    assert returned.prediction == 0

    inference.predict.assert_not_called()
    monitoring.track_inference.assert_not_called()
    monitoring.record_prediction.assert_not_called()


def test_inference_failure_does_not_record_prediction():
    event = make_transaction()

    inference = MagicMock()
    inference.predict.side_effect = RuntimeError(
        "Falha na inferência"
    )

    monitoring = MagicMock()

    db = MagicMock()
    context = make_database_context(db)

    with (
        patch(
            "fraudshield.streaming.persistence_service.SessionLocal",
            return_value=context,
        ),
        patch(
            "fraudshield.streaming.persistence_service.PredictionRepository"
        ) as prediction_repository_class,
        patch(
            "fraudshield.streaming.persistence_service.OutboxRepository"
        ),
    ):
        prediction_repository_class.return_value.get_by_event_id.return_value = (
            None
        )

        service = StreamingPersistenceService(
            inference_service=inference,
            monitoring_service=monitoring,
        )

        with pytest.raises(
            RuntimeError,
            match="Falha na inferência",
        ):
            service.process(event)

    monitoring.track_inference.assert_called_once()
    monitoring.record_prediction.assert_not_called()

    db.rollback.assert_called_once()
