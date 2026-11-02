
from fastapi import APIRouter, Request


router = APIRouter(
    tags=["Health"]
)


@router.get("/")
def root():
    return {
        "application": "FraudShield AI",
        "status": "running",
        "version": "1.0.0"
    }


@router.get("/health")
def health_check(request: Request):
    model_loaded = (
        getattr(
            request.app.state,
            "prediction_service",
            None
        ) is not None
    )

    return {
        "status": (
            "healthy"
            if model_loaded
            else "unhealthy"
        ),
        "service": "fraudshield-api",
        "model_loaded": model_loaded
    }
