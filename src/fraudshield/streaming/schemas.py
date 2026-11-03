
from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)

from fraudshield.api.schemas import PredictionRequest


class TransactionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)

    schema_version: int = Field(default=1, ge=1)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    features: dict[str, float]

    @model_validator(mode="after")
    def validate_transaction(self):
        # Garante que toda mensagem recebida,
        # inclusive diretamente do Kafka,
        # respeite o contrato de features da API.
        validated = PredictionRequest(
            features=self.features
        )

        self.features = validated.features

        return self

    @classmethod
    def from_features(
        cls,
        features: dict[str, float]
    ) -> "TransactionEvent":
        return cls(features=features)


class PredictionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    fraud_score: float = Field(ge=0, le=1)

    prediction: int = Field(ge=0, le=1)

    model_version: str


class DeadLetterEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID | None = None

    failed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    error: str

    original_payload: dict | str
