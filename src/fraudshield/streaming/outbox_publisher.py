
import json
import logging

from datetime import datetime, timezone

from confluent_kafka import Producer

from fraudshield.database.connection import SessionLocal
from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)
from fraudshield.streaming.backoff import (
    calculate_next_attempt_at,
)
from fraudshield.streaming.config import KAFKA_CONFIG


logger = logging.getLogger(__name__)


class OutboxPublisher:
    def __init__(self):
        self.producer = Producer(
            {
                "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
                "client.id": "fraudshield-outbox-publisher",
                "acks": "all",
                "enable.idempotence": True,
                "message.timeout.ms": 15000,
            }
        )

    def _publish_event(self, event):
        delivery = {
            "completed": False,
            "error": None,
        }

        def delivery_callback(error, message):
            delivery["completed"] = True
            delivery["error"] = error

            if error is None:
                logger.info(
                    "Kafka confirmou: topic=%s partition=%s offset=%s",
                    message.topic(),
                    message.partition(),
                    message.offset(),
                )

        payload = json.dumps(
            event.payload,
            ensure_ascii=False,
        ).encode("utf-8")

        self.producer.produce(
            topic=event.topic,
            key=str(event.event_id).encode("utf-8"),
            value=payload,
            on_delivery=delivery_callback,
        )

        remaining = self.producer.flush(timeout=20.0)

        if remaining > 0:
            raise TimeoutError(
                "Kafka não confirmou a entrega no prazo."
            )

        if not delivery["completed"]:
            raise RuntimeError(
                "Callback de entrega não foi executado."
            )

        if delivery["error"] is not None:
            raise RuntimeError(
                f"Falha na publicação Kafka: {delivery['error']}"
            )

    def publish_pending(
        self,
        limit: int = 100,
    ) -> tuple[int, int]:
        if limit <= 0:
            raise ValueError(
                "limit deve ser maior que zero"
            )

        published = 0
        failed = 0

        for _ in range(limit):
            with SessionLocal() as db:
                repository = OutboxRepository(db)
                events = repository.get_pending(limit=1)

                if not events:
                    db.rollback()
                    break

                event = events[0]

                try:
                    self._publish_event(event)

                except Exception:
                    logger.exception(
                        "Falha ao publicar evento: %s",
                        event.event_id,
                    )

                    # O bloqueio permanece ativo.
                    event.attempts += 1
                    event.next_attempt_at = (
                        calculate_next_attempt_at(
                            attempts=event.attempts,
                        )
                    )

                    db.commit()
                    failed += 1

                    logger.warning(
                        "Retry agendado: event_id=%s "
                        "attempts=%s next_attempt_at=%s",
                        event.event_id,
                        event.attempts,
                        event.next_attempt_at,
                    )

                else:
                    event.status = "published"
                    event.published_at = datetime.now(
                        timezone.utc
                    )
                    event.next_attempt_at = None

                    db.commit()
                    published += 1

                    logger.info(
                        "Evento publicado: %s",
                        event.event_id,
                    )

        return published, failed
