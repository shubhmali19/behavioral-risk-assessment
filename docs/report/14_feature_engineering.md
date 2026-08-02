# 14. Feature Engineering

## 14.1 Objective

Seven features are derived from the thirty raw columns. Their purpose is to express quantities that the model would otherwise have to reconstruct from combinations of inputs — a tree ensemble can approximate a ratio through repeated axis-aligned splits, but it does so inefficiently and with a boundary at every split, whereas supplying the ratio directly lets a single split capture the relationship.

After encoding and derivation, the table carries 61 columns, of which 48 are presented to the model as features. The remaining thirteen are the target column `risk_category`, the two unused targets `expected_savings_increase` and `financial_decision_score`, the five original categorical columns superseded by their encoded forms, and the five one-hot dummies of `investment_preference`, excluded because that column is itself a target. Section 14.5 gives the full accounting.

## 14.2 The Derived Features

| Feature | Definition |
|---|---|
| `debt_to_income_ratio` | `total_debt / (monthly_income × 12)` |
| `savings_ratio` | `(monthly_income − monthly_expenses) / monthly_income` |
| `expense_ratio` | `monthly_expenses / monthly_income` |
| `luxury_to_income_ratio` | `(luxury_spending_pct / 100) × monthly_expenses / monthly_income` |
| `age_income_ratio` | `monthly_income / age` |
| `behavioral_composite_score` | weighted min–max composite, scale 0–100 |
| `financial_discipline_score` | weighted min–max composite, scale 0–100 |

Observed ranges across the processed dataset:

| Feature | Min | Mean | Max |
|---|---|---|---|
| debt_to_income_ratio | 0.000 | 0.052 | 1.247 |
| savings_ratio | −0.582 | 0.319 | 0.857 |
| expense_ratio | 0.143 | 0.681 | 1.582 |
| luxury_to_income_ratio | 0.000 | 0.064 | 0.482 |
| age_income_ratio | 104.5 | 1508.6 | 6764.8 |
| behavioral_composite_score | 0.0 | 30.7 | 97.0 |
| financial_discipline_score | 7.3 | 66.7 | 100.0 |

Note that `savings_ratio` runs negative and `expense_ratio` exceeds unity for records whose expenses surpass income. Those records are real in the sense that the generator produces them, and they are retained rather than discarded.

## 14.3 The Two Composite Indices

The five ratio features are pointwise functions of a single record. The two composite indices are not, and this distinction turned out to matter more than anything else in the pipeline.

Each index is a weighted sum of min–max normalised components:

```
behavioral_composite_score = 100 × ( 0.35·norm(investment_experience_years)
                                   + 0.25·norm(investment_frequency_encoded)
                                   + 0.20·norm(insurance_coverage_encoded)
                                   + 0.20·norm(emergency_fund_months) )

financial_discipline_score = 100 × ( 0.40·norm(savings_rate)
                                   + 0.35·norm(credit_score)
                                   + 0.25·(1 − norm(debt_to_income_ratio)) )
```

The weights were assigned by judgement rather than fitted. Investment experience dominates the behavioural index on the reasoning that sustained participation in markets is a stronger indicator of engagement than any single-point attribute; savings rate dominates the discipline index because it is the most direct expression of whether a person lives below their means.

The normalisation is where the difficulty lies. `norm(·)` rescales a column by its minimum and maximum **across the entire training set**. A single incoming prediction request contains one record and therefore has no column from which to compute those bounds. An earlier implementation resolved this by inventing substitute formulas inside the inference module — capping savings at thirty points, scaling credit score against a 300–850 range, and so on — which produced numbers on the same 0–100 scale that bore no relation to the values the model was trained on.

The system now persists the fitted bounds. `preprocess.py` writes the minimum and maximum of each normalised component, together with the ordinal maps, the IQR clip bounds and the imputation medians, to `ml/models/preprocessing_params.json`. The inference module loads that file and reproduces the training computation exactly. Verification of the equivalence is reported in Section 9.7 and the defect itself in Section 22.

An incoming value outside the fitted range is clamped to `[0, 1]` after normalisation rather than allowed to extrapolate, since the training columns had already been IQR-clipped before their bounds were taken.

## 14.4 Redundancy Among the Derived Features

Three of the model's five most important features encode the same underlying quantity, and the feature set should not have been left in this state.

`savings_ratio` and `expense_ratio` are exact complements. From their definitions, `savings_ratio = 1 − expense_ratio` identically, and this is confirmed empirically: their Pearson correlation over the 22,000 records is **−1.000000**, and `|savings_ratio + expense_ratio − 1|` never exceeds 4.4 × 10⁻¹⁶. One carries no information the other lacks.

`savings_rate`, the raw dataset column, is a third encoding of the same quantity. The generator computes the implied surplus and then adds Gaussian noise of standard deviation 0.05 before clipping, so `savings_rate` is a noisy observation of `savings_ratio`, with a correlation of 0.944 between them.

The consequence is visible in the global SHAP ranking:

| Rank | Feature | Mean abs. SHAP |
|---|---|---|
| 1 | savings_rate | 0.0462 |
| 2 | financial_discipline_score | 0.0407 |
| 3 | emergency_fund_months | 0.0280 |
| 4 | savings_ratio | 0.0217 |
| 5 | expense_ratio | 0.0217 |
| 6 | investment_experience_years | 0.0147 |
| 7 | behavioral_composite_score | 0.0134 |
| 8 | credit_score | 0.0130 |

Ranks four and five carry identical importance to four decimal places, which is what one expects when a tree ensemble is offered two perfectly anti-correlated columns: each split that could have used one is equally likely to use the other, and the attribution divides between them. The apparent importance of the savings signal is thereby split across three rows of the table rather than concentrated in one, and a reader taking the ranking at face value would underestimate how dominant that single quantity is.

A Random Forest is not harmed in its predictive accuracy by collinear inputs the way a linear model is, so this redundancy costs little in performance. It costs a great deal in interpretability, which is the stated purpose of computing SHAP values at all. Removing `expense_ratio` — or equivalently, removing `savings_ratio` — would leave the model's accuracy essentially unchanged while making the explanation honest. This was identified after the model was trained and the results generated; it is recorded here and in Section 26 rather than silently corrected, because correcting it would require regenerating every figure in Section 23.

`financial_discipline_score` compounds the issue, since it takes `savings_rate` as its highest-weighted component at 0.40. The second-ranked feature is thus partly a function of the first.

## 14.5 Leakage

Two columns were excluded from the feature set on leakage grounds. `financial_decision_score` is a weighted sum of savings rate, credit score, debt burden, investment experience and emergency-fund coverage — the same five quantities that determine `risk_score`, from which the target label is cut. Supplying it as a feature would hand the model a noisy copy of the label. `expected_savings_increase` is likewise a function of the generator's internal discipline variable.

The five one-hot columns of `investment_preference` are also dropped, since that column serves as the secondary target.

Verification confirms that `feature_columns.json` contains none of these seven columns. The 48 features decompose as:

| Origin | Count |
|---|---|
| Raw numeric columns passed through unchanged | 16 |
| Ordinal encodings | 5 |
| One-hot dummies (gender, occupation, marital status, location, employment type) | 20 |
| Derived features | 7 |
| **Total** | **48** |

The five original categorical columns are absent, superseded by their encoded forms. Of the 25 dummies produced by one-hot encoding six nominal columns, the 5 belonging to `investment_preference` are excluded, leaving 20.

## 14.6 What Was Not Engineered

No interaction terms were constructed, since a tree ensemble discovers interactions through successive splits and explicit products would be redundant. No temporal features exist, because the dataset has no time dimension: each record is a single snapshot with no history. No text or free-form fields are present, so no embedding or vectorisation step is required.

Feature scaling was fitted and persisted as `scaler.pkl` during preprocessing but is not applied to the models actually deployed. Tree ensembles are invariant to monotone transformations of individual features, so standardisation changes nothing for the Random Forest that was selected. It would have mattered for the neural network, which was evaluated during model selection and rejected.

---

> **Figure 14.1** — *Scatter of `savings_ratio` against `expense_ratio`,* showing the exact anti-diagonal. A single plot demonstrates the redundancy argued in Section 14.4 more convincingly than the correlation coefficient. Generate with a two-line matplotlib block over `processed_dataset.csv`. Place in Section 14.4.

> **Figure 14.2** — *Global SHAP summary (beeswarm).* Already generated at `ml/plots/shap_summary.png`. Place in Section 14.4 alongside the importance table.

> **Figure 14.3** — *Distribution of the two composite scores,* `behavioral_composite_score` and `financial_discipline_score`, as overlaid histograms. Note in the caption that the behavioural index is left-skewed with mean 30.7, reflecting that most synthetic records have limited investment experience. Existing boxplots at `data/processed/plots/financial_discipline_vs_risk.png` may serve instead. Place in Section 14.3.

> **Table 14.1** — *Feature provenance.* Forty-eight rows grouped by origin: raw numeric (11), ordinal encoded (5), one-hot (25), derived (7). Mark each as used or excluded, and give the exclusion reason for the six leakage columns. Place as an appendix, referenced from Section 14.5.
