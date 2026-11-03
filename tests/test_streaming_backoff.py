
from datetime import datetime, timedelta, timezone

import pytest

from fraudshield.streaming.backoff import (
    calculate_backoff_seconds,
    calculate_next_attempt_at,
)


@pytest.mark.parametrize(
    "attempts, expected",
    [
        (1, 5),
        (2, 10),
        (3, 20),
        (4, 40),
        (5, 80),
        (6, 160),
        (7, 300),
        (8, 300),
        (20, 300),
    ],
)
def test_backoff_intervals(attempts, expected):
    assert calculate_backoff_seconds(attempts) == expected


@pytest.mark.parametrize("attempts", [0, -1, -10])
def test_backoff_rejects_invalid_attempts(attempts):
    with pytest.raises(ValueError):
        calculate_backoff_seconds(attempts)


def test_next_attempt_at():
    now = datetime(
        2026, 11, 3, 12, 0, 0,
        tzinfo=timezone.utc,
    )

    result = calculate_next_attempt_at(
        attempts=3,
        now=now,
    )

    assert result == now + timedelta(seconds=20)


def test_next_attempt_rejects_naive_datetime():
    now = datetime(2026, 11, 3, 12, 0, 0)

    with pytest.raises(ValueError):
        calculate_next_attempt_at(
            attempts=1,
            now=now,
        )
