import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import UserQuota
import logging

logger = logging.getLogger(__name__)

class QuotaManager:
    def __init__(self, db: Session):
        self.db = db

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
            logger.info(f"Quota for tenant {tenant_id}, type {quota_type} is near limit (>80%).")

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