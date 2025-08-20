from fastapi import FastAPI
from prometheus_client import make_asgi_app
from src.webapp.api import jobs, templates, auth # Import auth router
from src.utils.logger import setup_logging
from src.utils.telemetry import setup_telemetry
from src.utils.rate_limiter import RateLimitMiddleware # Import RateLimitMiddleware
from src.utils.idempotency import IdempotencyMiddleware # Import IdempotencyMiddleware
import os

# Set up logging as the first step
setup_logging()

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

# Add middleware for rate limiting and idempotency
# Ensure Redis is running and accessible at this URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app.add_middleware(RateLimitMiddleware, redis_url=REDIS_URL)
app.add_middleware(IdempotencyMiddleware)


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Performs a health check of the API."""
    return {"status": "ok"}

# Include the API routers
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"]) # Include auth router