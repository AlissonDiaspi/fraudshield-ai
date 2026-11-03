
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.persistence_service import (
    StreamingPersistenceService,
)
from fraudshield.streaming.schemas import (
    PredictionEvent,
    TransactionEvent,
)


def make_event():
    # model_construct evita depender das 30 features
    # reais neste teste isolado de persistência.
    return TransactionEvent.model_construct(
        event_id=uuid4(),
        schema_version=1,
        features={"V1": 0.5},
    )


def make_result(event):
    return PredictionEvent(
        event_id=event.event_id,
        fraud_score=0.85,
        prediction=1,
        model_version="1",
    )


@pytest.fixture
def setup_service():
    inference = MagicMock()
    service = StreamingPersistenceService(inference)

    db = MagicMock()
    context = MagicMock()
    context.__enter__.return_value = db
    context.__exit__.return_value = False

    with (
        patch(
            "fraudshield.streaming.persistence_service.SessionLocal",
            return_value=context,
        ),
        patch(
            "fraudshield.streaming.persistence_service.PredictionRepository",
        ) as prediction_repository_class,
        patch(
            "fraudshield.streaming.persistence_service.OutboxRepository",
        ) as outbox_repository_class,
    ):
        predictions = prediction_repository_class.return_value
        outbox = outbox_repository_class.return_value

        yield service, inference, db, predictions, outbox


def test_new_transaction_creates_prediction_and_outbox(
    setup_service,
):
    service, inference, db, predictions, outbox = setup_service

    event = make_event()
    result = make_result(event)

    predictions.get_by_event_id.return_value = None
    inference.predict.return_value = result

    response = service.process(event)

    assert response == result

    predictions.create.assert_called_once()
    outbox.create.assert_called_once()

    outbox.create.assert_called_with(
        event_id=event.event_id,
        topic=KAFKA_CONFIG.predicted_topic,
        payload=result.model_dump(mode="json"),
    )

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_duplicate_transaction_does_not_duplicate_records(
    setup_service,
):
    service, inference, db, predictions, outbox = setup_service

    event = make_event()

    existing = SimpleNamespace(
        event_id=event.event_id,
        fraud_score=0.85,
        prediction=1,
        model_version="1",
    )

    predictions.get_by_event_id.return_value = existing
    outbox.get_by_event_and_topic.return_value = SimpleNamespace(
        status="published",
    )

    response = service.process(event)

    assert response.event_id == event.event_id

    inference.predict.assert_not_called()
    predictions.create.assert_not_called()
    outbox.create.assert_not_called()

    db.commit.assert_not_called()


def test_outbox_failure_rolls_back_prediction(
    setup_service,
):
    service, inference, db, predictions, outbox = setup_service

    event = make_event()
    result = make_result(event)

    predictions.get_by_event_id.return_value = None
    inference.predict.return_value = result

    outbox.create.side_effect = RuntimeError(
        "Falha simulada na Outbox"
    )

    with pytest.raises(
        RuntimeError,
        match="Falha simulada na Outbox",
    ):
        service.process(event)

    predictions.create.assert_called_once()
    outbox.create.assert_called_once()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_existing_prediction_creates_missing_outbox(
    setup_service,
):
    service, inference, db, predictions, outbox = setup_service

    event = make_event()

    existing = SimpleNamespace(
        event_id=event.event_id,
        fraud_score=0.85,
        prediction=1,
        model_version="1",
    )

    predictions.get_by_event_id.return_value = existing
    outbox.get_by_event_and_topic.return_value = None

    response = service.process(event)

    assert response.event_id == event.event_id

    inference.predict.assert_not_called()
    predictions.create.assert_not_called()

    outbox.create.assert_called_once()
    db.commit.assert_called_once()
