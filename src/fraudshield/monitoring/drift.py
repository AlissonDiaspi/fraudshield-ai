
import numpy as np
import pandas as pd


def calculate_psi(
    reference: pd.Series,
    current: pd.Series,
    bins: int = 10,
    epsilon: float = 1e-6,
) -> float:
    """
    Calcula o Population Stability Index (PSI).

    Os intervalos são definidos a partir dos quantis
    da distribuição de referência.

    Quanto maior o PSI, maior a diferença entre
    as distribuições.
    """

    if bins < 2:
        raise ValueError(
            "O número de intervalos deve ser >= 2."
        )

    if epsilon <= 0:
        raise ValueError(
            "Epsilon deve ser maior que zero."
        )

    reference_values = pd.to_numeric(
        reference, errors="coerce"
    ).dropna().to_numpy(dtype=float)

    current_values = pd.to_numeric(
        current, errors="coerce"
    ).dropna().to_numpy(dtype=float)

    reference_values = reference_values[
        np.isfinite(reference_values)
    ]

    current_values = current_values[
        np.isfinite(current_values)
    ]

    if len(reference_values) == 0:
        raise ValueError(
            "A distribuição de referência está vazia."
        )

    if len(current_values) == 0:
        raise ValueError(
            "A distribuição atual está vazia."
        )

    quantiles = np.linspace(0, 1, bins + 1)

    edges = np.unique(
        np.quantile(reference_values, quantiles)
    )

    if len(edges) < 2:
        # A feature é constante na referência.
        # Qualquer valor diferente é tratado
        # como uma categoria separada.
        constant = reference_values[0]

        reference_counts = np.array([
            np.sum(reference_values == constant),
            np.sum(reference_values != constant),
        ])

        current_counts = np.array([
            np.sum(current_values == constant),
            np.sum(current_values != constant),
        ])

    else:
        # Incluido também valores fora do intervalo
        # observado no treinamento.
        edges[0] = -np.inf
        edges[-1] = np.inf

        reference_counts, _ = np.histogram(
            reference_values,
            bins=edges,
        )

        current_counts, _ = np.histogram(
            current_values,
            bins=edges,
        )

    reference_pct = (
        reference_counts / reference_counts.sum()
    )

    current_pct = (
        current_counts / current_counts.sum()
    )

    # Suavização para evitar log(0).
    reference_pct = np.maximum(
        reference_pct, epsilon
    )

    current_pct = np.maximum(
        current_pct, epsilon
    )

    # Renormalização após suavização.
    reference_pct /= reference_pct.sum()
    current_pct /= current_pct.sum()

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)
