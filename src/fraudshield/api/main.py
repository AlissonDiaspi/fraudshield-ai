
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fraudshield.api.routers import (
    health,
    predictions,
    history,
    statistics
)

from fraudshield.api.services.prediction_service import (
    PredictionService
)

from fraudshield.registry_loader import (
    load_registered_model_info
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== FRAUDSHIELD AI — STARTUP ===")

    print("Carregando modelo do MLflow Registry...")

    registered = load_registered_model_info()

    app.state.prediction_service = PredictionService(
        model=registered.model,
        model_version=registered.version
    )

    app.state.model_version = registered.version

    print(
        f"Modelo carregado! "
        f"Versão MLflow: {registered.version}"
    )

    yield

    print("Encerrando FraudShield AI...")

    app.state.prediction_service = None


app = FastAPI(
    title="FraudShield AI API",
    description=(
        "API de detecção de fraudes financeiras "
        "utilizando Machine Learning."
    ),
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(history.router)
app.include_router(statistics.router)
