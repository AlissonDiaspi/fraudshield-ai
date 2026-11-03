
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from fraudshield.streaming.outbox_publisher import OutboxPublisher


def make_outbox_event():
    return SimpleNamespace(
        id=uuid4(),
        event_id=uuid4(),
        topic="transactions.predicted",
        payload={
            "fraud_score": 0.85,
            "prediction": 1,
            "model_version": "1",
        },
        status="pending",
        attempts=0,
        published_at=None,
        next_attempt_at=None,
    )


@pytest.fixture
def publisher_setup():
    with patch(
        "fraudshield.streaming.outbox_publisher.Producer"
    ) as producer_class:
        producer = producer_class.return_value
        publisher = OutboxPublisher()

        yield publisher, producer


@pytest.fixture
def database_setup():
    with (
        patch(
            "fraudshield.streaming.outbox_publisher.SessionLocal"
        ) as session_class,
        patch(
            "fraudshield.streaming.outbox_publisher.OutboxRepository"
        ) as repository_class,
    ):
        db = MagicMock()

        context = MagicMock()
        context.__enter__.return_value = db
        context.__exit__.return_value = False

        session_class.return_value = context

        repository = repository_class.return_value

        yield db, repository, session_class


def test_successful_kafka_delivery(publisher_setup):
    publisher, producer = publisher_setup
    event = make_outbox_event()

    def simulate_delivery(*args, **kwargs):
        callback = kwargs["on_delivery"]

        message = MagicMock()
        message.topic.return_value = event.topic
        message.partition.return_value = 0
        message.offset.return_value = 10

        callback(None, message)

    producer.produce.side_effect = simulate_delivery
    producer.flush.return_value = 0

    publisher._publish_event(event)

    producer.produce.assert_called_once()
    producer.flush.assert_called_once_with(timeout=20.0)


def test_failed_kafka_delivery(publisher_setup):
    publisher, producer = publisher_setup
    event = make_outbox_event()

    def simulate_failure(*args, **kwargs):
        callback = kwargs["on_delivery"]

        callback(
            RuntimeError("Kafka indisponível"),
            MagicMock(),
        )

    producer.produce.side_effect = simulate_failure
    producer.flush.return_value = 0

    with pytest.raises(
        RuntimeError,
        match="Falha na publicação Kafka",
    ):
        publisher._publish_event(event)


def test_kafka_delivery_timeout(publisher_setup):
    publisher, producer = publisher_setup
    event = make_outbox_event()

    producer.flush.return_value = 1

    with pytest.raises(
        TimeoutError,
        match="Kafka não confirmou",
    ):
        publisher._publish_event(event)


def test_no_pending_events(publisher_setup, database_setup):
    publisher, _ = publisher_setup
    db, repository, _ = database_setup

    repository.get_pending.return_value = []

    published, failed = publisher.publish_pending()

    assert published == 0
    assert failed == 0

    repository.get_pending.assert_called_once_with(limit=1)

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_successful_publication_marks_event_as_published(
    publisher_setup,
    database_setup,
):
    publisher, _ = publisher_setup
    db, repository, _ = database_setup

    event = make_outbox_event()

    repository.get_pending.return_value = [event]

    with patch.object(
        publisher,
        "_publish_event",
    ) as publish_mock:
        published, failed = publisher.publish_pending(limit=1)

    assert published == 1
    assert failed == 0

    assert event.status == "published"
    assert event.published_at is not None
    assert event.next_attempt_at is None

    publish_mock.assert_called_once_with(event)

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_failed_publication_increments_attempts(
    publisher_setup,
    database_setup,
):
    publisher, _ = publisher_setup
    db, repository, session_class = database_setup

    event = make_outbox_event()

    repository.get_pending.return_value = [event]

    with patch.object(
        publisher,
        "_publish_event",
        side_effect=RuntimeError("Falha simulada no Kafka"),
    ):
        published, failed = publisher.publish_pending(limit=1)

    assert published == 0
    assert failed == 1

    assert event.status == "pending"
    assert event.attempts == 1

    assert event.next_attempt_at is not None
    assert event.next_attempt_at.tzinfo is not None

    # A falha é registrada na mesma transação.
    session_class.assert_called_once()

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_failed_publication_schedules_correct_backoff(
    publisher_setup,
    database_setup,
):
    publisher, _ = publisher_setup
    db, repository, _ = database_setup

    event = make_outbox_event()

    # Simula um evento que já falhou duas vezes.
    event.attempts = 2

    repository.get_pending.return_value = [event]

    before = datetime.now(timezone.utc)

    with patch.object(
        publisher,
        "_publish_event",
        side_effect=RuntimeError("Falha simulada"),
    ):
        published, failed = publisher.publish_pending(limit=1)

    after = datetime.now(timezone.utc)

    assert published == 0
    assert failed == 1

    # Terceira falha = 20 segundos de espera.
    assert event.attempts == 3

    assert event.next_attempt_at is not None

    assert (
        before + timedelta(seconds=20)
        <= event.next_attempt_at
        <= after + timedelta(seconds=20)
    )

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_failed_event_remains_pending(
    publisher_setup,
    database_setup,
):
    publisher, _ = publisher_setup
    db, repository, _ = database_setup

    event = make_outbox_event()

    repository.get_pending.return_value = [event]

    with patch.object(
        publisher,
        "_publish_event",
        side_effect=RuntimeError("Kafka indisponível"),
    ):
        published, failed = publisher.publish_pending(limit=1)

    assert published == 0
    assert failed == 1

    # O evento não pode ser marcado como publicado.
    assert event.status == "pending"
    assert event.published_at is None

    # Mas deve ter uma próxima tentativa agendada.
    assert event.attempts == 1
    assert event.next_attempt_at is not None

    db.commit.assert_called_once()


def test_invalid_publish_limit(publisher_setup):
    publisher, _ = publisher_setup

    with pytest.raises(
        ValueError,
        match="limit deve ser maior que zero",
    ):
        publisher.publish_pending(limit=0)

    with pytest.raises(
        ValueError,
        match="limit deve ser maior que zero",
    ):
        publisher.publish_pending(limit=-1)
