
import os

from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


def main():
    print("Teste postgre")

    username = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    database = os.environ["POSTGRES_DB"]

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=username,
        password=password,
        host="127.0.0.1",
        port=5433,
        database=database
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )

            database_name = result.scalar_one()

            print("Conexão estabelecida com sucesso!")
            print(f"Banco conectado: {database_name}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
