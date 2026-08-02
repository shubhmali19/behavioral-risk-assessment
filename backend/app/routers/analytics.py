from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import AnalyticsResponse
from app.services import assessment_service

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    data = assessment_service.get_analytics(db)
    return AnalyticsResponse(**data)
