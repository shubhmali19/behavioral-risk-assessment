from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AssessmentInput(BaseModel):
    # Demographics
    age: int = Field(ge=18, le=100)
    gender: Literal["Male", "Female", "Other"]
    education: Literal["High School", "Graduate", "Post Graduate", "PhD"]
    occupation: Literal["Salaried", "Self-Employed", "Business", "Freelancer", "Student", "Retired"]
    income_level: Literal["Low", "Middle", "High"]
    marital_status: Literal["Single", "Married", "Divorced", "Widowed"]
    dependents: int = Field(ge=0, le=10)
    location: Literal["Urban", "Semi-Urban", "Rural"]
    employment_type: Literal["Full-Time", "Part-Time", "Contract", "Unemployed"]
    years_of_experience: int = Field(ge=0, le=50)
    # Financial
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(gt=0)
    savings_rate: float = Field(ge=0, le=100)
    emergency_fund_months: float = Field(ge=0, le=36)
    total_debt: float = Field(ge=0)
    loan_amount: float = Field(ge=0)
    credit_score: int = Field(ge=300, le=900)
    investment_experience_years: float = Field(ge=0, le=50)
    investment_frequency: Literal["Never", "Rarely", "Monthly", "Weekly"]
    insurance_coverage: Literal["None", "Basic", "Comprehensive"]
    # Lifestyle
    shopping_frequency: Literal["Rarely", "Monthly", "Weekly", "Daily"]
    online_spending_pct: float = Field(ge=0, le=100)
    luxury_spending_pct: float = Field(ge=0, le=100)
    subscription_count: int = Field(ge=0, le=30)
    gaming_expenses_monthly: float = Field(ge=0)
    travel_expenses_annual: float = Field(ge=0)

    model_config = {"extra": "forbid"}


class PredictionResult(BaseModel):
    risk_category: str
    risk_confidence: float
    risk_probabilities: Dict[str, float]
    investment_preference: str
    investment_confidence: float
    financial_decision_score: float
    behavioral_composite_score: float
    financial_discipline_score: float
    shap_values: Dict[str, float]
    feature_importance: Dict[str, float]
    recommendations: List[str]
    behavioral_biases: List[str]


class PredictionResponse(BaseModel):
    success: bool = True
    data: PredictionResult


class AssessmentResponse(BaseModel):
    success: bool = True
    assessment_id: str
    data: PredictionResult


class AssessmentRecord(BaseModel):
    id: str
    created_at: datetime
    status: str
    age: Optional[int] = None
    gender: Optional[str] = None
    income_level: Optional[str] = None
    prediction: Optional[PredictionResult] = None

    model_config = {"from_attributes": True}


class AssessmentsListResponse(BaseModel):
    success: bool = True
    total: int
    items: List[AssessmentRecord]


class AnalyticsResponse(BaseModel):
    total_assessments: int
    risk_distribution: Dict[str, int]
    investment_distribution: Dict[str, int]
    avg_financial_decision_score: float
    avg_behavioral_composite_score: float
    avg_financial_discipline_score: float
    assessments_by_date: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database: str
    version: str
