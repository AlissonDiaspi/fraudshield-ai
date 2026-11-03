
import argparse
import logging

from sqlalchemy.exc import (
    OperationalError,
    InterfaceError,
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

    args = parser.parse_args()

    print("Carregando modelo champion do MLflow...")

    inference_service = (
        StreamingInferenceService.from_registry()
    )

    persistence_service = StreamingPersistenceService(
        inference_service=inference_service
    )

    print(
        "Modelo carregado. "
        "Iniciando consumer com persistência e retry..."
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
            else "LEGÍTIMA"
        )

        print("\n" + "=" * 55)
        print("FRAUDSHIELD - PREVISÃO PERSISTIDA")
        print("=" * 55)
        print(f"Event ID: {result.event_id}")
        print(f"Fraud Score: {result.fraud_score:.6f}")
        print(f"Classificação: {classification}")
        print(f"Modelo: {result.model_version}")
        print("=" * 55 + "\n")

    consumer = TransactionConsumer(
        group_id=args.group_id
    )

    consumer.start(
        handler=handle_transaction,
        max_messages=args.limit,
    )


if __name__ == "__main__":
    main()
