
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
from fraudshield.config import MODEL_CONFIG
from fraudshield.model_io import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Carregando modelo FraudShield AI...")

    model = load_model(
        MODEL_CONFIG.model_path
    )

    app.state.prediction_service = PredictionService(
        model=model
    )

    print("Modelo carregado com sucesso!")

    yield

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