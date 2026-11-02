
from datetime import datetime
from math import ceil
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from fraudshield.api.schemas import (
    PredictionHistoryItem,
    PredictionHistoryResponse
)

from fraudshield.api.services.history_service import (
    HistoryService
)

from fraudshield.database.connection import get_db


router = APIRouter(
    prefix="/predictions",
    tags=["Prediction History"]
)


def get_history_service(
    db: Session = Depends(get_db)
) -> HistoryService:

    return HistoryService(db)


@router.get(
    "",
    response_model=PredictionHistoryResponse
)
def list_predictions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    prediction: int | None = Query(
        default=None,
        ge=0,
        le=1
    ),
    model_version: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: HistoryService = Depends(
        get_history_service
    )
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="start_date não pode ser posterior a end_date."
        )

    if any(
        value is not None and value.utcoffset() is None
        for value in (start_date, end_date)
    ):
        raise HTTPException(
            status_code=422,
            detail="As datas devem incluir fuso horário."
        )

    items, total = service.list_predictions(
        page=page,
        page_size=page_size,
        prediction=prediction,
        model_version=model_version,
        start_date=start_date,
        end_date=end_date
    )

    return PredictionHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size)
    )


@router.get(
    "/{prediction_id}",
    response_model=PredictionHistoryItem
)
def get_prediction(
    prediction_id: UUID,
    service: HistoryService = Depends(
        get_history_service
    )
):
    record = service.get_by_id(
        prediction_id
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Previsão não encontrada."
        )

    return record
