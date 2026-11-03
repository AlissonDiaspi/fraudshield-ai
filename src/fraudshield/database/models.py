
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    text,
)

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from fraudshield.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    __table_args__ = (
        CheckConstraint(
            "prediction IN (0, 1)",
            name="ck_predictions_prediction",
        ),
        CheckConstraint(
            "threshold >= 0 AND threshold <= 1",
            name="ck_predictions_threshold",
        ),
        CheckConstraint(
            "fraud_score >= 0 AND fraud_score <= 1",
            name="ck_predictions_fraud_score",
        ),
        UniqueConstraint(
            "event_id",
            name="uq_predictions_event_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    features: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    fraud_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    prediction: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'published')",
            name="ck_outbox_status",
        ),
        CheckConstraint(
            "attempts >= 0",
            name="ck_outbox_attempts",
        ),
        UniqueConstraint(
            "event_id",
            "topic",
            name="uq_outbox_event_topic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # NOVO: controla quando o evento poderá
    # ser processado novamente após uma falha.
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
