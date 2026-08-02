# Backend — Behavioral Risk Assessment

FastAPI REST API that loads the trained ML model, runs inference, persists assessments to PostgreSQL, and serves the frontend at port 8000.

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | 0.110+ | Web framework |
| Uvicorn | 0.27+ | ASGI server |
| SQLAlchemy | 2.0 | ORM |
| Alembic | 1.13+ | DB migrations |
| Pydantic v2 | 2.0+ | Request/response validation |
| pydantic-settings | 2.0+ | Env-based config |
| psycopg2-binary | 2.9+ | PostgreSQL driver |
| aiosqlite | 0.20+ | SQLite driver (dev fallback) |

## Project Structure

```
app/
  main.py                    # FastAPI app, CORS, lifespan startup
  config.py                  # Settings loaded from env (DATABASE_URL, etc.)
  database.py                # SQLAlchemy engine, session factory, init_db()
  models/
    db_models.py             # ORM: User, Assessment, Prediction, AuditLog, BehavioralScore
  schemas/
    assessment.py            # Pydantic: AssessmentInput, PredictionResponse, AssessmentResponse
  routers/
    predict.py               # POST /predict  (no DB write)
    assessment.py            # POST /assessment, GET /assessment/{id}, GET /assessments
    analytics.py             # GET /analytics
    health.py                # GET /health, GET /model/info
  services/
    ml_service.py            # Singleton wrapper around ml/inference.predict()
    assessment_service.py    # DB CRUD operations
  middleware/
    logging_middleware.py    # Request duration logging + async AuditLog writes
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check — model loaded, DB connected |
| GET | `/model/info` | model_metadata.json content |
| POST | `/predict` | Run ML prediction, no DB write |
| POST | `/assessment` | Run prediction + save to DB, returns assessment_id |
| GET | `/assessment/{id}` | Retrieve stored assessment + prediction |
| GET | `/assessments` | List assessments (limit/offset query params) |
| GET | `/analytics` | Aggregate stats: risk distribution, avg scores, trends |

Swagger UI: `http://localhost:8000/docs`

## Database Schema

```
users            → id (UUID), session_id, created_at, ip_address
assessments      → id, user_id FK, all 26 raw input fields, created_at, status
predictions      → id, assessment_id FK (unique), risk_category, confidences,
                   scores, shap_values JSON, recommendations JSON, behavioral_biases JSON
audit_logs       → id, endpoint, method, request_body JSON, response_status, duration_ms
behavioral_scores→ id, assessment_id FK, score_type, score_value
```

Default dev database: **SQLite** (`risk_assessment.db` in backend/).
Production: **PostgreSQL** via `DATABASE_URL` env var.

## ML Integration

The ML model lives in `../ml/`. The backend never retrains — it only calls inference:

```python
# app/services/ml_service.py
from inference import predict as ml_predict_fn   # loaded from /ml or ML_PATH env
```

`ML_PATH` env var overrides the default `/ml` Docker mount. For local dev the service auto-detects the relative path `../../ml/`.

The `predict()` function in `ml/inference.py` accepts a raw dict of the 26 form fields and returns the full prediction result including SHAP values.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./risk_assessment.db` | DB connection string |
| `ML_PATH` | `/ml` | Path to the ml/ directory inside Docker |
| `SECRET_KEY` | `your-secret-key-here` | App secret |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

Copy `.env.example` to `.env` before running locally.

## Development

```bash
pip install -r requirements.txt
DATABASE_URL=sqlite:///./risk_assessment.db uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
docker build -t risk-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/risk_assessment \
  -v $(pwd)/../ml:/ml \
  risk-backend
```

The `../ml` volume mount is required — the backend loads models from `/ml/models/` at startup.

## API Contract

**Single source of truth:** [`../docs/api-contract.json`](../docs/api-contract.json)

Before making any API change:
1. Update `../docs/api-contract.json` first — agree on the shape
2. Update `app/schemas/assessment.py` to match
3. Notify the frontend agent to sync `src/types/index.ts`

All responses use the envelope `{ "success": true, "data": { ... } }` (or `{ "success": true, "assessment_id": "...", "data": { ... } }` for assessment endpoints). Never return bare payloads — the frontend depends on this wrapper.

## Key Conventions

- All input validation is done in Pydantic schemas (`app/schemas/assessment.py`). Never validate in the router.
- Routers call services; services call the DB or ml_service. Routers never touch SQLAlchemy directly.
- All DB operations go through `assessment_service.py`. Never write raw SQLAlchemy queries in routers.
- The `AuditLog` is written asynchronously by the logging middleware — do not duplicate it in routers.
- `POST /predict` is stateless (no DB write). Use it for the frontend's live preview. `POST /assessment` persists the result.

---

## Agents

### agent:backend-dev
**Role:** Backend feature development, new endpoints, and bug fixes.

**Scope:** All files under `app/`. Do not touch `ml/`, `frontend/`, or `data/`.

**Capabilities:**
- Add new API endpoints by creating a router in `app/routers/` and registering it in `app/main.py`
- Extend Pydantic schemas in `app/schemas/assessment.py`
- Add new ORM models to `app/models/db_models.py` (then create an Alembic migration)
- Extend `assessment_service.py` with new DB queries
- Update CORS origins in `app/main.py` when new frontend ports are added

**Must not:**
- Modify `ml/train.py` or retrain models
- Write business logic that belongs in `ml/inference.py`
- Access the DB from routers directly (always go through services)

**How to verify:** Start the server with SQLite and hit the endpoint with curl. Check `http://localhost:8000/docs` for schema correctness.

---

### agent:db-migration
**Role:** Create and apply Alembic database migrations.

**Scope:** `app/models/db_models.py` and `alembic/` directory.

**Trigger:** Run after any change to ORM models.

**Task:**
1. Generate a new migration: `alembic revision --autogenerate -m "<description>"`
2. Review the generated script in `alembic/versions/`
3. Apply: `alembic upgrade head`
4. Verify the table schema matches `db_models.py`

**Must not:** Run `alembic downgrade` or drop tables without explicit instruction.

---

### agent:api-tester
**Role:** Write and run API integration tests.

**Scope:** `../tests/test_api.py` and backend running on `http://localhost:8000`.

**Task:** For each endpoint in the API, write a pytest test covering:
- Happy path with valid input
- Validation failure (422) with invalid input
- 404 for non-existent resource IDs
- Analytics returns correct aggregate structure

Run tests with: `python -m pytest ../tests/test_api.py -v`
