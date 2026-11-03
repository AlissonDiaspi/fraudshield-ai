
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from fraudshield.database.models import Prediction


class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_event_id(
        self,
        event_id: uuid.UUID,
    ) -> Prediction | None:
        statement = select(Prediction).where(
            Prediction.event_id == event_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        *,
        features: dict,
        fraud_score: float,
        prediction: int,
        threshold: float,
        model_version: str,
        event_id: uuid.UUID | None = None,
    ) -> Prediction:
        record = Prediction(
            event_id=event_id,
            features=features,
            fraud_score=fraud_score,
            prediction=prediction,
            threshold=threshold,
            model_version=model_version,
        )

        self.db.add(record)
        self.db.flush()

        return record
