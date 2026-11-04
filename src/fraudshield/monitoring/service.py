
from contextlib import contextmanager
from time import perf_counter

from fraudshield.monitoring.metrics import (
    INFERENCE_DURATION,
    INFERENCE_ERRORS,
    INFERENCE_IN_PROGRESS,
    PREDICTIONS_TOTAL,
    TRANSACTIONS_PROCESSED,
)


class MonitoringService:
    @contextmanager
    def track_inference(self):
        """
        Mede o tempo de inferencia e registra
        falhas ocorridas durante a execucao.
        """
        start = perf_counter()

        INFERENCE_IN_PROGRESS.inc()

        try:
            yield

        except Exception:
            INFERENCE_ERRORS.inc()
            raise

        finally:
            duration = perf_counter() - start

            INFERENCE_DURATION.observe(duration)
            INFERENCE_IN_PROGRESS.dec()

    def record_prediction(self, prediction: int) -> None:
        """
        Registra uma previsao processada com sucesso.
        """
        if prediction not in (0, 1):
            raise ValueError(
                "prediction deve ser 0 ou 1"
            )

        TRANSACTIONS_PROCESSED.inc()

        PREDICTIONS_TOTAL.labels(
            prediction=str(prediction)
        ).inc()
