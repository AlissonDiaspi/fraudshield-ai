
import logging

from fraudshield.streaming.retry import execute_with_retry


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class TemporaryError(Exception):
    pass


attempts = 0


def unstable_operation() -> str:
    global attempts

    attempts += 1

    print(f"Executando tentativa {attempts}")

    if attempts < 3:
        raise TemporaryError(
            "Serviço temporariamente indisponível"
        )

    return "Operação concluída com sucesso"


def main():
    result = execute_with_retry(
        unstable_operation,
        max_attempts=4,
        initial_delay=1.0,
        backoff_factor=2.0,
        retryable_exceptions=(TemporaryError,),
    )

    print("\n" + "=" * 50)
    print("FRAUDSHIELD AI - TESTE DE RETRY")
    print("=" * 50)
    print(result)
    print(f"Total de tentativas: {attempts}")
    print("=" * 50)


if __name__ == "__main__":
    main()
