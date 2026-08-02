"""Unit tests for ML inference module."""
import sys, pytest
sys.path.insert(0, "/Users/chiragmali/Documents/Summer Internship/risk_assessment/behavioral-risk-assessment/ml")

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

def test_predict_returns_all_keys():
    from inference import predict
    result = predict(SAMPLE_INPUT)
    required_keys = [
        "risk_category", "risk_confidence", "risk_probabilities",
        "investment_preference", "investment_confidence",
        "financial_decision_score", "behavioral_composite_score",
        "financial_discipline_score", "shap_values",
        "feature_importance", "recommendations", "behavioral_biases"
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"

def test_risk_category_valid():
    from inference import predict
    result = predict(SAMPLE_INPUT)
    assert result["risk_category"] in ["Low", "Medium", "High"]

def test_confidence_in_range():
    from inference import predict
    result = predict(SAMPLE_INPUT)
    assert 0 <= result["risk_confidence"] <= 1
    assert 0 <= result["investment_confidence"] <= 1

def test_scores_in_range():
    from inference import predict
    result = predict(SAMPLE_INPUT)
    assert 0 <= result["financial_decision_score"] <= 100
    assert 0 <= result["behavioral_composite_score"] <= 100
    assert 0 <= result["financial_discipline_score"] <= 100

def test_recommendations_nonempty():
    from inference import predict
    result = predict(SAMPLE_INPUT)
    assert len(result["recommendations"]) >= 1
