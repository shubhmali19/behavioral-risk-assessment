import sys
import logging

logger = logging.getLogger(__name__)

_ml_predict = None
_load_error = None

try:
    import os
    # Support both Docker mount (/ml) and local dev (relative to repo root)
    ml_path = os.environ.get("ML_PATH", "/ml")
    if not os.path.exists(ml_path):
        # fallback for local dev: two levels up from backend/
        ml_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "ml")
    sys.path.insert(0, os.path.abspath(ml_path))
    from inference import predict as ml_predict_fn
    _ml_predict = ml_predict_fn
    logger.info("ML inference module loaded successfully.")
except Exception as e:
    _load_error = str(e)
    logger.error(f"Failed to load ML inference module: {e}")


class MLService:
    @property
    def is_loaded(self) -> bool:
        return _ml_predict is not None

    def predict(self, input_dict: dict) -> dict:
        if _ml_predict is None:
            raise RuntimeError(
                f"ML model is not available. Load error: {_load_error}"
            )
        return _ml_predict(input_dict)


# Singleton
ml_service = MLService()
