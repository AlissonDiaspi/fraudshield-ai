
import uuid

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from fraudshield.database.models import OutboxEvent


class OutboxRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        event_id: uuid.UUID,
        topic: str,
        payload: dict,
    ) -> OutboxEvent:
        record = OutboxEvent(
            event_id=event_id,
            topic=topic,
            payload=payload,
        )

        self.db.add(record)
        self.db.flush()

        return record

    def get_by_event_and_topic(
        self,
        event_id: uuid.UUID,
        topic: str,
    ) -> OutboxEvent | None:
        statement = select(OutboxEvent).where(
            OutboxEvent.event_id == event_id,
            OutboxEvent.topic == topic,
        )

        return self.db.scalar(statement)

    def get_pending(
        self,
        limit: int = 100,
    ) -> list[OutboxEvent]:
        if limit <= 0:
            raise ValueError(
                "limit deve ser maior que zero"
            )

        now = datetime.now(timezone.utc)

        statement = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status == "pending",
                or_(
                    OutboxEvent.next_attempt_at.is_(None),
                    OutboxEvent.next_attempt_at <= now,
                ),
            )
            .order_by(
                OutboxEvent.created_at,
                OutboxEvent.id,
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        return list(
            self.db.scalars(statement).all()
        )
