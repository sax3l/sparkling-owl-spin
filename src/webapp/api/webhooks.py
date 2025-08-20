from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from src.database.manager import get_db
from src.database.models import WebhookEndpoint, WebhookEndpointCreate, WebhookDelivery, WebhookEventType
from src.webhooks.service import WebhookService
from src.webapp.security import get_current_tenant_id, authorize_with_scopes
import logging
import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/endpoints", response_model=WebhookEndpoint, status_code=201, dependencies=[Depends(authorize_with_scopes(["webhooks:write"]))])
async def create_webhook_endpoint(
    endpoint_create: WebhookEndpointCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Registers a new webhook endpoint for a tenant."""
    logger.info(f"Creating webhook endpoint for tenant {tenant_id}", extra={"tenant_id": str(tenant_id)})
    webhook_service = WebhookService(db)
    
    # Generate secret server-side
    new_endpoint = WebhookEndpoint(
        tenant_id=tenant_id,
        url=endpoint_create.url,
        event_types=endpoint_create.event_types,
        description=endpoint_create.description,
        active=endpoint_create.active,
        secret=f"whsec_{uuid.uuid4().hex}" # Generate a secure secret
    )
    
    db.add(new_endpoint)
    db.commit()
    db.refresh(new_endpoint)
    
    logger.info(f"Webhook endpoint {new_endpoint.id} created.", extra={"endpoint_id": str(new_endpoint.id), "tenant_id": str(tenant_id)})
    return new_endpoint

@router.get("/webhooks/endpoints", response_model=List[WebhookEndpoint], dependencies=[Depends(authorize_with_scopes(["webhooks:read"]))])
async def list_webhook_endpoints(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    active: Optional[bool] = Query(None),
    event_type: Optional[WebhookEventType] = Query(None)
):
    """Lists all webhook endpoints for the authenticated tenant."""
    query = db.query(WebhookEndpoint).filter(WebhookEndpoint.tenant_id == tenant_id)
    if active is not None:
        query = query.filter(WebhookEndpoint.active == active)
    if event_type:
        query = query.filter(WebhookEndpoint.event_types.contains([event_type.value])) # Check if array contains value
    
    endpoints = query.all()
    return endpoints

@router.patch("/webhooks/endpoints/{endpoint_id}", response_model=WebhookEndpoint, dependencies=[Depends(authorize_with_scopes(["webhooks:write"]))])
async def update_webhook_endpoint(
    endpoint_id: UUID,
    update_data: dict, # Use dict for partial updates
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Updates an existing webhook endpoint (e.g., activate/deactivate, rotate secret)."""
    db_endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == endpoint_id,
        WebhookEndpoint.tenant_id == tenant_id
    ).first()

    if not db_endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found.")

    if "secret_rotate" in update_data and update_data["secret_rotate"]:
        db_endpoint.secret = f"whsec_{uuid.uuid4().hex}"
        logger.info(f"Webhook endpoint {endpoint_id} secret rotated.", extra={"endpoint_id": str(endpoint_id), "tenant_id": str(tenant_id)})
        del update_data["secret_rotate"] # Remove this field so it's not applied directly

    for key, value in update_data.items():
        if hasattr(db_endpoint, key):
            setattr(db_endpoint, key, value)
    
    db_endpoint.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

@router.get("/webhooks/deliveries", response_model=List[WebhookDelivery], dependencies=[Depends(authorize_with_scopes(["webhooks:read"]))])
async def list_webhook_deliveries(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    endpoint_id: Optional[UUID] = Query(None),
    event_id: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Lists webhook delivery attempts for the authenticated tenant."""
    # Note: WebhookDelivery model currently doesn't have tenant_id.
    # For production, you'd want to filter deliveries by tenant_id as well.
    # Assuming for now that endpoint_id implies tenant ownership.
    query = db.query(WebhookDelivery)

    if endpoint_id:
        # Verify endpoint belongs to tenant
        endpoint = db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == endpoint_id,
            WebhookEndpoint.tenant_id == tenant_id
        ).first()
        if not endpoint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found for this tenant.")
        query = query.filter(WebhookDelivery.endpoint_id == endpoint_id)
    
    if event_id:
        query = query.filter(WebhookDelivery.event_id == event_id)
    if status_code:
        query = query.filter(WebhookDelivery.status_code == status_code)
    
    deliveries = query.order_by(WebhookDelivery.created_at.desc()).offset(offset).limit(limit).all()
    return deliveries