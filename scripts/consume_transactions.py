
import argparse
import logging

from fraudshield.streaming.consumer import TransactionConsumer
from fraudshield.streaming.schemas import TransactionEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def handle_transaction(event: TransactionEvent) -> None:
    print("\n" + "=" * 50)
    print("TRANSAÇÃO RECEBIDA")
    print("=" * 50)

    print(f"Event ID: {event.event_id}")
    print(f"Criada em: {event.created_at}")
    print(f"Schema version: {event.schema_version}")

    print(f"Valor: {event.features['Amount']:.2f}")
    print(f"Time: {event.features['Time']}")

    print(f"Total de features: {len(event.features)}")

    print("=" * 50 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FraudShield Kafka Consumer"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Quantidade de mensagens a processar",
    )

    args = parser.parse_args()

    consumer = TransactionConsumer()

    consumer.start(
        handler=handle_transaction,
        max_messages=args.limit,
    )


if __name__ == "__main__":
    main()
