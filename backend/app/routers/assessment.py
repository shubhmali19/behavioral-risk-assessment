from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.assessment import (
    AssessmentInput,
    AssessmentResponse,
    AssessmentsListResponse,
    AssessmentRecord,
    PredictionResult,
)
from app.services.ml_service import ml_service
from app.services import assessment_service

router = APIRouter()


@router.post("/assessment", response_model=AssessmentResponse)
def create_assessment(input_data: AssessmentInput, db: Session = Depends(get_db)):
    """Run prediction and persist assessment + prediction to DB."""
    assessment = assessment_service.create_assessment(db, input_data)

    try:
        result = ml_service.predict(input_data.model_dump())
        assessment_service.save_prediction(db, assessment.id, result)
        assessment_service.mark_assessment_complete(db, assessment.id)
    except Exception as e:
        assessment_service.mark_assessment_failed(db, assessment.id)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return AssessmentResponse(
        assessment_id=assessment.id,
        data=PredictionResult(**result),
    )


@router.get("/assessment/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = assessment_service.get_assessment_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if not assessment.prediction:
        raise HTTPException(status_code=404, detail="Prediction not found for this assessment")

    pred = assessment.prediction
    result = PredictionResult(
        risk_category=pred.risk_category,
        risk_confidence=pred.risk_confidence,
        risk_probabilities=pred.risk_probabilities or {},
        investment_preference=pred.investment_preference,
        investment_confidence=pred.investment_confidence,
        financial_decision_score=pred.financial_decision_score,
        behavioral_composite_score=pred.behavioral_composite_score,
        financial_discipline_score=pred.financial_discipline_score,
        shap_values=pred.shap_values or {},
        feature_importance=pred.feature_importance or {},
        recommendations=pred.recommendations or [],
        behavioral_biases=pred.behavioral_biases or [],
    )
    return AssessmentResponse(assessment_id=assessment.id, data=result)


@router.get("/assessments", response_model=AssessmentsListResponse)
def list_assessments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = assessment_service.count_assessments(db)
    assessments = assessment_service.get_assessments(db, limit=limit, offset=offset)

    items = []
    for a in assessments:
        pred_result = None
        if a.prediction:
            p = a.prediction
            pred_result = PredictionResult(
                risk_category=p.risk_category,
                risk_confidence=p.risk_confidence,
                risk_probabilities=p.risk_probabilities or {},
                investment_preference=p.investment_preference,
                investment_confidence=p.investment_confidence,
                financial_decision_score=p.financial_decision_score,
                behavioral_composite_score=p.behavioral_composite_score,
                financial_discipline_score=p.financial_discipline_score,
                shap_values=p.shap_values or {},
                feature_importance=p.feature_importance or {},
                recommendations=p.recommendations or [],
                behavioral_biases=p.behavioral_biases or [],
            )
        items.append(
            AssessmentRecord(
                id=a.id,
                created_at=a.created_at,
                status=a.status,
                age=a.age,
                gender=a.gender,
                income_level=a.income_level,
                prediction=pred_result,
            )
        )

    return AssessmentsListResponse(total=total, items=items)
