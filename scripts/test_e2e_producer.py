
import uuid
import pandas as pd

from confluent_kafka import Producer

from fraudshield.streaming.config import KAFKA_CONFIG
from fraudshield.streaming.schemas import TransactionEvent


def main():
    df = pd.read_csv("data/raw/creditcard.csv")

    # Seleciona uma transação real do dataset.
    row = df.iloc[0]

    features = {
        column: float(row[column])
        for column in df.columns
        if column != "Class"
    }

    event = TransactionEvent(
        event_id=uuid.uuid4(),
        features=features,
    )

    producer = Producer({
        "bootstrap.servers": KAFKA_CONFIG.bootstrap_servers,
        "acks": "all",
    })

    def delivery_callback(error, message):
        if error is not None:
            print(f"Falha na publicação: {error}")
        else:
            print("Transação publicada com sucesso!")
            print(f"Topic: {message.topic()}")
            print(f"Partition: {message.partition()}")
            print(f"Offset: {message.offset()}")

    producer.produce(
        topic=KAFKA_CONFIG.raw_topic,
        key=str(event.event_id),
        value=event.model_dump_json(),
        on_delivery=delivery_callback,
    )

    remaining = producer.flush(timeout=20)

    if remaining:
        raise RuntimeError(
            "Kafka não confirmou todas as mensagens."
        )

    print(f"\nEVENT_ID: {event.event_id}")
    print("Guarde esse identificador para a validação.")


if __name__ == "__main__":
    main()
