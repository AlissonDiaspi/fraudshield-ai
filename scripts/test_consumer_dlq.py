
import json
import logging

from confluent_kafka import Producer

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.schemas import TransactionEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    producer = Producer({
        "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
        "acks": "all",
    })

    invalid_payload = {
        "event_id": "invalid-uuid",
        "schema_version": 1,
        "features": {
            "V1": "invalid-value",
        },
    }

    producer.produce(
        topic=KAFKA_CONFIG.raw_topic,
        key=b"dlq-test-invalid",
        value=json.dumps(
            invalid_payload
        ).encode("utf-8"),
    )

    print("Mensagem inválida enviada.")

    
    import pandas as pd

    dataset = pd.read_csv(
        "data/raw/creditcard.csv",
        nrows=1,
    )

    features = dataset.drop(
        columns=["Class"]
    ).iloc[0].to_dict()

    valid_event = TransactionEvent.from_features(
        features
    )

    producer.produce(
        topic=KAFKA_CONFIG.raw_topic,
        key=str(valid_event.event_id).encode("utf-8"),
        value=valid_event.model_dump_json().encode("utf-8"),
    )

    print("Mensagem válida enviada.")
    print(f"Event ID válido: {valid_event.event_id}")

    remaining = producer.flush(timeout=30)

    if remaining:
        raise RuntimeError(
            f"{remaining} mensagens não confirmadas."
        )


if __name__ == "__main__":
    main()
