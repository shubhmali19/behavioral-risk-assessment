from fastapi import APIRouter, HTTPException
from app.schemas.assessment import AssessmentInput, PredictionResponse, PredictionResult
from app.services.ml_service import ml_service

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(input_data: AssessmentInput):
    """Quick predict — does NOT save to DB."""
    try:
        result = ml_service.predict(input_data.model_dump())
        return PredictionResponse(data=PredictionResult(**result))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
