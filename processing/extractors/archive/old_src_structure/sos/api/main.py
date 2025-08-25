from fastapi import FastAPI
from starlette.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from ..core.config import get_settings
from ..core.logging import setup_logging
from ..db.session import engine
from ..db.models import Base
from .routers import health, templates, jobs

setup_logging()
app = FastAPI(title="Sparkling Owl Spin API")

@app.on_event("startup")
async def on_startup():
    # engångs-init av tabeller (MVP). I prod: använd Alembic migrationer.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(health.router)
app.include_router(templates.router)
app.include_router(jobs.router)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
