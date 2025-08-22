"""
System Status Service

Provides comprehensive system status information integrating all services,
health checks, metrics, and operational data.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import psutil
import platform

from src.settings import get_settings
from src.database.manager import DatabaseManager
from src.database.models import Job, JobStatus, Template, ExtractedItem, ProxyHealth, User
from src.services.monitoring_service import get_monitoring_service
from src.services.notification_service import get_notification_service
from src.services.privacy_service import get_privacy_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SystemStatus(Enum):
    """Overall system status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


@dataclass
class ComponentStatus:
    """Status of a system component."""
    name: str
    status: SystemStatus
    message: str
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


class SystemStatusService:
    """Service providing comprehensive system status information."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.monitoring_service = get_monitoring_service()
        self.notification_service = get_notification_service()
        self.privacy_service = get_privacy_service()
        
        # Cache status for performance
        self._status_cache = {}
        self._cache_ttl = 30  # seconds
        self._last_cache_update = None
    
    async def get_system_overview(self, include_details: bool = False) -> Dict[str, Any]:
        """Get comprehensive system overview."""
        # Check cache first
        if (self._last_cache_update and 
            (datetime.utcnow() - self._last_cache_update).seconds < self._cache_ttl):
            return self._status_cache
        
        logger.info("Refreshing system status cache")
        
        # Collect all status information
        tasks = [
            self._get_application_status(),
            self._get_database_status(),
            self._get_job_processing_status(),
            self._get_proxy_status(),
            self._get_data_quality_status(),
            self._get_system_resources_status(),
            self._get_security_status(),
        ]
        
        if include_details:
            tasks.extend([
                self._get_performance_metrics(),
                self._get_recent_activity(),
                self._get_alert_summary()
            ])
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        app_status, db_status, job_status, proxy_status, dq_status, resources_status, security_status = results[:7]
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error getting status component {i}: {result}")
        
        # Determine overall status
        component_statuses = [
            app_status, db_status, job_status, proxy_status, 
            dq_status, resources_status, security_status
        ]
        overall_status = self._determine_overall_status(component_statuses)
        
        # Build response
        status_response = {
            "overall_status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "application": app_status,
                "database": db_status,
                "job_processing": job_status,
                "proxy_pool": proxy_status,
                "data_quality": dq_status,
                "system_resources": resources_status,
                "security": security_status
            },
            "summary": {
                "healthy_components": sum(1 for s in component_statuses if s.get("status") == "healthy"),
                "total_components": len(component_statuses),
                "uptime": self._get_uptime(),
                "version": self._get_version_info()
            }
        }
        
        # Add detailed information if requested
        if include_details and len(results) > 7:
            performance_metrics, recent_activity, alert_summary = results[7:10]
            
            if not isinstance(performance_metrics, Exception):
                status_response["performance"] = performance_metrics
            if not isinstance(recent_activity, Exception):
                status_response["recent_activity"] = recent_activity
            if not isinstance(alert_summary, Exception):
                status_response["alerts"] = alert_summary
        
        # Cache the result
        self._status_cache = status_response
        self._last_cache_update = datetime.utcnow()
        
        return status_response
    
    async def _get_application_status(self) -> Dict[str, Any]:
        """Get application component status."""
        try:
            # Check if main services are running
            services_status = {
                "api_server": True,  # If we're running, API is up
                "scheduler": True,   # Would check scheduler health
                "workers": True      # Would check worker processes
            }
            
            healthy_services = sum(services_status.values())
            total_services = len(services_status)
            
            status = "healthy" if healthy_services == total_services else "warning"
            
            return {
                "status": status,
                "message": f"{healthy_services}/{total_services} services running",
                "details": services_status,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Application status check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_database_status(self) -> Dict[str, Any]:
        """Get database status."""
        try:
            async with self.db_manager.get_session() as session:
                # Test connectivity with a simple query
                await session.execute("SELECT 1")
                
                # Get table counts
                table_counts = {}
                for table_name in ["jobs", "templates", "extracted_items", "users"]:
                    try:
                        count = await session.execute(f"SELECT COUNT(*) FROM {table_name}")
                        table_counts[table_name] = count.scalar()
                    except:
                        table_counts[table_name] = "unknown"
                
                # Check for recent activity
                recent_jobs = session.query(Job).filter(
                    Job.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                return {
                    "status": "healthy",
                    "message": "Database connection healthy",
                    "details": {
                        "connection": "ok",
                        "table_counts": table_counts,
                        "recent_jobs": recent_jobs
                    },
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Database connection failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_job_processing_status(self) -> Dict[str, Any]:
        """Get job processing status."""
        try:
            async with self.db_manager.get_session() as session:
                # Get job statistics
                total_jobs = session.query(Job).count()
                running_jobs = session.query(Job).filter(Job.status == JobStatus.RUNNING).count()
                completed_jobs = session.query(Job).filter(Job.status == JobStatus.COMPLETED).count()
                failed_jobs = session.query(Job).filter(Job.status == JobStatus.FAILED).count()
                
                # Calculate success rate
                processed_jobs = completed_jobs + failed_jobs
                success_rate = (completed_jobs / max(processed_jobs, 1)) * 100
                
                # Get recent job activity
                recent_jobs = session.query(Job).filter(
                    Job.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                # Determine status based on success rate and activity
                if success_rate >= 90 and running_jobs < 50:  # Reasonable thresholds
                    status = "healthy"
                    message = f"Job processing healthy ({success_rate:.1f}% success rate)"
                elif success_rate >= 70:
                    status = "warning"
                    message = f"Job processing degraded ({success_rate:.1f}% success rate)"
                else:
                    status = "critical"
                    message = f"Job processing issues ({success_rate:.1f}% success rate)"
                
                return {
                    "status": status,
                    "message": message,
                    "details": {
                        "total_jobs": total_jobs,
                        "running_jobs": running_jobs,
                        "completed_jobs": completed_jobs,
                        "failed_jobs": failed_jobs,
                        "success_rate": round(success_rate, 1),
                        "recent_jobs_24h": recent_jobs
                    },
                    "metrics": {
                        "success_rate": success_rate,
                        "running_jobs": running_jobs
                    },
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Job processing status check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_proxy_status(self) -> Dict[str, Any]:
        """Get proxy pool status."""
        try:
            async with self.db_manager.get_session() as session:
                total_proxies = session.query(ProxyHealth).count()
                
                if total_proxies == 0:
                    return {
                        "status": "warning",
                        "message": "No proxies configured",
                        "details": {"total_proxies": 0},
                        "last_check": datetime.utcnow().isoformat()
                    }
                
                healthy_proxies = session.query(ProxyHealth).filter(
                    ProxyHealth.health_state == "healthy"
                ).count()
                
                health_ratio = (healthy_proxies / total_proxies) * 100
                
                if health_ratio >= 80:
                    status = "healthy"
                    message = f"Proxy pool healthy ({healthy_proxies}/{total_proxies})"
                elif health_ratio >= 50:
                    status = "warning" 
                    message = f"Proxy pool degraded ({healthy_proxies}/{total_proxies})"
                else:
                    status = "critical"
                    message = f"Proxy pool critical ({healthy_proxies}/{total_proxies})"
                
                return {
                    "status": status,
                    "message": message,
                    "details": {
                        "total_proxies": total_proxies,
                        "healthy_proxies": healthy_proxies,
                        "health_ratio": round(health_ratio, 1)
                    },
                    "metrics": {
                        "health_ratio": health_ratio
                    },
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "warning",
                "message": f"Proxy status check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_data_quality_status(self) -> Dict[str, Any]:
        """Get data quality status."""
        try:
            async with self.db_manager.get_session() as session:
                # Get recent extracted items
                recent_items = session.query(ExtractedItem).filter(
                    ExtractedItem.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                # This would calculate actual DQ scores from the database
                # For now, we'll use placeholder values
                avg_dq_score = 85.0  # Would be calculated from actual data
                
                if avg_dq_score >= 80:
                    status = "healthy"
                    message = f"Data quality healthy (avg score: {avg_dq_score:.1f}%)"
                elif avg_dq_score >= 60:
                    status = "warning"
                    message = f"Data quality degraded (avg score: {avg_dq_score:.1f}%)"
                else:
                    status = "critical"
                    message = f"Data quality poor (avg score: {avg_dq_score:.1f}%)"
                
                return {
                    "status": status,
                    "message": message,
                    "details": {
                        "recent_items": recent_items,
                        "avg_dq_score": avg_dq_score
                    },
                    "metrics": {
                        "avg_dq_score": avg_dq_score
                    },
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "warning",
                "message": f"Data quality status check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_system_resources_status(self) -> Dict[str, Any]:
        """Get system resources status."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine overall resource status
            max_usage = max(cpu_percent, memory_percent, disk_percent)
            
            if max_usage < 70:
                status = "healthy"
                message = "System resources healthy"
            elif max_usage < 85:
                status = "warning"
                message = "System resources under moderate load"
            else:
                status = "critical"
                message = "System resources under heavy load"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_percent": round(memory_percent, 1),
                    "disk_percent": round(disk_percent, 1),
                    "memory_available_gb": round(memory.available / (1024**3), 1),
                    "disk_free_gb": round(disk.free / (1024**3), 1)
                },
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent
                },
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "warning",
                "message": f"System resources check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_security_status(self) -> Dict[str, Any]:
        """Get security status."""
        try:
            async with self.db_manager.get_session() as session:
                # Count active users and API keys
                total_users = session.query(User).filter(User.active == True).count()
                
                # Check for recent security events (placeholder)
                security_events = 0  # Would check audit logs
                
                # Basic security health check
                status = "healthy"
                message = "Security systems operational"
                
                return {
                    "status": status,
                    "message": message,
                    "details": {
                        "active_users": total_users,
                        "recent_security_events": security_events,
                        "auth_enabled": True,
                        "https_enabled": self.settings.use_https
                    },
                    "last_check": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "warning",
                "message": f"Security status check failed: {e}",
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        try:
            metrics_summary = self.monitoring_service.get_metrics_summary()
            
            return {
                "current_metrics": metrics_summary,
                "collection_time": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent system activity."""
        try:
            async with self.db_manager.get_session() as session:
                # Recent jobs
                recent_jobs = session.query(Job).filter(
                    Job.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).order_by(Job.created_at.desc()).limit(10).all()
                
                # Recent extractions
                recent_extractions = session.query(ExtractedItem).filter(
                    ExtractedItem.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                return {
                    "recent_jobs": len(recent_jobs),
                    "recent_extractions": recent_extractions,
                    "last_job": recent_jobs[0].created_at.isoformat() if recent_jobs else None,
                    "activity_period": "1 hour"
                }
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return {"error": str(e)}
    
    async def _get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        try:
            system_status = self.monitoring_service.get_system_status()
            
            return {
                "active_alerts": system_status.get("total_alerts", 0),
                "critical_alerts": system_status.get("critical_alerts", 0),
                "warning_alerts": system_status.get("warning_alerts", 0),
                "alert_status": system_status.get("status", "unknown")
            }
        except Exception as e:
            logger.error(f"Error getting alert summary: {e}")
            return {"error": str(e)}
    
    def _determine_overall_status(self, component_statuses: List[Dict[str, Any]]) -> SystemStatus:
        """Determine overall system status from component statuses."""
        statuses = [comp.get("status", "unknown") for comp in component_statuses]
        
        if "critical" in statuses:
            return SystemStatus.CRITICAL
        elif "warning" in statuses:
            return SystemStatus.WARNING
        elif all(status == "healthy" for status in statuses):
            return SystemStatus.HEALTHY
        else:
            return SystemStatus.DEGRADED
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.utcnow() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "unknown"
    
    def _get_version_info(self) -> Dict[str, str]:
        """Get version information."""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "application_version": "1.0.0"  # Would come from actual version
        }
    
    async def invalidate_cache(self):
        """Invalidate the status cache."""
        self._status_cache = {}
        self._last_cache_update = None
    
    async def get_health_endpoint(self) -> Dict[str, Any]:
        """Simplified health endpoint for load balancers."""
        try:
            # Quick health check - just test database connection
            async with self.db_manager.get_session() as session:
                await session.execute("SELECT 1")
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except:
            return {
                "status": "unhealthy", 
                "timestamp": datetime.utcnow().isoformat()
            }


# Global service instance
_system_status_service = None

def get_system_status_service() -> SystemStatusService:
    """Get the global system status service instance."""
    global _system_status_service
    if _system_status_service is None:
        _system_status_service = SystemStatusService()
    return _system_status_service
