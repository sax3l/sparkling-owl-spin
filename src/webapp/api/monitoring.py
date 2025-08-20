from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from src.database.manager import get_db
from src.webapp.security import authorize_with_scopes, get_current_tenant_id
from src.anti_bot.policy_manager import PolicyManager # Assuming PolicyManager can provide stats
from src.database.models import DataQualityMetric # Import DataQualityMetric model
import logging
import os
import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@router.get("/monitoring/proxy-stats", dependencies=[Depends(authorize_with_scopes(["monitoring:read", "admin:*"]))])
async def get_proxy_stats(
    db: Session = Depends(get_db) # db is not directly used here, but kept for consistency with other endpoints
) -> Dict[str, Any]:
    """
    Retrieves current statistics about the proxy pool and anti-bot policies.
    """
    logger.info("Fetching proxy statistics.")
    try:
        policy_manager = PolicyManager(redis_url=REDIS_URL)
        # This is a simplified representation. In a real system, PolicyManager.stats()
        # would aggregate more detailed metrics from the proxy pool.
        stats = {
            "active_proxies": 0, # Placeholder
            "healthy_proxies": 0, # Placeholder
            "unhealthy_proxies": 0, # Placeholder
            "domains_in_backoff": 0, # Placeholder
            "total_requests_last_hour": 0, # Placeholder
            "average_latency_ms": 0, # Placeholder
            "policy_manager_status": "active",
            "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
        }
        # You would ideally fetch real stats from PolicyManager or a dedicated ProxyPoolManager
        # For now, we'll just return placeholders and a status.
        
        # Example of how you might get some real data if PolicyManager exposed it:
        # policy_stats = policy_manager.get_all_domain_policies()
        # stats["domains_in_backoff"] = sum(1 for p in policy_stats.values() if p.backoff_until > time.time())

        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve proxy stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve proxy statistics."
        )

@router.post("/data-quality-metrics", status_code=201, dependencies=[Depends(authorize_with_scopes(["data_quality:write", "admin:*"]))])
async def submit_data_quality_metrics(
    metrics: List[Dict[str, Any]], # Expecting a list of metric dictionaries
    tenant_id: str = Depends(get_current_tenant_id), # Assuming tenant_id is passed as string or UUID
    db: Session = Depends(get_db)
):
    """
    Submits data quality metrics for entities.
    This endpoint allows external systems (e.g., ETL pipelines) to report DQ results.
    """
    logger.info(f"Received {len(metrics)} data quality metrics for tenant {tenant_id}.", extra={"tenant_id": str(tenant_id)})
    
    new_metrics = []
    for metric_data in metrics:
        try:
            # Ensure required fields are present and types are correct
            # Note: DataQualityMetric model does not have tenant_id, but it should for multi-tenancy.
            # For now, we'll just log the tenant_id and assume the metric applies to the tenant's data.
            # A proper implementation would add tenant_id to DataQualityMetric table.
            new_metric = DataQualityMetric(
                entity_type=metric_data["entity_type"],
                entity_id=metric_data["entity_id"],
                field_name=metric_data.get("field_name"),
                completeness=metric_data.get("completeness"),
                validity=metric_data.get("validity"),
                consistency=metric_data.get("consistency"),
                measured_at=datetime.datetime.utcnow()
            )
            new_metrics.append(new_metric)
        except KeyError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required field in metric data: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid metric data format: {e}")

    db.add_all(new_metrics)
    db.commit()
    
    logger.info(f"Successfully submitted {len(new_metrics)} data quality metrics.", extra={"tenant_id": str(tenant_id)})
    return {"message": f"Successfully submitted {len(new_metrics)} data quality metrics."}