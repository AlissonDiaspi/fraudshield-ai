
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
    ):
        self.inference_service = inference_service

    @staticmethod
    def _prediction_from_record(record) -> PredictionEvent:
        return PredictionEvent(
            event_id=record.event_id,
            fraud_score=record.fraud_score,
            prediction=record.prediction,
            model_version=record.model_version,
        )

    def process(
        self,
        event: TransactionEvent,
    ) -> PredictionEvent:
        with SessionLocal() as db:
            predictions = PredictionRepository(db)
            outbox = OutboxRepository(db)

            try:
                existing = predictions.get_by_event_id(
                    event.event_id
                )

                if existing is not None:
                    result = self._prediction_from_record(
                        existing
                    )

                    # Também cobre previsões salvas antes
                    # da implementação da outbox.
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

                    return result

                result = self.inference_service.predict(
                    event
                )

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

                # Commit único: previsão + outbox.
                db.commit()

                logger.info(
                    "Previsão e outbox persistidas: event_id=%s",
                    event.event_id,
                )

                return result

            except IntegrityError:
                db.rollback()

                # Possível corrida entre consumers.
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
                    # A outra transação pode ter sido criada
                    # por um fluxo legado. A próxima entrega
                    # poderá tentar criar a outbox.
                    raise

                logger.info(
                    "Evento já persistido por outro consumer: %s",
                    event.event_id,
                )

                return self._prediction_from_record(
                    existing
                )

            except Exception:
                db.rollback()
                raise
