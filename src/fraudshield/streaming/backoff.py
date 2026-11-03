
from datetime import datetime, timedelta, timezone


INITIAL_DELAY_SECONDS = 5
MAX_DELAY_SECONDS = 300


def calculate_backoff_seconds(attempts: int) -> int:
    """
    Calcula o intervalo até a próxima tentativa.

    attempts representa o número de falhas já registradas.
    """
    if attempts < 1:
        raise ValueError(
            "attempts deve ser maior ou igual a 1"
        )

    delay = INITIAL_DELAY_SECONDS * (2 ** min(attempts - 1, 6))

    return min(delay, MAX_DELAY_SECONDS)


def calculate_next_attempt_at(
    attempts: int,
    now: datetime | None = None,
) -> datetime:
    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError(
            "now deve conter informação de fuso horário"
        )

    delay = calculate_backoff_seconds(attempts)

    return now + timedelta(seconds=delay)
