
import numpy as np
import pandas as pd
import pytest

from fraudshield.monitoring.drift_detector import (
    calculate_psi_from_baseline,
    classify_drift,
    detect_data_drift,
)


@pytest.fixture
def baseline():
    rng = np.random.default_rng(42)

    reference = rng.normal(
        loc=100,
        scale=20,
        size=10000,
    )

    edges = np.unique(
        np.quantile(
            reference,
            np.linspace(0, 1, 11),
        )
    )

    edges[0] = -np.inf
    edges[-1] = np.inf

    counts, _ = np.histogram(
        reference,
        bins=edges,
    )

    return {
        "features": {
            "Amount": {
                "bin_edges": [
                    "-Infinity"
                    if edge == -np.inf
                    else "Infinity"
                    if edge == np.inf
                    else float(edge)
                    for edge in edges
                ],
                "bin_counts": counts.tolist(),
            }
        }
    }


def test_similar_distribution_is_stable(baseline):
    rng = np.random.default_rng(123)

    current = pd.Series(
        rng.normal(100, 20, 10000)
    )

    psi = calculate_psi_from_baseline(
        baseline["features"]["Amount"],
        current,
    )

    assert psi < 0.10
    assert classify_drift(psi) == "STABLE"


def test_shifted_distribution_has_significant_drift(
    baseline,
):
    rng = np.random.default_rng(123)

    current = pd.Series(
        rng.normal(160, 20, 10000)
    )

    psi = calculate_psi_from_baseline(
        baseline["features"]["Amount"],
        current,
    )

    assert psi > 0.25
    assert classify_drift(psi) == "SIGNIFICANT"


def test_identical_histogram_has_zero_psi():
    reference = {
        "bin_edges": [
            "-Infinity",
            0.0,
            "Infinity",
        ],
        "bin_counts": [50, 50],
    }

    current = pd.Series(
        [-1.0] * 50 + [1.0] * 50
    )

    psi = calculate_psi_from_baseline(
        reference,
        current,
    )

    assert psi == pytest.approx(0.0)


def test_insufficient_data(baseline):
    transactions = [
        {"Amount": 100.0}
        for _ in range(13)
    ]

    result = detect_data_drift(
        baseline,
        transactions,
        min_samples=100,
    )

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["sample_size"] == 13


def test_missing_feature(baseline):
    transactions = [
        {"V1": 1.0}
        for _ in range(100)
    ]

    result = detect_data_drift(
        baseline,
        transactions,
    )

    assert (
        result["features"]["Amount"]["status"]
        == "MISSING_FEATURE"
    )


def test_constant_reference_feature():
    reference = {
        "bin_edges": [5.0],
        "bin_counts": [100, 0],
    }

    unchanged = pd.Series([5.0] * 100)
    changed = pd.Series([8.0] * 100)

    stable_psi = calculate_psi_from_baseline(
        reference,
        unchanged,
    )

    changed_psi = calculate_psi_from_baseline(
        reference,
        changed,
    )

    assert stable_psi == pytest.approx(0.0)
    assert changed_psi > 0.25


def test_missing_values_are_reported(baseline):
    transactions = (
        [{"Amount": 100.0}] * 80
        + [{"Amount": None}] * 20
    )

    result = detect_data_drift(
        baseline,
        transactions,
    )

    feature = result["features"]["Amount"]

    assert result["status"] == "ANALYZED"
    assert feature["missing_rate"] == pytest.approx(0.20)


def test_invalid_baseline_counts():
    reference = {
        "bin_edges": [
            "-Infinity",
            0.0,
            "Infinity",
        ],
        "bin_counts": [100],
    }

    with pytest.raises(ValueError):
        calculate_psi_from_baseline(
            reference,
            pd.Series([-1.0, 1.0]),
        )
