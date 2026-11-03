
import logging

from confluent_kafka import Producer

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.schemas import TransactionEvent


logger = logging.getLogger(__name__)


class TransactionProducer:
    def __init__(self):
        self.producer = Producer({
            "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
            "client.id": "fraudshield-producer",
            "acks": "all",
            "enable.idempotence": True,
        })

    def publish(self, event: TransactionEvent) -> None:
        payload = event.model_dump_json().encode("utf-8")

        self.producer.poll(0)

        self.producer.produce(
            topic=KAFKA_CONFIG.raw_topic,
            key=str(event.event_id).encode("utf-8"),
            value=payload,
            on_delivery=self._delivery_callback,
        )

    @staticmethod
    def _delivery_callback(err, msg):
        if err is not None:
            logger.error("Falha ao publicar evento: %s", err)
        else:
            logger.info(
                "Evento publicado: topic=%s partition=%s offset=%s",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )

    def flush(self, timeout: float = 30.0) -> int:
        return self.producer.flush(timeout)
