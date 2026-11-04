
import argparse
import json
from pathlib import Path

from fraudshield.database.connection import (
    SessionLocal,
)
from fraudshield.database.repositories.prediction_repository import (
    PredictionRepository,
)
from fraudshield.monitoring.drift_detector import (
    detect_data_drift,
    load_baseline,
)


BASELINE_PATH = Path(
    "artifacts/monitoring/drift_baseline.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Data Drift"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
    )

    parser.add_argument(
        "--min-samples",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--model-version",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    baseline = load_baseline(BASELINE_PATH)

    with SessionLocal() as db:
        repository = PredictionRepository(db)

        transactions = (
            repository.get_recent_features(
                limit=args.limit,
                model_version=args.model_version,
            )
        )

    report = detect_data_drift(
        baseline,
        transactions,
        min_samples=args.min_samples,
    )

    print(
        "\n=== FRAUDSHIELD AI - DATA DRIFT ==="
    )

    print(
        f"Transações analisadas: "
        f"{report['sample_size']}"
    )

    print(
        f"Status: {report['status']}"
    )

    if report["status"] == "ANALYZED":
        print(
            f"Features com drift significativo: "
            f"{report['significant_features']}"
        )

        print(
            f"Features com drift moderado: "
            f"{report['moderate_features']}"
        )

        print("\n=== RESULTADOS POR FEATURE ===")

        for feature, result in (
            report["features"].items()
        ):
            print(
                f"{feature}: "
                f"PSI={result['psi']} | "
                f"{result['status']}"
            )

    output_path = Path(
        "artifacts/monitoring/drift_report.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            allow_nan=False,
        )

    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()
