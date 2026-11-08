
import numpy as np
import pandas as pd

from fraudshield.monitoring.drift_detector import (
    calculate_psi_from_baseline,
    classify_drift,
)


def main() -> None:
    rng = np.random.default_rng(42)

    # Distribuição de referência simulada.
    reference = rng.normal(
        loc=100,
        scale=20,
        size=10000,
    )

    # Intervalos definidos exclusivamente
    # pela distribuição de referência.
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

    baseline = {
        "bin_edges": [
            float(edge) for edge in edges
        ],
        "bin_counts": counts.tolist(),
    }

    # Cenário 1: distribuição semelhante.
    stable = rng.normal(
        loc=100,
        scale=20,
        size=10000,
    )

    # Cenário 2: distribuição deslocada.
    shifted = rng.normal(
        loc=160,
        scale=20,
        size=10000,
    )

    stable_psi = calculate_psi_from_baseline(
        baseline,
        pd.Series(stable),
    )

    shifted_psi = calculate_psi_from_baseline(
        baseline,
        pd.Series(shifted),
    )

    print(
        "\nSimulacao de drift"
    )

    print("\nCenario 1 - Distribuicao semelhante")
    print(f"PSI: {stable_psi:.6f}")
    print(f"Status: {classify_drift(stable_psi)}")

    print("\nCenario 2 - Distribuicao deslocada")
    print(f"PSI: {shifted_psi:.6f}")
    print(f"Status: {classify_drift(shifted_psi)}")

    assert stable_psi < 0.10
    assert shifted_psi > 0.25
    assert shifted_psi > stable_psi

    print("\nSimulacao validada com sucesso!")


if __name__ == "__main__":
    main()
