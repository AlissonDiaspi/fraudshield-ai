
import argparse

from fraudshield.pytorch.trainer import (
    TrainingConfig,
    train_pytorch_model,
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Treina a rede neural experimental "
            "do FraudShield AI."
        )
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=512,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--patience",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    config = TrainingConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        patience=args.patience,
    )

    train_pytorch_model(config)


if __name__ == "__main__":
    main()
