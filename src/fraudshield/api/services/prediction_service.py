
import pandas as pd

from sqlalchemy.orm import Session
from xgboost import XGBClassifier

from fraudshield.config import MODEL_CONFIG
from fraudshield.inference import predict_fraud

from fraudshield.api.schemas import (
    PredictionRequest,
    PredictionResponse,
)

from fraudshield.database.repositories.prediction_repository import (
    PredictionRepository,
)


class PredictionService:
    def __init__(
        self,
        model: XGBClassifier,
        model_version: str | None = None,
    ):
        self.model = model

        self.model_version = (
            model_version
            if model_version is not None
            else MODEL_CONFIG.model_version
        )

    def predict(
        self,
        payload: PredictionRequest,
        db: Session,
    ) -> PredictionResponse:
        transactions = pd.DataFrame(
            [payload.features]
        )

        results = predict_fraud(
            model=self.model,
            transactions=transactions,
            threshold=MODEL_CONFIG.threshold,
        )

        fraud_score = float(
            results.iloc[0]["fraud_score"]
        )

        prediction = int(
            results.iloc[0]["prediction"]
        )

        repository = PredictionRepository(db)

        try:
            prediction_record = repository.create(
                features=payload.features,
                fraud_score=fraud_score,
                prediction=prediction,
                threshold=MODEL_CONFIG.threshold,
                model_version=self.model_version,
            )

            db.commit()
            db.refresh(prediction_record)

        except Exception:
            db.rollback()
            raise

        return PredictionResponse(
            id=prediction_record.id,
            fraud_score=fraud_score,
            prediction=prediction,
            classification=(
                "fraud"
                if prediction == 1
                else "legitimate"
            ),
            threshold=MODEL_CONFIG.threshold,
            model_version=self.model_version,
        )
