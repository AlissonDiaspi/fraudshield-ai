
from unittest.mock import patch

import pytest

from fraudshield.monitoring.server import (
    start_metrics_server,
)


def test_metrics_server_starts():
    with patch(
        "fraudshield.monitoring.server.start_http_server"
    ) as server_mock:
        start_metrics_server(
            port=8001,
            addr="127.0.0.1",
        )

        server_mock.assert_called_once_with(
            port=8001,
            addr="127.0.0.1",
        )


@pytest.mark.parametrize(
    "port",
    [0, -1, 65536],
)
def test_invalid_metrics_port(port):
    with pytest.raises(
        ValueError,
        match="A porta deve estar entre",
    ):
        start_metrics_server(port=port)



def test_metrics_port_from_environment():
    with (
        patch.dict(
            "os.environ",
            {
                "FRAUDSHIELD_METRICS_PORT": "9001",
                "FRAUDSHIELD_METRICS_HOST": "127.0.0.1",
            },
        ),
        patch(
            "fraudshield.monitoring.server.start_http_server"
        ) as server_mock,
    ):
        start_metrics_server()

    server_mock.assert_called_once_with(
        port=9001,
        addr="127.0.0.1",
    )

