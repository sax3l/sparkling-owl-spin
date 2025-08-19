from fastapi import FastAPI
from prometheus_client import make_asgi_app
from src.webapp.api import jobs, templates
from src.utils.logger import setup_logging
from src.utils.telemetry import setup_telemetry

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

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Performs a health check of the API."""
    return {"status": "ok"}

# Include the API routers
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])