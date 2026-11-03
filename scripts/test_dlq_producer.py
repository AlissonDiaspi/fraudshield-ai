
import logging
import uuid

from fraudshield.streaming.dlq_producer import (
    DeadLetterProducer,
)
from fraudshield.streaming.schemas import DeadLetterEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    event = DeadLetterEvent(
        event_id=uuid.uuid4(),
        error="Teste: transação com dados inválidos",
        original_payload={
            "features": {
                "V1": "valor_invalido",
            }
        },
    )

    producer = DeadLetterProducer()

    producer.publish(event)

    print("\n" + "=" * 50)
    print("FRAUDSHIELD AI - TESTE DLQ")
    print("=" * 50)
    print("Mensagem publicada com sucesso!")
    print(f"Event ID: {event.event_id}")
    print(f"Erro: {event.error}")
    print("=" * 50)


if __name__ == "__main__":
    main()
