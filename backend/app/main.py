import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import health, predict, assessment, analytics

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database...")
    init_db()
    logger.info("Database initialized.")
    # Pre-load ML models at startup
    try:
        from app.services.ml_service import ml_service
        if ml_service.is_loaded:
            logger.info("ML models loaded and ready.")
        else:
            logger.warning("ML models failed to load — /predict will return 503.")
    except Exception as e:
        logger.error(f"ML service startup error: {e}")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Behavioral Risk Assessment API",
    description="AI-powered financial risk assessment using behavioral economics",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(assessment.router, tags=["Assessment"])
app.include_router(analytics.router, tags=["Analytics"])
