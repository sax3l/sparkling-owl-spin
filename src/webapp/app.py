from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from prometheus_client import make_asgi_app
from src.webapp.api import jobs, templates, auth, exports
from src.utils.logger import setup_logging
from src.utils.telemetry import setup_telemetry
from src.utils.rate_limiter import RateLimitMiddleware
from src.utils.idempotency import IdempotencyMiddleware
from src.utils.deprecation import DeprecationMiddleware
from src.utils.error_models import ErrorResponse # Import the new error model
from src.observability.instrumentation import get_context # To get request_id
import os
import logging

# Set up logging as the first step
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ethical Crawler & Data Platform",
    description="API for managing scraping jobs and accessing data.",
    version="0.1.0",
)

# Set up OpenTelemetry
setup_telemetry(app)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Add middleware for rate limiting, idempotency, and deprecation
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app.add_middleware(RateLimitMiddleware, redis_url=REDIS_URL)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(DeprecationMiddleware)

# Custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = get_context().get("request_id") # Get request_id from context
    error_response = ErrorResponse(
        code=exc.detail.replace(" ", "_").upper() if isinstance(exc.detail, str) else "HTTP_ERROR",
        message=exc.detail,
        request_id=request_id
    )
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}", extra={"status_code": exc.status_code, "request_id": request_id})
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )

# Custom exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = get_context().get("request_id")
    details = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if str(loc) != "body")
        details[field] = {"reason": error["msg"], "code": error["type"].upper()}
    
    error_response = ErrorResponse(
        code="VALIDATION_FAILED",
        message="Request validation failed.",
        details=details,
        request_id=request_id
    )
    logger.error(f"Validation Error: {exc.errors()}", extra={"request_id": request_id, "validation_errors": exc.errors()})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(exclude_none=True)
    )

# Generic exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = get_context().get("request_id")
    error_response = ErrorResponse(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
        request_id=request_id
    )
    logger.exception("Unhandled exception caught by generic handler.", extra={"request_id": request_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True)
    )

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Performs a health check of the API."""
    return {"status": "ok"}

# Include the API routers
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(exports.router, prefix="/api/v1", tags=["Exports"])