
import logging
import os

from prometheus_client import start_http_server


logger = logging.getLogger(__name__)


def start_metrics_server(
    port: int | None = None,
    addr: str | None = None,
) -> None:
    """
    Inicia um servidor HTTP para expor
    as metricas Prometheus do processo.
    """
    if port is None:
        port = int(
            os.getenv("FRAUDSHIELD_METRICS_PORT", "8001")
        )

    if addr is None:
        addr = os.getenv(
            "FRAUDSHIELD_METRICS_HOST",
            "127.0.0.1",
        )

    if not 1 <= port <= 65535:
        raise ValueError(
            "A porta deve estar entre 1 e 65535."
        )

    start_http_server(
        port=port,
        addr=addr,
    )

    logger.info(
        "Servidor de metricas iniciado em "
        "http://%s:%s/metrics",
        addr,
        port,
    )
