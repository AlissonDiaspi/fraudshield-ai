
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from fraudshield.database.connection import SessionLocal
from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)
from fraudshield.streaming.config import KAFKA_CONFIG


def main():
    event_id = uuid.uuid4()

    # Criamos um evento pendente exclusivo para o teste.
    with SessionLocal() as db:
        repository = OutboxRepository(db)

        record = repository.create(
            event_id=event_id,
            topic=KAFKA_CONFIG.predicted_topic,
            payload={
                "event_id": str(event_id),
                "fraud_score": 0.5,
                "prediction": 0,
                "model_version": "concurrency-test",
            },
        )

        record_id = record.id
        db.commit()

    lock_acquired = Event()
    release_lock = Event()

    def publisher_a():
        with SessionLocal() as db:
            repository = OutboxRepository(db)

            events = repository.get_pending(limit=1)

            if not events:
                raise RuntimeError(
                    "Publisher A não encontrou evento."
                )

            locked_event = events[0]

            print(
                "Publisher A bloqueou:",
                locked_event.event_id,
            )

            lock_acquired.set()

            if not release_lock.wait(timeout=10):
                raise TimeoutError(
                    "Tempo esgotado aguardando liberação."
                )

            db.rollback()

    def publisher_b():
        if not lock_acquired.wait(timeout=10):
            raise TimeoutError(
                "Publisher A não adquiriu o bloqueio."
            )

        with SessionLocal() as db:
            repository = OutboxRepository(db)

            events = repository.get_pending(limit=1)

            selected_ids = [
                event.event_id for event in events
            ]

            print(
                "Publisher B selecionou:",
                selected_ids,
            )

            assert event_id not in selected_ids, (
                "Publisher B selecionou o evento "
                "bloqueado pelo Publisher A."
            )

            db.rollback()

        release_lock.set()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(publisher_a)
            future_b = executor.submit(publisher_b)

            try:
                future_b.result(timeout=15)
            finally:
                release_lock.set()

            future_a.result(timeout=15)

        print("\nConcorrência validada com sucesso!")

    finally:
        # Remove somente o registro criado pelo teste.
        with SessionLocal() as db:
            from fraudshield.database.models import OutboxEvent

            record = db.get(OutboxEvent, record_id)

            if record is not None:
                db.delete(record)
                db.commit()


if __name__ == "__main__":
    main()
