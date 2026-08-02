"""
train.py — ML training pipeline for Behavioral Economics Based AI Risk Assessment System.
Trains models for risk_category classification and investment_preference classification.
"""

import matplotlib
matplotlib.use('Agg')

import json
import pickle
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# Sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Boosting
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# SHAP
import shap

# Plotting
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "processed_dataset.csv"
ML_DIR = Path(__file__).parent
MODELS_DIR = ML_DIR / "models"
PLOTS_DIR = ML_DIR / "plots"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── 1. Load & Prepare Data ───────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading and preparing data")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"Dataset shape: {df.shape}")
print(f"risk_category distribution:\n{df['risk_category'].value_counts()}")

# Columns to drop from feature set
TARGET_COLS = ['risk_category', 'expected_savings_increase', 'financial_decision_score']
OHE_DROP_COLS = [c for c in df.columns if c.startswith('investment_preference_') or c.startswith('risk_category_')]
# Raw ordinal string columns already have encoded counterparts (*_encoded) — drop raw strings
RAW_ORDINAL_COLS = ['education', 'income_level', 'investment_frequency', 'insurance_coverage', 'shopping_frequency']

# Reconstruct investment_preference from OHE columns
ohe_inv_cols = [c for c in df.columns if c.startswith('investment_preference_')]
inv_map = {col: col.replace('investment_preference_', '') for col in ohe_inv_cols}
df['investment_preference'] = df[ohe_inv_cols].idxmax(axis=1).map(inv_map)
print(f"\ninvestment_preference distribution:\n{df['investment_preference'].value_counts()}")

# Build feature matrix
drop_from_features = TARGET_COLS + OHE_DROP_COLS + RAW_ORDINAL_COLS + ['investment_preference']
feature_cols = [c for c in df.columns if c not in drop_from_features]
print(f"\nNumber of features: {len(feature_cols)}")

X = df[feature_cols].copy()
y_risk = df['risk_category'].copy()
y_invest = df['investment_preference'].copy()

# Label encode risk_category: Low=0, Medium=1, High=2
le_risk = LabelEncoder()
le_risk.classes_ = np.array(['Low', 'Medium', 'High'])
y_risk_enc = y_risk.map({'Low': 0, 'Medium': 1, 'High': 2}).astype(int)

# Label encode investment_preference
le_invest = LabelEncoder()
y_invest_enc = le_invest.fit_transform(y_invest)

print(f"\nRisk label mapping: {dict(zip(le_risk.classes_, range(3)))}")
print(f"Investment label mapping: {dict(zip(le_invest.classes_, range(len(le_invest.classes_))))}")

# Train/test split — stratified, 80/20
X_train, X_test, yr_train, yr_test = train_test_split(
    X, y_risk_enc, test_size=0.2, random_state=42, stratify=y_risk_enc
)
_, _, yi_train, yi_test = train_test_split(
    X, y_invest_enc, test_size=0.2, random_state=42, stratify=y_invest_enc
)

print(f"\nTrain size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# ─── 2. Define Models ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Training models for risk_category")
print("=" * 60)

models = {
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=200, random_state=42, eval_metric='mlogloss',
                              use_label_encoder=False, verbosity=0),
    "LightGBM": LGBMClassifier(n_estimators=200, random_state=42, verbose=-1),
    "CatBoost": CatBoostClassifier(iterations=200, random_seed=42, verbose=0),
    "Neural Network": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=300,
                                    random_state=42, early_stopping=True),
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, yr_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    acc = accuracy_score(yr_test, y_pred)
    prec = precision_score(yr_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(yr_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(yr_test, y_pred, average='weighted', zero_division=0)
    auc = roc_auc_score(yr_test, y_proba, multi_class='ovr', average='weighted')

    results[name] = {
        "model": model,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc,
    }
    print(f"  Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")

# ─── 3. Select Best Model ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Selecting best model by F1 weighted score")
print("=" * 60)

best_model_name = max(results, key=lambda k: results[k]['f1_score'])
best_result = results[best_model_name]
best_model = best_result['model']
print(f"Best model: {best_model_name} (F1={best_result['f1_score']:.4f})")

# ─── 4. Hyperparameter Tuning on Best Model ───────────────────────────────────
print("\n" + "=" * 60)
print(f"STEP 4: Hyperparameter tuning for {best_model_name}")
print("=" * 60)

param_grids = {
    "Random Forest": {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2'],
    },
    "XGBoost": {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7, 9],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 1.0],
        'colsample_bytree': [0.7, 0.8, 1.0],
        'reg_alpha': [0, 0.1, 0.5],
        'reg_lambda': [1, 1.5, 2],
    },
    "LightGBM": {
        'n_estimators': [100, 200, 300],
        'max_depth': [-1, 5, 10, 15],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'num_leaves': [31, 50, 100],
        'subsample': [0.7, 0.8, 1.0],
        'colsample_bytree': [0.7, 0.8, 1.0],
    },
    "CatBoost": {
        'iterations': [100, 200, 300],
        'depth': [4, 6, 8, 10],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'l2_leaf_reg': [1, 3, 5, 7],
    },
    "Neural Network": {
        'hidden_layer_sizes': [(64, 32), (128, 64), (256, 128), (128, 64, 32)],
        'alpha': [0.0001, 0.001, 0.01],
        'learning_rate_init': [0.001, 0.01],
        'activation': ['relu', 'tanh'],
        'max_iter': [300, 500],
    },
}

if best_model_name in param_grids:
    # Re-instantiate fresh model for tuning
    fresh_models = {
        "Random Forest": RandomForestClassifier(random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(random_state=42, eval_metric='mlogloss',
                                  use_label_encoder=False, verbosity=0),
        "LightGBM": LGBMClassifier(random_state=42, verbose=-1),
        "CatBoost": CatBoostClassifier(random_seed=42, verbose=0),
        "Neural Network": MLPClassifier(random_state=42, early_stopping=True),
    }
    fresh_model = fresh_models[best_model_name]
    search = RandomizedSearchCV(
        fresh_model,
        param_grids[best_model_name],
        n_iter=20,
        cv=3,
        scoring='f1_weighted',
        n_jobs=-1,
        random_state=42,
        verbose=1,
    )
    search.fit(X_train, yr_train)
    tuned_model = search.best_estimator_
    y_pred_tuned = tuned_model.predict(X_test)
    y_proba_tuned = tuned_model.predict_proba(X_test)

    tuned_f1 = f1_score(yr_test, y_pred_tuned, average='weighted', zero_division=0)
    tuned_auc = roc_auc_score(yr_test, y_proba_tuned, multi_class='ovr', average='weighted')
    print(f"Tuned {best_model_name} F1: {tuned_f1:.4f} (was {best_result['f1_score']:.4f})")
    print(f"Best params: {search.best_params_}")

    if tuned_f1 >= best_result['f1_score']:
        best_model = tuned_model
        best_result['accuracy'] = accuracy_score(yr_test, y_pred_tuned)
        best_result['precision'] = precision_score(yr_test, y_pred_tuned, average='weighted', zero_division=0)
        best_result['recall'] = recall_score(yr_test, y_pred_tuned, average='weighted', zero_division=0)
        best_result['f1_score'] = tuned_f1
        best_result['roc_auc'] = tuned_auc
        print(f"Using tuned model (improved or equal F1).")
    else:
        print(f"Keeping original model (tuning did not improve F1).")

# ─── 5. Cross-Validation on Best Model ───────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5: 5-fold cross-validation on best model")
print("=" * 60)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(best_model, X, y_risk_enc, cv=skf, scoring='f1_weighted', n_jobs=-1)
cv_mean = cv_scores.mean()
cv_std = cv_scores.std()
print(f"CV F1 (5-fold): {cv_mean:.4f} ± {cv_std:.4f}")
print(f"Individual folds: {[f'{s:.4f}' for s in cv_scores]}")

# ─── 6. SHAP Explanations ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 6: Computing SHAP values")
print("=" * 60)

tree_models = ("Random Forest", "XGBoost", "LightGBM", "CatBoost")

if best_model_name in tree_models:
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(X_test)
else:
    # KernelExplainer on 100-sample background
    background = shap.sample(X_train, 100)
    explainer = shap.KernelExplainer(best_model.predict_proba, background)
    shap_values = explainer.shap_values(X_test.iloc[:200])
    if isinstance(shap_values, list):
        # KernelExplainer returns list of 2D arrays; stack to 3D for uniform handling
        shap_values = np.stack(shap_values, axis=2)  # (n_samples, n_features, n_classes)

# Handle multi-class: shap_values may be list of 2D arrays or a single 3D array (new SHAP API)
if isinstance(shap_values, list):
    # Old API: list of (n_samples, n_features) arrays, one per class
    shap_abs_mean = np.mean([np.abs(sv) for sv in shap_values], axis=0)  # (n_samples, n_features)
elif shap_values.ndim == 3:
    # New API: (n_samples, n_features, n_classes)
    shap_abs_mean = np.abs(shap_values).mean(axis=2)  # (n_samples, n_features)
else:
    shap_abs_mean = np.abs(shap_values)  # (n_samples, n_features)

# SHAP summary plot
print("Saving shap_summary.png ...")
X_plot = X_test if best_model_name in tree_models else X_test.iloc[:200]
# For summary_plot, use the mean-abs per feature (bar plot) to avoid 3D shape issues
fig, ax = plt.subplots(figsize=(10, 8))
mean_abs_per_feature = shap_abs_mean.mean(axis=0)  # (n_features,)
fi_summary = pd.DataFrame({'feature': feature_cols, 'mean_abs_shap': mean_abs_per_feature})
fi_summary = fi_summary.sort_values('mean_abs_shap', ascending=False).head(20)
ax.barh(fi_summary['feature'][::-1], fi_summary['mean_abs_shap'][::-1], color='tomato')
ax.set_xlabel('Mean |SHAP Value|', fontsize=12)
ax.set_title(f"SHAP Summary — {best_model_name}", fontsize=14, pad=10)
ax.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "shap_summary.png", dpi=150, bbox_inches='tight')
plt.close()
print("  Saved shap_summary.png")

# Feature importance plot (top 20 by mean |SHAP|)
print("Saving feature_importance.png ...")
mean_shap = shap_abs_mean.mean(axis=0)  # (n_features,)
fi_df = pd.DataFrame({'feature': feature_cols, 'importance': mean_shap.tolist()})
fi_df = fi_df.sort_values('importance', ascending=False).head(20)

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(fi_df['feature'][::-1], fi_df['importance'][::-1], color='steelblue')
ax.set_xlabel('Mean |SHAP Value|', fontsize=12)
ax.set_title(f'Top 20 Features by SHAP Importance — {best_model_name}', fontsize=13)
ax.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "feature_importance.png", dpi=150, bbox_inches='tight')
plt.close()
print("  Saved feature_importance.png")

# Top 10 feature importance dict
top10_importance = dict(zip(fi_df['feature'].head(10).tolist(), fi_df['importance'].head(10).round(6).tolist()))

# ─── 7. Secondary Model: investment_preference ────────────────────────────────
print("\n" + "=" * 60)
print("STEP 7: Training secondary model for investment_preference")
print("=" * 60)

invest_model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
invest_model.fit(X_train, yi_train)
yi_pred = invest_model.predict(X_test)
yi_proba = invest_model.predict_proba(X_test)

invest_acc = accuracy_score(yi_test, yi_pred)
invest_f1 = f1_score(yi_test, yi_pred, average='weighted', zero_division=0)
invest_auc = roc_auc_score(yi_test, yi_proba, multi_class='ovr', average='weighted')
print(f"Investment Model — Accuracy: {invest_acc:.4f} | F1: {invest_f1:.4f} | AUC: {invest_auc:.4f}")

# ─── 8. Save Artifacts ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 8: Saving model artifacts")
print("=" * 60)

# Risk model
with open(MODELS_DIR / "risk_model.pkl", 'wb') as f:
    pickle.dump(best_model, f)
print("  Saved risk_model.pkl")

# Investment model
with open(MODELS_DIR / "investment_model.pkl", 'wb') as f:
    pickle.dump(invest_model, f)
print("  Saved investment_model.pkl")

# Label encoders
with open(MODELS_DIR / "label_encoder_risk.pkl", 'wb') as f:
    pickle.dump(le_risk, f)
print("  Saved label_encoder_risk.pkl")

with open(MODELS_DIR / "label_encoder_investment.pkl", 'wb') as f:
    pickle.dump(le_invest, f)
print("  Saved label_encoder_investment.pkl")

# Feature columns
with open(MODELS_DIR / "feature_columns.json", 'w') as f:
    json.dump(feature_cols, f, indent=2)
print("  Saved feature_columns.json")

# Model metadata
metadata = {
    "best_model_name": best_model_name,
    "accuracy": round(best_result['accuracy'], 6),
    "precision": round(best_result['precision'], 6),
    "recall": round(best_result['recall'], 6),
    "f1_score": round(best_result['f1_score'], 6),
    "roc_auc": round(best_result['roc_auc'], 6),
    "cv_f1_mean": round(float(cv_mean), 6),
    "cv_f1_std": round(float(cv_std), 6),
    "training_date": datetime.now().isoformat(),
    "n_features": len(feature_cols),
    "n_samples": len(df),
    "class_names": ["Low", "Medium", "High"],
    "feature_importance_top10": top10_importance,
    "all_model_results": {
        name: {k: round(v, 6) for k, v in res.items() if k != 'model'}
        for name, res in results.items()
    },
    "investment_model": {
        "model_name": "Random Forest",
        "accuracy": round(invest_acc, 6),
        "f1_score": round(invest_f1, 6),
        "roc_auc": round(invest_auc, 6),
        "classes": le_invest.classes_.tolist(),
    }
}

with open(MODELS_DIR / "model_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)
print("  Saved model_metadata.json")

# ─── Summary ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TRAINING COMPLETE — SUMMARY")
print("=" * 60)
print(f"Best Model:  {best_model_name}")
print(f"Accuracy:    {best_result['accuracy']:.4f}")
print(f"Precision:   {best_result['precision']:.4f}")
print(f"Recall:      {best_result['recall']:.4f}")
print(f"F1 (wtd):    {best_result['f1_score']:.4f}")
print(f"ROC AUC:     {best_result['roc_auc']:.4f}")
print(f"CV F1:       {cv_mean:.4f} ± {cv_std:.4f}")
print(f"\nArtifacts saved to: {MODELS_DIR}")
print(f"Plots saved to:     {PLOTS_DIR}")

print("\nAGENT3_COMPLETE")
