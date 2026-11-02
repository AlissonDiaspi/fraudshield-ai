
import math
from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)


EXPECTED_FEATURES = {
    "Time",
    "Amount",
    *(f"V{i}" for i in range(1, 29))
}


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    features: dict[str, float] = Field(
        description="Time, Amount e V1 até V28"
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, features):
        received = set(features.keys())

        missing = EXPECTED_FEATURES - received
        extra = received - EXPECTED_FEATURES

        if missing or extra:
            raise ValueError(
                f"Features ausentes: {sorted(missing)}. "
                f"Features extras: {sorted(extra)}."
            )

        for name, value in features.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"A feature '{name}' deve ser finita."
                )

        if features["Amount"] < 0:
            raise ValueError(
                "Amount não pode ser negativo."
            )

        if features["Time"] < 0:
            raise ValueError(
                "Time não pode ser negativo."
            )

        return features






class PredictionResponse(BaseModel):
    id: UUID
    fraud_score: float
    prediction: int
    classification: str
    threshold: float
    model_version: str



class PredictionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    features: dict[str, float]
    fraud_score: float
    prediction: int
    threshold: float
    model_version: str


class PredictionHistoryResponse(BaseModel):
    items: list[PredictionHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class StatisticsOverviewResponse(BaseModel):
    total_predictions: int
    fraud_alerts: int
    legitimate_predictions: int
    alert_rate: float
    average_fraud_score: float
    last_prediction_at: datetime | None

