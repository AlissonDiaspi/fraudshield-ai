
import argparse
import logging

from pathlib import Path

from sqlalchemy.exc import (
    OperationalError,
    InterfaceError,
)

from fraudshield.monitoring.server import (
    start_metrics_server,
)
from fraudshield.monitoring.drift_scheduler import (
    DriftScheduler,
)
from fraudshield.streaming.consumer import (
    TransactionConsumer,
)
from fraudshield.streaming.inference_service import (
    StreamingInferenceService,
)
from fraudshield.streaming.persistence_service import (
    StreamingPersistenceService,
)
from fraudshield.streaming.retry import (
    execute_with_retry,
)
from fraudshield.streaming.schemas import (
    TransactionEvent,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="FraudShield - Kafka + XGBoost + PostgreSQL"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--group-id",
        type=str,
        default="fraudshield-persistence",
        help="Grupo de consumidores Kafka",
    )

    parser.add_argument(
        "--drift-interval",
        type=int,
        default=300,
        help="Intervalo entre analises de drift, em segundos",
    )

    parser.add_argument(
        "--drift-limit",
        type=int,
        default=1000,
        help="Quantidade maxima de transacoes analisadas",
    )

    parser.add_argument(
        "--drift-min-samples",
        type=int,
        default=100,
        help="Minimo de transacoes para calcular drift",
    )

    parser.add_argument(
        "--disable-drift",
        action="store_true",
        help="Desativa o monitoramento periodico de drift",
    )

    args = parser.parse_args()

    print("Carregando modelo champion do MLflow...")

    inference_service = (
        StreamingInferenceService.from_registry()
    )

    persistence_service = StreamingPersistenceService(
        inference_service=inference_service
    )

    start_metrics_server()

    drift_scheduler = None

    if not args.disable_drift:
        baseline_path = Path(
            "artifacts/monitoring/drift_baseline.json"
        )

        if baseline_path.exists():
            drift_scheduler = DriftScheduler(
                baseline_path=baseline_path,
                interval_seconds=args.drift_interval,
                sample_limit=args.drift_limit,
                min_samples=args.drift_min_samples,
            )

            drift_scheduler.start()

            logger.info(
                "Monitoramento de Data Drift iniciado."
            )

        else:
            logger.warning(
                "Baseline de drift nao encontrado. "
                "Monitoramento de drift desativado."
            )

    print(
        "Modelo carregado. "
        "Iniciando consumer com persistencia e retry..."
    )

    def handle_transaction(
        event: TransactionEvent,
    ) -> None:
        result = execute_with_retry(
            operation=lambda: persistence_service.process(
                event
            ),
            max_attempts=4,
            initial_delay=1.0,
            backoff_factor=2.0,
            retryable_exceptions=(
                OperationalError,
                InterfaceError,
                ConnectionError,
                TimeoutError,
            ),
        )

        classification = (
            "FRAUDE"
            if result.prediction == 1
            else "LEGITIMA"
        )

        print("\n" + "=" * 55)
        print("FRAUDSHIELD - PREVISAO PERSISTIDA")
        print("=" * 55)
        print(f"Event ID: {result.event_id}")
        print(f"Fraud Score: {result.fraud_score:.6f}")
        print(f"Classificacao: {classification}")
        print(f"Modelo: {result.model_version}")
        print("=" * 55 + "\n")

    consumer = TransactionConsumer(
        group_id=args.group_id
    )

    try:
        consumer.start(
            handler=handle_transaction,
            max_messages=args.limit,
        )

    finally:
        if drift_scheduler is not None:
            drift_scheduler.stop()

            logger.info(
                "Monitoramento de Data Drift encerrado."
            )


if __name__ == "__main__":
    main()
