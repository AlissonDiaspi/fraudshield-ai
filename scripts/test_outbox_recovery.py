
import uuid

from fraudshield.database.connection import SessionLocal
from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)
from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.schemas import PredictionEvent


def main():
    event_id = uuid.uuid4()

    event = PredictionEvent(
        event_id=event_id,
        fraud_score=0.85,
        prediction=1,
        model_version="recovery-test",
    )

    with SessionLocal() as db:
        repository = OutboxRepository(db)

        repository.create(
            event_id=event_id,
            topic=KAFKA_CONFIG.predicted_topic,
            payload=event.model_dump(mode="json"),
        )

        db.commit()

    print("Evento de teste criado!")
    print(f"Event ID: {event_id}")
    print("Status: pending")


if __name__ == "__main__":
    main()
