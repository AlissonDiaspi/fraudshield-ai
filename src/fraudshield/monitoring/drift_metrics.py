
from datetime import datetime, timezone

from fraudshield.monitoring.metrics import (
    DATA_DRIFT_ANALYSIS_STATUS,
    DATA_DRIFT_LAST_ANALYSIS_TIMESTAMP,
    DATA_DRIFT_MODERATE_FEATURES,
    DATA_DRIFT_PSI,
    DATA_DRIFT_SAMPLE_SIZE,
    DATA_DRIFT_SIGNIFICANT_FEATURES,
)


def publish_drift_metrics(report: dict) -> None:
    """
    Atualiza as metricas Prometheus com
    os resultados de uma analise de drift.

    Esta funcao deve ser executada no
    processo que hospeda o servidor
    de metricas.
    """

    status = report.get("status")

    if status not in (
        "ANALYZED",
        "INSUFFICIENT_DATA",
    ):
        raise ValueError(
            f"Status de drift invalido: {status}"
        )

    sample_size = int(
        report.get("sample_size", 0)
    )

    DATA_DRIFT_SAMPLE_SIZE.set(sample_size)

    DATA_DRIFT_LAST_ANALYSIS_TIMESTAMP.set(
        datetime.now(timezone.utc).timestamp()
    )

    if status == "INSUFFICIENT_DATA":
        DATA_DRIFT_ANALYSIS_STATUS.set(0)

        DATA_DRIFT_SIGNIFICANT_FEATURES.set(0)
        DATA_DRIFT_MODERATE_FEATURES.set(0)

        DATA_DRIFT_PSI.clear()
        return

    DATA_DRIFT_ANALYSIS_STATUS.set(1)

    DATA_DRIFT_SIGNIFICANT_FEATURES.set(
        int(
            report.get(
                "significant_features", 0
            )
        )
    )

    DATA_DRIFT_MODERATE_FEATURES.set(
        int(
            report.get(
                "moderate_features", 0
            )
        )
    )

    # Limpa os valores da analise anterior
    # para evitar expor features antigas.
    DATA_DRIFT_PSI.clear()

    for feature, result in (
        report.get("features", {}).items()
    ):
        psi = result.get("psi")

        if psi is None:
            continue

        DATA_DRIFT_PSI.labels(
            feature=feature
        ).set(float(psi))
