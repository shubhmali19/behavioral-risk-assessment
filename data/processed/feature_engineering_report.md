# Feature Engineering Report

## Overview
Seven derived features were created to capture financial health and behavioral patterns
that are not directly observable in raw columns.

---

## 1. `debt_to_income_ratio`
**Formula:** `total_debt / (monthly_income × 12)`
**Rationale:** Standard credit-risk metric. A higher ratio signals over-leverage and
is a strong predictor of financial distress and elevated risk appetite.

---

## 2. `savings_ratio`
**Formula:** `(monthly_income − monthly_expenses) / monthly_income`
**Rationale:** Measures the fraction of income saved each month. Higher values indicate
financial discipline and lower risk tolerance. Equivalent to (1 − expense_ratio).

---

## 3. `expense_ratio`
**Formula:** `monthly_expenses / monthly_income`
**Rationale:** Complement of savings ratio. Captures how much of income is consumed.
High expense ratio is a behavioral indicator of lower saving discipline.

---

## 4. `behavioral_composite_score` (0–100)
**Formula:**
```
0.35 × inv_exp_normalized
+ 0.25 × inv_freq_normalized
+ 0.20 × ins_cov_normalized
+ 0.20 × emergency_fund_normalized
```
**Rationale:** Aggregates four behavioral indicators of financial sophistication.
Investment experience and frequency are weighted highest because they directly reflect
active engagement with financial markets. Insurance coverage and emergency fund capture
risk-preparedness behavior.

---

## 5. `financial_discipline_score` (0–100)
**Formula:**
```
0.40 × savings_rate_normalized
+ 0.35 × credit_score_normalized
+ 0.25 × (1 − debt_to_income_ratio_normalized)
```
**Rationale:** Combines the three strongest objective signals of financial discipline.
Savings rate gets the highest weight as it is the most direct proxy. Credit score
reflects historical payment behavior. Inverted DTI penalizes over-leverage.

---

## 6. `luxury_to_income_ratio`
**Formula:** `(luxury_spending_pct / 100 × monthly_expenses) / monthly_income`
**Rationale:** Converts the percentage of expenses spent on luxury into a fraction of
income. High values may correlate with impulsive spending behavior and higher risk
tolerance in financial decisions.

---

## 7. `age_income_ratio`
**Formula:** `monthly_income / age`
**Rationale:** Proxy for income trajectory relative to career stage. A young person
with high income has a different risk profile than an older person with the same income.
Higher values suggest early financial success, often associated with higher risk capacity.

---

## Encoding Details
- **Ordinal label-encoded:** education, income_level, investment_frequency,
  insurance_coverage, shopping_frequency
- **One-hot encoded (nominal):** gender, occupation, marital_status, location,
  employment_type, investment_preference
- **Outlier clipping:** IQR method (1.5×IQR) applied to 9 key numeric columns
