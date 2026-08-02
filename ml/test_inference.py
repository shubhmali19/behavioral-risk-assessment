"""
test_inference.py — Sanity check for the ML inference module.
Run: python ml/test_inference.py
"""

import json
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.inference import predict, load_models, preprocess_input

# ─── Sample input (mirrors assessment form fields) ────────────────────────────
SAMPLE_INPUT = {
    # Demographics
    "age": 35,
    "gender": "Male",
    "education": "Graduate",
    "occupation": "Salaried",
    "marital_status": "Married",
    "dependents": 2,
    "location": "Urban",
    "employment_type": "Full-Time",
    "years_of_experience": 12,
    "income_level": "Medium",

    # Financials
    "monthly_income": 75000.0,
    "monthly_expenses": 45000.0,
    "savings_rate": 25.0,
    "emergency_fund_months": 4,
    "total_debt": 150000.0,
    "loan_amount": 50000.0,
    "credit_score": 740,

    # Investment profile
    "investment_experience_years": 5.0,
    "investment_frequency": "Monthly",
    "insurance_coverage": "Comprehensive",

    # Spending behavior
    "shopping_frequency": "Monthly",
    "online_spending_pct": 30.0,
    "luxury_spending_pct": 15.0,
    "subscription_count": 4,
    "gaming_expenses_monthly": 500.0,
    "travel_expenses_annual": 60000.0,
}

EXPECTED_KEYS = [
    "risk_category",
    "risk_confidence",
    "risk_probabilities",
    "investment_preference",
    "investment_confidence",
    "financial_decision_score",
    "behavioral_composite_score",
    "financial_discipline_score",
    "shap_values",
    "feature_importance",
    "recommendations",
    "behavioral_biases",
]


def test_load_models():
    print("=" * 60)
    print("TEST 1: load_models()")
    print("=" * 60)
    artifacts = load_models()
    assert "risk_model" in artifacts, "risk_model missing"
    assert "invest_model" in artifacts, "invest_model missing"
    assert "le_risk" in artifacts, "le_risk missing"
    assert "le_invest" in artifacts, "le_invest missing"
    assert "feature_columns" in artifacts, "feature_columns missing"
    assert "metadata" in artifacts, "metadata missing"
    print(f"  Models loaded successfully.")
    print(f"  Best risk model: {artifacts['metadata']['best_model_name']}")
    print(f"  Feature columns: {len(artifacts['feature_columns'])}")
    print(f"  Risk classes: {artifacts['le_risk'].classes_.tolist()}")
    print(f"  Investment classes: {artifacts['le_invest'].classes_.tolist()}")
    print("  PASS\n")


def test_preprocess_input():
    print("=" * 60)
    print("TEST 2: preprocess_input()")
    print("=" * 60)
    df = preprocess_input(SAMPLE_INPUT)
    artifacts = load_models()
    expected_cols = artifacts['feature_columns']
    assert list(df.columns) == expected_cols, f"Column mismatch: got {list(df.columns)[:5]}..."
    assert df.shape[0] == 1, f"Expected 1 row, got {df.shape[0]}"
    assert df.isnull().sum().sum() == 0, "NaN values found in preprocessed output"
    print(f"  DataFrame shape: {df.shape}")
    print(f"  Sample values: {df.iloc[0, :5].to_dict()}")
    print("  PASS\n")


def test_predict():
    print("=" * 60)
    print("TEST 3: predict()")
    print("=" * 60)
    result = predict(SAMPLE_INPUT)

    # Assert all expected keys present
    for key in EXPECTED_KEYS:
        assert key in result, f"Missing key in result: '{key}'"

    # Type checks
    assert isinstance(result['risk_category'], str), "risk_category must be str"
    assert result['risk_category'] in ('Low', 'Medium', 'High'), \
        f"Unexpected risk_category: {result['risk_category']}"
    assert 0.0 <= result['risk_confidence'] <= 1.0, "risk_confidence out of [0,1]"
    assert isinstance(result['risk_probabilities'], dict), "risk_probabilities must be dict"
    assert set(result['risk_probabilities'].keys()) == {'Low', 'Medium', 'High'}, \
        f"Unexpected keys in risk_probabilities: {result['risk_probabilities'].keys()}"
    assert abs(sum(result['risk_probabilities'].values()) - 1.0) < 0.01, \
        "risk_probabilities should sum to ~1.0"

    assert isinstance(result['investment_preference'], str), "investment_preference must be str"
    assert 0.0 <= result['investment_confidence'] <= 1.0, "investment_confidence out of [0,1]"

    assert isinstance(result['financial_decision_score'], float), "financial_decision_score must be float"
    assert 0.0 <= result['financial_decision_score'] <= 100.0, "financial_decision_score out of [0,100]"
    assert isinstance(result['behavioral_composite_score'], float), "behavioral_composite_score must be float"
    assert isinstance(result['financial_discipline_score'], float), "financial_discipline_score must be float"

    assert isinstance(result['shap_values'], dict), "shap_values must be dict"
    assert isinstance(result['feature_importance'], dict), "feature_importance must be dict"
    assert isinstance(result['recommendations'], list), "recommendations must be list"
    assert isinstance(result['behavioral_biases'], list), "behavioral_biases must be list"
    assert 1 <= len(result['recommendations']) <= 5, \
        f"Expected 1-5 recommendations, got {len(result['recommendations'])}"

    print("  All assertions passed.")
    print("\n" + "=" * 60)
    print("FULL PREDICTION OUTPUT")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print("  PASS\n")
    return result


def test_edge_cases():
    print("=" * 60)
    print("TEST 4: Edge cases")
    print("=" * 60)

    # Minimal input (most fields missing)
    minimal_input = {
        "age": 25,
        "monthly_income": 20000,
        "monthly_expenses": 18000,
        "savings_rate": 5,
        "credit_score": 550,
        "total_debt": 80000,
        "investment_frequency": "Weekly",
        "subscription_count": 8,
        "investment_experience_years": 1,
        "insurance_coverage": "None",
        "shopping_frequency": "Daily",
        "online_spending_pct": 60,
        "luxury_spending_pct": 25,
        "emergency_fund_months": 0,
        "loan_amount": 20000,
        "gaming_expenses_monthly": 2000,
        "travel_expenses_annual": 5000,
    }

    result_min = predict(minimal_input)
    for key in EXPECTED_KEYS:
        assert key in result_min, f"Missing key '{key}' in minimal input result"
    print(f"  Minimal input: risk={result_min['risk_category']}, invest={result_min['investment_preference']}")
    print(f"  Biases detected: {len(result_min['behavioral_biases'])}")
    print(f"  Recommendations: {len(result_min['recommendations'])}")

    # Zero-income edge case
    zero_income = dict(SAMPLE_INPUT)
    zero_income['monthly_income'] = 0
    try:
        result_zero = predict(zero_income)
        print(f"  Zero income: risk={result_zero['risk_category']} (no crash)")
    except Exception as e:
        print(f"  Zero income raised: {type(e).__name__}: {e}")

    print("  PASS\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ML INFERENCE SANITY CHECK")
    print("=" * 60 + "\n")

    try:
        test_load_models()
        test_preprocess_input()
        result = test_predict()
        test_edge_cases()

        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)

        # Print summary
        print(f"\nPrediction Summary for sample input:")
        print(f"  Risk Category:          {result['risk_category']} (confidence: {result['risk_confidence']:.1%})")
        print(f"  Investment Preference:  {result['investment_preference']} (confidence: {result['investment_confidence']:.1%})")
        print(f"  Financial Dec. Score:   {result['financial_decision_score']:.1f}/100")
        print(f"  Behavioral Composite:   {result['behavioral_composite_score']:.1f}/100")
        print(f"  Financial Discipline:   {result['financial_discipline_score']:.1f}/100")
        print(f"  Biases detected:        {len(result['behavioral_biases'])}")
        print(f"  Recommendations:        {len(result['recommendations'])}")

    except AssertionError as e:
        print(f"\nASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)
