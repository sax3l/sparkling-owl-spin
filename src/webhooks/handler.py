"""
Webhook Handler Implementation
=============================

Handler for receiving and processing webhook events in the ECaDP platform.
Supports validation, event processing, and response handling.
"""

import json
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from functools import wraps
import asyncio
import time

from fastapi import Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

@dataclass
class WebhookEvent:
    """Incoming webhook event"""
    event_id: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    source: str
    headers: Dict[str, str]
    signature: Optional[str] = None
    verified: bool = False

@dataclass
class WebhookResponse:
    """Webhook processing response"""
    success: bool
    message: str
    event_id: str
    processed_at: datetime
    processing_time: float
    error: Optional[str] = None

class WebhookValidator:
    """Webhook signature validation"""
    
    def __init__(self, secret: str):
        self.secret = secret.encode('utf-8')
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        try:
            if not signature:
                return False
            
            # Extract signature from header (e.g., "sha256=abc123")
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.secret,
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures securely
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

class WebhookHandler:
    """
    Main webhook handler for processing incoming webhook events
    
    Features:
    - Signature verification
    - Event routing and processing
    - Background task execution
    - Rate limiting and validation
    - Event history and logging
    """
    
    def __init__(
        self,
        secret: Optional[str] = None,
        max_payload_size: int = 1024 * 1024,  # 1MB
        rate_limit_window: int = 60,  # seconds
        rate_limit_max_requests: int = 100
    ):
        self.validator = WebhookValidator(secret) if secret else None
        self.max_payload_size = max_payload_size
        self.rate_limit_window = rate_limit_window
        self.rate_limit_max_requests = rate_limit_max_requests
        
        # Event handlers registry
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.global_handlers: List[Callable] = []
        
        # Rate limiting tracking
        self.request_history: List[datetime] = []
        
        # Processing statistics
        self.total_events = 0
        self.successful_events = 0
        self.failed_events = 0
        self.event_history: List[WebhookEvent] = []
    
    def register_handler(self, event_type: str):
        """Decorator to register event handlers"""
        def decorator(func: Callable):
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(func)
            return func
        return decorator
    
    def register_global_handler(self, func: Callable):
        """Register a global event handler"""
        self.global_handlers.append(func)
        return func
    
    async def _check_rate_limit(self, source_ip: str) -> bool:
        """Check if request is within rate limits"""
        now = datetime.utcnow()
        
        # Clean old entries
        cutoff = now - timedelta(seconds=self.rate_limit_window)
        self.request_history = [
            ts for ts in self.request_history if ts > cutoff
        ]
        
        # Check limit
        if len(self.request_history) >= self.rate_limit_max_requests:
            logger.warning(f"Rate limit exceeded for {source_ip}")
            return False
        
        # Add current request
        self.request_history.append(now)
        return True
    
    async def _validate_payload_size(self, content_length: int) -> bool:
        """Validate payload size"""
        if content_length > self.max_payload_size:
            logger.warning(f"Payload too large: {content_length} bytes")
            return False
        return True
    
    async def _parse_webhook_event(self, request: Request) -> WebhookEvent:
        """Parse incoming webhook request into WebhookEvent"""
        try:
            # Get headers
            headers = dict(request.headers)
            
            # Get body
            body = await request.body()
            payload_str = body.decode('utf-8')
            
            # Parse JSON payload
            try:
                payload_data = json.loads(payload_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON payload: {e}")
            
            # Extract event information
            event_id = payload_data.get('event_id') or headers.get('x-event-id', f"evt_{int(time.time() * 1000)}")
            event_type = payload_data.get('event_type') or headers.get('x-event-type', 'unknown')
            
            # Parse timestamp
            timestamp_str = payload_data.get('timestamp') or headers.get('x-timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.utcnow()
            else:
                timestamp = datetime.utcnow()
            
            # Extract signature
            signature = headers.get('x-ecadp-signature') or headers.get('x-hub-signature-256')
            
            # Determine source
            source = headers.get('user-agent', 'unknown')
            
            # Verify signature if validator is configured
            verified = False
            if self.validator and signature:
                verified = self.validator.verify_signature(payload_str, signature)
            elif not self.validator:
                verified = True  # No validation configured
            
            return WebhookEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=timestamp,
                payload=payload_data.get('data', payload_data),  # Use 'data' field or entire payload
                source=source,
                headers=headers,
                signature=signature,
                verified=verified
            )
            
        except Exception as e:
            logger.error(f"Failed to parse webhook event: {e}")
            raise ValueError(f"Invalid webhook format: {e}")
    
    async def _process_event(self, event: WebhookEvent, background_tasks: BackgroundTasks) -> WebhookResponse:
        """Process a webhook event"""
        start_time = time.time()
        
        try:
            # Check signature verification
            if self.validator and not event.verified:
                raise ValueError("Invalid signature")
            
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            all_handlers = self.global_handlers + handlers
            
            if not all_handlers:
                logger.warning(f"No handlers registered for event type: {event.event_type}")
                # Still consider it successful - just no processing needed
                processing_time = time.time() - start_time
                self.successful_events += 1
                
                return WebhookResponse(
                    success=True,
                    message=f"Event received but no handlers registered for {event.event_type}",
                    event_id=event.event_id,
                    processed_at=datetime.utcnow(),
                    processing_time=processing_time
                )
            
            # Process with all handlers
            results = []
            for handler in all_handlers:
                try:
                    # Check if handler is async
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(event)
                    else:
                        # Run sync handler in background
                        background_tasks.add_task(handler, event)
                        result = "scheduled"
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Handler {handler.__name__} failed for event {event.event_id}: {e}")
                    results.append(f"error: {e}")
            
            processing_time = time.time() - start_time
            self.successful_events += 1
            
            return WebhookResponse(
                success=True,
                message=f"Event processed by {len(all_handlers)} handlers",
                event_id=event.event_id,
                processed_at=datetime.utcnow(),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.failed_events += 1
            
            logger.error(f"Failed to process webhook event {event.event_id}: {e}")
            
            return WebhookResponse(
                success=False,
                message="Event processing failed",
                event_id=event.event_id,
                processed_at=datetime.utcnow(),
                processing_time=processing_time,
                error=str(e)
            )
    
    async def handle_webhook(self, request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
        """Main webhook handling endpoint"""
        start_time = time.time()
        
        try:
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Check rate limiting
            if not await self._check_rate_limit(client_ip):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Check payload size
            content_length = int(request.headers.get('content-length', 0))
            if not await self._validate_payload_size(content_length):
                raise HTTPException(status_code=413, detail="Payload too large")
            
            # Parse webhook event
            event = await self._parse_webhook_event(request)
            
            # Store event in history
            self.event_history.append(event)
            self.total_events += 1
            
            # Keep only recent events in memory
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-1000:]
            
            logger.info(f"Received webhook event: {event.event_type} (ID: {event.event_id})")
            
            # Process the event
            response = await self._process_event(event, background_tasks)
            
            # Return appropriate HTTP response
            status_code = 200 if response.success else 400
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "success": response.success,
                    "message": response.message,
                    "event_id": response.event_id,
                    "processed_at": response.processed_at.isoformat(),
                    "processing_time": response.processing_time,
                    "error": response.error
                }
            )
            
        except HTTPException:
            raise
        except ValueError as e:
            # Client error (bad request)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid webhook request",
                    "error": str(e),
                    "processed_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            # Server error
            logger.error(f"Webhook handling error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "error": str(e),
                    "processed_at": datetime.utcnow().isoformat()
                }
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        return {
            "total_events": self.total_events,
            "successful_events": self.successful_events,
            "failed_events": self.failed_events,
            "success_rate": (
                self.successful_events / max(1, self.total_events) * 100
            ),
            "registered_event_types": list(self.event_handlers.keys()),
            "global_handlers": len(self.global_handlers),
            "recent_events": len(self.event_history),
            "rate_limit_window": self.rate_limit_window,
            "rate_limit_max_requests": self.rate_limit_max_requests
        }
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent webhook events"""
        recent_events = self.event_history[-limit:]
        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "verified": event.verified
            }
            for event in recent_events
        ]


# Example event handlers

class DefaultEventHandlers:
    """Default webhook event handlers"""
    
    def __init__(self, webhook_handler: WebhookHandler):
        self.handler = webhook_handler
        self._register_handlers()
    
    def _register_handlers(self):
        """Register default event handlers"""
        
        @self.handler.register_handler("job.started")
        async def handle_job_started(event: WebhookEvent):
            """Handle job started events"""
            job_id = event.payload.get('job_id')
            job_type = event.payload.get('job_type')
            
            logger.info(f"Job {job_id} ({job_type}) started")
            
            # Add your job started logic here
            # e.g., update database, send notifications, etc.
            
            return {"status": "handled", "action": "job_started_processed"}
        
        @self.handler.register_handler("job.completed")
        async def handle_job_completed(event: WebhookEvent):
            """Handle job completed events"""
            job_id = event.payload.get('job_id')
            job_type = event.payload.get('job_type')
            status = event.payload.get('status')
            
            logger.info(f"Job {job_id} ({job_type}) completed with status: {status}")
            
            # Add your job completion logic here
            # e.g., process results, send notifications, cleanup, etc.
            
            return {"status": "handled", "action": "job_completed_processed"}
        
        @self.handler.register_handler("job.failed")
        async def handle_job_failed(event: WebhookEvent):
            """Handle job failed events"""
            job_id = event.payload.get('job_id')
            job_type = event.payload.get('job_type')
            error = event.payload.get('error')
            
            logger.error(f"Job {job_id} ({job_type}) failed: {error}")
            
            # Add your job failure logic here
            # e.g., retry logic, error reporting, cleanup, etc.
            
            return {"status": "handled", "action": "job_failure_processed"}
        
        @self.handler.register_handler("system.alert")
        async def handle_system_alert(event: WebhookEvent):
            """Handle system alert events"""
            alert_type = event.payload.get('alert_type')
            message = event.payload.get('message')
            severity = event.payload.get('severity', 'info')
            
            logger.warning(f"System alert ({severity}): {alert_type} - {message}")
            
            # Add your alert handling logic here
            # e.g., escalation, notifications, automated responses, etc.
            
            return {"status": "handled", "action": "alert_processed"}
        
        @self.handler.register_handler("data.extracted")
        async def handle_data_extracted(event: WebhookEvent):
            """Handle data extraction events"""
            extraction_id = event.payload.get('extraction_id')
            template_name = event.payload.get('template_name')
            records_count = event.payload.get('records_count', 0)
            
            logger.info(f"Data extracted: {records_count} records using template {template_name}")
            
            # Add your data processing logic here
            # e.g., validation, transformation, storage, notifications, etc.
            
            return {"status": "handled", "action": "data_extraction_processed"}
        
        @self.handler.register_global_handler
        async def log_all_events(event: WebhookEvent):
            """Global handler to log all events"""
            logger.debug(
                f"Webhook event received: {event.event_type} "
                f"from {event.source} at {event.timestamp}"
            )
            
            # Add global event logging/auditing logic here
            # e.g., store in audit log, send to monitoring system, etc.
            
            return {"status": "logged", "action": "global_logging"}


# Convenience functions for creating webhook handlers

def create_webhook_handler(
    secret: Optional[str] = None,
    **kwargs
) -> WebhookHandler:
    """Create a webhook handler with default configuration"""
    handler = WebhookHandler(secret=secret, **kwargs)
    
    # Register default handlers
    DefaultEventHandlers(handler)
    
    return handler

def create_simple_webhook_handler(
    event_handlers: Dict[str, Callable],
    secret: Optional[str] = None,
    **kwargs
) -> WebhookHandler:
    """Create a simple webhook handler with custom event handlers"""
    handler = WebhookHandler(secret=secret, **kwargs)
    
    # Register custom handlers
    for event_type, handler_func in event_handlers.items():
        handler.event_handlers[event_type] = [handler_func]
    
    return handler
