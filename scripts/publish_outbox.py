
import argparse
import logging

from fraudshield.streaming.outbox_publisher import (
    OutboxPublisher,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Outbox Publisher"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Quantidade máxima de eventos por execução",
    )

    args = parser.parse_args()

    publisher = OutboxPublisher()

    published, failed = publisher.publish_pending(
        limit=args.limit,
    )

    print("\n" + "=" * 50)
    print("FRAUDSHIELD AI - OUTBOX PUBLISHER")
    print("=" * 50)
    print(f"Publicados: {published}")
    print(f"Falhas: {failed}")
    print("=" * 50)


if __name__ == "__main__":
    main()
