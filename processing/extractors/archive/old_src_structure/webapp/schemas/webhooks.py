"""
Webhook Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class WebhookStatus(str, Enum):
    """Webhook status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class DeliveryStatus(str, Enum):
    """Webhook delivery status enumeration."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXHAUSTED = "exhausted"


class WebhookCreate(BaseModel):
    """Schema for creating webhooks."""
    name: str = Field(..., min_length=1, max_length=255, description="Webhook name")
    description: Optional[str] = Field(None, max_length=1000, description="Webhook description")
    url: HttpUrl = Field(..., description="Webhook URL")
    secret: Optional[str] = Field(None, min_length=8, max_length=255, description="Webhook secret for HMAC")
    events: List[str] = Field(..., min_items=1, description="List of events to subscribe to")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers to send")
    filters: Optional[Dict[str, Any]] = Field(None, description="Event filters")
    retry_attempts: int = Field(3, ge=0, le=10, description="Number of retry attempts")
    retry_backoff_seconds: int = Field(60, ge=1, le=3600, description="Retry backoff time in seconds")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Request timeout in seconds")
    rate_limit_per_minute: int = Field(60, ge=1, le=1000, description="Rate limit per minute")
    
    @validator('events')
    def validate_events(cls, v):
        valid_events = [
            "job.created", "job.started", "job.completed", "job.failed",
            "crawl.page_found", "crawl.page_processed", "crawl.error",
            "scrape.data_extracted", "scrape.error",
            "user.created", "user.updated", "user.deleted",
            "api_key.created", "api_key.used", "api_key.revoked",
            "*"  # All events
        ]
        for event in v:
            if event not in valid_events:
                raise ValueError(f'Invalid event type: {event}')
        return v


class WebhookUpdate(BaseModel):
    """Schema for updating webhooks."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Webhook name")
    description: Optional[str] = Field(None, max_length=1000, description="Webhook description")
    url: Optional[HttpUrl] = Field(None, description="Webhook URL")
    secret: Optional[str] = Field(None, min_length=8, max_length=255, description="Webhook secret for HMAC")
    events: Optional[List[str]] = Field(None, min_items=1, description="List of events to subscribe to")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers to send")
    filters: Optional[Dict[str, Any]] = Field(None, description="Event filters")
    status: Optional[WebhookStatus] = Field(None, description="Webhook status")
    retry_attempts: Optional[int] = Field(None, ge=0, le=10, description="Number of retry attempts")
    retry_backoff_seconds: Optional[int] = Field(None, ge=1, le=3600, description="Retry backoff time")
    timeout_seconds: Optional[int] = Field(None, ge=5, le=300, description="Request timeout")
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000, description="Rate limit per minute")


class WebhookResponse(BaseModel):
    """Schema for webhook responses."""
    id: str = Field(..., description="Webhook ID")
    name: str = Field(..., description="Webhook name")
    description: Optional[str] = Field(None, description="Webhook description")
    url: str = Field(..., description="Webhook URL")
    status: WebhookStatus = Field(..., description="Webhook status")
    is_verified: bool = Field(..., description="URL verification status")
    events: List[str] = Field(..., description="Subscribed events")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")
    filters: Optional[Dict[str, Any]] = Field(None, description="Event filters")
    retry_attempts: int = Field(..., description="Number of retry attempts")
    retry_backoff_seconds: int = Field(..., description="Retry backoff time")
    timeout_seconds: int = Field(..., description="Request timeout")
    rate_limit_per_minute: int = Field(..., description="Rate limit per minute")
    last_delivery_attempt: Optional[datetime] = Field(None, description="Last delivery attempt")
    last_successful_delivery: Optional[datetime] = Field(None, description="Last successful delivery")
    consecutive_failures: int = Field(..., description="Consecutive failure count")
    total_deliveries: int = Field(..., description="Total deliveries")
    total_failures: int = Field(..., description="Total failures")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    user_id: str = Field(..., description="Owner user ID")
    health_status: Dict[str, Any] = Field(..., description="Webhook health status")
    
    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery record responses."""
    id: str = Field(..., description="Delivery record ID")
    webhook_id: str = Field(..., description="Webhook ID")
    delivery_id: str = Field(..., description="Unique delivery ID")
    event_type: str = Field(..., description="Event type")
    attempt_number: int = Field(..., description="Attempt number")
    status: DeliveryStatus = Field(..., description="Delivery status")
    request_url: str = Field(..., description="Request URL")
    request_headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    response_status_code: Optional[int] = Field(None, description="Response status code")
    response_headers: Optional[Dict[str, str]] = Field(None, description="Response headers")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    scheduled_at: datetime = Field(..., description="Scheduled timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class WebhookTest(BaseModel):
    """Schema for testing webhooks."""
    event_type: str = Field("test.webhook", description="Test event type")
    test_data: Optional[Dict[str, Any]] = Field(None, description="Test payload data")


class WebhookTestResponse(BaseModel):
    """Schema for webhook test responses."""
    success: bool = Field(..., description="Whether test was successful")
    delivery_id: str = Field(..., description="Test delivery ID")
    response_status: Optional[int] = Field(None, description="Response status code")
    response_time_ms: Optional[int] = Field(None, description="Response time")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class WebhookStats(BaseModel):
    """Schema for webhook statistics."""
    total_webhooks: int = Field(..., description="Total number of webhooks")
    active_webhooks: int = Field(..., description="Number of active webhooks")
    total_deliveries: int = Field(..., description="Total deliveries across all webhooks")
    successful_deliveries: int = Field(..., description="Successful deliveries")
    failed_deliveries: int = Field(..., description="Failed deliveries")
    average_response_time_ms: float = Field(..., description="Average response time")
    success_rate: float = Field(..., description="Overall success rate percentage")


class WebhookEventCreate(BaseModel):
    """Schema for creating webhook events (internal use)."""
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    source: str = Field("system", description="Event source")
    
    
class WebhookDeliveryFilter(BaseModel):
    """Schema for filtering webhook deliveries."""
    webhook_id: Optional[str] = Field(None, description="Filter by webhook ID")
    event_type: Optional[str] = Field(None, description="Filter by event type")
    status: Optional[DeliveryStatus] = Field(None, description="Filter by delivery status")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    

class WebhookBulkAction(BaseModel):
    """Schema for bulk webhook actions."""
    webhook_ids: List[str] = Field(..., min_items=1, description="List of webhook IDs")
    action: str = Field(..., description="Action to perform")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ["pause", "resume", "disable", "test", "verify"]
        if v not in valid_actions:
            raise ValueError(f'Invalid action: {v}')
        return v


class WebhookBulkActionResponse(BaseModel):
    """Schema for bulk webhook action responses."""
    total_requested: int = Field(..., description="Total webhooks requested")
    successful: int = Field(..., description="Successfully processed webhooks")
    failed: int = Field(..., description="Failed webhook operations")
    results: List[Dict[str, Any]] = Field(..., description="Detailed results")


class WebhookRetryRequest(BaseModel):
    """Schema for retrying webhook deliveries."""
    delivery_ids: List[str] = Field(..., min_items=1, description="List of delivery IDs to retry")
    

class WebhookVerificationRequest(BaseModel):
    """Schema for webhook URL verification."""
    challenge: str = Field(..., description="Verification challenge")


class WebhookVerificationResponse(BaseModel):
    """Schema for webhook verification response."""
    verified: bool = Field(..., description="Whether verification was successful")
    challenge: Optional[str] = Field(None, description="Challenge response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Verification timestamp")


class WebhookPayload(BaseModel):
    """Schema for webhook payload structure."""
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    delivery_id: str = Field(..., description="Unique delivery ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    webhook_id: str = Field(..., description="Webhook ID")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    source: str = Field("system", description="Event source")
    version: str = Field("1.0", description="Payload version")


class WebhookSecurityConfig(BaseModel):
    """Schema for webhook security configuration."""
    require_https: bool = Field(True, description="Require HTTPS URLs")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    allowed_hosts: Optional[List[str]] = Field(None, description="Allowed host patterns")
    blocked_hosts: Optional[List[str]] = Field(None, description="Blocked host patterns")
    max_redirects: int = Field(3, ge=0, le=10, description="Maximum redirects to follow")
