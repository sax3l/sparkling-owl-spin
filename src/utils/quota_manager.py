import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.models import UserQuota
from src.webhooks.events import quota_near_limit_event # Assuming this event exists
from src.webhooks.service import WebhookService # Assuming this service exists
import logging

logger = logging.getLogger(__name__)

class QuotaManager:
    def __init__(self, db: Session, webhook_service: WebhookService):
        self.db = db
        self.webhook_service = webhook_service

    async def get_quota(self, tenant_id: str, quota_type: str) -> Optional[UserQuota]:
        """Retrieves the current quota for a tenant and type."""
        return self.db.query(UserQuota).filter(
            UserQuota.tenant_id == tenant_id,
            UserQuota.quota_type == quota_type
        ).first()

    async def increment_quota(self, tenant_id: str, quota_type: str, amount: float = 1.0):
        """Increments the usage of a specific quota."""
        quota = await self.get_quota(tenant_id, quota_type)
        if not quota:
            logger.warning(f"Quota for tenant {tenant_id}, type {quota_type} not found. Cannot increment.")
            return

        quota.current_usage += amount
        quota.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(quota)

        # Check for quota near limit
        if quota.limit > 0 and (quota.current_usage / quota.limit) > 0.8:
            logger.info(f"Quota for tenant {tenant_id}, type {quota_type} is near limit (>80%). Triggering webhook.")
            event = quota_near_limit_event(
                tenant_id=str(tenant_id),
                quota_type=quota_type,
                current_usage=float(quota.current_usage),
                limit=float(quota.limit)
            )
            await self.webhook_service.process_event(event)

    async def reset_quotas(self, tenant_id: Optional[str] = None, quota_type: Optional[str] = None):
        """Resets quotas for a tenant or all tenants."""
        query = self.db.query(UserQuota)
        if tenant_id:
            query = query.filter(UserQuota.tenant_id == tenant_id)
        if quota_type:
            query = query.filter(UserQuota.quota_type == quota_type)
        
        quotas_to_reset = query.all()
        for quota in quotas_to_reset:
            quota.current_usage = 0
            quota.period_start = datetime.datetime.utcnow()
            # Set period_end based on quota_type (e.g., monthly, daily)
            # For simplicity, assuming monthly for now
            quota.period_end = quota.period_start + datetime.timedelta(days=30)
            quota.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        logger.info(f"Quotas reset for tenant {tenant_id or 'all'}, type {quota_type or 'all'}.")

# Add quota_near_limit_event to src/webhooks/events.py
<dyad-write path="src/webhooks/events.py" description="Add quota_near_limit_event to webhook events.">
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