"""
preprocess.py — Agent 2: Data Analyst
Behavioral Economics Based AI Risk Assessment System
Cleans, engineers features, encodes, scales, and produces EDA plots.
"""

import os
import json
import pickle
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(BASE, "..", "raw", "dataset.csv")
PLOTS = os.path.join(BASE, "plots")
os.makedirs(PLOTS, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD & INSPECT
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("STEP 1 — LOAD & INSPECT")
print("=" * 60)

df = pd.read_csv(RAW)
print(f"Shape          : {df.shape}")
print(f"Duplicates     : {df.duplicated().sum()}")
print("\n— dtypes —")
print(df.dtypes)
print("\n— Missing values —")
mv = df.isnull().sum()
print(mv[mv > 0] if mv.sum() > 0 else "  None")

# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA CLEANING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 2 — DATA CLEANING")
print("=" * 60)

# Remove duplicates
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"Duplicates removed : {before - len(df)}")

# Impute missing values
numeric_cols   = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols       = df.select_dtypes(include=["object", "string"]).columns.tolist()

for c in numeric_cols:
    if df[c].isnull().any():
        df[c] = df[c].fillna(df[c].median())
        print(f"  Imputed (median) : {c}")

for c in cat_cols:
    if df[c].isnull().any():
        df[c] = df[c].fillna(df[c].mode()[0])
        print(f"  Imputed (mode)   : {c}")

# Clip outliers via IQR on key numeric columns
key_numeric = [
    "monthly_income", "monthly_expenses", "total_debt", "loan_amount",
    "credit_score", "travel_expenses_annual", "gaming_expenses_monthly",
    "investment_experience_years", "emergency_fund_months",
]
clip_bounds = {}
for c in key_numeric:
    if c in df.columns:
        Q1, Q3 = df[c].quantile(0.25), df[c].quantile(0.75)
        IQR = Q3 - Q1
        lo, hi = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        clipped = ((df[c] < lo) | (df[c] > hi)).sum()
        df[c] = df[c].clip(lo, hi)
        clip_bounds[c] = {"lo": float(lo), "hi": float(hi)}
        if clipped:
            print(f"  Clipped {clipped:4d} outliers in {c}")

print(f"Shape after cleaning : {df.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 3. ENCODING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 3 — ENCODING")
print("=" * 60)

# Ordinal mappings
ordinal_mappings = {
    "education": {"High School": 0, "Graduate": 1, "Post Graduate": 2, "PhD": 3},
    "income_level": {"Low": 0, "Middle": 1, "High": 2},
    "investment_frequency": {"Never": 0, "Rarely": 1, "Monthly": 2, "Weekly": 3},
    "insurance_coverage": {"Basic": 0, "Comprehensive": 1},
    "shopping_frequency": {"Rarely": 0, "Monthly": 1, "Weekly": 2, "Daily": 3},
}

for col, mapping in ordinal_mappings.items():
    if col in df.columns:
        df[f"{col}_encoded"] = df[col].map(mapping)
        # fallback for unseen values
        df[f"{col}_encoded"] = df[f"{col}_encoded"].fillna(
            df[f"{col}_encoded"].median()
        ).astype(int)
        print(f"  Label-encoded : {col} → {col}_encoded")

# One-hot encode nominal columns
nominal_cols = [
    "gender", "occupation", "marital_status",
    "location", "employment_type", "investment_preference",
]
df = pd.get_dummies(df, columns=nominal_cols, drop_first=False)
print(f"  One-hot encoded  : {nominal_cols}")
print(f"Shape after encoding : {df.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 4 — FEATURE ENGINEERING")
print("=" * 60)

# Avoid division-by-zero helpers
safe_income    = df["monthly_income"].replace(0, np.nan)
safe_age       = df["age"].replace(0, np.nan)
annual_income  = safe_income * 12

df["debt_to_income_ratio"] = df["total_debt"] / annual_income
df["savings_ratio"]        = (df["monthly_income"] - df["monthly_expenses"]) / safe_income
df["expense_ratio"]        = df["monthly_expenses"] / safe_income
df["luxury_to_income_ratio"] = (df["luxury_spending_pct"] / 100 * df["monthly_expenses"]) / safe_income
df["age_income_ratio"]     = safe_income / safe_age

# Normalize helpers for composite scores (0-1 range)
def minmax_norm(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-9)

inv_exp_norm   = minmax_norm(df["investment_experience_years"])
inv_freq_norm  = minmax_norm(df["investment_frequency_encoded"])
ins_cov_norm   = minmax_norm(df["insurance_coverage_encoded"])
emf_norm       = minmax_norm(df["emergency_fund_months"])
savings_norm   = minmax_norm(df["savings_rate"])
credit_norm    = minmax_norm(df["credit_score"])
dti_inv_norm   = minmax_norm(1 - minmax_norm(df["debt_to_income_ratio"].fillna(0)))

# behavioral_composite_score (weights: inv_exp 0.35, inv_freq 0.25, ins_cov 0.20, emf 0.20)
df["behavioral_composite_score"] = (
    0.35 * inv_exp_norm +
    0.25 * inv_freq_norm +
    0.20 * ins_cov_norm +
    0.20 * emf_norm
) * 100

# financial_discipline_score (weights: savings 0.40, credit 0.35, dti_inv 0.25)
df["financial_discipline_score"] = (
    0.40 * savings_norm +
    0.35 * credit_norm +
    0.25 * dti_inv_norm
) * 100

# Fill any NaN from division-by-zero
for col in ["debt_to_income_ratio", "savings_ratio", "expense_ratio",
            "luxury_to_income_ratio", "age_income_ratio",
            "behavioral_composite_score", "financial_discipline_score"]:
    df[col] = df[col].fillna(df[col].median())

print("  Created: debt_to_income_ratio")
print("  Created: savings_ratio")
print("  Created: expense_ratio")
print("  Created: behavioral_composite_score  (scale 0-100)")
print("  Created: financial_discipline_score  (scale 0-100)")
print("  Created: luxury_to_income_ratio")
print("  Created: age_income_ratio")
print(f"Shape after feature engineering : {df.shape}")

# ──────────────────────────────────────────────────────────────────────────────
# Persist the constants fitted here so inference.py reproduces these features
# exactly. The composite scores depend on column-wide min/max, which a single
# request cannot recompute. Written to ml/models/preprocessing_params.json.
# ──────────────────────────────────────────────────────────────────────────────
def _mm(series):
    return {"min": float(series.min()), "max": float(series.max())}

preprocessing_params = {
    "ordinal_mappings": ordinal_mappings,
    "savings_rate_scale": "fraction",  # raw dataset stores 0.0-0.6, not 0-100
    # IQR bounds fitted on the training data. Inference clips incoming values to
    # these so engineered ratios are computed on the same domain as training.
    "clip_bounds": clip_bounds,
    "minmax": {
        "investment_experience_years": _mm(df["investment_experience_years"]),
        "investment_frequency_encoded": _mm(df["investment_frequency_encoded"]),
        "insurance_coverage_encoded": _mm(df["insurance_coverage_encoded"]),
        "emergency_fund_months": _mm(df["emergency_fund_months"]),
        "savings_rate": _mm(df["savings_rate"]),
        "credit_score": _mm(df["credit_score"]),
        "debt_to_income_ratio": _mm(df["debt_to_income_ratio"].fillna(0)),
    },
    "composite_weights": {
        "behavioral_composite_score": {
            "investment_experience_years": 0.35,
            "investment_frequency_encoded": 0.25,
            "insurance_coverage_encoded": 0.20,
            "emergency_fund_months": 0.20,
        },
        "financial_discipline_score": {
            "savings_rate": 0.40,
            "credit_score": 0.35,
            "debt_to_income_ratio_inverted": 0.25,
        },
    },
    "medians": {
        c: float(df[c].median())
        for c in ["debt_to_income_ratio", "savings_ratio", "expense_ratio",
                  "luxury_to_income_ratio", "age_income_ratio",
                  "behavioral_composite_score", "financial_discipline_score"]
    },
    # Fallback for categories never seen in training (e.g. insurance_coverage="None").
    # preprocess.py maps unseen values to NaN then fills with the column median.
    "ordinal_medians": {
        f"{c}_encoded": float(df[f"{c}_encoded"].median())
        for c in ordinal_mappings if f"{c}_encoded" in df.columns
    },
}

_params_path = Path(__file__).resolve().parents[2] / "ml" / "models" / "preprocessing_params.json"
_params_path.parent.mkdir(parents=True, exist_ok=True)
with open(_params_path, "w") as f:
    json.dump(preprocessing_params, f, indent=2)
print(f"  Saved preprocessing params → {_params_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. SCALING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 5 — SCALING")
print("=" * 60)

# Identify final numeric feature columns (exclude target & ID-like cols)
target_cols = ["risk_category"]
exclude_cols = target_cols + [c for c in df.columns if df[c].dtype == object or str(df[c].dtype) == "string"]

# Collect all boolean/dummy columns (from one-hot)
bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()
# Convert booleans to int before scaling
for bc in bool_cols:
    df[bc] = df[bc].astype(int)

scale_cols = [
    c for c in df.columns
    if c not in exclude_cols
    and c not in target_cols
    and df[c].dtype in [np.float64, np.int64, np.float32, np.int32, float, int]
]

print(f"  Columns to scale : {len(scale_cols)}")

# Keep unscaled version for output (ML agent does its own scaling)
df_unscaled = df.copy()

# Fit and save scaler
scaler = StandardScaler()
df[scale_cols] = scaler.fit_transform(df[scale_cols])

scaler_path = os.path.join(BASE, "scaler.pkl")
with open(scaler_path, "wb") as f:
    pickle.dump(scaler, f)
print(f"  Scaler saved → {scaler_path}")

# ══════════════════════════════════════════════════════════════════════════════
# 6. EDA PLOTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 6 — EDA PLOTS")
print("=" * 60)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight"})

# Use unscaled df for readable plots
dfu = df_unscaled

# 6a. Correlation matrix
print("  Plotting correlation_matrix …")
num_for_corr = [
    "age", "monthly_income", "monthly_expenses", "savings_rate",
    "emergency_fund_months", "total_debt", "credit_score",
    "investment_experience_years", "debt_to_income_ratio",
    "savings_ratio", "expense_ratio", "behavioral_composite_score",
    "financial_discipline_score", "luxury_to_income_ratio",
    "age_income_ratio", "financial_decision_score",
]
num_for_corr = [c for c in num_for_corr if c in dfu.columns]
fig, ax = plt.subplots(figsize=(14, 11))
corr = dfu[num_for_corr].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
    linewidths=0.5, ax=ax, annot_kws={"size": 7},
    vmin=-1, vmax=1
)
ax.set_title("Correlation Matrix — Key Numeric Features", fontsize=14, pad=12)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "correlation_matrix.png"))
plt.close()
print("    Saved correlation_matrix.png")

# 6b. Risk category distribution
print("  Plotting risk_category_distribution …")
order = ["Low", "Medium", "High"]
fig, ax = plt.subplots(figsize=(7, 5))
sns.countplot(data=dfu, x="risk_category", order=order,
              palette={"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}, ax=ax)
for p in ax.patches:
    ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center", va="bottom", fontsize=10)
ax.set_title("Risk Category Distribution", fontsize=13)
ax.set_xlabel("Risk Category")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "risk_category_distribution.png"))
plt.close()
print("    Saved risk_category_distribution.png")

# 6c. Investment preference distribution
print("  Plotting investment_preference_distribution …")
# Reconstruct from one-hot columns
inv_pref_cols = [c for c in dfu.columns if c.startswith("investment_preference_")]
if inv_pref_cols:
    inv_pref_series = dfu[inv_pref_cols].idxmax(axis=1).str.replace("investment_preference_", "")
else:
    inv_pref_series = dfu.get("investment_preference", pd.Series(dtype=str))

fig, ax = plt.subplots(figsize=(8, 5))
vc = inv_pref_series.value_counts()
sns.barplot(x=vc.index, y=vc.values, palette="Blues_d", ax=ax)
for i, v in enumerate(vc.values):
    ax.text(i, v + 50, f"{v:,}", ha="center", va="bottom", fontsize=10)
ax.set_title("Investment Preference Distribution", fontsize=13)
ax.set_xlabel("Investment Preference")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "investment_preference_distribution.png"))
plt.close()
print("    Saved investment_preference_distribution.png")

# 6d. Feature distributions (4×4 grid)
print("  Plotting feature_distributions …")
dist_features = [
    "age", "monthly_income", "monthly_expenses", "savings_rate",
    "credit_score", "total_debt", "emergency_fund_months", "investment_experience_years",
    "debt_to_income_ratio", "savings_ratio", "behavioral_composite_score",
    "financial_discipline_score", "luxury_to_income_ratio", "age_income_ratio",
    "financial_decision_score", "loan_amount",
]
dist_features = [c for c in dist_features if c in dfu.columns][:16]
fig, axes = plt.subplots(4, 4, figsize=(18, 14))
axes = axes.flatten()
for i, feat in enumerate(dist_features):
    sns.histplot(dfu[feat].dropna(), bins=40, ax=axes[i], color="#5C85D6", edgecolor="white", linewidth=0.3)
    axes[i].set_title(feat.replace("_", " ").title(), fontsize=9)
    axes[i].set_xlabel("")
    axes[i].set_ylabel("")
for j in range(len(dist_features), len(axes)):
    axes[j].set_visible(False)
fig.suptitle("Key Feature Distributions", fontsize=15, y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "feature_distributions.png"))
plt.close()
print("    Saved feature_distributions.png")

# 6e. Financial discipline score vs risk category
print("  Plotting financial_discipline_vs_risk …")
fig, ax = plt.subplots(figsize=(8, 5))
order_risk = ["Low", "Medium", "High"]
palette_risk = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
sns.boxplot(
    data=dfu, x="risk_category", y="financial_discipline_score",
    order=order_risk, palette=palette_risk, ax=ax,
    flierprops={"marker": "o", "alpha": 0.4, "markersize": 3}
)
ax.set_title("Financial Discipline Score by Risk Category", fontsize=13)
ax.set_xlabel("Risk Category")
ax.set_ylabel("Financial Discipline Score (0–100)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "financial_discipline_vs_risk.png"))
plt.close()
print("    Saved financial_discipline_vs_risk.png")

# 6f. Behavioral composite score vs investment preference
print("  Plotting behavioral_composite_vs_investment …")
# Reconstruct investment preference label
if inv_pref_cols:
    dfu = dfu.copy()
    dfu["_inv_pref_label"] = dfu[inv_pref_cols].idxmax(axis=1).str.replace("investment_preference_", "")
    x_col = "_inv_pref_label"
else:
    x_col = "investment_preference"

fig, ax = plt.subplots(figsize=(9, 5))
pref_order = ["FD", "Gold", "Mutual Funds", "Stocks", "Crypto"]
pref_order = [p for p in pref_order if p in dfu[x_col].unique()]
sns.boxplot(
    data=dfu, x=x_col, y="behavioral_composite_score",
    order=pref_order, palette="Set2", ax=ax,
    flierprops={"marker": "o", "alpha": 0.4, "markersize": 3}
)
ax.set_title("Behavioral Composite Score by Investment Preference", fontsize=13)
ax.set_xlabel("Investment Preference")
ax.set_ylabel("Behavioral Composite Score (0–100)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS, "behavioral_composite_vs_investment.png"))
plt.close()
print("    Saved behavioral_composite_vs_investment.png")

# ══════════════════════════════════════════════════════════════════════════════
# 7. SAVE OUTPUTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 7 — SAVING OUTPUTS")
print("=" * 60)

# 7a. processed_dataset.csv — UNSCALED
out_csv = os.path.join(BASE, "processed_dataset.csv")
df_unscaled.to_csv(out_csv, index=False)
print(f"  processed_dataset.csv  → {out_csv}  ({df_unscaled.shape})")

# 7b. feature_names.json
feature_cols = [c for c in df_unscaled.columns if c != "risk_category"]
feat_path = os.path.join(BASE, "feature_names.json")
with open(feat_path, "w") as f:
    json.dump(feature_cols, f, indent=2)
print(f"  feature_names.json     → {feat_path}  ({len(feature_cols)} features)")

# ── Helpers for report ────────────────────────────────────────────────────────
risk_dist = dfu["risk_category"].value_counts().to_dict()
top_corrs = []
corr_flat = corr.unstack().reset_index()
corr_flat.columns = ["feat1", "feat2", "corr"]
corr_flat = corr_flat[corr_flat["feat1"] != corr_flat["feat2"]]
corr_flat["abs_corr"] = corr_flat["corr"].abs()
corr_flat = corr_flat.sort_values("abs_corr", ascending=False).drop_duplicates(subset=["abs_corr"])
for _, row in corr_flat.head(10).iterrows():
    top_corrs.append(f"  - {row['feat1']} ↔ {row['feat2']}: {row['corr']:.3f}")

# 7c. eda_report.md
eda_path = os.path.join(BASE, "eda_report.md")
eda_md = f"""# EDA Report — Behavioral Risk Assessment Dataset

## 1. Dataset Overview
| Metric | Value |
|--------|-------|
| Rows (after cleaning) | {df_unscaled.shape[0]:,} |
| Columns | {df_unscaled.shape[1]} |
| Original columns | 30 |
| Engineered features | 7 |

## 2. Missing Values (pre-cleaning)
Missing values were detected in `insurance_coverage` and imputed with mode.
All numeric columns had no missing values. After imputation: **0 missing values**.

## 3. Class Distribution — `risk_category`
| Category | Count | % |
|----------|-------|---|
{chr(10).join([f"| {k} | {v:,} | {v/df_unscaled.shape[0]*100:.1f}% |" for k, v in sorted(risk_dist.items())])}

## 4. Key Correlations (top 10 by absolute value)
{chr(10).join(top_corrs)}

## 5. Engineered Features Summary
| Feature | Range |
|---------|-------|
| debt_to_income_ratio | {df_unscaled['debt_to_income_ratio'].min():.3f} – {df_unscaled['debt_to_income_ratio'].max():.3f} |
| savings_ratio | {df_unscaled['savings_ratio'].min():.3f} – {df_unscaled['savings_ratio'].max():.3f} |
| expense_ratio | {df_unscaled['expense_ratio'].min():.3f} – {df_unscaled['expense_ratio'].max():.3f} |
| behavioral_composite_score | {df_unscaled['behavioral_composite_score'].min():.1f} – {df_unscaled['behavioral_composite_score'].max():.1f} |
| financial_discipline_score | {df_unscaled['financial_discipline_score'].min():.1f} – {df_unscaled['financial_discipline_score'].max():.1f} |
| luxury_to_income_ratio | {df_unscaled['luxury_to_income_ratio'].min():.3f} – {df_unscaled['luxury_to_income_ratio'].max():.3f} |
| age_income_ratio | {df_unscaled['age_income_ratio'].min():.1f} – {df_unscaled['age_income_ratio'].max():.1f} |

## 6. Plots Generated
- `plots/correlation_matrix.png`
- `plots/risk_category_distribution.png`
- `plots/investment_preference_distribution.png`
- `plots/feature_distributions.png`
- `plots/financial_discipline_vs_risk.png`
- `plots/behavioral_composite_vs_investment.png`
"""
with open(eda_path, "w") as f:
    f.write(eda_md)
print(f"  eda_report.md          → {eda_path}")

# 7d. feature_engineering_report.md
fe_path = os.path.join(BASE, "feature_engineering_report.md")
fe_md = """# Feature Engineering Report

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
"""
with open(fe_path, "w") as f:
    f.write(fe_md)
print(f"  feature_engineering_report.md → {fe_path}")

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Final dataset shape       : {df_unscaled.shape}")
print(f"Numeric feature count     : {len(scale_cols)}")
print(f"Total feature count (all) : {len(feature_cols)}")
print(f"Target column             : risk_category")
print(f"Outputs saved to          : {BASE}")

print("\nAGENT2_COMPLETE")
