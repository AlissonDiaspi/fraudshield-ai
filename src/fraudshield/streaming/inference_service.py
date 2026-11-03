
import pandas as pd
from xgboost import XGBClassifier

from fraudshield.config import MODEL_CONFIG
from fraudshield.inference import predict_fraud
from fraudshield.registry_loader import load_registered_model_info
from fraudshield.streaming.schemas import (
    PredictionEvent,
    TransactionEvent,
)


class StreamingInferenceService:
    def __init__(
        self,
        model: XGBClassifier,
        model_version: str,
    ):
        self.model = model
        self.model_version = model_version

    @classmethod
    def from_registry(cls) -> "StreamingInferenceService":
        registered = load_registered_model_info()

        return cls(
            model=registered.model,
            model_version=registered.version,
        )

    def predict(
        self,
        event: TransactionEvent,
    ) -> PredictionEvent:
        transactions = pd.DataFrame([event.features])

        results = predict_fraud(
            model=self.model,
            transactions=transactions,
            threshold=MODEL_CONFIG.threshold,
        )

        fraud_score = float(results.iloc[0]["fraud_score"])
        prediction = int(results.iloc[0]["prediction"])

        return PredictionEvent(
            event_id=event.event_id,
            fraud_score=fraud_score,
            prediction=prediction,
            model_version=self.model_version,
        )
