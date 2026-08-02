# Behavioral Economics Based AI Risk Assessment System

End-to-end AI web application that predicts a user's financial decision-making and behavioral risk profile using Behavioral Economics, Machine Learning, and Explainable AI.

## Repository Layout

```
behavioral-risk-assessment/
  frontend/          ← React + TypeScript + TailwindCSS (see frontend/CLAUDE.md)
  backend/           ← FastAPI + SQLAlchemy + PostgreSQL (see backend/CLAUDE.md)
  ml/                ← Training pipeline + inference module (see ml/CLAUDE.md)
  data/
    raw/             ← dataset.csv (22,000 synthetic records, 30 columns)
    processed/       ← processed_dataset.csv (61 columns, 7 engineered features)
  docs/              ← Architecture and design documents
  database/          ← SQL schemas and migration scripts
  tests/
    test_api.py      ← Integration tests against live backend (6 tests)
    test_inference.py← ML unit tests (5 tests)
  scripts/
    start_dev.sh     ← Launch backend + frontend for local development
  docker-compose.yml ← Full stack: PostgreSQL + backend + frontend
  README.md
```

Each sub-project has its own CLAUDE.md with detailed context, conventions, and agents. **Open those directories independently** when working on a specific layer.

## Architecture

```
User Browser
     │
     ▼
[Frontend :3000]  React + TypeScript + TailwindCSS
     │  REST API calls
     ▼
[Backend :8000]   FastAPI + Pydantic + SQLAlchemy
     │                    │
     │              [PostgreSQL :5432]
     │              Users / Assessments / Predictions
     │              AuditLogs / BehavioralScores
     │
     ▼
[ML Module /ml]   inference.predict(user_input)
     │
     ├── risk_model.pkl         Random Forest → Low/Medium/High
     ├── investment_model.pkl   Random Forest → FD/MF/Stocks/Gold/Crypto
     └── SHAP values + recommendations
```

## Live URLs (Docker)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 / db: risk_assessment |

## Quick Start

### Option 1 — Docker Compose (recommended)
```bash
docker-compose up --build
```

### Option 2 — Local dev
```bash
bash scripts/start_dev.sh
# Backend: http://localhost:8000  Frontend: http://localhost:5173
```

### Option 3 — Manual
```bash
# Terminal 1 — Backend
cd backend
DATABASE_URL=sqlite:///./risk_assessment.db uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

## Running Tests

```bash
# ML unit tests (no server needed)
python3 -m pytest tests/test_inference.py -v

# API integration tests (backend must be running)
python3 -m pytest tests/test_api.py -v
```

## Data Pipeline

```
data/raw/generate_dataset.py        → dataset.csv (22,000 rows)
         ↓
data/processed/preprocess.py        → processed_dataset.csv (61 cols)
         ↓
ml/train.py                         → models/*.pkl + model_metadata.json
         ↓
ml/inference.py                     → predict(user_input) called by backend
```

To regenerate everything from scratch:
```bash
cd data/raw    && python3 generate_dataset.py
cd data/processed && python3 preprocess.py
cd ml          && python3 train.py
```

## ML Model Performance

Best model: **Random Forest** (selected by highest weighted F1 among 5 candidates)

| Metric | Score |
|--------|-------|
| Accuracy | 0.604 |
| F1 (weighted) | 0.601 |
| ROC AUC | 0.746 |
| CV F1 (5-fold) | 0.600 ± 0.003 |

Top predictive features: `savings_rate`, `financial_discipline_score`, `emergency_fund_months`, `savings_ratio`, `expense_ratio`.

## API Contract

**Single source of truth:** [`docs/api-contract.json`](docs/api-contract.json)

This file defines every endpoint's URL, request shape, response shape, and field names. **Before adding or changing any API endpoint:**
1. Update `docs/api-contract.json` first
2. Update `backend/app/schemas/assessment.py` to match
3. Update `frontend/src/types/index.ts` to match
4. Run `npm run build` in frontend — zero TypeScript errors required

The backend wraps all responses in `{ "success": true, "data": { ... } }`. The frontend unwraps this envelope in `src/api/assessments.ts` before returning to components — components always receive the inner payload.

### Key Inter-Service Contracts

#### Backend → ML
The backend calls `ml/inference.py:predict(dict)` with the 26 raw form fields. The ML module handles all feature engineering internally. **Never change the `predict()` return dict keys without updating both `backend/app/schemas/assessment.py` and `docs/api-contract.json`.**

#### Frontend → Backend
All API calls go through `frontend/src/api/assessments.ts`. The full type contract lives in `frontend/src/types/index.ts`. **When backend Pydantic schemas change, update `docs/api-contract.json` first, then the TypeScript types.**

#### ML → Data
`ml/inference.py` replicates the feature engineering from `data/processed/preprocess.py`. **These two files must stay in sync.** If you add a derived feature to `preprocess.py`, add the same computation to `inference.py`.

## Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | backend | `sqlite:///./risk_assessment.db` | DB connection |
| `ML_PATH` | backend | `/ml` | Path to ml/ directory |
| `SECRET_KEY` | backend | `your-secret-key-here` | App secret |
| `LOG_LEVEL` | backend | `INFO` | Log verbosity |

---

## Agents

### agent:team-lead
**Role:** Orchestrate cross-cutting changes that span multiple sub-projects.

**Scope:** The entire repository. Reads all CLAUDE.md files before acting. Coordinates changes across `frontend/`, `backend/`, and `ml/` when a single feature requires all three to change together.

**Use this agent for:**
- Adding a new input field to the assessment form end-to-end (form → schema → inference → frontend type → UI)
- Updating the prediction response shape (inference return → backend schema → frontend types → Results page)
- Debugging issues where the root cause is unclear (could be frontend, backend, or ML)
- Running the full test suite and fixing failures across layers
- Docker Compose troubleshooting

**Workflow for cross-cutting changes:**
1. Read `ml/CLAUDE.md`, `backend/CLAUDE.md`, `frontend/CLAUDE.md`
2. Identify all files that need changing across all three layers
3. Make changes in dependency order: ML → backend → frontend
4. Run `tests/test_inference.py` then `tests/test_api.py` then `npm run build`
5. Confirm Docker Compose still builds and all containers start healthy

---

### agent:devops
**Role:** Docker, CI/CD, and infrastructure.

**Scope:** `docker-compose.yml`, `frontend/Dockerfile`, `backend/Dockerfile`, `scripts/`.

**Capabilities:**
- Modify Docker Compose services (add volumes, env vars, health checks)
- Optimize Dockerfiles (layer caching, multi-stage builds)
- Write GitHub Actions workflows for CI (lint, test, build)
- Update `scripts/start_dev.sh` for new services

**Key facts:**
- The `./ml` directory is mounted into the backend container at `/ml` — the backend loads models from there at startup
- Frontend is served by nginx; SPA routing is handled by `try_files` in `frontend/nginx.conf`
- The `version` key in `docker-compose.yml` triggers a deprecation warning — safe to remove

---

### agent:data-engineer
**Role:** Regenerate or extend the synthetic dataset and preprocessing pipeline.

**Scope:** `data/raw/` and `data/processed/`. After changing data, notify the ml-retrain agent.

**Capabilities:**
- Modify `generate_dataset.py` to add new columns or adjust distributions
- Extend `preprocess.py` with new engineered features
- After adding a new feature column: update `ml/inference.py` with the same computation, then retrain

**Critical constraint:** Any new feature added to `processed_dataset.csv` must be mirrored in `ml/inference.py:preprocess_input()` so live predictions use the same features as training.

---

### agent:qa-engineer
**Role:** End-to-end quality assurance across the full stack.

**Scope:** `tests/`, plus reading `frontend/src/`, `backend/app/`, `ml/inference.py`.

**Task:** Ensure the full user journey works:
1. Start Docker Compose stack
2. POST a sample assessment to `/assessment` — verify 200 + all response fields present
3. GET `/assessment/{id}` — verify retrieval
4. GET `/analytics` — verify distributions populated
5. GET `/health` — verify `model_loaded: true`
6. Run `pytest tests/ -v` — all tests green
7. Run `npm run build` in frontend — zero TypeScript errors

Report any failures with the exact curl command or test name that failed.
