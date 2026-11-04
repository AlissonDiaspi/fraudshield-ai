
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_baseline(
    path: str | Path,
) -> dict:
    """
    Carrega e valida o baseline estatístico.
    """

    with Path(path).open(
        "r", encoding="utf-8"
    ) as file:
        baseline = json.load(file)

    if not isinstance(
        baseline.get("features"), dict
    ) or not baseline["features"]:
        raise ValueError(
            "Baseline sem features válidas."
        )

    return baseline


def calculate_psi_from_baseline(
    feature_baseline: dict,
    current: pd.Series,
    epsilon: float = 1e-6,
) -> float:
    """
    Calcula PSI usando os intervalos fixos
    armazenados no baseline.
    """

    if epsilon <= 0:
        raise ValueError(
            "epsilon deve ser maior que zero."
        )

    values = pd.to_numeric(
        current, errors="coerce"
    ).to_numpy(dtype=float)

    values = values[np.isfinite(values)]

    if len(values) == 0:
        raise ValueError(
            "A amostra não possui valores válidos."
        )

    edges = feature_baseline["bin_edges"]

    reference_counts = np.asarray(
        feature_baseline["bin_counts"],
        dtype=float,
    )

    if len(edges) == 1:
        # Feature constante no treinamento.
        constant = float(edges[0])

        current_counts = np.array([
            np.sum(values == constant),
            np.sum(values != constant),
        ], dtype=float)

    else:
        numeric_edges = np.asarray(
            [float(edge) for edge in edges],
            dtype=float,
        )

        if (
            len(numeric_edges)
            != len(reference_counts) + 1
        ):
            raise ValueError(
                "Intervalos incompatíveis com "
                "as contagens do baseline."
            )

        if not np.all(
            np.diff(numeric_edges) > 0
        ):
            raise ValueError(
                "Os intervalos devem ser crescentes."
            )

        current_counts, _ = np.histogram(
            values,
            bins=numeric_edges,
        )

    if (
        len(reference_counts)
        != len(current_counts)
    ):
        raise ValueError(
            "Contagens incompatíveis."
        )

    if reference_counts.sum() <= 0:
        raise ValueError(
            "Baseline sem observações válidas."
        )

    reference_pct = (
        reference_counts / reference_counts.sum()
    )

    current_pct = (
        current_counts / current_counts.sum()
    )

    reference_pct = np.maximum(
        reference_pct, epsilon
    )
    current_pct = np.maximum(
        current_pct, epsilon
    )

    reference_pct /= reference_pct.sum()
    current_pct /= current_pct.sum()

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def classify_drift(psi: float) -> str:
    """
    Classificação heurística do PSI.
    """

    if psi < 0.10:
        return "STABLE"

    if psi < 0.25:
        return "MODERATE"

    return "SIGNIFICANT"


def detect_data_drift(
    baseline: dict,
    transactions: list[dict],
    min_samples: int = 100,
) -> dict:
    """
    Compara transações recentes com o baseline.

    Não classifica drift quando a quantidade
    de transações é insuficiente.
    """

    if min_samples < 1:
        raise ValueError(
            "min_samples deve ser positivo."
        )

    if not transactions:
        return {
            "status": "INSUFFICIENT_DATA",
            "sample_size": 0,
            "features": {},
        }

    if len(transactions) < min_samples:
        return {
            "status": "INSUFFICIENT_DATA",
            "sample_size": len(transactions),
            "features": {},
        }

    df = pd.DataFrame(transactions)

    results = {}

    for feature, reference in (
        baseline["features"].items()
    ):
        if feature not in df.columns:
            results[feature] = {
                "status": "MISSING_FEATURE",
                "psi": None,
            }
            continue

        values = pd.to_numeric(
            df[feature],
            errors="coerce",
        )

        valid_values = values.replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        missing_rate = (
            1 - len(valid_values) / len(df)
        )

        if valid_values.empty:
            results[feature] = {
                "status": "NO_VALID_VALUES",
                "psi": None,
                "missing_rate": missing_rate,
            }
            continue

        psi = calculate_psi_from_baseline(
            reference,
            valid_values,
        )

        results[feature] = {
            "psi": round(psi, 6),
            "status": classify_drift(psi),
            "missing_rate": round(
                missing_rate, 6
            ),
        }

    significant = sum(
        result["status"] == "SIGNIFICANT"
        for result in results.values()
    )

    moderate = sum(
        result["status"] == "MODERATE"
        for result in results.values()
    )

    return {
        "status": "ANALYZED",
        "sample_size": len(transactions),
        "total_features": len(results),
        "significant_features": significant,
        "moderate_features": moderate,
        "features": results,
    }
