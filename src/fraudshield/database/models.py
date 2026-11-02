
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    CheckConstraint
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from fraudshield.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    __table_args__ = (
        CheckConstraint(
            "prediction IN (0, 1)",
            name="ck_predictions_prediction"
        ),
        CheckConstraint(
            "threshold >= 0 AND threshold <= 1",
            name="ck_predictions_threshold"
        ),
        CheckConstraint(
            "fraud_score >= 0 AND fraud_score <= 1",
            name="ck_predictions_fraud_score"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    features: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    fraud_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    prediction: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
