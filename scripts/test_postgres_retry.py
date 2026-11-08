
import logging

from sqlalchemy.exc import OperationalError

from fraudshield.database.connection import SessionLocal
from fraudshield.streaming.retry import execute_with_retry


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class SimulatedDatabaseService:
    def __init__(self):
        self.attempts = 0

    def check_connection(self):
        self.attempts += 1

        print(
            f"\nTentativa de conexão: {self.attempts}"
        )

        if self.attempts <= 2:
            raise OperationalError(
                statement="SELECT 1",
                params=None,
                orig=ConnectionError(
                    "PostgreSQL temporariamente indisponível"
                ),
            )

        with SessionLocal() as db:
            result = db.execute(
                __import__("sqlalchemy").text("SELECT 1")
            ).scalar_one()

        return result


def main():
    service = SimulatedDatabaseService()

    result = execute_with_retry(
        operation=service.check_connection,
        max_attempts=4,
        initial_delay=1.0,
        backoff_factor=2.0,
        retryable_exceptions=(
            OperationalError,
        ),
    )

    print("\n" + "=" * 55)
    print("Postgre retry test")
    print("=" * 55)
    print(f"Resultado SQL: {result}")
    print(f"Total de tentativas: {service.attempts}")
    print("Recuperação: SUCESSO")
    print("=" * 55)


if __name__ == "__main__":
    main()
