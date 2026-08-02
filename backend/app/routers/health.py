import json
from pathlib import Path
from fastapi import APIRouter
from app.schemas.assessment import HealthResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()

MODEL_METADATA_PATH = Path(
    "/Users/chiragmali/Documents/Summer Internship/risk_assessment/"
    "behavioral-risk-assessment/ml/models/model_metadata.json"
)


@router.get("/health", response_model=HealthResponse)
def health_check():
    from app.services.ml_service import ml_service
    from app.database import engine
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            db_status = "connected"
    except Exception:
        pass

    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_loaded,
        database=db_status,
        version=settings.VERSION,
    )


@router.get("/model/info")
def model_info():
    if MODEL_METADATA_PATH.exists():
        with open(MODEL_METADATA_PATH) as f:
            return json.load(f)
    return {"error": "model_metadata.json not found"}
