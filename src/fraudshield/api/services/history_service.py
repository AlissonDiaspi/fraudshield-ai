
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fraudshield.database.models import Prediction


class HistoryService:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        prediction_id: UUID
    ) -> Prediction | None:

        return self.db.get(
            Prediction,
            prediction_id
        )

    def list_predictions(
        self,
        page: int = 1,
        page_size: int = 20,
        prediction: int | None = None,
        model_version: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> tuple[list[Prediction], int]:

        filters = []

        if prediction is not None:
            filters.append(
                Prediction.prediction == prediction
            )

        if model_version is not None:
            filters.append(
                Prediction.model_version == model_version
            )

        if start_date is not None:
            filters.append(
                Prediction.created_at >= start_date
            )

        if end_date is not None:
            filters.append(
                Prediction.created_at <= end_date
            )

        count_query = select(
            func.count(Prediction.id)
        ).where(*filters)

        total = self.db.scalar(count_query) or 0

        offset = (page - 1) * page_size

        query = (
            select(Prediction)
            .where(*filters)
            .order_by(
                Prediction.created_at.desc(),
                Prediction.id.desc()
            )
            .offset(offset)
            .limit(page_size)
        )

        items = self.db.scalars(query).all()

        return list(items), total
