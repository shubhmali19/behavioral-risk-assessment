import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import Assessment, Prediction, BehavioralScore
from app.schemas.assessment import AssessmentInput


def create_assessment(db: Session, input_data: AssessmentInput) -> Assessment:
    data = input_data.model_dump()
    assessment = Assessment(
        id=str(uuid.uuid4()),
        status="pending",
        **data
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def save_prediction(db: Session, assessment_id: str, pred: dict) -> Prediction:
    prediction = Prediction(
        id=str(uuid.uuid4()),
        assessment_id=assessment_id,
        risk_category=pred["risk_category"],
        risk_confidence=pred["risk_confidence"],
        risk_probabilities=pred["risk_probabilities"],
        investment_preference=pred["investment_preference"],
        investment_confidence=pred["investment_confidence"],
        financial_decision_score=pred["financial_decision_score"],
        behavioral_composite_score=pred["behavioral_composite_score"],
        financial_discipline_score=pred["financial_discipline_score"],
        shap_values=pred["shap_values"],
        feature_importance=pred["feature_importance"],
        recommendations=pred["recommendations"],
        behavioral_biases=pred["behavioral_biases"],
    )
    db.add(prediction)

    # Save behavioral scores
    score_map = {
        "behavioral_composite": pred["behavioral_composite_score"],
        "financial_discipline": pred["financial_discipline_score"],
        "decision": pred["financial_decision_score"],
    }
    for score_type, score_value in score_map.items():
        bs = BehavioralScore(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            score_type=score_type,
            score_value=score_value,
        )
        db.add(bs)

    db.commit()
    db.refresh(prediction)
    return prediction


def mark_assessment_complete(db: Session, assessment_id: str):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment:
        assessment.status = "completed"
        db.commit()


def mark_assessment_failed(db: Session, assessment_id: str):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if assessment:
        assessment.status = "failed"
        db.commit()


def get_assessment_by_id(db: Session, assessment_id: str) -> Optional[Assessment]:
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()


def get_assessments(db: Session, limit: int = 20, offset: int = 0) -> List[Assessment]:
    return (
        db.query(Assessment)
        .order_by(Assessment.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_assessments(db: Session) -> int:
    return db.query(func.count(Assessment.id)).scalar()


def get_analytics(db: Session) -> dict:
    total = db.query(func.count(Assessment.id)).scalar() or 0

    # Risk distribution
    risk_rows = (
        db.query(Prediction.risk_category, func.count(Prediction.id))
        .group_by(Prediction.risk_category)
        .all()
    )
    risk_distribution = {r[0]: r[1] for r in risk_rows if r[0]}

    # Investment distribution
    inv_rows = (
        db.query(Prediction.investment_preference, func.count(Prediction.id))
        .group_by(Prediction.investment_preference)
        .all()
    )
    investment_distribution = {r[0]: r[1] for r in inv_rows if r[0]}

    # Averages
    avgs = db.query(
        func.avg(Prediction.financial_decision_score),
        func.avg(Prediction.behavioral_composite_score),
        func.avg(Prediction.financial_discipline_score),
    ).first()

    avg_financial_decision_score = round(float(avgs[0] or 0), 2)
    avg_behavioral_composite_score = round(float(avgs[1] or 0), 2)
    avg_financial_discipline_score = round(float(avgs[2] or 0), 2)

    # Assessments by date — dialect-aware date truncation
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    if dialect == "sqlite":
        date_label = func.strftime("%Y-%m-%d", Assessment.created_at).label("date")
    else:
        # PostgreSQL
        date_label = func.to_char(Assessment.created_at, "YYYY-MM-DD").label("date")

    date_rows = (
        db.query(date_label, func.count(Assessment.id).label("count"))
        .group_by(date_label)
        .order_by(date_label)
        .all()
    )
    assessments_by_date = [{"date": r[0], "count": r[1]} for r in date_rows]

    return {
        "total_assessments": total,
        "risk_distribution": risk_distribution,
        "investment_distribution": investment_distribution,
        "avg_financial_decision_score": avg_financial_decision_score,
        "avg_behavioral_composite_score": avg_behavioral_composite_score,
        "avg_financial_discipline_score": avg_financial_discipline_score,
        "assessments_by_date": assessments_by_date,
    }
