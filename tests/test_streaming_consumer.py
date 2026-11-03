
from unittest.mock import MagicMock, patch

import pytest

from fraudshield.streaming.consumer import TransactionConsumer
from fraudshield.streaming.schemas import TransactionEvent


def make_kafka_message(payload: bytes):
    message = MagicMock()
    message.value.return_value = payload
    message.error.return_value = None
    message.partition.return_value = 0
    message.offset.return_value = 10
    return message


@pytest.fixture
def consumer_setup():
    with (
        patch(
            "fraudshield.streaming.consumer.Consumer"
        ) as consumer_class,
        patch(
            "fraudshield.streaming.consumer.DeadLetterProducer"
        ) as dlq_class,
    ):
        kafka = consumer_class.return_value
        dlq = dlq_class.return_value

        consumer = TransactionConsumer(
            group_id="fraudshield-unit-test"
        )

        yield consumer, kafka, dlq


def test_valid_message_is_processed_and_committed(
    consumer_setup,
):
    consumer, kafka, dlq = consumer_setup

    event = TransactionEvent.model_construct(
        event_id=__import__("uuid").uuid4(),
        schema_version=1,
        features={"V1": 0.5},
    )

    message = make_kafka_message(
        event.model_dump_json().encode("utf-8")
    )

    kafka.poll.return_value = message

    handler = MagicMock()

    with patch(
        "fraudshield.streaming.consumer.TransactionEvent.model_validate_json",
        return_value=event,
    ):
        consumer.start(
            handler=handler,
            max_messages=1,
        )

    handler.assert_called_once_with(event)

    kafka.commit.assert_called_once_with(
        message=message,
        asynchronous=False,
    )

    dlq.publish.assert_not_called()
    kafka.close.assert_called_once()



def test_invalid_message_is_sent_to_dlq_before_commit(
    consumer_setup,
):
    consumer, kafka, dlq = consumer_setup

    message = make_kafka_message(
        b'{"event_id":"invalid-uuid","features":{}}'
    )

    kafka.poll.return_value = message

    handler = MagicMock()

    # Um mock compartilhado registra a ordem das chamadas.
    operations = MagicMock()

    operations.attach_mock(
        dlq.publish,
        "publish_to_dlq",
    )

    operations.attach_mock(
        kafka.commit,
        "commit_offset",
    )

    consumer.start(
        handler=handler,
        max_messages=1,
    )

    handler.assert_not_called()

    assert operations.mock_calls == [
        __import__("unittest.mock", fromlist=["call"]).call.publish_to_dlq(
            dlq.publish.call_args.args[0]
        ),
        __import__("unittest.mock", fromlist=["call"]).call.commit_offset(
            message=message,
            asynchronous=False,
        ),
    ]

    kafka.close.assert_called_once()



def test_dlq_failure_does_not_commit_offset(
    consumer_setup,
):
    consumer, kafka, dlq = consumer_setup

    message = make_kafka_message(
        b'{"event_id":"invalid-uuid","features":{}}'
    )

    kafka.poll.return_value = message

    dlq.publish.side_effect = RuntimeError(
        "Kafka DLQ indisponível"
    )

    handler = MagicMock()

    with pytest.raises(
        RuntimeError,
        match="Kafka DLQ indisponível",
    ):
        consumer.start(
            handler=handler,
            max_messages=1,
        )

    handler.assert_not_called()
    kafka.commit.assert_not_called()
    kafka.close.assert_called_once()


def test_handler_failure_does_not_commit_offset(
    consumer_setup,
):
    consumer, kafka, dlq = consumer_setup

    event = TransactionEvent.model_construct(
        event_id=__import__("uuid").uuid4(),
        schema_version=1,
        features={"V1": 0.5},
    )

    message = make_kafka_message(
        event.model_dump_json().encode("utf-8")
    )

    kafka.poll.return_value = message

    handler = MagicMock(
        side_effect=RuntimeError(
            "PostgreSQL indisponível"
        )
    )

    with (
        patch(
            "fraudshield.streaming.consumer.TransactionEvent.model_validate_json",
            return_value=event,
        ),
        pytest.raises(
            RuntimeError,
            match="PostgreSQL indisponível",
        ),
    ):
        consumer.start(
            handler=handler,
            max_messages=1,
        )

    handler.assert_called_once_with(event)
    kafka.commit.assert_not_called()
    dlq.publish.assert_not_called()
    kafka.close.assert_called_once()
