"""
Webhooks router for event notifications and integrations.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field, validator
from sqlalchemy.orm import Session
import hmac
import hashlib
import json
import uuid
from enum import Enum

from ..deps import (
    get_database,
    get_current_active_user,
    get_admin_user,
    RateLimiter
)

router = APIRouter()

# Enums
class WebhookEventType(str, Enum):
    """Webhook event types."""
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"
    DATA_EXPORTED = "data.exported"
    SCRAPE_COMPLETED = "scrape.completed"
    SCRAPE_FAILED = "scrape.failed"
    ANALYSIS_COMPLETED = "analysis.completed"
    ERROR_OCCURRED = "error.occurred"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"

class WebhookStatus(str, Enum):
    """Webhook status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    SUSPENDED = "suspended"

class DeliveryStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"

# Pydantic models
class WebhookCreate(BaseModel):
    """Webhook creation model."""
    name: str = Field(max_length=255)
    url: HttpUrl
    events: List[WebhookEventType]
    secret: Optional[str] = Field(default=None, max_length=255)
    active: bool = True
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    timeout: int = Field(default=30, ge=1, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)
    
    @validator('headers')
    def validate_headers(cls, v):
        if v and len(v) > 20:
            raise ValueError("Too many custom headers (max 20)")
        return v

class WebhookUpdate(BaseModel):
    """Webhook update model."""
    name: Optional[str] = Field(default=None, max_length=255)
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEventType]] = None
    secret: Optional[str] = Field(default=None, max_length=255)
    active: Optional[bool] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = Field(default=None, ge=1, le=300)
    retry_count: Optional[int] = Field(default=None, ge=0, le=10)

class WebhookResponse(BaseModel):
    """Webhook response model."""
    id: int
    name: str
    url: str
    events: List[str]
    active: bool
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_delivery: Optional[datetime]
    delivery_success_count: int
    delivery_failure_count: int
    headers: Optional[Dict[str, str]]
    timeout: int
    retry_count: int

class WebhookDelivery(BaseModel):
    """Webhook delivery model."""
    id: int
    webhook_id: int
    event_type: str
    payload: Dict[str, Any]
    status: str
    response_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_count: int
    created_at: datetime
    delivered_at: Optional[datetime]
    next_retry_at: Optional[datetime]

class WebhookEvent(BaseModel):
    """Webhook event payload model."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "crawler_platform"
    version: str = "1.0"

class WebhookTestResult(BaseModel):
    """Webhook test result model."""
    success: bool
    status_code: Optional[int]
    response_time: float
    error: Optional[str]
    timestamp: datetime

# Services
class WebhookService:
    """Webhook management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_webhook(self, user_id: int, webhook_data: WebhookCreate) -> "Webhook":
        """Create a new webhook."""
        # Generate secret if not provided
        secret = webhook_data.secret
        if not secret:
            secret = self._generate_secret()
        
        db_webhook = Webhook(
            user_id=user_id,
            name=webhook_data.name,
            url=str(webhook_data.url),
            events=webhook_data.events,
            secret=secret,
            active=webhook_data.active,
            headers=webhook_data.headers or {},
            timeout=webhook_data.timeout,
            retry_count=webhook_data.retry_count,
            status=WebhookStatus.ACTIVE if webhook_data.active else WebhookStatus.INACTIVE,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_webhook)
        self.db.commit()
        self.db.refresh(db_webhook)
        
        return db_webhook
    
    def update_webhook(self, webhook_id: int, user_id: int, update_data: WebhookUpdate) -> "Webhook":
        """Update a webhook."""
        webhook = self.db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.user_id == user_id
        ).first()
        
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "url" and value:
                value = str(value)
            setattr(webhook, field, value)
        
        webhook.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(webhook)
        
        return webhook
    
    def delete_webhook(self, webhook_id: int, user_id: int) -> bool:
        """Delete a webhook."""
        webhook = self.db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.user_id == user_id
        ).first()
        
        if not webhook:
            return False
        
        self.db.delete(webhook)
        self.db.commit()
        return True
    
    def get_user_webhooks(self, user_id: int, skip: int = 0, limit: int = 100) -> List["Webhook"]:
        """Get user's webhooks."""
        return self.db.query(Webhook).filter(
            Webhook.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_webhook_deliveries(
        self, 
        webhook_id: int, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List["WebhookDeliveryRecord"]:
        """Get webhook delivery history."""
        # Verify webhook belongs to user
        webhook = self.db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.user_id == user_id
        ).first()
        
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        return self.db.query(WebhookDeliveryRecord).filter(
            WebhookDeliveryRecord.webhook_id == webhook_id
        ).order_by(WebhookDeliveryRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    async def send_webhook(
        self, 
        webhook: "Webhook", 
        event_type: WebhookEventType, 
        payload: Dict[str, Any]
    ) -> "WebhookDeliveryRecord":
        """Send webhook with event data."""
        import httpx
        
        # Create webhook event
        event = WebhookEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=payload
        )
        
        # Create delivery record
        delivery = WebhookDeliveryRecord(
            webhook_id=webhook.id,
            event_type=event_type,
            payload=event.dict(),
            status=DeliveryStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Crawler-Platform-Webhook/1.0",
            "X-Webhook-Event": event_type,
            "X-Webhook-Delivery": str(delivery.id),
            "X-Webhook-Timestamp": str(int(datetime.utcnow().timestamp()))
        }
        
        # Add custom headers
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Add signature if secret is provided
        payload_json = json.dumps(event.dict(), sort_keys=True)
        if webhook.secret:
            signature = self._create_signature(payload_json, webhook.secret)
            headers["X-Webhook-Signature"] = signature
        
        # Send webhook
        try:
            async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                start_time = datetime.utcnow()
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers
                )
                end_time = datetime.utcnow()
                
                # Update delivery record
                delivery.status = DeliveryStatus.DELIVERED if response.is_success else DeliveryStatus.FAILED
                delivery.response_code = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response body size
                delivery.delivered_at = end_time
                delivery.attempt_count = 1
                
                # Update webhook stats
                if response.is_success:
                    webhook.delivery_success_count += 1
                    webhook.last_delivery = end_time
                else:
                    webhook.delivery_failure_count += 1
                
        except Exception as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)[:500]
            delivery.attempt_count = 1
            webhook.delivery_failure_count += 1
            
            # Schedule retry if configured
            if webhook.retry_count > 0:
                delivery.status = DeliveryStatus.RETRYING
                delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
        
        self.db.commit()
        return delivery
    
    async def test_webhook(self, webhook: "Webhook") -> WebhookTestResult:
        """Test webhook connectivity."""
        import httpx
        
        test_event = WebhookEvent(
            event_type="test.ping",
            timestamp=datetime.utcnow(),
            data={"message": "This is a test webhook delivery"}
        )
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Crawler-Platform-Webhook/1.0",
            "X-Webhook-Event": "test.ping",
            "X-Webhook-Test": "true"
        }
        
        if webhook.headers:
            headers.update(webhook.headers)
        
        payload_json = json.dumps(test_event.dict(), sort_keys=True)
        if webhook.secret:
            signature = self._create_signature(payload_json, webhook.secret)
            headers["X-Webhook-Signature"] = signature
        
        try:
            start_time = datetime.utcnow()
            async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers
                )
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds()
            
            return WebhookTestResult(
                success=response.is_success,
                status_code=response.status_code,
                response_time=response_time,
                timestamp=end_time
            )
            
        except Exception as e:
            return WebhookTestResult(
                success=False,
                status_code=None,
                response_time=0.0,
                error=str(e),
                timestamp=datetime.utcnow()
            )
    
    def _generate_secret(self) -> str:
        """Generate webhook secret."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _create_signature(self, payload: str, secret: str) -> str:
        """Create webhook signature."""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

# Routes
@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database),
    rate_limit: dict = Depends(RateLimiter("10/hour"))
):
    """Create a new webhook."""
    service = WebhookService(db)
    webhook = service.create_webhook(current_user.id, webhook_data)
    return WebhookResponse.from_orm(webhook)

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """List user's webhooks."""
    service = WebhookService(db)
    webhooks = service.get_user_webhooks(current_user.id, skip, limit)
    return [WebhookResponse.from_orm(webhook) for webhook in webhooks]

@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return WebhookResponse.from_orm(webhook)

@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update a webhook."""
    service = WebhookService(db)
    webhook = service.update_webhook(webhook_id, current_user.id, webhook_data)
    return WebhookResponse.from_orm(webhook)

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Delete a webhook."""
    service = WebhookService(db)
    success = service.delete_webhook(webhook_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return {"message": "Webhook deleted successfully"}

@router.post("/{webhook_id}/test", response_model=WebhookTestResult)
async def test_webhook(
    webhook_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Test webhook connectivity."""
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    service = WebhookService(db)
    result = await service.test_webhook(webhook)
    return result

@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get webhook delivery history."""
    service = WebhookService(db)
    deliveries = service.get_webhook_deliveries(webhook_id, current_user.id, skip, limit)
    return [WebhookDelivery.from_orm(delivery) for delivery in deliveries]

@router.post("/{webhook_id}/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    webhook_id: int,
    delivery_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Retry a failed webhook delivery."""
    # Verify webhook ownership
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.user_id == current_user.id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Get delivery record
    delivery = db.query(WebhookDeliveryRecord).filter(
        WebhookDeliveryRecord.id == delivery_id,
        WebhookDeliveryRecord.webhook_id == webhook_id
    ).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    if delivery.status not in [DeliveryStatus.FAILED, DeliveryStatus.RETRYING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed deliveries can be retried"
        )
    
    # Schedule retry in background
    service = WebhookService(db)
    background_tasks.add_task(
        service.send_webhook,
        webhook,
        delivery.event_type,
        delivery.payload["data"]
    )
    
    return {"message": "Delivery retry scheduled"}

# Webhook event receivers
@router.post("/receive/{webhook_id}")
async def receive_webhook(
    webhook_id: int,
    request: Request,
    db: Session = Depends(get_database)
):
    """Receive incoming webhook (for webhook chaining)."""
    # Get webhook configuration
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    # Verify signature if secret is configured
    if webhook.secret:
        signature = request.headers.get("X-Webhook-Signature")
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature"
            )
        
        body = await request.body()
        expected_signature = hmac.new(
            webhook.secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    # Process webhook payload
    try:
        payload = await request.json()
        
        # Log webhook receipt
        receipt = WebhookReceipt(
            webhook_id=webhook_id,
            payload=payload,
            headers=dict(request.headers),
            source_ip=request.client.host,
            received_at=datetime.utcnow()
        )
        
        db.add(receipt)
        db.commit()
        
        return {"status": "received", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook payload: {str(e)}"
        )

# Admin routes
@router.get("/admin/webhooks", response_model=List[WebhookResponse])
async def admin_list_all_webhooks(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """List all webhooks (admin only)."""
    webhooks = db.query(Webhook).offset(skip).limit(limit).all()
    return [WebhookResponse.from_orm(webhook) for webhook in webhooks]

@router.get("/admin/deliveries/failed")
async def admin_get_failed_deliveries(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """Get failed webhook deliveries (admin only)."""
    deliveries = db.query(WebhookDeliveryRecord).filter(
        WebhookDeliveryRecord.status == DeliveryStatus.FAILED
    ).order_by(WebhookDeliveryRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return [WebhookDelivery.from_orm(delivery) for delivery in deliveries]

# Event types endpoint
@router.get("/events", response_model=List[str])
async def list_webhook_events():
    """List available webhook event types."""
    return [event.value for event in WebhookEventType]

# Health check
@router.get("/health")
async def webhooks_health_check():
    """Health check for webhooks service."""
    return {
        "status": "healthy",
        "service": "webhooks",
        "timestamp": datetime.utcnow().isoformat()
    }
