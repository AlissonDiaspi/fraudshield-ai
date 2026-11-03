
import argparse
import logging
import time

from fraudshield.config import PROJECT_ROOT
from fraudshield.data import load_dataset, split_features_target
from fraudshield.streaming.producer import TransactionProducer
from fraudshield.streaming.schemas import TransactionEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de transações FraudShield AI"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Quantidade de transações a enviar",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Intervalo entre transações em segundos",
    )

    args = parser.parse_args()

    if args.limit <= 0:
        parser.error("--limit deve ser maior que zero")

    if args.interval < 0:
        parser.error("--interval não pode ser negativo")

    dataset_path = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"

    print("Carregando dataset...")
    df = load_dataset(dataset_path)

    X, _ = split_features_target(df)

    producer = TransactionProducer()

    total = min(args.limit, len(X))

    print(f"Enviando {total} transações para o Kafka...")

    for index in range(total):
        features = {
            key: float(value)
            for key, value in X.iloc[index].to_dict().items()
        }

        event = TransactionEvent.from_features(features)

        producer.publish(event)

        print(
            f"[{index + 1}/{total}] "
            f"Evento enviado para fila: {event.event_id}"
        )

        if index < total - 1:
            time.sleep(args.interval)

    remaining = producer.flush()

    if remaining:
        raise RuntimeError(
            f"{remaining} mensagens ainda pendentes após o flush"
        )

    print("Envio finalizado. Verifique os callbacks de entrega.")


if __name__ == "__main__":
    main()
