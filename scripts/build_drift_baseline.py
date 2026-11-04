
from pathlib import Path

from fraudshield.monitoring.baseline import (
    build_baseline,
    save_baseline,
)


def main() -> None:
    dataset_path = Path("data/raw/creditcard.csv")

    output_path = Path(
        "artifacts/monitoring/drift_baseline.json"
    )

    baseline = build_baseline(dataset_path)

    save_baseline(baseline, output_path)

    print("\n=== FRAUDSHIELD AI — DRIFT BASELINE ===")
    print(f"Dataset: {baseline['dataset']}")
    print(f"Features: {len(baseline['features'])}")
    print(f"Intervalos solicitados: {baseline['bins']}")
    print(f"Arquivo: {output_path}")


if __name__ == "__main__":
    main()
