
import pytest

from fraudshield.streaming.retry import execute_with_retry


class TemporaryError(Exception):
    pass


class PermanentError(Exception):
    pass


def test_retry_succeeds_on_third_attempt(monkeypatch):
    attempts = 0
    delays = []

    monkeypatch.setattr(
        "fraudshield.streaming.retry.time.sleep",
        lambda seconds: delays.append(seconds),
    )

    def operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise TemporaryError("Falha temporária")

        return "success"

    result = execute_with_retry(
        operation=operation,
        max_attempts=4,
        initial_delay=1.0,
        backoff_factor=2.0,
        retryable_exceptions=(TemporaryError,),
    )

    assert result == "success"
    assert attempts == 3
    assert delays == [1.0, 2.0]


def test_retry_raises_after_max_attempts(monkeypatch):
    attempts = 0

    monkeypatch.setattr(
        "fraudshield.streaming.retry.time.sleep",
        lambda seconds: None,
    )

    def operation():
        nonlocal attempts
        attempts += 1
        raise TemporaryError("Serviço indisponível")

    with pytest.raises(TemporaryError):
        execute_with_retry(
            operation=operation,
            max_attempts=4,
            initial_delay=1.0,
            backoff_factor=2.0,
            retryable_exceptions=(TemporaryError,),
        )

    assert attempts == 4


def test_retry_does_not_repeat_permanent_errors():
    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        raise PermanentError("Erro permanente")

    with pytest.raises(PermanentError):
        execute_with_retry(
            operation=operation,
            max_attempts=4,
            retryable_exceptions=(TemporaryError,),
        )

    assert attempts == 1


def test_retry_succeeds_immediately():
    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        return 42

    result = execute_with_retry(
        operation=operation,
        max_attempts=4,
        retryable_exceptions=(TemporaryError,),
    )

    assert result == 42
    assert attempts == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"initial_delay": -1},
        {"backoff_factor": 0.5},
        {"retryable_exceptions": ()},
    ],
)
def test_retry_rejects_invalid_configuration(kwargs):
    config = {
        "max_attempts": 4,
        "initial_delay": 1.0,
        "backoff_factor": 2.0,
        "retryable_exceptions": (TemporaryError,),
    }

    config.update(kwargs)

    with pytest.raises(ValueError):
        execute_with_retry(
            operation=lambda: "success",
            **config,
        )
