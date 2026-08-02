<div align="center">

# Behavioral Economics-Based AI Risk Assessment System

**An end-to-end platform that classifies investor risk profiles from behavioral and financial data, explains every prediction with SHAP, and evaluates itself against a mathematically derived accuracy ceiling rather than against 100%.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Results at a Glance](#results-at-a-glance)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [How the ML Pipeline Works](#how-the-ml-pipeline-works)
- [Model Comparison](#model-comparison)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Environment Variables](#environment-variables)
- [Known Limitations](#known-limitations)

---

## Overview

Retail financial risk profiling is traditionally done with static questionnaires scored against fixed rubrics — transparent, but built on hand-picked weights that can't capture interactions between a person's attributes. This project replaces the rubric with a trained classifier while keeping per-answer explainability, using **SHAP (Shapley values)** so every prediction can be traced back to the inputs that drove it.

A user completes a four-step behavioral and financial questionnaire (26 attributes: demographics, income, spending habits, investment history, insurance coverage) in the React frontend. The FastAPI backend validates the payload, runs it through a tuned Random Forest classifier, computes SHAP attributions, detects behavioral biases, generates personalized recommendations, and persists the result for later retrieval and analytics.

The dataset is **synthetic** (22,000 records, generated from a documented scoring function) since no public dataset joins these attributes to a behavioral risk label. That synthetic construction is deliberately exploited for evaluation: because the label is a known linear score plus Gaussian noise, the **Bayes-optimal accuracy** — the mathematical ceiling no classifier could exceed — can be derived exactly, and the model is graded against that ceiling instead of against a naive 100%.

## Results at a Glance

| Metric | Value | Interpretation |
|---|---|---|
| Test accuracy | **60.39%** | Against a 45% majority-class baseline |
| Weighted F1 | **0.6006** | Selection criterion across 5 candidate models |
| ROC AUC (one-vs-rest) | **0.7461** | Class-ranking quality |
| 5-fold CV F1 | 0.5996 ± 0.0032 | Confirms the held-out score isn't a lucky split |
| **Bayes-optimal accuracy (ceiling)** | 0.6104 | Derived exactly from the label's known noise model |
| **Model as % of ceiling** | **98.9%** | Nearly all recoverable signal was extracted |
| Model as % of headroom above baseline | 95.9% | (accuracy − 0.45) / (ceiling − 0.45) |

A Random Forest was selected by controlled comparison against XGBoost, LightGBM, CatBoost, and a neural network (see [Model Comparison](#model-comparison)), then tuned via randomized search and validated by 5-fold cross-validation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                             │
│                   React + TypeScript + Tailwind                 │
│                    (localhost:5173 / :3000)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                            │
│              (localhost:8000 / Docker :8000)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  /predict   │  │ /assessment  │  │  /analytics /health   │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────────────┘  │
│         │                │                                       │
│  ┌──────▼────────────────▼──────────────────────────────────┐   │
│  │              ML Service (inference.py)                    │   │
│  │   Random Forest Risk Model + Investment Preference Model  │   │
│  │   SHAP Explainability + Behavioral Bias Detection         │   │
│  └───────────────────────────────────────────────────────────┘   │
│         │                                                        │
│  ┌──────▼────────────────────────────────────────────────────┐   │
│  │     SQLAlchemy ORM → SQLite (dev) / PostgreSQL (prod)     │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Data Pipeline:
  dataset.csv (22,000 rows)
    → data/processed/processed_dataset.csv (feature engineering)
      → ml/train.py → ml/models/*.pkl (Random Forest models)
        → ml/inference.py (served by FastAPI)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, TailwindCSS, Vite |
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| ML | scikit-learn (Random Forest), SHAP, pandas, NumPy |
| Database | SQLAlchemy ORM, SQLite (dev), PostgreSQL (prod) |
| Migrations | Alembic |
| Containerization | Docker, Docker Compose, Nginx |
| Testing | pytest, requests |

## Features

- **26-attribute behavioral assessment** — demographics, income, spending, investment history, and insurance, collected through a four-step form with schemas shared between client and server
- **Three-band risk classification** — Low / Medium / High, via a tuned Random Forest
- **SHAP-based explainability** — per-prediction feature attributions computed with the exact tree-based Shapley algorithm
- **Behavioral bias detection** — rule-based flags (e.g. overspending, under-insurance, low emergency reserves) with personalized recommendations
- **Assessment history & analytics** — persisted results with an aggregate analytics dashboard
- **Dockerized full stack** — frontend, backend, and database orchestrated via Docker Compose

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (for the containerized option)
- pip / npm
- [Git LFS](https://git-lfs.com/) (required to pull the trained model `.pkl` files in `ml/models/`)

## Quick Start

### Option 1: Docker Compose (recommended for a production-like setup)

```bash
git clone https://github.com/shubhmali19/behavioral-risk-assessment.git
cd behavioral-risk-assessment
docker compose up --build
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Dev script (runs both services locally)

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start everything
bash scripts/start_dev.sh
```

### Option 3: Manual (individual services)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./risk_assessment.db uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check — model status, DB connectivity |
| GET | `/model/info` | ML model metadata, accuracy, feature importance |
| POST | `/predict` | Run risk prediction (no DB save) |
| POST | `/assessment` | Run prediction and persist result to DB |
| GET | `/assessment/{id}` | Retrieve a saved assessment by ID |
| GET | `/analytics` | Aggregate stats — totals, risk distribution |

<details>
<summary><strong>Example curl commands</strong></summary>

**Health check:**
```bash
curl http://localhost:8000/health
```

**Run a prediction:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Save an assessment:**
```bash
curl -X POST http://localhost:8000/assessment \
  -H "Content-Type: application/json" \
  -d '{ ...same payload as above... }'
```

**Get analytics:**
```bash
curl http://localhost:8000/analytics
```

</details>

## How the ML Pipeline Works

1. **Data Generation** — 22,000 synthetic profiles with 26 behavioral and financial features, generated from a documented scoring function with explicit conditional dependencies between attributes (not sampled independently).

2. **Preprocessing** (`data/processed/`) — ordinal encoding for ordered categories (education, income level, investment frequency), one-hot encoding for nominal categories (gender, occupation, location), and derived features:
   - `savings_ratio` = monthly_income / monthly_expenses
   - `expense_ratio` = monthly_expenses / monthly_income
   - `financial_discipline_score` — composite from savings rate, emergency fund, credit score
   - `behavioral_composite_score` — composite from spending patterns and investment behavior

   All fitted constants are persisted to `preprocessing_params.json` so preprocessing is byte-identical between training and inference.

3. **Training** (`ml/train.py`) — five classifiers (Random Forest, XGBoost, LightGBM, CatBoost, a neural network) are trained on an identical 80/20 stratified split and compared on weighted F1. The winner is tuned via randomized search (20 candidates, 3-fold CV) and validated with 5-fold cross-validation.

4. **Inference** (`ml/inference.py`) — applies the same feature engineering at prediction time, runs the model, computes SHAP values for explainability, detects behavioral biases, and generates personalized recommendations.

5. **Top predictive features** (by importance): `savings_rate` (4.6%), `financial_discipline_score` (4.1%), `emergency_fund_months` (2.8%), `savings_ratio` (2.2%), `expense_ratio` (2.2%)

## Model Comparison

Five classifiers, identical 80/20 stratified split (17,600 train / 4,400 test), library-default hyperparameters:

| Model | Accuracy | Precision (w) | Recall (w) | F1 (w) | ROC AUC (ovr, w) |
|---|---|---|---|---|---|
| **Random Forest** (tuned) | **0.6039** | 0.6177 | 0.6039 | **0.6006** | **0.7461** |
| LightGBM | 0.5845 | 0.5923 | 0.5845 | 0.5830 | 0.7359 |
| CatBoost | 0.5841 | 0.5906 | 0.5841 | 0.5827 | 0.7290 |
| XGBoost | 0.5620 | 0.5686 | 0.5620 | 0.5609 | 0.7164 |
| Neural Network | 0.5332 | 0.5447 | 0.5332 | 0.5000 | 0.6550 |

Bagging (Random Forest) beat boosting here because roughly half the label's variance is irreducible noise by construction — boosting's advantage is fitting residual structure across rounds, which becomes a liability when the residual is mostly noise. Full methodology and per-class breakdown are in [`docs/report/15_ml_model_selection.md`](docs/report/15_ml_model_selection.md) and [`docs/report/23_performance_metrics.md`](docs/report/23_performance_metrics.md).

## Project Structure

```
behavioral-risk-assessment/
├── data/
│   ├── raw/dataset.csv                  # 22,000-row synthetic dataset (gitignored — regenerate via data/raw/generate_dataset.py)
│   └── processed/processed_dataset.csv  # Cleaned + feature-engineered (gitignored — regenerate via data/processed/preprocess.py)
├── ml/
│   ├── train.py                         # Model training script
│   ├── inference.py                     # Inference module (used by backend)
│   └── models/                          # .pkl files tracked via Git LFS
│       ├── risk_model.pkl               # Random Forest risk classifier
│       ├── investment_model.pkl         # Investment preference classifier
│       ├── label_encoder_risk.pkl       # Label encoder for risk categories
│       ├── label_encoder_investment.pkl # Label encoder for investment
│       ├── feature_columns.json         # Ordered feature column list
│       └── model_metadata.json          # Accuracy, F1, feature importance
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app + lifespan hooks
│   │   ├── config.py                    # Settings (pydantic-settings)
│   │   ├── database.py                  # SQLAlchemy engine + session
│   │   ├── models/                      # SQLAlchemy ORM models
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── routers/                     # Route handlers
│   │   └── services/ml_service.py       # ML inference wrapper
│   ├── alembic/                         # DB migration scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                  # Reusable UI components
│   │   └── pages/                       # Page-level components
│   ├── Dockerfile                       # Multi-stage build (node → nginx)
│   ├── nginx.conf                       # Nginx config with API proxy
│   ├── package.json
│   └── vite.config.ts
├── docs/report/                         # Full project report (30 sections, IEEE paper, PDFs)
├── tests/
│   ├── test_api.py                      # API integration tests (pytest + requests)
│   └── test_inference.py                # ML inference unit tests
├── scripts/
│   └── start_dev.sh                     # Launch backend + frontend together
├── docker-compose.yml                   # Full stack: db + backend + frontend
└── README.md
```

## Running Tests

**Install test dependencies:**
```bash
pip install pytest requests
```

**ML unit tests (no server needed):**
```bash
python -m pytest tests/test_inference.py -v
```

**API integration tests (requires backend running):**
```bash
# Terminal 1 — start backend
cd backend
DATABASE_URL=sqlite:///./risk_assessment.db uvicorn app.main:app --port 8000

# Terminal 2 — run tests
python -m pytest tests/test_api.py -v
```

**Run all tests:**
```bash
python -m pytest tests/ -v
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./risk_assessment.db` | SQLAlchemy database connection string |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG/INFO/WARNING) |
| `VERSION` | `1.0.0` | API version string returned by `/health` |

For PostgreSQL (Docker Compose default):
```
DATABASE_URL=postgresql://postgres:<password>@db:5432/risk_assessment
```

## Known Limitations

- **Investment preference is a negative result.** The secondary classifier for investment preference scores at chance level (0.2586 accuracy vs. a 0.2869 majority baseline). Inspection of the data generator showed the label is drawn independently of every feature, making this target unlearnable by construction — not a tuning failure.
- **Dataset is synthetic.** All 22,000 records come from a documented scoring function rather than real financial behavior, so results don't carry an empirical claim about real users. This was a deliberate tradeoff: it enables computing an exact Bayes-optimal ceiling for evaluation, which real data would not allow.
- **No authentication.** All endpoints are unauthenticated and assessments are anonymous — appropriate for a demonstration system, not for production use with real financial disclosures.

Full methodology, model comparison, and a candid discussion of defects found and fixed during development are documented in [`docs/report/`](docs/report/).

---

<div align="center">

Built as part of a Summer Internship project.

</div>
