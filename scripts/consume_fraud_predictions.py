
import argparse
import logging

from fraudshield.streaming.consumer import TransactionConsumer
from fraudshield.streaming.inference_service import (
    StreamingInferenceService,
)
from fraudshield.streaming.schemas import TransactionEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Kafka Fraud Detection"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Quantidade de transações para analisar",
    )

    args = parser.parse_args()

    print("Carregando modelo champion do MLflow...")

    inference_service = StreamingInferenceService.from_registry()

    print(
        f"Modelo carregado, Versão: "
        f"{inference_service.model_version}"
    )

    def handle_transaction(event: TransactionEvent) -> None:
        result = inference_service.predict(event)

        classification = (
            "FRAUDE"
            if result.prediction == 1
            else "LEGÍTIMA"
        )

        print("\n" + "=" * 55)
        print("Analise")
        print("=" * 55)

        print(f"Event ID: {result.event_id}")
        print(f"Valor: {event.features['Amount']:.2f}")
        print(f"Fraud Score: {result.fraud_score:.6f}")
        print(f"Classificação: {classification}")
        print(f"Modelo MLflow: {result.model_version}")

        print("=" * 55 + "\n")

    consumer = TransactionConsumer(
        group_id="fraudshield-inference-test"
    )

    consumer.start(
        handler=handle_transaction,
        max_messages=args.limit,
    )


if __name__ == "__main__":
    main()
