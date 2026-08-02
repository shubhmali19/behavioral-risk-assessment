"""Integration tests for the backend API."""
import pytest, requests

BASE_URL = "http://localhost:8000"

SAMPLE_INPUT = {
    "age": 30, "gender": "Male", "education": "Graduate",
    "occupation": "Salaried", "income_level": "Middle",
    "marital_status": "Single", "dependents": 0, "location": "Urban",
    "employment_type": "Full-Time", "years_of_experience": 5,
    "monthly_income": 50000, "monthly_expenses": 35000,
    "savings_rate": 30, "emergency_fund_months": 3,
    "total_debt": 100000, "loan_amount": 500000,
    "credit_score": 720, "investment_experience_years": 3,
    "investment_frequency": "Monthly", "insurance_coverage": "Basic",
    "shopping_frequency": "Monthly", "online_spending_pct": 30,
    "luxury_spending_pct": 10, "subscription_count": 3,
    "gaming_expenses_monthly": 500, "travel_expenses_annual": 20000
}

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_model_info():
    r = requests.get(f"{BASE_URL}/model/info")
    assert r.status_code == 200
    data = r.json()
    assert "best_model_name" in data or "accuracy" in data

def test_predict():
    r = requests.post(f"{BASE_URL}/predict", json=SAMPLE_INPUT)
    assert r.status_code == 200
    body = r.json()
    # Response may be wrapped in {"success": true, "data": {...}} or flat
    data = body.get("data", body)
    assert data["risk_category"] in ["Low", "Medium", "High"]
    assert 0 <= data["risk_confidence"] <= 1
    assert "investment_preference" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)

def test_assessment_create_and_retrieve():
    r = requests.post(f"{BASE_URL}/assessment", json=SAMPLE_INPUT)
    assert r.status_code == 200
    data = r.json()
    assert "assessment_id" in data or "id" in data
    aid = data.get("assessment_id") or data.get("id")

    r2 = requests.get(f"{BASE_URL}/assessment/{aid}")
    assert r2.status_code == 200

def test_analytics():
    r = requests.get(f"{BASE_URL}/analytics")
    assert r.status_code == 200
    data = r.json()
    assert "total_assessments" in data
    assert "risk_distribution" in data

def test_predict_validation():
    bad = {**SAMPLE_INPUT, "age": 10}  # age < 18, should fail
    r = requests.post(f"{BASE_URL}/predict", json=bad)
    assert r.status_code == 422
