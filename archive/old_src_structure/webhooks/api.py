from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import APIKeyHeader
from typing import List, Optional
from .models import (
    WebhookEndpoint,
    WebhookEndpointCreate,
    WebhookDelivery,
    WebhookEventType
)
from .service import WebhookService
from ..database import get_db

router = APIRouter(prefix="/v1/webhooks")
api_key_header = APIKeyHeader(name="X-API-Key")

@router.post("/endpoints", response_model=WebhookEndpoint)
async def create_endpoint(
    endpoint: WebhookEndpointCreate,
    api_key: str = Depends(api_key_header),
    db=Depends(get_db)
):
    webhook_service = WebhookService(db)
    return await webhook_service.create_endpoint(endpoint)

@router.get("/endpoints", response_model=List[WebhookEndpoint])
async def list_endpoints(
    active: Optional[bool] = None,
    event_type: Optional[WebhookEventType] = None,
    api_key: str = Depends(api_key_header),
    db=Depends(get_db)
):
    webhook_service = WebhookService(db)
    return await webhook_service.list_endpoints(active, event_type)

@router.patch("/endpoints/{endpoint_id}", response_model=WebhookEndpoint)
async def update_endpoint(
    endpoint_id: str,
    update: dict,
    api_key: str = Depends(api_key_header),
    db=Depends(get_db)
):
    webhook_service = WebhookService(db)
    return await webhook_service.update_endpoint(endpoint_id, update)

@router.get("/deliveries", response_model=List[WebhookDelivery])
async def list_deliveries(
    endpoint_id: Optional[str] = None,
    event_id: Optional[str] = None,
    status_code: Optional[int] = None,
    limit: int = 100,
    api_key: str = Depends(api_key_header),
    db=Depends(get_db)
):
    webhook_service = WebhookService(db)
    return await webhook_service.list_deliveries(
        endpoint_id, event_id, status_code, limit
    )

@router.post("/verify")
async def verify_webhook(
    body: bytes,
    x_hook_signature: str = Header(...),
    x_hook_timestamp: str = Header(...),
    x_hook_id: str = Header(...),
    db=Depends(get_db)
):
    webhook_service = WebhookService(db)
    endpoint = await db.get_endpoint(x_hook_id)
    if not endpoint:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Endpoint not found")

    if not webhook_service.verify_signature(
        body,
        x_hook_signature,
        endpoint.secret,
        int(x_hook_timestamp)
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

    return {"status": "verified"}