
import logging

from sqlalchemy.exc import IntegrityError

from fraudshield.config import MODEL_CONFIG
from fraudshield.database.connection import SessionLocal
from fraudshield.database.repositories.prediction_repository import (
    PredictionRepository,
)
from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)
from fraudshield.monitoring.service import MonitoringService
from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.inference_service import (
    StreamingInferenceService,
)
from fraudshield.streaming.schemas import (
    PredictionEvent,
    TransactionEvent,
)


logger = logging.getLogger(__name__)


class StreamingPersistenceService:
    def __init__(
        self,
        inference_service: StreamingInferenceService,
        monitoring_service: MonitoringService | None = None,
    ):
        self.inference_service = inference_service
        self.monitoring = monitoring_service or MonitoringService()

    @staticmethod
    def _prediction_from_record(record) -> PredictionEvent:
        return PredictionEvent(
            event_id=record.event_id,
            fraud_score=record.fraud_score,
            prediction=record.prediction,
            model_version=record.model_version,
        )

    def process(self, event: TransactionEvent) -> PredictionEvent:
        with SessionLocal() as db:
            predictions = PredictionRepository(db)
            outbox = OutboxRepository(db)

            try:
                existing = predictions.get_by_event_id(
                    event.event_id
                )

                if existing is not None:
                    result = self._prediction_from_record(existing)

                    pending = outbox.get_by_event_and_topic(
                        event.event_id,
                        KAFKA_CONFIG.predicted_topic,
                    )

                    if pending is None:
                        outbox.create(
                            event_id=event.event_id,
                            topic=KAFKA_CONFIG.predicted_topic,
                            payload=result.model_dump(mode="json"),
                        )

                        db.commit()

                    logger.info(
                        "Transação já processada: event_id=%s",
                        event.event_id,
                    )

                    # Evento duplicado: não contamos novamente.
                    return result

                # Mede somente a execução da inferência.
                with self.monitoring.track_inference():
                    result = self.inference_service.predict(event)

                predictions.create(
                    event_id=event.event_id,
                    features=event.features,
                    fraud_score=result.fraud_score,
                    prediction=result.prediction,
                    threshold=MODEL_CONFIG.threshold,
                    model_version=result.model_version,
                )

                outbox.create(
                    event_id=event.event_id,
                    topic=KAFKA_CONFIG.predicted_topic,
                    payload=result.model_dump(mode="json"),
                )

                db.commit()

                # Contabiliza somente após persistência.
                self.monitoring.record_prediction(
                    result.prediction
                )

                logger.info(
                    "Previsão e outbox persistidas: event_id=%s",
                    event.event_id,
                )

                return result

            except IntegrityError:
                db.rollback()

                existing = predictions.get_by_event_id(
                    event.event_id
                )

                if existing is None:
                    raise

                pending = outbox.get_by_event_and_topic(
                    event.event_id,
                    KAFKA_CONFIG.predicted_topic,
                )

                if pending is None:
                    raise

                logger.info(
                    "Evento já persistido por outro consumer: %s",
                    event.event_id,
                )

                # Outro consumer persistiu primeiro.
                # Não duplicamos a métrica de processamento.
                return self._prediction_from_record(existing)

            except Exception:
                db.rollback()
                raise
