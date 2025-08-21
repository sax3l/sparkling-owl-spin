"""
Webhook System
=============

Comprehensive webhook system for the ECaDP platform.

This module provides:
- WebhookClient: For sending webhook notifications
- WebhookHandler: For receiving and processing webhook events
- WebhookEventData: Event data structures
- Event builders and dispatchers
"""

from .client import WebhookClient, WebhookManager, send_job_notification, send_system_alert
from .handler import WebhookHandler, WebhookValidator, WebhookResponse, create_webhook_handler
from .events import (
    EventType,
    EventSeverity,
    WebhookEventData,
    WebhookEventDispatcher,
    JobEventBuilder,
    DataEventBuilder,
    SystemEventBuilder,
    CrawlerEventBuilder,
    event_dispatcher,
    # Convenience functions
    emit_job_started,
    emit_job_completed,
    emit_job_failed,
    emit_data_extracted,
    emit_system_alert,
    emit_crawler_started,
    # Legacy compatibility functions
    job_completed_event,
    template_drift_event,
    banrate_spike_event,
    quota_near_limit_event,
    export_ready_event
)

__all__ = [
    # Client components
    "WebhookClient",
    "WebhookManager",
    "send_job_notification",
    "send_system_alert",
    
    # Handler components
    "WebhookHandler",
    "WebhookValidator",
    "WebhookResponse",
    "create_webhook_handler",
    
    # Event system
    "EventType",
    "EventSeverity",
    "WebhookEventData",
    "WebhookEventDispatcher",
    "event_dispatcher",
    
    # Event builders
    "JobEventBuilder",
    "DataEventBuilder",
    "SystemEventBuilder",
    "CrawlerEventBuilder",
    
    # Convenience functions
    "emit_job_started",
    "emit_job_completed",
    "emit_job_failed",
    "emit_data_extracted",
    "emit_system_alert",
    "emit_crawler_started",
    
    # Legacy compatibility
    "job_completed_event",
    "template_drift_event",
    "banrate_spike_event",
    "quota_near_limit_event",
    "export_ready_event"
]
