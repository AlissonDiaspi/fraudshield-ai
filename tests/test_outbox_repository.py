
from unittest.mock import MagicMock

import pytest

from sqlalchemy.dialects import postgresql

from fraudshield.database.repositories.outbox_repository import (
    OutboxRepository,
)


def test_get_pending_uses_skip_locked():
    db = MagicMock()

    db.scalars.return_value.all.return_value = []

    repository = OutboxRepository(db)

    result = repository.get_pending(limit=10)

    assert result == []

    db.scalars.assert_called_once()

    statement = db.scalars.call_args.args[0]

    # Compila a consulta utilizando o dialeto PostgreSQL.
    compiled = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={
                "literal_binds": True,
            },
        )
    )

    assert "FOR UPDATE SKIP LOCKED" in compiled
    assert "LIMIT 10" in compiled


@pytest.mark.parametrize(
    "limit",
    [0, -1, -10],
)
def test_get_pending_rejects_invalid_limit(limit):
    repository = OutboxRepository(
        MagicMock()
    )

    with pytest.raises(ValueError):
        repository.get_pending(limit=limit)
