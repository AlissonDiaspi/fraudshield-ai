
import argparse
import logging
import time

from fraudshield.streaming.outbox_publisher import (
    OutboxPublisher,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Outbox Publisher contínuo"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Intervalo entre consultas em segundos",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Quantidade máxima de eventos por ciclo",
    )

    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval deve ser maior que zero")

    if args.limit <= 0:
        parser.error("--limit deve ser maior que zero")

    publisher = OutboxPublisher()

    logger.info(
        "Outbox Publisher iniciado. Intervalo: %.1fs",
        args.interval,
    )

    try:
        while True:
            try:
                published, failed = publisher.publish_pending(
                    limit=args.limit,
                )

                if published > 0 or failed > 0:
                    logger.info(
                        "Ciclo concluído: publicados=%s falhas=%s",
                        published,
                        failed,
                    )

            except Exception:
                logger.exception(
                    "Erro no ciclo do publisher. "
                    "Nova tentativa no próximo ciclo."
                )

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info(
            "Encerrando Outbox Publisher..."
        )


if __name__ == "__main__":
    main()
