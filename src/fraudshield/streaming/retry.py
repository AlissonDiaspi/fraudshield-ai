
import logging
import time

from collections.abc import Callable
from typing import TypeVar


logger = logging.getLogger(__name__)

T = TypeVar("T")


def execute_with_retry(
    operation: Callable[[], T],
    *,
    max_attempts: int = 4,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...],
) -> T:
    """
    Executa uma operação com retentativas.

    Apenas exceções explicitamente configuradas
    como recuperáveis provocam novas tentativas.
    """

    if max_attempts < 1:
        raise ValueError(
            "max_attempts deve ser maior ou igual a 1"
        )

    if initial_delay < 0:
        raise ValueError(
            "initial_delay não pode ser negativo"
        )

    if backoff_factor < 1:
        raise ValueError(
            "backoff_factor deve ser maior ou igual a 1"
        )

    if not retryable_exceptions:
        raise ValueError(
            "Informe pelo menos uma exceção recuperável"
        )

    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()

        except retryable_exceptions as error:
            if attempt == max_attempts:
                logger.error(
                    "Operação falhou após %s tentativas: %s",
                    max_attempts,
                    error,
                )
                raise

            logger.warning(
                "Tentativa %s/%s falhou: %s. "
                "Nova tentativa em %.1f segundo(s).",
                attempt,
                max_attempts,
                error,
                delay,
            )

            time.sleep(delay)
            delay *= backoff_factor

    raise RuntimeError(
        "Estado inesperado na execução de retry"
    )
