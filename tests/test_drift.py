
import numpy as np
import pandas as pd
import pytest

from fraudshield.monitoring.drift import calculate_psi


def test_psi_identical_distributions():
    reference = pd.Series(
        np.arange(1000, dtype=float)
    )

    current = reference.copy()

    psi = calculate_psi(reference, current)

    assert psi == pytest.approx(0.0, abs=1e-10)


def test_psi_detects_distribution_change():
    reference = pd.Series(
        np.linspace(0, 100, 1000)
    )

    current = pd.Series(
        np.linspace(200, 300, 1000)
    )

    psi = calculate_psi(reference, current)

    assert psi > 0.25


def test_psi_constant_feature_without_change():
    reference = pd.Series([5.0] * 100)

    current = pd.Series([5.0] * 100)

    psi = calculate_psi(reference, current)

    assert psi == pytest.approx(0.0)


def test_psi_constant_feature_with_change():
    reference = pd.Series([5.0] * 100)

    current = pd.Series([8.0] * 100)

    psi = calculate_psi(reference, current)

    assert psi > 0.25


def test_psi_rejects_empty_reference():
    with pytest.raises(ValueError):
        calculate_psi(
            pd.Series(dtype=float),
            pd.Series([1.0, 2.0]),
        )


def test_psi_rejects_empty_current():
    with pytest.raises(ValueError):
        calculate_psi(
            pd.Series([1.0, 2.0]),
            pd.Series(dtype=float),
        )


def test_psi_rejects_invalid_bins():
    with pytest.raises(ValueError):
        calculate_psi(
            pd.Series([1.0, 2.0]),
            pd.Series([1.0, 2.0]),
            bins=1,
        )


def test_psi_handles_missing_values():
    reference = pd.Series([
        1.0, 2.0, np.nan, 3.0, 4.0
    ])

    current = pd.Series([
        1.0, np.nan, 2.0, 3.0, 4.0
    ])

    psi = calculate_psi(reference, current)

    assert psi == pytest.approx(0.0)
