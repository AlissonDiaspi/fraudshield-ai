
import pytest

from prometheus_client import REGISTRY

from fraudshield.monitoring.drift_metrics import (
    publish_drift_metrics,
)


def get_metric_value(
    metric_name: str,
    labels: dict | None = None,
):
    return REGISTRY.get_sample_value(
        metric_name,
        labels=labels or {},
    )


def test_publish_analyzed_drift_metrics():
    report = {
        "status": "ANALYZED",
        "sample_size": 1000,
        "significant_features": 1,
        "moderate_features": 1,
        "features": {
            "Amount": {
                "psi": 0.45,
                "status": "SIGNIFICANT",
            },
            "V1": {
                "psi": 0.15,
                "status": "MODERATE",
            },
            "V2": {
                "psi": 0.02,
                "status": "STABLE",
            },
        },
    }

    publish_drift_metrics(report)

    assert get_metric_value(
        "fraudshield_data_drift_sample_size"
    ) == 1000

    assert get_metric_value(
        "fraudshield_data_drift_analysis_status"
    ) == 1

    assert get_metric_value(
        "fraudshield_data_drift_significant_features"
    ) == 1

    assert get_metric_value(
        "fraudshield_data_drift_moderate_features"
    ) == 1

    assert get_metric_value(
        "fraudshield_data_drift_psi",
        {"feature": "Amount"},
    ) == pytest.approx(0.45)


def test_insufficient_data_clears_psi():
    publish_drift_metrics({
        "status": "ANALYZED",
        "sample_size": 100,
        "significant_features": 1,
        "moderate_features": 0,
        "features": {
            "Amount": {
                "psi": 0.5,
                "status": "SIGNIFICANT",
            },
        },
    })

    publish_drift_metrics({
        "status": "INSUFFICIENT_DATA",
        "sample_size": 13,
        "features": {},
    })

    assert get_metric_value(
        "fraudshield_data_drift_analysis_status"
    ) == 0

    assert get_metric_value(
        "fraudshield_data_drift_sample_size"
    ) == 13

    assert get_metric_value(
        "fraudshield_data_drift_psi",
        {"feature": "Amount"},
    ) is None


def test_invalid_drift_status():
    with pytest.raises(ValueError):
        publish_drift_metrics({
            "status": "UNKNOWN",
            "sample_size": 100,
        })
