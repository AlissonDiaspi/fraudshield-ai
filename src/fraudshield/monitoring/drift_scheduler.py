
import logging
import threading

from pathlib import Path

from fraudshield.database.connection import (
    SessionLocal,
)
from fraudshield.database.repositories.prediction_repository import (
    PredictionRepository,
)
from fraudshield.monitoring.drift_detector import (
    detect_data_drift,
    load_baseline,
)
from fraudshield.monitoring.drift_metrics import (
    publish_drift_metrics,
)


logger = logging.getLogger(__name__)


class DriftScheduler:
    """
    Executa analises periodicas de Data Drift
    sem bloquear o consumer Kafka.
    """

    def __init__(
        self,
        baseline_path: str | Path,
        interval_seconds: int = 300,
        sample_limit: int = 1000,
        min_samples: int = 100,
    ):
        if interval_seconds < 1:
            raise ValueError(
                "interval_seconds deve ser positivo."
            )

        if sample_limit < 1:
            raise ValueError(
                "sample_limit deve ser positivo."
            )

        if min_samples < 1:
            raise ValueError(
                "min_samples deve ser positivo."
            )

        self.baseline = load_baseline(
            baseline_path
        )

        self.interval_seconds = interval_seconds
        self.sample_limit = sample_limit
        self.min_samples = min_samples

        self._stop_event = threading.Event()
        self._thread = None

    def run_once(self) -> dict:
        """
        Executa uma analise de Data Drift.
        """

        with SessionLocal() as db:
            repository = PredictionRepository(db)

            transactions = (
                repository.get_recent_features(
                    limit=self.sample_limit
                )
            )

        report = detect_data_drift(
            self.baseline,
            transactions,
            min_samples=self.min_samples,
        )

        publish_drift_metrics(report)

        logger.info(
            "Data Drift | status=%s | "
            "amostra=%s | significativas=%s",
            report["status"],
            report["sample_size"],
            report.get(
                "significant_features", 0
            ),
        )

        return report

    def _run_loop(self) -> None:
        """
        Executa imediatamente e repete
        conforme o intervalo configurado.
        """

        while not self._stop_event.is_set():
            try:
                self.run_once()

            except Exception:
                logger.exception(
                    "Falha na analise de Data Drift. "
                    "O consumer continuara funcionando."
                )

            if self._stop_event.wait(
                self.interval_seconds
            ):
                break

    def start(self) -> None:
        """
        Inicia a thread de monitoramento.
        """

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            raise RuntimeError(
                "DriftScheduler ja esta em execucao."
            )

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run_loop,
            name="fraudshield-drift-monitor",
            daemon=True,
        )

        self._thread.start()

    def stop(self) -> None:
        """
        Solicita a parada e aguarda a thread.
        """

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(
                timeout=10
            )
