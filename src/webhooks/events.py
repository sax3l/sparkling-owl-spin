from datetime import datetime, timezone
from typing import Dict, Any
from .models import WebhookEvent, WebhookEventType

def job_completed_event(job_id: str, job_type: str, counts: Dict[str, int], export: list, tags: list) -> WebhookEvent:
    return WebhookEvent(
        event_type=WebhookEventType.JOB_COMPLETED,
        data={
            "job_id": job_id,
            "type": job_type,
            "status": "completed",
            "counts": counts,
            "export": export,
            "tags": tags
        }
    )

def template_drift_event(template_id: str, version: str, domain: str, validity: float, failed_fields: list) -> WebhookEvent:
    return WebhookEvent(
        event_type=WebhookEventType.TEMPLATE_DRIFT,
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

def banrate_spike_event(domain: str, current_rate: float, threshold: float) -> WebhookEvent:
    return WebhookEvent(
        event_type=WebhookEventType.BANRATE_SPIKE,
        data={
            "domain": domain,
            "current_rate": current_rate,
            "threshold": threshold,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def quota_near_limit_event(tenant_id: str, quota_type: str, current_usage: float, limit: float) -> WebhookEvent:
    return WebhookEvent(
        event_type=WebhookEventType.QUOTA_LIMIT,
        data={
            "tenant_id": tenant_id,
            "quota_type": quota_type,
            "current_usage": current_usage,
            "limit": limit,
            "percentage_used": (current_usage / limit) * 100 if limit > 0 else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def export_ready_event(export_id: str, user_id: str, file_name: str, download_url: str) -> WebhookEvent:
    return WebhookEvent(
        event_type=WebhookEventType.EXPORT_READY, # This needs to be added to WebhookEventType enum
        data={
            "export_id": export_id,
            "user_id": user_id,
            "file_name": file_name,
            "download_url": download_url,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )