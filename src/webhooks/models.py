from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field, validator
import uuid

class WebhookEventType(str, Enum):
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    TEMPLATE_DRIFT = "template.drift_detected"
    BANRATE_SPIKE = "banrate.spike"
    DQ_THRESHOLD = "dq.threshold_breach"
    PROXY_POOL_LOW = "proxy.pool.low"
    QUOTA_LIMIT = "quota.near_limit"

class WebhookEndpointCreate(BaseModel):
    url: HttpUrl
    event_types: List[WebhookEventType]
    description: str = Field(..., max_length=200)
    active: bool = True

class WebhookEndpoint(WebhookEndpointCreate):
    id: str = Field(default_factory=lambda: f"wh_{uuid.uuid4().hex[:16]}")
    secret: str = Field(default_factory=lambda: f"whsec_{uuid.uuid4().hex}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('secret')
    def secret_masked(cls, v):
        return f"{v[:8]}..." if v else v

class WebhookDelivery(BaseModel):
    id: str = Field(default_factory=lambda: f"whd_{uuid.uuid4().hex[:16]}")
    endpoint_id: str
    event_id: str
    status_code: Optional[int]
    attempt_count: int = 0
    last_attempt_at: Optional[datetime]
    next_attempt_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:16]}")
    event_type: WebhookEventType
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]