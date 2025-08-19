from fastapi import FastAPI
from src.webapp import api

app = FastAPI(
    title="Ethical Crawler & Data Platform",
    description="API for managing scraping jobs and accessing data.",
    version="0.1.0",
)

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Performs a health check of the API."""
    return {"status": "ok"}

# Include the API router
app.include_router(api.router, prefix="/api/v1", tags=["Jobs"])