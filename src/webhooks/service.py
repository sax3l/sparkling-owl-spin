import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
import backoff
from fastapi import HTTPException, status
from .models import WebhookEndpoint, WebhookEvent, WebhookDelivery

class WebhookService:
    def __init__(self, db):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)

    async def verify_signature(
        self, 
        payload: bytes, 
        signature: str, 
        secret: str,
        timestamp: int,
        tolerance: int = 300
    ) -> bool:
        # Verify timestamp is within tolerance
        now = int(datetime.utcnow().timestamp())
        if abs(now - timestamp) > tolerance:
            return False

        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_sig = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(f"sha256={expected_sig}", signature)

    @backoff.on_exception(
        backoff.expo,
        httpx.RequestError,
        max_tries=5,
        max_time=86400  # 24 hours
    )
    async def deliver_webhook(
        self,
        endpoint: WebhookEndpoint,
        event: WebhookEvent
    ) -> WebhookDelivery:
        payload = event.json().encode()
        timestamp = int(datetime.utcnow().timestamp())
        signature = hmac.new(
            endpoint.secret.encode(),
            f"{timestamp}.{payload.decode()}".encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Hook-Id": endpoint.id,
            "X-Hook-Timestamp": str(timestamp),
            "X-Hook-Signature": f"sha256={signature}",
            "X-Hook-Event": event.event_type,
            "X-Hook-Event-Id": event.event_id
        }

        try:
            response = await self.client.post(
                endpoint.url,
                content=payload,
                headers=headers
            )
            
            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                event_id=event.event_id,
                status_code=response.status_code,
                last_attempt_at=datetime.utcnow()
            )

            if response.is_error:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Webhook delivery failed: {response.text}"
                )

            return delivery

        except Exception as e:
            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                event_id=event.event_id,
                status_code=None,
                error_message=str(e),
                last_attempt_at=datetime.utcnow()
            )
            raise
        finally:
            await self.db.save_delivery(delivery)

    async def process_event(self, event: WebhookEvent):
        endpoints = await self.db.get_active_endpoints_for_event(event.event_type)
        for endpoint in endpoints:
            await self.deliver_webhook(endpoint, event)