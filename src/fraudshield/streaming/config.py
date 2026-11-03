
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KafkaConfig:
    bootstrap_servers: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "127.0.0.1:9092"
    )

    raw_topic: str = "transactions.raw"
    predicted_topic: str = "transactions.predicted"
    dlq_topic: str = "transactions.dlq"

    consumer_group: str = "fraudshield-detector"


KAFKA_CONFIG = KafkaConfig()
