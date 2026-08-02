# EDA Report — Behavioral Risk Assessment Dataset

## 1. Dataset Overview
| Metric | Value |
|--------|-------|
| Rows (after cleaning) | 22,000 |
| Columns | 61 |
| Original columns | 30 |
| Engineered features | 7 |

## 2. Missing Values (pre-cleaning)
Missing values were detected in `insurance_coverage` and imputed with mode.
All numeric columns had no missing values. After imputation: **0 missing values**.

## 3. Class Distribution — `risk_category`
| Category | Count | % |
|----------|-------|---|
| High | 4,400 | 20.0% |
| Low | 7,700 | 35.0% |
| Medium | 9,900 | 45.0% |

## 4. Key Correlations (top 10 by absolute value)
  - expense_ratio ↔ savings_ratio: -1.000
  - savings_rate ↔ expense_ratio: -0.944
  - savings_rate ↔ savings_ratio: 0.944
  - monthly_expenses ↔ monthly_income: 0.925
  - monthly_income ↔ age_income_ratio: 0.881
  - savings_rate ↔ financial_discipline_score: 0.836
  - age_income_ratio ↔ monthly_expenses: 0.806
  - expense_ratio ↔ financial_discipline_score: -0.788
  - financial_discipline_score ↔ financial_decision_score: 0.767
  - credit_score ↔ financial_discipline_score: 0.740

## 5. Engineered Features Summary
| Feature | Range |
|---------|-------|
| debt_to_income_ratio | 0.000 – 1.247 |
| savings_ratio | -0.582 – 0.857 |
| expense_ratio | 0.143 – 1.582 |
| behavioral_composite_score | 0.0 – 97.0 |
| financial_discipline_score | 7.3 – 100.0 |
| luxury_to_income_ratio | 0.000 – 0.482 |
| age_income_ratio | 104.5 – 6764.8 |

## 6. Plots Generated
- `plots/correlation_matrix.png`
- `plots/risk_category_distribution.png`
- `plots/investment_preference_distribution.png`
- `plots/feature_distributions.png`
- `plots/financial_discipline_vs_risk.png`
- `plots/behavioral_composite_vs_investment.png`
