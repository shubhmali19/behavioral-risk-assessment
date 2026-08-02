import time
import json
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        request_body = None

        try:
            if request.method in ("POST", "PUT", "PATCH"):
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = json.loads(body_bytes)
                    except Exception:
                        request_body = body_bytes.decode("utf-8", errors="replace")
        except Exception:
            pass

        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} "
            f"({duration_ms:.1f}ms)"
        )

        # Optionally persist to DB (non-blocking best-effort)
        try:
            from app.database import SessionLocal
            from app.models.db_models import AuditLog
            db = SessionLocal()
            try:
                log = AuditLog(
                    id=str(uuid.uuid4()),
                    endpoint=str(request.url.path),
                    method=request.method,
                    request_body=request_body if isinstance(request_body, dict) else None,
                    response_status=response.status_code,
                    duration_ms=round(duration_ms, 2),
                )
                db.add(log)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Audit log write failed: {e}")

        return response
