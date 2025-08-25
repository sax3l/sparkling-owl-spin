from fastapi import APIRouter
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/livez")
def livez():
    return {"status": "live"}
