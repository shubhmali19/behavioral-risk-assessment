import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)

    assessments = relationship("Assessment", back_populates="user")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Demographics
    age = Column(Integer)
    gender = Column(String)
    education = Column(String)
    occupation = Column(String)
    income_level = Column(String)
    marital_status = Column(String)
    dependents = Column(Integer)
    location = Column(String)
    employment_type = Column(String)
    years_of_experience = Column(Integer)

    # Financial
    monthly_income = Column(Float)
    monthly_expenses = Column(Float)
    savings_rate = Column(Float)
    emergency_fund_months = Column(Float)
    total_debt = Column(Float)
    loan_amount = Column(Float)
    credit_score = Column(Integer)
    investment_experience_years = Column(Float)
    investment_frequency = Column(String)
    insurance_coverage = Column(String)

    # Lifestyle
    shopping_frequency = Column(String)
    online_spending_pct = Column(Float)
    luxury_spending_pct = Column(Float)
    subscription_count = Column(Integer)
    gaming_expenses_monthly = Column(Float)
    travel_expenses_annual = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # "pending" / "completed" / "failed"

    user = relationship("User", back_populates="assessments")
    prediction = relationship("Prediction", back_populates="assessment", uselist=False)
    behavioral_scores = relationship("BehavioralScore", back_populates="assessment")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), unique=True, nullable=False)

    risk_category = Column(String)
    risk_confidence = Column(Float)
    risk_probabilities = Column(JSON)
    investment_preference = Column(String)
    investment_confidence = Column(Float)
    financial_decision_score = Column(Float)
    behavioral_composite_score = Column(Float)
    financial_discipline_score = Column(Float)
    shap_values = Column(JSON)
    feature_importance = Column(JSON)
    recommendations = Column(JSON)
    behavioral_biases = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="prediction")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    endpoint = Column(String)
    method = Column(String)
    request_body = Column(JSON, nullable=True)
    response_status = Column(Integer)
    duration_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class BehavioralScore(Base):
    __tablename__ = "behavioral_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    score_type = Column(String)   # "behavioral_composite" / "financial_discipline" / "decision"
    score_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="behavioral_scores")
