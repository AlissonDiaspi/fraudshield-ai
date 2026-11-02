
from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from fraudshield.api.schemas import (
    StatisticsOverviewResponse
)

from fraudshield.api.services.statistics_service import (
    StatisticsService
)

from fraudshield.database.connection import get_db


router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)


def get_statistics_service(
    db: Session = Depends(get_db)
) -> StatisticsService:

    return StatisticsService(db)


@router.get(
    "/overview",
    response_model=StatisticsOverviewResponse
)
def get_overview(
    service: StatisticsService = Depends(
        get_statistics_service
    )
):
    return service.get_overview()
