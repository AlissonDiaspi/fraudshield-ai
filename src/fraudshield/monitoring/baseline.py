
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from fraudshield.data import (
    load_dataset,
    split_dataset,
    split_features_target,
)


def build_baseline(
    dataset_path: str | Path,
    bins: int = 10,
) -> dict:
    """
    Cria um baseline estatístico utilizando
    exclusivamente os dados de treinamento.

    O baseline será utilizado para comparar
    a distribuição das features com dados
    recebidos posteriormente.
    """

    if bins < 2:
        raise ValueError(
            "bins deve ser maior ou igual a 2."
        )

    df = load_dataset(dataset_path)

    X, y = split_features_target(df)

    X_train, _, _, _, _, _ = split_dataset(X, y)

    features = {}

    for column in X_train.columns:
        values = pd.to_numeric(
            X_train[column],
            errors="coerce",
        ).to_numpy(dtype=float)

        finite_values = values[
            np.isfinite(values)
        ]

        if len(finite_values) == 0:
            raise ValueError(
                f"Feature sem valores válidos: {column}"
            )

        quantiles = np.linspace(
            0,
            1,
            bins + 1,
        )

        edges = np.unique(
            np.quantile(
                finite_values,
                quantiles,
            )
        )

        if len(edges) < 2:
            # Caso especial:
            # a feature possui apenas um valor
            # na distribuição de treinamento.
            constant_value = float(
                finite_values[0]
            )

            counts = [
                int(len(finite_values)),
                0,
            ]

            edges_list = [constant_value]

        else:
            # Incluímos valores menores ou maiores
            # que os encontrados no treinamento.
            edges[0] = -np.inf
            edges[-1] = np.inf

            counts_array, _ = np.histogram(
                finite_values,
                bins=edges,
            )

            counts = (
                counts_array.astype(int).tolist()
            )

            # JSON não aceita Infinity e -Infinity
            # como valores numéricos.
            #
            # Por isso, armazenamos esses limites
            # como strings.
            #
            # Na leitura, float("Infinity") e
            # float("-Infinity") restauram os
            # valores numéricos originais.
            edges_list = [
                "-Infinity"
                if value == -np.inf
                else "Infinity"
                if value == np.inf
                else float(value)
                for value in edges
            ]

        features[column] = {
            "count": int(
                len(finite_values)
            ),
            "missing_count": int(
                len(values) - len(finite_values)
            ),
            "mean": float(
                np.mean(finite_values)
            ),
            "std": float(
                np.std(finite_values)
            ),
            "min": float(
                np.min(finite_values)
            ),
            "max": float(
                np.max(finite_values)
            ),
            "median": float(
                np.median(finite_values)
            ),
            "bin_edges": edges_list,
            "bin_counts": counts,
        }

    baseline = {
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataset": Path(dataset_path).name,
        "split_random_state": 42,
        "training_fraction": 0.70,
        "bins": bins,
        "features": features,
    }

    return baseline


def save_baseline(
    baseline: dict,
    output_path: str | Path,
) -> None:
    """
    Salva o baseline estatístico em JSON.

    Utiliza allow_nan=False para garantir
    que o arquivo gerado seja compatível
    com o padrão JSON.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            baseline,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
