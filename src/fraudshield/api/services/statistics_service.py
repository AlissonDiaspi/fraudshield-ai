
from sqlalchemy import (
    select,
    func,
    case
)
from sqlalchemy.orm import Session

from fraudshield.database.models import Prediction


class StatisticsService:

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> dict:
        """
        Calcula indicadores agregados
        das previsões armazenadas.
        """

        query = select(
            func.count(Prediction.id).label("total"),

            func.sum(
                case(
                    (Prediction.prediction == 1, 1),
                    else_=0
                )
            ).label("fraud_alerts"),

            func.avg(
                Prediction.fraud_score
            ).label("average_score"),

            func.max(
                Prediction.created_at
            ).label("last_prediction_at")
        )

        result = self.db.execute(query).one()

        total = int(result.total or 0)
        fraud_alerts = int(result.fraud_alerts or 0)

        legitimate_predictions = (
            total - fraud_alerts
        )

        alert_rate = (
            fraud_alerts / total
            if total > 0
            else 0.0
        )

        average_score = float(
            result.average_score or 0.0
        )

        return {
            "total_predictions": total,
            "fraud_alerts": fraud_alerts,
            "legitimate_predictions": legitimate_predictions,
            "alert_rate": alert_rate,
            "average_fraud_score": average_score,
            "last_prediction_at": result.last_prediction_at
        }
