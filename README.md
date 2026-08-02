# Behavioral Economics Based AI Risk Assessment System

An end-to-end AI-powered financial risk assessment platform that applies behavioral economics principles to classify investor risk profiles and deliver personalized recommendations.

---

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

---

## Tech Stack

| Layer        | Technology                                   |
|--------------|----------------------------------------------|
| Frontend     | React 18, TypeScript, TailwindCSS, Vite      |
| Backend      | FastAPI, Uvicorn, Pydantic v2                |
| ML           | scikit-learn (Random Forest), SHAP, pandas   |
| Database     | SQLAlchemy ORM, SQLite (dev), PostgreSQL (prod) |
| Migrations   | Alembic                                      |
| Containerize | Docker, Docker Compose, Nginx                |
| Testing      | pytest, requests                             |

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (for containerized option)
- pip / npm
- [Git LFS](https://git-lfs.com/) (required to pull the trained model `.pkl` files in `ml/models/`)

---

## Quick Start

### Option 1: Docker Compose (recommended for production-like setup)

```bash
git clone <repo-url>
cd behavioral-risk-assessment
docker compose up --build
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Dev Script (runs both services locally)

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

---

## API Endpoints

| Method | Endpoint           | Description                                      |
|--------|--------------------|--------------------------------------------------|
| GET    | `/health`          | Health check — model status, DB connectivity     |
| GET    | `/model/info`      | ML model metadata, accuracy, feature importance  |
| POST   | `/predict`         | Run risk prediction (no DB save)                 |
| POST   | `/assessment`      | Run prediction and persist result to DB          |
| GET    | `/assessment/{id}` | Retrieve a saved assessment by ID                |
| GET    | `/analytics`       | Aggregate stats — totals, risk distribution      |

### Example curl commands

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

---

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
├── tests/
│   ├── test_api.py                      # API integration tests (pytest + requests)
│   └── test_inference.py               # ML inference unit tests
├── scripts/
│   └── start_dev.sh                     # Launch backend + frontend together
├── docker-compose.yml                   # Full stack: db + backend + frontend
└── README.md
```

---

## How the ML Pipeline Works

1. **Data Generation** — 22,000 synthetic profiles with 26 behavioral and financial features covering demographics, spending habits, investment behavior, and insurance coverage.

2. **Preprocessing** (`data/processed/`) — ordinal encoding for ordered categories (education, income level, investment frequency), one-hot encoding for nominal categories (gender, occupation, location), and derived features:
   - `savings_ratio` = monthly_income / monthly_expenses
   - `expense_ratio` = monthly_expenses / monthly_income
   - `financial_discipline_score` — composite from savings rate, emergency fund, credit score
   - `behavioral_composite_score` — composite from spending patterns and investment behavior

3. **Training** (`ml/train.py`) — trains a Random Forest classifier for:
   - **Risk Category**: Low / Medium / High (accuracy ~60%, ROC-AUC 0.75)
   - **Investment Preference**: Conservative / Moderate / Aggressive

4. **Inference** (`ml/inference.py`) — applies the same feature engineering at prediction time, runs both models, computes SHAP values for explainability, detects behavioral biases, and generates personalized recommendations.

5. **Top predictive features** (by importance):
   - savings_rate (4.6%), financial_discipline_score (4.1%), emergency_fund_months (2.8%), savings_ratio (2.2%), expense_ratio (2.2%)

---

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

---

## Environment Variables

| Variable       | Default                                              | Description                              |
|----------------|------------------------------------------------------|------------------------------------------|
| `DATABASE_URL` | `sqlite:///./risk_assessment.db`                     | SQLAlchemy database connection string    |
| `LOG_LEVEL`    | `INFO`                                               | Logging verbosity (DEBUG/INFO/WARNING)   |
| `VERSION`      | `1.0.0`                                              | API version string returned by /health   |

For PostgreSQL (Docker Compose default):
```
DATABASE_URL=postgresql://postgres:password@db:5432/risk_assessment
```

---

## Screenshots

_Screenshots placeholder — add UI screenshots here after first run._

| View              | Screenshot |
|-------------------|------------|
| Assessment Form   | _(pending)_ |
| Risk Results Page | _(pending)_ |
| Analytics Dashboard | _(pending)_ |
