
import time
import uuid

from datetime import datetime, timezone
from unittest.mock import patch

from sqlalchemy import select

from fraudshield.database.connection import SessionLocal
from fraudshield.database.models import OutboxEvent
from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)
from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.outbox_publisher import OutboxPublisher


def main():
    event_id = uuid.uuid4()
    record_id = None

    print("\nOutbox Backoff")

    # 1. Criar um evento real no PostgreSQL.
    with SessionLocal() as db:
        repository = OutboxRepository(db)

        record = repository.create(
            event_id=event_id,
            topic=KAFKA_CONFIG.predicted_topic,
            payload={
                "event_id": str(event_id),
                "fraud_score": 0.85,
                "prediction": 1,
                "model_version": "backoff-integration-test",
            },
        )

        record_id = record.id
        db.commit()

    print(f"\nEvento criado: {event_id}")

    publisher = OutboxPublisher()

    try:
        # 2. Simular falha de publicação.
        with patch.object(
            publisher,
            "_publish_event",
            side_effect=RuntimeError(
                "Falha simulada no Kafka"
            ),
        ):
            published, failed = publisher.publish_pending(
                limit=1
            )

        assert published == 0
        assert failed == 1

        with SessionLocal() as db:
            record = db.get(OutboxEvent, record_id)

            assert record is not None
            assert record.status == "pending"
            assert record.attempts == 1
            assert record.next_attempt_at is not None

            next_attempt_at = record.next_attempt_at

        print("\nFalha registrada no PostgreSQL.")
        print(f"Tentativas: 1")
        print(f"Próxima tentativa: {next_attempt_at}")

        # 3. Verificar se o evento está bloqueado
        # pelo agendamento do backoff.
        with SessionLocal() as db:
            repository = OutboxRepository(db)

            pending = repository.get_pending(limit=100)

            selected_ids = {
                event.event_id for event in pending
            }

            assert event_id not in selected_ids

            db.rollback()

        print("\nBackoff validado: evento não está elegível.")

        # 4. Aguardar o horário da próxima tentativa.
        remaining = (
            next_attempt_at - datetime.now(timezone.utc)
        ).total_seconds()

        if remaining > 0:
            print(
                f"\nAguardando {remaining:.1f}s para o retry..."
            )
            time.sleep(remaining + 0.5)

        # 5. Publicar no Kafka real.
        published, failed = publisher.publish_pending(
            limit=1
        )

        assert published == 1
        assert failed == 0

        with SessionLocal() as db:
            record = db.get(OutboxEvent, record_id)

            assert record is not None
            assert record.status == "published"
            assert record.published_at is not None
            assert record.next_attempt_at is None

        print("\nEvento publicado no Kafka com sucesso!")
        print("Status final: published")
        print("\nTESTE DE BACKOFF CONCLUÍDO COM SUCESSO!")

    finally:
        # Remover somente o registro criado pelo teste.
        if record_id is not None:
            with SessionLocal() as db:
                record = db.get(OutboxEvent, record_id)

                if record is not None:
                    db.delete(record)
                    db.commit()


if __name__ == "__main__":
    main()
