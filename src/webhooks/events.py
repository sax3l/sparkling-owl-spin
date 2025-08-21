"""
Webhook Events System
====================

Event definitions and dispatching system for webhook notifications.
Provides structured event creation and management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Standard webhook event types"""
    
    # Job events
    JOB_CREATED = "job.created"
    JOB_STARTED = "job.started"
    JOB_PROGRESS = "job.progress"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"
    JOB_RETRYING = "job.retrying"
    
    # Data events
    DATA_EXTRACTED = "data.extracted"
    DATA_VALIDATED = "data.validated"
    DATA_EXPORTED = "data.exported"
    DATA_QUALITY_ISSUE = "data.quality_issue"
    
    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ALERT = "system.alert"
    SYSTEM_ERROR = "system.error"
    SYSTEM_HEALTH_CHECK = "system.health_check"
    
    # Crawler events
    CRAWLER_STARTED = "crawler.started"
    CRAWLER_COMPLETED = "crawler.completed"
    CRAWLER_FAILED = "crawler.failed"
    CRAWLER_SITEMAP_GENERATED = "crawler.sitemap_generated"
    CRAWLER_RATE_LIMITED = "crawler.rate_limited"
    
    # Scraper events
    SCRAPER_STARTED = "scraper.started"
    SCRAPER_COMPLETED = "scraper.completed"
    SCRAPER_FAILED = "scraper.failed"
    SCRAPER_TEMPLATE_LOADED = "scraper.template_loaded"
    SCRAPER_DATA_EXTRACTED = "scraper.data_extracted"
    
    # Proxy events
    PROXY_UPDATED = "proxy.updated"
    PROXY_HEALTH_CHECK = "proxy.health_check"
    PROXY_FAILED = "proxy.failed"
    PROXY_ROTATION = "proxy.rotation"
    
    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_UPDATED = "user.updated"
    
    # Template events
    TEMPLATE_CREATED = "template.created"
    TEMPLATE_UPDATED = "template.updated"
    TEMPLATE_VALIDATED = "template.validated"
    TEMPLATE_DELETED = "template.deleted"
    TEMPLATE_DRIFT = "template.drift"
    
    # Webhook events
    WEBHOOK_SENT = "webhook.sent"
    WEBHOOK_FAILED = "webhook.failed"
    WEBHOOK_RETRY = "webhook.retry"
    
    # Legacy compatibility events
    BANRATE_SPIKE = "banrate.spike"
    QUOTA_LIMIT = "quota.limit"
    
    # Test events
    TEST_EVENT = "test.event"

class EventSeverity(Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class WebhookEventData:
    """Base webhook event data structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "ecadp"
    severity: EventSeverity = EventSeverity.INFO
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "severity": self.severity.value,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

# Event builders for different event types

class JobEventBuilder:
    """Builder for job-related events"""
    
    @staticmethod
    def created(
        job_id: str,
        job_type: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> WebhookEventData:
        """Create job created event"""
        return WebhookEventData(
            event_type=EventType.JOB_CREATED.value,
            data={
                "job_id": job_id,
                "job_type": job_type,
                "user_id": user_id,
                "status": "created",
                **kwargs
            }
        )
    
    @staticmethod
    def started(
        job_id: str,
        job_type: str,
        worker_id: Optional[str] = None,
        **kwargs
    ) -> WebhookEventData:
        """Create job started event"""
        return WebhookEventData(
            event_type=EventType.JOB_STARTED.value,
            data={
                "job_id": job_id,
                "job_type": job_type,
                "worker_id": worker_id,
                "status": "started",
                "started_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def progress(
        job_id: str,
        job_type: str,
        progress_percentage: float,
        current_step: str,
        **kwargs
    ) -> WebhookEventData:
        """Create job progress event"""
        return WebhookEventData(
            event_type=EventType.JOB_PROGRESS.value,
            data={
                "job_id": job_id,
                "job_type": job_type,
                "progress_percentage": progress_percentage,
                "current_step": current_step,
                "status": "in_progress",
                **kwargs
            }
        )
    
    @staticmethod
    def completed(
        job_id: str,
        job_type: str,
        duration: float,
        results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> WebhookEventData:
        """Create job completed event"""
        return WebhookEventData(
            event_type=EventType.JOB_COMPLETED.value,
            severity=EventSeverity.INFO,
            data={
                "job_id": job_id,
                "job_type": job_type,
                "status": "completed",
                "duration": duration,
                "completed_at": datetime.utcnow().isoformat(),
                "results": results or {},
                **kwargs
            }
        )
    
    @staticmethod
    def failed(
        job_id: str,
        job_type: str,
        error: str,
        duration: Optional[float] = None,
        **kwargs
    ) -> WebhookEventData:
        """Create job failed event"""
        return WebhookEventData(
            event_type=EventType.JOB_FAILED.value,
            severity=EventSeverity.ERROR,
            data={
                "job_id": job_id,
                "job_type": job_type,
                "status": "failed",
                "error": error,
                "duration": duration,
                "failed_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )

class DataEventBuilder:
    """Builder for data-related events"""
    
    @staticmethod
    def extracted(
        extraction_id: str,
        template_name: str,
        records_count: int,
        source_url: str,
        **kwargs
    ) -> WebhookEventData:
        """Create data extracted event"""
        return WebhookEventData(
            event_type=EventType.DATA_EXTRACTED.value,
            data={
                "extraction_id": extraction_id,
                "template_name": template_name,
                "records_count": records_count,
                "source_url": source_url,
                "extracted_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def validated(
        validation_id: str,
        records_count: int,
        valid_records: int,
        invalid_records: int,
        **kwargs
    ) -> WebhookEventData:
        """Create data validated event"""
        return WebhookEventData(
            event_type=EventType.DATA_VALIDATED.value,
            data={
                "validation_id": validation_id,
                "records_count": records_count,
                "valid_records": valid_records,
                "invalid_records": invalid_records,
                "validation_rate": valid_records / max(1, records_count) * 100,
                "validated_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def exported(
        export_id: str,
        format: str,
        records_count: int,
        file_path: str,
        **kwargs
    ) -> WebhookEventData:
        """Create data exported event"""
        return WebhookEventData(
            event_type=EventType.DATA_EXPORTED.value,
            data={
                "export_id": export_id,
                "format": format,
                "records_count": records_count,
                "file_path": file_path,
                "exported_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )

class SystemEventBuilder:
    """Builder for system-related events"""
    
    @staticmethod
    def alert(
        alert_type: str,
        message: str,
        severity: EventSeverity = EventSeverity.WARNING,
        **kwargs
    ) -> WebhookEventData:
        """Create system alert event"""
        return WebhookEventData(
            event_type=EventType.SYSTEM_ALERT.value,
            severity=severity,
            data={
                "alert_type": alert_type,
                "message": message,
                "severity": severity.value,
                **kwargs
            }
        )
    
    @staticmethod
    def error(
        error_type: str,
        error_message: str,
        component: str,
        **kwargs
    ) -> WebhookEventData:
        """Create system error event"""
        return WebhookEventData(
            event_type=EventType.SYSTEM_ERROR.value,
            severity=EventSeverity.ERROR,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "component": component,
                "occurred_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def health_check(
        component: str,
        status: str,
        metrics: Dict[str, Any],
        **kwargs
    ) -> WebhookEventData:
        """Create health check event"""
        severity = EventSeverity.INFO if status == "healthy" else EventSeverity.WARNING
        
        return WebhookEventData(
            event_type=EventType.SYSTEM_HEALTH_CHECK.value,
            severity=severity,
            data={
                "component": component,
                "status": status,
                "metrics": metrics,
                "checked_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )

class CrawlerEventBuilder:
    """Builder for crawler-related events"""
    
    @staticmethod
    def started(
        crawl_id: str,
        target_urls: List[str],
        template_name: str,
        **kwargs
    ) -> WebhookEventData:
        """Create crawler started event"""
        return WebhookEventData(
            event_type=EventType.CRAWLER_STARTED.value,
            data={
                "crawl_id": crawl_id,
                "target_urls": target_urls,
                "template_name": template_name,
                "url_count": len(target_urls),
                "started_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def completed(
        crawl_id: str,
        urls_processed: int,
        urls_successful: int,
        urls_failed: int,
        duration: float,
        **kwargs
    ) -> WebhookEventData:
        """Create crawler completed event"""
        return WebhookEventData(
            event_type=EventType.CRAWLER_COMPLETED.value,
            data={
                "crawl_id": crawl_id,
                "urls_processed": urls_processed,
                "urls_successful": urls_successful,
                "urls_failed": urls_failed,
                "success_rate": urls_successful / max(1, urls_processed) * 100,
                "duration": duration,
                "completed_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )
    
    @staticmethod
    def sitemap_generated(
        crawl_id: str,
        sitemap_url: str,
        url_count: int,
        **kwargs
    ) -> WebhookEventData:
        """Create sitemap generated event"""
        return WebhookEventData(
            event_type=EventType.CRAWLER_SITEMAP_GENERATED.value,
            data={
                "crawl_id": crawl_id,
                "sitemap_url": sitemap_url,
                "url_count": url_count,
                "generated_at": datetime.utcnow().isoformat(),
                **kwargs
            }
        )

class WebhookEventDispatcher:
    """
    Event dispatcher for webhook notifications
    
    Manages event creation, queuing, and delivery.
    """
    
    def __init__(self):
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_handlers: List[Callable] = []
        self.event_history: List[WebhookEventData] = []
        
        # Statistics
        self.total_events = 0
        self.dispatched_events = 0
        self.failed_events = 0
    
    def add_handler(self, handler: Callable[[WebhookEventData], None]):
        """Add an event handler"""
        self.event_handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """Remove an event handler"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    async def dispatch_event(self, event: WebhookEventData, immediate: bool = True):
        """Dispatch an event to all handlers"""
        try:
            # Add to history
            self.event_history.append(event)
            self.total_events += 1
            
            # Keep only recent events in memory
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-1000:]
            
            logger.info(f"Dispatching event: {event.event_type} (ID: {event.event_id})")
            
            if immediate:
                await self._process_event(event)
            else:
                await self.event_queue.put(event)
                
        except Exception as e:
            logger.error(f"Failed to dispatch event {event.event_id}: {e}")
            self.failed_events += 1
    
    async def _process_event(self, event: WebhookEventData):
        """Process an event with all handlers"""
        try:
            # Call all handlers
            tasks = []
            for handler in self.event_handlers:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Run sync handler in executor
                    task = asyncio.get_event_loop().run_in_executor(None, handler, event)
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log any errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        handler_name = getattr(self.event_handlers[i], '__name__', 'unknown')
                        logger.error(f"Handler {handler_name} failed for event {event.event_id}: {result}")
            
            self.dispatched_events += 1
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            self.failed_events += 1
    
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
            
            logger.info(f"Processing {len(events)} queued events")
            
            # Process events
            for event in events:
                await self._process_event(event)
                
        except Exception as e:
            logger.error(f"Error processing event queue: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event dispatcher statistics"""
        return {
            "total_events": self.total_events,
            "dispatched_events": self.dispatched_events,
            "failed_events": self.failed_events,
            "success_rate": (
                self.dispatched_events / max(1, self.total_events) * 100
            ),
            "registered_handlers": len(self.event_handlers),
            "queue_size": self.event_queue.qsize(),
            "recent_events": len(self.event_history)
        }
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events"""
        recent_events = self.event_history[-limit:]
        return [event.to_dict() for event in recent_events]


# Global event dispatcher instance
event_dispatcher = WebhookEventDispatcher()

# Convenience functions for common events

async def emit_job_started(job_id: str, job_type: str, **kwargs):
    """Emit job started event"""
    event = JobEventBuilder.started(job_id, job_type, **kwargs)
    await event_dispatcher.dispatch_event(event)

async def emit_job_completed(job_id: str, job_type: str, duration: float, **kwargs):
    """Emit job completed event"""
    event = JobEventBuilder.completed(job_id, job_type, duration, **kwargs)
    await event_dispatcher.dispatch_event(event)

async def emit_job_failed(job_id: str, job_type: str, error: str, **kwargs):
    """Emit job failed event"""
    event = JobEventBuilder.failed(job_id, job_type, error, **kwargs)
    await event_dispatcher.dispatch_event(event)

async def emit_data_extracted(extraction_id: str, template_name: str, records_count: int, source_url: str, **kwargs):
    """Emit data extracted event"""
    event = DataEventBuilder.extracted(extraction_id, template_name, records_count, source_url, **kwargs)
    await event_dispatcher.dispatch_event(event)

async def emit_system_alert(alert_type: str, message: str, severity: EventSeverity = EventSeverity.WARNING, **kwargs):
    """Emit system alert event"""
    event = SystemEventBuilder.alert(alert_type, message, severity, **kwargs)
    await event_dispatcher.dispatch_event(event)

async def emit_crawler_started(crawl_id: str, target_urls: List[str], template_name: str, **kwargs):
    """Emit crawler started event"""
    event = CrawlerEventBuilder.started(crawl_id, target_urls, template_name, **kwargs)
    await event_dispatcher.dispatch_event(event)

# Legacy compatibility functions for existing code

def job_completed_event(job_id: str, job_type: str, counts: Dict[str, int], export: list, tags: list) -> WebhookEventData:
    """Legacy compatibility function for job completed events"""
    return JobEventBuilder.completed(
        job_id=job_id,
        job_type=job_type,
        duration=0.0,  # Default duration for legacy compatibility
        results={
            "counts": counts,
            "export": export,
            "tags": tags
        }
    )

def template_drift_event(template_id: str, version: str, domain: str, validity: float, failed_fields: list) -> WebhookEventData:
    """Legacy compatibility function for template drift events"""
    return WebhookEventData(
        event_type=EventType.TEMPLATE_DRIFT.value,
        severity=EventSeverity.WARNING,
        data={
            "template_id": template_id,
            "version": version,
            "domain": domain,
            "min_validity_required": 0.90,
            "observed_validity": validity,
            "failed_fields": failed_fields,
            "action": "review_selectors"
        }
    )

def banrate_spike_event(domain: str, current_rate: float, threshold: float) -> WebhookEventData:
    """Legacy compatibility function for ban rate spike events"""
    return WebhookEventData(
        event_type=EventType.BANRATE_SPIKE.value,
        severity=EventSeverity.WARNING,
        data={
            "domain": domain,
            "current_rate": current_rate,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def quota_near_limit_event(tenant_id: str, quota_type: str, current_usage: float, limit: float) -> WebhookEventData:
    """Legacy compatibility function for quota limit events"""
    return WebhookEventData(
        event_type=EventType.QUOTA_LIMIT.value,
        severity=EventSeverity.WARNING,
        data={
            "tenant_id": tenant_id,
            "quota_type": quota_type,
            "current_usage": current_usage,
            "limit": limit,
            "percentage_used": (current_usage / limit) * 100 if limit > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def export_ready_event(export_id: str, user_id: str, file_name: str, download_url: str) -> WebhookEventData:
    """Legacy compatibility function for export ready events"""
    return WebhookEventData(
        event_type=EventType.DATA_EXPORTED.value,
        severity=EventSeverity.INFO,
        data={
            "export_id": export_id,
            "user_id": user_id,
            "file_name": file_name,
            "download_url": download_url,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    )