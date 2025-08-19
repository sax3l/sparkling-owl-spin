from datetime import datetime, timezone
from typing import Dict, Any
from .models import WebhookEvent

def job_completed_event(job_id: str, job_type: str, counts: Dict[str, int], export: list, tags: list) -> WebhookEvent:
    return WebhookEvent(
        event_type="job.completed",
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
        event_type="template.drift_detected",
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
        event_type="banrate.spike",
        data={
            "domain": domain,
            "current_rate": current_rate,
            "threshold": threshold,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )