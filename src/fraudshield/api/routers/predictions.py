
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from sqlalchemy.orm import Session

from fraudshield.api.schemas import (
    PredictionRequest,
    PredictionResponse
)

from fraudshield.api.services.prediction_service import (
    PredictionService
)

from fraudshield.database.connection import get_db


router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)


def get_prediction_service(
    request: Request
) -> PredictionService:
    return request.app.state.prediction_service


@router.post(
    "",
    response_model=PredictionResponse
)
def predict_transaction(
    payload: PredictionRequest,
    service: PredictionService = Depends(
        get_prediction_service
    ),
    db: Session = Depends(get_db)
):
    try:
        return service.predict(
            payload=payload,
            db=db
        )

    except (ValueError, TypeError, OverflowError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error
