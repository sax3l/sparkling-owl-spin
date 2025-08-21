"""
Webhook models for event-driven integrations.
"""

import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import BaseModel


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
    EXHAUSTED = "exhausted"  # Max retries reached


class Webhook(BaseModel):
    """Webhook model for event-driven integrations."""
    
    __tablename__ = "webhooks"
    
    # Basic webhook information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False)
    
    # Security
    secret = Column(String(255), nullable=True)  # For HMAC signature verification
    headers = Column(JSONB, nullable=True)  # Additional headers to send
    
    # Status and configuration
    status = Column(SQLEnum(WebhookStatus), default=WebhookStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # URL verification status
    
    # Event filtering
    events = Column(Text, nullable=False)  # Comma-separated event types
    filters = Column(JSONB, nullable=True)  # JSON filters for event data
    
    # Retry configuration
    retry_attempts = Column(Integer, default=3, nullable=False)
    retry_backoff_seconds = Column(Integer, default=60, nullable=False)  # Base backoff time
    timeout_seconds = Column(Integer, default=30, nullable=False)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)
    
    # Monitoring
    last_delivery_attempt = Column(DateTime(timezone=True), nullable=True)
    last_successful_delivery = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    total_deliveries = Column(Integer, default=0, nullable=False)
    total_failures = Column(Integer, default=0, nullable=False)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Delivery records
    delivery_records = relationship("WebhookDeliveryRecord", back_populates="webhook", cascade="all, delete-orphan")
    
    def get_events(self) -> List[str]:
        """Get list of events this webhook subscribes to."""
        return [event.strip() for event in self.events.split(",")]
    
    def subscribes_to_event(self, event_type: str) -> bool:
        """Check if webhook subscribes to a specific event type."""
        return event_type in self.get_events() or "*" in self.get_events()
    
    def generate_signature(self, payload: str) -> Optional[str]:
        """Generate HMAC signature for payload."""
        if not self.secret:
            return None
            
        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify HMAC signature for payload."""
        if not self.secret:
            return True  # No secret means no verification required
            
        expected_signature = self.generate_signature(payload)
        if not expected_signature:
            return False
            
        return hmac.compare_digest(expected_signature, signature)
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers to send with webhook requests."""
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Crawler-Webhook/1.0"
        }
        
        if self.headers:
            default_headers.update(self.headers)
            
        return default_headers
    
    def should_deliver(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Check if webhook should receive this event."""
        if self.status != WebhookStatus.ACTIVE:
            return False
            
        if not self.subscribes_to_event(event_type):
            return False
            
        # Apply filters if configured
        if self.filters:
            return self._matches_filters(event_data, self.filters)
            
        return True
    
    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if event data matches configured filters."""
        for key, expected_value in filters.items():
            if key not in data:
                return False
                
            actual_value = data[key]
            
            # Handle different filter types
            if isinstance(expected_value, dict):
                if "$in" in expected_value:
                    if actual_value not in expected_value["$in"]:
                        return False
                elif "$eq" in expected_value:
                    if actual_value != expected_value["$eq"]:
                        return False
                elif "$ne" in expected_value:
                    if actual_value == expected_value["$ne"]:
                        return False
            else:
                if actual_value != expected_value:
                    return False
                    
        return True
    
    def record_delivery_attempt(self, success: bool) -> None:
        """Record a delivery attempt."""
        self.last_delivery_attempt = datetime.utcnow()
        self.total_deliveries += 1
        
        if success:
            self.last_successful_delivery = datetime.utcnow()
            self.consecutive_failures = 0
        else:
            self.total_failures += 1
            self.consecutive_failures += 1
            
            # Disable webhook after too many consecutive failures
            if self.consecutive_failures >= 10:
                self.status = WebhookStatus.ERROR
    
    def calculate_retry_delay(self, attempt: int) -> int:
        """Calculate retry delay with exponential backoff."""
        return self.retry_backoff_seconds * (2 ** attempt)
    
    def disable_on_error(self) -> None:
        """Disable webhook due to errors."""
        self.status = WebhookStatus.ERROR
    
    def pause(self) -> None:
        """Pause webhook deliveries."""
        self.status = WebhookStatus.PAUSED
    
    def resume(self) -> None:
        """Resume webhook deliveries."""
        if self.status == WebhookStatus.PAUSED:
            self.status = WebhookStatus.ACTIVE
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get webhook health status."""
        total_attempts = self.total_deliveries
        success_rate = 0
        
        if total_attempts > 0:
            success_rate = ((total_attempts - self.total_failures) / total_attempts) * 100
            
        return {
            "status": self.status.value,
            "is_healthy": self.consecutive_failures < 5,
            "success_rate": round(success_rate, 2),
            "total_deliveries": self.total_deliveries,
            "total_failures": self.total_failures,
            "consecutive_failures": self.consecutive_failures,
            "last_delivery": self.last_delivery_attempt.isoformat() if self.last_delivery_attempt else None,
            "last_success": self.last_successful_delivery.isoformat() if self.last_successful_delivery else None
        }
    
    def to_dict(self, include_secret: bool = False) -> dict:
        """Convert webhook to dictionary."""
        exclude_fields = []
        if not include_secret:
            exclude_fields.append("secret")
            
        data = super().to_dict(exclude_fields=exclude_fields)
        data["events_list"] = self.get_events()
        data["health_status"] = self.get_health_status()
        
        return data


class WebhookDeliveryRecord(BaseModel):
    """Record of webhook delivery attempts."""
    
    __tablename__ = "webhook_delivery_records"
    
    # Associated webhook
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)
    webhook = relationship("Webhook", back_populates="delivery_records")
    
    # Event information
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSONB, nullable=False)
    
    # Delivery details
    delivery_id = Column(String(100), unique=True, nullable=False)  # Unique ID for this delivery
    attempt_number = Column(Integer, default=1, nullable=False)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False)
    
    # Request/Response details
    request_url = Column(String(1000), nullable=False)
    request_headers = Column(JSONB, nullable=True)
    request_body = Column(Text, nullable=True)
    
    # Response details
    response_status_code = Column(Integer, nullable=True)
    response_headers = Column(JSONB, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    @classmethod
    def create_delivery(
        cls,
        webhook: Webhook,
        event_type: str,
        event_data: Dict[str, Any],
        delivery_id: str
    ) -> "WebhookDeliveryRecord":
        """Create a new delivery record."""
        return cls(
            webhook_id=webhook.id,
            event_type=event_type,
            event_data=event_data,
            delivery_id=delivery_id,
            request_url=webhook.url,
            request_headers=webhook.get_headers(),
            request_body=json.dumps({
                "event_type": event_type,
                "data": event_data,
                "delivery_id": delivery_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            scheduled_at=datetime.utcnow()
        )
    
    def mark_delivered(self, status_code: int, response_headers: Dict, response_body: str, response_time_ms: int) -> None:
        """Mark delivery as successful."""
        self.status = DeliveryStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.response_status_code = status_code
        self.response_headers = response_headers
        self.response_body = response_body
        self.response_time_ms = response_time_ms
    
    def mark_failed(self, error_message: str, error_code: str = None, status_code: int = None) -> None:
        """Mark delivery as failed."""
        self.status = DeliveryStatus.FAILED
        self.error_message = error_message
        self.error_code = error_code
        self.response_status_code = status_code
        
    def schedule_retry(self, delay_seconds: int) -> None:
        """Schedule retry for failed delivery."""
        self.status = DeliveryStatus.RETRYING
        self.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.attempt_number += 1
        
    def mark_exhausted(self) -> None:
        """Mark delivery as exhausted (max retries reached)."""
        self.status = DeliveryStatus.EXHAUSTED
        
    def is_ready_for_retry(self) -> bool:
        """Check if delivery is ready for retry."""
        if self.status != DeliveryStatus.RETRYING:
            return False
            
        if not self.next_retry_at:
            return True
            
        return datetime.utcnow() >= self.next_retry_at
    
    def get_delivery_summary(self) -> Dict[str, Any]:
        """Get summary of delivery attempt."""
        return {
            "delivery_id": self.delivery_id,
            "event_type": self.event_type,
            "status": self.status.value,
            "attempt_number": self.attempt_number,
            "scheduled_at": self.scheduled_at.isoformat(),
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "response_status": self.response_status_code,
            "response_time_ms": self.response_time_ms,
            "error_message": self.error_message,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None
        }
