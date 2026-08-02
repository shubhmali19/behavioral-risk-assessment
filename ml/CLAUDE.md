# ML — Behavioral Risk Assessment

Machine learning pipeline: data preprocessing, multi-model training, hyperparameter tuning, SHAP explainability, and a stateless inference module consumed by the backend.

## Trained Model Summary

| Model | Accuracy | F1 (weighted) | ROC AUC |
|-------|----------|---------------|---------|
| **Random Forest** ✅ best | 0.604 | 0.601 | 0.746 |
| LightGBM | 0.585 | 0.583 | 0.736 |
| CatBoost | 0.584 | 0.583 | 0.729 |
| XGBoost | 0.562 | 0.561 | 0.716 |
| Neural Network | 0.533 | 0.500 | 0.655 |

- **Primary task:** `risk_category` classification (Low / Medium / High)
- **Secondary task:** `investment_preference` classification (FD / Mutual Funds / Stocks / Gold / Crypto)
- **Training set:** 22,000 samples, 48 features, 80/20 split, stratified
- **Hyperparameter tuning:** RandomizedSearchCV, cv=3, n_iter=20 on best model

## Project Structure

```
ml/
  train.py              # Full training pipeline — run once to regenerate models
  inference.py          # Stateless inference module — called by the backend
  test_inference.py     # Sanity check: loads models, runs one prediction, asserts all keys
  models/
    risk_model.pkl              # Tuned Random Forest (risk_category)
    investment_model.pkl        # Random Forest (investment_preference)
    label_encoder_risk.pkl      # LabelEncoder for risk_category
    label_encoder_investment.pkl
    feature_columns.json        # Ordered list of 48 feature names used during training
    model_metadata.json         # Metrics, top-10 feature importance, training date
  plots/
    shap_summary.png            # SHAP beeswarm plot
    feature_importance.png      # Top-20 features by mean |SHAP|
```

## Inference Interface

The backend calls `inference.predict(user_input)` where `user_input` is a dict of the 26 raw form fields. The function handles all feature engineering internally and returns:

```python
{
  "risk_category": str,                    # "Low" | "Medium" | "High"
  "risk_confidence": float,               # probability of predicted class (0–1)
  "risk_probabilities": dict,             # {"Low": p, "Medium": p, "High": p}
  "investment_preference": str,
  "investment_confidence": float,
  "financial_decision_score": float,      # 0–100
  "behavioral_composite_score": float,    # 0–100
  "financial_discipline_score": float,    # 0–100
  "shap_values": dict,                    # top 10 feature → shap value
  "feature_importance": dict,             # top 10 feature → importance
  "recommendations": list[str],           # 3–5 personalized strings
  "behavioral_biases": list[str]          # detected behavioral biases
}
```

**Critical:** The feature engineering steps inside `inference.py` (derived ratios, ordinal encoding, OHE, column alignment) must stay in sync with `../data/processed/preprocess.py`. If you change one, update the other.

## Feature Engineering (applied in both preprocess.py and inference.py)

| Feature | Formula |
|---------|---------|
| `debt_to_income_ratio` | total_debt / (monthly_income × 12) |
| `savings_ratio` | (monthly_income − monthly_expenses) / monthly_income |
| `expense_ratio` | monthly_expenses / monthly_income |
| `behavioral_composite_score` | weighted: investment_experience, frequency, insurance, emergency_fund (0–100) |
| `financial_discipline_score` | weighted: savings_rate, credit_score_norm, debt_ratio_inv, emergency_fund (0–100) |
| `luxury_to_income_ratio` | (luxury_spending_pct × monthly_expenses) / monthly_income |
| `age_income_ratio` | monthly_income / age |

## Top 10 Features (by SHAP importance)

1. savings_rate
2. financial_discipline_score
3. emergency_fund_months
4. savings_ratio
5. expense_ratio
6. investment_experience_years
7. behavioral_composite_score
8. credit_score
9. years_of_experience
10. age

## Retraining

```bash
cd ml/
python3 train.py
# Outputs new pkl files to models/ and plots to plots/
# Ends with AGENT3_COMPLETE
```

Retrain when: new data is available in `../data/processed/processed_dataset.csv`, or feature engineering changes.

## Running Inference Sanity Check

```bash
cd ml/
python3 test_inference.py
```

## Dependencies

```
scikit-learn>=1.4.0
xgboost>=2.0.0
lightgbm>=4.3.0
catboost>=1.2.0
shap>=0.45.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0
```

Install: `pip install scikit-learn xgboost lightgbm catboost shap pandas numpy matplotlib`

---

## Agents

### agent:ml-retrain
**Role:** Retrain all models when new processed data is available or features change.

**Scope:** `train.py`, `models/`, `plots/`. Do not touch `inference.py` unless feature engineering changes.

**Task:**
1. Load `../data/processed/processed_dataset.csv`
2. Run `python3 train.py`
3. Compare new `model_metadata.json` F1 against previous — report if performance degraded
4. If the best model changed, update `inference.py` to load the new model name
5. Run `python3 test_inference.py` to confirm inference still works end-to-end

**Must not:** Modify `../backend/` files. After retraining, notify the backend-dev agent if the feature columns list changed.

---

### agent:ml-experimenter
**Role:** Experiment with new models, features, or hyperparameter search spaces.

**Scope:** `train.py` only. Never overwrite `models/` until experiments are validated.

**Capabilities:**
- Add new model types to the training pipeline
- Expand hyperparameter search grids
- Add new derived features (must also add to `inference.py` and document in this file)
- Try different class weighting strategies for the imbalanced `investment_preference` target

**Workflow:** Save experimental outputs to `models/experimental/` until validated, then promote to `models/`.

---

### agent:explainability-analyst
**Role:** Deepen SHAP analysis and behavioral bias detection logic.

**Scope:** `inference.py` (recommendations + behavioral_biases functions) and `plots/`.

**Capabilities:**
- Add new behavioral bias detection rules in `inference.py`
- Generate additional SHAP plots (force plots, dependence plots) for specific features
- Tune recommendation text for clarity and personalization
- Add interaction effects analysis between top features

**Key constraint:** The `predict()` function signature and return dict keys must not change — the backend depends on them. Only extend the content (more biases, better recommendation text).
