"""
Webhook Client Implementation
============================

Client for sending webhook notifications from the ECaDP platform.
Handles webhook delivery, retries, and event management.
"""

import asyncio
import logging
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import aiohttp
import time

logger = logging.getLogger(__name__)

@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    event_id: str
    delivery_id: Optional[str] = None

@dataclass
class WebhookDelivery:
    """Webhook delivery result"""
    event_id: str
    delivery_id: str
    webhook_url: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    delivery_time: Optional[float] = None
    attempt: int = 1
    delivered_at: Optional[datetime] = None

class WebhookClient:
    """
    Webhook client for sending HTTP webhook notifications
    
    Features:
    - Automatic retries with exponential backoff
    - Signature verification support
    - Event queuing and batch delivery
    - Delivery status tracking
    - Custom headers and authentication
    """
    
    def __init__(
        self,
        webhook_url: str,
        secret: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30,
        retry_delay: float = 1.0,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        self.webhook_url = webhook_url
        self.secret = secret
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.custom_headers = custom_headers or {}
        
        # Statistics
        self.total_events = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        self.retry_attempts = 0
        
        # Event queue for batch processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.delivery_history: List[WebhookDelivery] = []
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload"""
        if not self.secret:
            return ""
        
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def _prepare_headers(self, payload: str) -> Dict[str, str]:
        """Prepare headers for webhook request"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ECaDP-Webhook/1.0',
            'X-ECaDP-Event': 'webhook',
            'X-ECaDP-Timestamp': str(int(time.time()))
        }
        
        # Add signature if secret is configured
        if self.secret:
            headers['X-ECaDP-Signature'] = self._generate_signature(payload)
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        return headers
    
    async def send_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        event_id: Optional[str] = None,
        immediate: bool = True
    ) -> WebhookDelivery:
        """
        Send a webhook event
        
        Args:
            event_type: Type of event (e.g., 'job.completed')
            payload: Event payload data
            event_id: Optional custom event ID
            immediate: Whether to send immediately or queue for batch processing
            
        Returns:
            WebhookDelivery: Delivery result
        """
        try:
            # Generate event ID if not provided
            if event_id is None:
                event_id = f"evt_{int(time.time() * 1000)}_{len(self.delivery_history)}"
            
            # Create event object
            event = WebhookEvent(
                event_type=event_type,
                payload=payload,
                timestamp=datetime.utcnow(),
                event_id=event_id
            )
            
            self.total_events += 1
            
            if immediate:
                return await self._deliver_event(event)
            else:
                await self.event_queue.put(event)
                # Return placeholder delivery for queued events
                return WebhookDelivery(
                    event_id=event_id,
                    delivery_id=f"queued_{event_id}",
                    webhook_url=self.webhook_url
                )
                
        except Exception as e:
            logger.error(f"Failed to send webhook event {event_type}: {e}")
            self.failed_deliveries += 1
            
            return WebhookDelivery(
                event_id=event_id or "unknown",
                delivery_id=f"failed_{int(time.time())}",
                webhook_url=self.webhook_url,
                error=str(e)
            )
    
    async def _deliver_event(self, event: WebhookEvent) -> WebhookDelivery:
        """Deliver a single webhook event with retries"""
        delivery_id = f"del_{event.event_id}_{int(time.time() * 1000)}"
        
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                
                # Prepare payload
                webhook_payload = {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'timestamp': event.timestamp.isoformat(),
                    'data': event.payload
                }
                
                payload_json = json.dumps(webhook_payload)
                headers = self._prepare_headers(payload_json)
                
                # Ensure session is available
                await self._ensure_session()
                
                # Send webhook request
                async with self._session.post(
                    self.webhook_url,
                    data=payload_json,
                    headers=headers
                ) as response:
                    delivery_time = time.time() - start_time
                    response_body = await response.text()
                    
                    delivery = WebhookDelivery(
                        event_id=event.event_id,
                        delivery_id=delivery_id,
                        webhook_url=self.webhook_url,
                        status_code=response.status,
                        response_body=response_body[:1000],  # Truncate long responses
                        delivery_time=delivery_time,
                        attempt=attempt,
                        delivered_at=datetime.utcnow()
                    )
                    
                    # Check if delivery was successful
                    if 200 <= response.status < 300:
                        self.successful_deliveries += 1
                        self.delivery_history.append(delivery)
                        
                        logger.info(
                            f"Webhook delivered successfully: {event.event_type} "
                            f"(attempt {attempt}, {delivery_time:.2f}s)"
                        )
                        
                        return delivery
                    else:
                        # HTTP error status
                        error_msg = f"HTTP {response.status}: {response_body[:200]}"
                        delivery.error = error_msg
                        
                        if attempt < self.max_retries:
                            logger.warning(
                                f"Webhook delivery failed (attempt {attempt}): {error_msg}. "
                                f"Retrying in {self.retry_delay * attempt}s..."
                            )
                            await asyncio.sleep(self.retry_delay * attempt)
                            self.retry_attempts += 1
                        else:
                            self.failed_deliveries += 1
                            self.delivery_history.append(delivery)
                            
                            logger.error(
                                f"Webhook delivery failed after {self.max_retries} attempts: {error_msg}"
                            )
                            
                            return delivery
                            
            except asyncio.TimeoutError:
                error_msg = f"Webhook delivery timeout (attempt {attempt})"
                
                if attempt < self.max_retries:
                    logger.warning(f"{error_msg}. Retrying...")
                    await asyncio.sleep(self.retry_delay * attempt)
                    self.retry_attempts += 1
                else:
                    self.failed_deliveries += 1
                    
                    delivery = WebhookDelivery(
                        event_id=event.event_id,
                        delivery_id=delivery_id,
                        webhook_url=self.webhook_url,
                        error=error_msg,
                        attempt=attempt
                    )
                    
                    self.delivery_history.append(delivery)
                    logger.error(f"Webhook delivery failed after {self.max_retries} timeout attempts")
                    
                    return delivery
                    
            except Exception as e:
                error_msg = f"Webhook delivery error (attempt {attempt}): {str(e)}"
                
                if attempt < self.max_retries:
                    logger.warning(f"{error_msg}. Retrying...")
                    await asyncio.sleep(self.retry_delay * attempt)
                    self.retry_attempts += 1
                else:
                    self.failed_deliveries += 1
                    
                    delivery = WebhookDelivery(
                        event_id=event.event_id,
                        delivery_id=delivery_id,
                        webhook_url=self.webhook_url,
                        error=error_msg,
                        attempt=attempt
                    )
                    
                    self.delivery_history.append(delivery)
                    logger.error(f"Webhook delivery failed after {self.max_retries} attempts: {e}")
                    
                    return delivery
        
        # This shouldn't be reached, but just in case
        return WebhookDelivery(
            event_id=event.event_id,
            delivery_id=delivery_id,
            webhook_url=self.webhook_url,
            error="Unknown delivery failure"
        )
    
    async def process_queue(self, batch_size: int = 10):
        """Process queued events in batches"""
        try:
            events = []
            
            # Collect events from queue
            for _ in range(batch_size):
                try:
                    event = self.event_queue.get_nowait()
                    events.append(event)
                except asyncio.QueueEmpty:
                    break
            
            if not events:
                return
            
            logger.info(f"Processing {len(events)} queued webhook events")
            
            # Process events concurrently
            tasks = [self._deliver_event(event) for event in events]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            successful = sum(1 for r in results if isinstance(r, WebhookDelivery) and not r.error)
            failed = len(results) - successful
            
            logger.info(f"Batch processing completed: {successful} successful, {failed} failed")
            
        except Exception as e:
            logger.error(f"Error processing webhook queue: {e}")
    
    async def send_test_event(self) -> WebhookDelivery:
        """Send a test webhook event"""
        test_payload = {
            'message': 'This is a test webhook from ECaDP',
            'timestamp': datetime.utcnow().isoformat(),
            'test': True
        }
        
        return await self.send_event('test.webhook', test_payload)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get webhook delivery statistics"""
        return {
            'total_events': self.total_events,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'retry_attempts': self.retry_attempts,
            'success_rate': (
                self.successful_deliveries / max(1, self.total_events) * 100
            ),
            'recent_deliveries': len([
                d for d in self.delivery_history[-100:]  # Last 100 deliveries
                if d.delivered_at and d.delivered_at > datetime.utcnow() - timedelta(hours=24)
            ])
        }
    
    def get_recent_deliveries(self, limit: int = 50) -> List[WebhookDelivery]:
        """Get recent webhook deliveries"""
        return self.delivery_history[-limit:]
    
    def clear_history(self):
        """Clear delivery history (keeping only recent entries)"""
        # Keep only last 1000 entries
        if len(self.delivery_history) > 1000:
            self.delivery_history = self.delivery_history[-1000:]


class WebhookManager:
    """
    Manager for multiple webhook clients
    
    Handles multiple webhook endpoints and event routing.
    """
    
    def __init__(self):
        self.clients: Dict[str, WebhookClient] = {}
        self.event_routing: Dict[str, List[str]] = {}  # event_type -> client_names
    
    def add_webhook(
        self,
        name: str,
        webhook_url: str,
        secret: Optional[str] = None,
        **kwargs
    ):
        """Add a webhook client"""
        self.clients[name] = WebhookClient(
            webhook_url=webhook_url,
            secret=secret,
            **kwargs
        )
    
    def remove_webhook(self, name: str):
        """Remove a webhook client"""
        if name in self.clients:
            asyncio.create_task(self.clients[name].close())
            del self.clients[name]
            
            # Clean up routing
            for event_type, client_names in self.event_routing.items():
                if name in client_names:
                    client_names.remove(name)
    
    def route_event(self, event_type: str, client_names: List[str]):
        """Configure event routing to specific clients"""
        self.event_routing[event_type] = client_names
    
    async def send_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        client_names: Optional[List[str]] = None
    ) -> List[WebhookDelivery]:
        """Send event to multiple webhook clients"""
        # Determine target clients
        if client_names is None:
            client_names = self.event_routing.get(event_type, list(self.clients.keys()))
        
        # Send to all specified clients
        tasks = []
        for client_name in client_names:
            if client_name in self.clients:
                task = self.clients[client_name].send_event(event_type, payload)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if isinstance(r, WebhookDelivery)]
        
        return []
    
    async def close_all(self):
        """Close all webhook clients"""
        tasks = [client.close() for client in self.clients.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.clients.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for all webhook clients"""
        stats = {}
        for name, client in self.clients.items():
            stats[name] = client.get_statistics()
        return stats


# Convenience functions for common webhook patterns

async def send_job_notification(
    webhook_url: str,
    job_id: str,
    job_type: str,
    status: str,
    **additional_data
):
    """Send a job status notification webhook"""
    async with WebhookClient(webhook_url) as client:
        payload = {
            'job_id': job_id,
            'job_type': job_type,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **additional_data
        }
        
        event_type = f"job.{status}"
        return await client.send_event(event_type, payload)

async def send_system_alert(
    webhook_url: str,
    alert_type: str,
    message: str,
    severity: str = "info",
    **additional_data
):
    """Send a system alert webhook"""
    async with WebhookClient(webhook_url) as client:
        payload = {
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            **additional_data
        }
        
        event_type = f"system.{alert_type}"
        return await client.send_event(event_type, payload)
