
import pandas as pd

from sqlalchemy.orm import Session
from xgboost import XGBClassifier

from fraudshield.api.schemas import (
    PredictionRequest,
    PredictionResponse
)
from fraudshield.config import MODEL_CONFIG
from fraudshield.database.models import Prediction
from fraudshield.inference import predict_fraud


class PredictionService:

    def __init__(
        self,
        model: XGBClassifier
    ):
        self.model = model

    def predict(
        self,
        payload: PredictionRequest,
        db: Session
    ) -> PredictionResponse:

        transaction = pd.DataFrame(
            [payload.features]
        )

        result = predict_fraud(
            model=self.model,
            transactions=transaction,
            threshold=MODEL_CONFIG.threshold
        )

        fraud_score = float(
            result.iloc[0]["fraud_score"]
        )

        prediction = int(
            result.iloc[0]["prediction"]
        )

        record = Prediction(
            features=payload.features,
            fraud_score=fraud_score,
            prediction=prediction,
            threshold=MODEL_CONFIG.threshold,
            model_version=MODEL_CONFIG.model_version
        )

        db.add(record)

        try:
            db.commit()
            db.refresh(record)

        except Exception:
            db.rollback()
            raise

        return PredictionResponse(
            id=record.id,
            fraud_score=record.fraud_score,
            prediction=record.prediction,
            classification=(
                "fraud"
                if record.prediction == 1
                else "legitimate"
            ),
            threshold=record.threshold,
            model_version=record.model_version
        )
