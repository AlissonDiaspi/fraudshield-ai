
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ModelConfig:
    """
    Configurações da versão inicial
    do modelo FraudShield AI.
    """

    model_name: str = "fraud_xgboost"
    model_version: str = "1.0.0"

    threshold: float = 0.5

    random_state: int = 42

    n_estimators: int = 300
    max_depth: int = 5
    learning_rate: float = 0.1
    subsample: float = 1.0
    colsample_bytree: float = 0.8
    min_child_weight: int = 3

    @property
    def model_path(self) -> Path:
        return (
            PROJECT_ROOT
            / "artifacts"
            / "models"
            / f"{self.model_name}.json"
        )


MODEL_CONFIG = ModelConfig()
