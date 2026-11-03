
import logging

from confluent_kafka import Producer

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.schemas import DeadLetterEvent


logger = logging.getLogger(__name__)


class DeadLetterProducer:
    def __init__(self):
        self.producer = Producer({
            "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
            "client.id": "fraudshield-dlq-producer",
            "acks": "all",
            "enable.idempotence": True,
            "message.timeout.ms": 15000,
        })

    def publish(self, event: DeadLetterEvent) -> None:
        delivery = {
            "completed": False,
            "error": None,
        }

        def delivery_callback(error, message):
            delivery["completed"] = True
            delivery["error"] = error

            if error is None:
                logger.info(
                    "Mensagem enviada à DLQ: partition=%s offset=%s",
                    message.partition(),
                    message.offset(),
                )

        self.producer.produce(
            topic=KAFKA_CONFIG.dlq_topic,
            key=(
                str(event.event_id).encode("utf-8")
                if event.event_id is not None
                else None
            ),
            value=event.model_dump_json().encode("utf-8"),
            on_delivery=delivery_callback,
        )

        remaining = self.producer.flush(timeout=20.0)

        if remaining > 0:
            raise TimeoutError(
                "Kafka não confirmou a entrega na DLQ."
            )

        if not delivery["completed"]:
            raise RuntimeError(
                "Callback da DLQ não foi executado."
            )

        if delivery["error"] is not None:
            raise RuntimeError(
                f"Falha ao publicar na DLQ: {delivery['error']}"
            )
