
import json
import logging

from collections.abc import Callable
from uuid import UUID

from confluent_kafka import Consumer, KafkaException
from pydantic import ValidationError

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.dlq_producer import (
    DeadLetterProducer,
)
from fraudshield.streaming.schemas import (
    DeadLetterEvent,
    TransactionEvent,
)


logger = logging.getLogger(__name__)


class TransactionConsumer:
    def __init__(
        self,
        group_id: str = KAFKA_CONFIG.consumer_group,
    ):
        self.consumer = Consumer({
            "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })

        self.dlq_producer = DeadLetterProducer()

    @staticmethod
    def _extract_original_payload(
        payload: bytes | None,
    ) -> dict | str:
        if payload is None:
            return "<empty Kafka message>"

        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError:
            return f"<invalid UTF-8: {payload.hex()}>"

        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            return decoded

        if isinstance(parsed, dict):
            return parsed

        return decoded

    @staticmethod
    def _extract_event_id(
        original_payload: dict | str,
    ) -> UUID | None:
        if not isinstance(original_payload, dict):
            return None

        value = original_payload.get("event_id")

        if not isinstance(value, str):
            return None

        try:
            return UUID(value)
        except ValueError:
            return None

    def _send_to_dlq(
        self,
        payload: bytes | None,
        error: Exception,
    ) -> None:
        original_payload = self._extract_original_payload(
            payload
        )

        event = DeadLetterEvent(
            event_id=self._extract_event_id(
                original_payload
            ),
            error=str(error),
            original_payload=original_payload,
        )

        # Se a publicação falhar, a exceção será propagada.
        # Assim, não confirmaremos o offset original.
        self.dlq_producer.publish(event)

    def start(
        self,
        handler: Callable[[TransactionEvent], None],
        max_messages: int | None = None,
    ) -> None:
        if max_messages is not None and max_messages <= 0:
            raise ValueError(
                "max_messages deve ser maior que zero"
            )

        processed = 0
        sent_to_dlq = 0

        self.consumer.subscribe([
            KAFKA_CONFIG.raw_topic
        ])

        logger.info(
            "Consumer iniciado. Aguardando mensagens..."
        )

        try:
            while True:
                message = self.consumer.poll(1.0)

                if message is None:
                    continue

                if message.error():
                    raise KafkaException(
                        message.error()
                    )

                payload = message.value()

                try:
                    if payload is None:
                        raise ValueError(
                            "Mensagem Kafka sem conteúdo"
                        )

                    event = (
                        TransactionEvent.model_validate_json(
                            payload
                        )
                    )

                except (
                    ValidationError,
                    ValueError,
                    UnicodeDecodeError,
                ) as error:
                    logger.warning(
                        "Mensagem inválida: partition=%s offset=%s",
                        message.partition(),
                        message.offset(),
                    )

                    self._send_to_dlq(
                        payload=payload,
                        error=error,
                    )

                    # Confirma apenas após a DLQ receber
                    # a mensagem com sucesso.
                    self.consumer.commit(
                        message=message,
                        asynchronous=False,
                    )

                    sent_to_dlq += 1
                    processed += 1

                    logger.info(
                        "Mensagem encaminhada à DLQ."
                    )

                else:
                    # Erros do handler não são capturados
                    # pelo bloco de validação.
                    # Portanto, não serão enviados à DLQ
                    # automaticamente.
                    handler(event)

                    self.consumer.commit(
                        message=message,
                        asynchronous=False,
                    )

                    processed += 1

                    logger.info(
                        "Mensagem processada: partition=%s offset=%s",
                        message.partition(),
                        message.offset(),
                    )

                if (
                    max_messages is not None
                    and processed >= max_messages
                ):
                    break

        except KeyboardInterrupt:
            logger.info(
                "Consumer interrompido pelo usuário."
            )

        finally:
            self.consumer.close()

            logger.info(
                "Consumer encerrado. "
                "Total=%s | DLQ=%s",
                processed,
                sent_to_dlq,
            )
