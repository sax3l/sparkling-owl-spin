"""
Monitoring Service

Comprehensive monitoring and alerting service for ECaDP platform.
Integrates with metrics, health checks, performance monitoring, and alerting.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import deque, defaultdict

from src.settings import get_settings
from src.database.manager import DatabaseManager  
from src.database.models import Job, JobStatus, ExtractedItem, ProxyHealth
from src.services.notification_service import get_notification_service, NotificationType, NotificationContext
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics we monitor."""
    JOB_SUCCESS_RATE = "job_success_rate"
    JOB_DURATION = "job_duration"
    DATA_QUALITY_SCORE = "data_quality_score"
    PROXY_HEALTH = "proxy_health"
    QUEUE_DEPTH = "queue_depth"
    ERROR_RATE = "error_rate"
    SYSTEM_LOAD = "system_load"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"


@dataclass
class MetricThreshold:
    """Threshold configuration for a metric."""
    name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str = "above"  # "above", "below"
    window_minutes: int = 5
    min_samples: int = 3


@dataclass
class Alert:
    """An active alert."""
    id: str
    metric_name: str
    level: AlertLevel
    message: str
    current_value: float
    threshold: float
    first_seen: datetime
    last_seen: datetime
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricCollector:
    """Collects and stores time-series metrics."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.last_collection = {}
    
    def record_metric(self, name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a metric value."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.metrics[name].append((timestamp, value))
        self.last_collection[name] = timestamp
    
    def get_recent_values(self, name: str, window_minutes: int = 5) -> List[float]:
        """Get recent metric values within the specified window."""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        values = []
        
        for timestamp, value in self.metrics[name]:
            if timestamp >= cutoff:
                values.append(value)
        
        return values
    
    def get_metric_stats(self, name: str, window_minutes: int = 5) -> Dict[str, float]:
        """Get statistics for a metric."""
        values = self.get_recent_values(name, window_minutes)
        
        if not values:
            return {}
        
        return {
            "count": len(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0
        }


class HealthChecker:
    """Performs health checks on various system components."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.checks: Dict[str, Callable] = {}
        self.register_default_checks()
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def register_default_checks(self):
        """Register default health checks."""
        self.checks.update({
            "database": self._check_database_health,
            "job_processing": self._check_job_processing_health,
            "proxy_pool": self._check_proxy_health,
            "queue_health": self._check_queue_health,
            "data_quality": self._check_data_quality_health
        })
    
    async def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    "status": "healthy" if result.get("healthy", True) else "unhealthy",
                    "details": result,
                    "checked_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "checked_at": datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            async with self.db_manager.get_session() as session:
                # Simple query to test connectivity
                result = await session.execute("SELECT 1")
                
                # Check for recent activity
                recent_jobs = session.query(Job).filter(
                    Job.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                return {
                    "healthy": True,
                    "recent_jobs": recent_jobs,
                    "connection": "ok"
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_job_processing_health(self) -> Dict[str, Any]:
        """Check job processing health."""
        try:
            async with self.db_manager.get_session() as session:
                # Count jobs by status
                total_jobs = session.query(Job).count()
                running_jobs = session.query(Job).filter(Job.status == JobStatus.RUNNING).count()
                failed_jobs = session.query(Job).filter(
                    Job.status == JobStatus.FAILED,
                    Job.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                success_rate = ((total_jobs - failed_jobs) / max(total_jobs, 1)) * 100
                
                return {
                    "healthy": success_rate >= 80,  # 80% success rate threshold
                    "total_jobs": total_jobs,
                    "running_jobs": running_jobs,
                    "failed_jobs_24h": failed_jobs,
                    "success_rate": success_rate
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_proxy_health(self) -> Dict[str, Any]:
        """Check proxy pool health."""
        try:
            async with self.db_manager.get_session() as session:
                total_proxies = session.query(ProxyHealth).count()
                healthy_proxies = session.query(ProxyHealth).filter(
                    ProxyHealth.health_state == "healthy"
                ).count()
                
                health_ratio = (healthy_proxies / max(total_proxies, 1)) * 100
                
                return {
                    "healthy": health_ratio >= 50,  # At least 50% proxies healthy
                    "total_proxies": total_proxies,
                    "healthy_proxies": healthy_proxies,
                    "health_ratio": health_ratio
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_queue_health(self) -> Dict[str, Any]:
        """Check URL queue health."""
        # This would integrate with Redis to check queue depths
        # For now, return a basic check
        return {
            "healthy": True,
            "queue_depth": 0  # Would be actual queue depth from Redis
        }
    
    async def _check_data_quality_health(self) -> Dict[str, Any]:
        """Check data quality metrics."""
        try:
            async with self.db_manager.get_session() as session:
                # Get recent items with DQ scores
                recent_items = session.query(ExtractedItem).filter(
                    ExtractedItem.created_at >= datetime.utcnow() - timedelta(hours=24),
                    ExtractedItem.dq_status.isnot(None)
                ).all()
                
                if not recent_items:
                    return {
                        "healthy": True,
                        "message": "No recent items with DQ data"
                    }
                
                # Calculate average DQ score (assuming it's stored in dq_status)
                # This would need to be adjusted based on actual DQ score storage
                avg_dq_score = 0.85  # Placeholder
                
                return {
                    "healthy": avg_dq_score >= 0.7,  # 70% quality threshold
                    "avg_dq_score": avg_dq_score,
                    "recent_items": len(recent_items)
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }


class MonitoringService:
    """Main monitoring service that coordinates all monitoring activities."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.notification_service = get_notification_service()
        
        self.metric_collector = MetricCollector()
        self.health_checker = HealthChecker(self.db_manager)
        
        # Active alerts
        self.active_alerts: Dict[str, Alert] = {}
        
        # Thresholds configuration
        self.thresholds = self._load_thresholds()
        
        # Background tasks
        self.monitoring_tasks = []
        
    def _load_thresholds(self) -> List[MetricThreshold]:
        """Load monitoring thresholds from configuration."""
        # This would typically load from config files
        return [
            MetricThreshold(
                name="job_success_rate",
                warning_threshold=85.0,
                critical_threshold=70.0,
                comparison="below",
                window_minutes=10,
                min_samples=5
            ),
            MetricThreshold(
                name="data_quality_score",
                warning_threshold=80.0,
                critical_threshold=60.0,
                comparison="below",
                window_minutes=15,
                min_samples=3
            ),
            MetricThreshold(
                name="proxy_health",
                warning_threshold=60.0,
                critical_threshold=30.0,
                comparison="below",
                window_minutes=5,
                min_samples=2
            ),
            MetricThreshold(
                name="error_rate",
                warning_threshold=5.0,
                critical_threshold=10.0,
                comparison="above",
                window_minutes=5,
                min_samples=3
            )
        ]
    
    async def start_monitoring(self):
        """Start background monitoring tasks."""
        logger.info("Starting monitoring service")
        
        # Schedule periodic health checks
        self.monitoring_tasks.append(
            asyncio.create_task(self._periodic_health_checks())
        )
        
        # Schedule metric collection
        self.monitoring_tasks.append(
            asyncio.create_task(self._periodic_metric_collection())
        )
        
        # Schedule alert evaluation
        self.monitoring_tasks.append(
            asyncio.create_task(self._periodic_alert_evaluation())
        )
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks."""
        logger.info("Stopping monitoring service")
        
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        self.monitoring_tasks.clear()
    
    async def _periodic_health_checks(self):
        """Run health checks periodically."""
        while True:
            try:
                health_results = await self.health_checker.run_all_checks()
                
                # Process health check results
                for check_name, result in health_results.items():
                    if result["status"] == "unhealthy":
                        await self._handle_health_alert(check_name, result)
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health checks: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_metric_collection(self):
        """Collect system metrics periodically."""
        while True:
            try:
                await self._collect_job_metrics()
                await self._collect_proxy_metrics()
                await self._collect_quality_metrics()
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(30)
    
    async def _periodic_alert_evaluation(self):
        """Evaluate alert conditions periodically."""
        while True:
            try:
                await self._evaluate_thresholds()
                await asyncio.sleep(60)  # Evaluate every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error evaluating alerts: {e}")
                await asyncio.sleep(60)
    
    async def _collect_job_metrics(self):
        """Collect job-related metrics."""
        async with self.db_manager.get_session() as session:
            # Job success rate
            total_recent = session.query(Job).filter(
                Job.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            successful_recent = session.query(Job).filter(
                Job.created_at >= datetime.utcnow() - timedelta(hours=1),
                Job.status == JobStatus.COMPLETED
            ).count()
            
            if total_recent > 0:
                success_rate = (successful_recent / total_recent) * 100
                self.metric_collector.record_metric("job_success_rate", success_rate)
            
            # Error rate
            failed_recent = session.query(Job).filter(
                Job.created_at >= datetime.utcnow() - timedelta(hours=1),
                Job.status == JobStatus.FAILED
            ).count()
            
            if total_recent > 0:
                error_rate = (failed_recent / total_recent) * 100
                self.metric_collector.record_metric("error_rate", error_rate)
    
    async def _collect_proxy_metrics(self):
        """Collect proxy-related metrics."""
        async with self.db_manager.get_session() as session:
            total_proxies = session.query(ProxyHealth).count()
            healthy_proxies = session.query(ProxyHealth).filter(
                ProxyHealth.health_state == "healthy"
            ).count()
            
            if total_proxies > 0:
                health_ratio = (healthy_proxies / total_proxies) * 100
                self.metric_collector.record_metric("proxy_health", health_ratio)
    
    async def _collect_quality_metrics(self):
        """Collect data quality metrics."""
        # This would collect actual DQ metrics from the system
        # For now, record a placeholder
        self.metric_collector.record_metric("data_quality_score", 85.0)
    
    async def _evaluate_thresholds(self):
        """Evaluate metric thresholds and trigger alerts."""
        for threshold in self.thresholds:
            values = self.metric_collector.get_recent_values(
                threshold.name, 
                threshold.window_minutes
            )
            
            if len(values) < threshold.min_samples:
                continue
            
            current_value = statistics.mean(values)
            
            # Check thresholds
            if threshold.comparison == "above":
                if current_value >= threshold.critical_threshold:
                    await self._trigger_alert(threshold.name, AlertLevel.CRITICAL, current_value, threshold.critical_threshold)
                elif current_value >= threshold.warning_threshold:
                    await self._trigger_alert(threshold.name, AlertLevel.WARNING, current_value, threshold.warning_threshold)
            else:  # below
                if current_value <= threshold.critical_threshold:
                    await self._trigger_alert(threshold.name, AlertLevel.CRITICAL, current_value, threshold.critical_threshold)
                elif current_value <= threshold.warning_threshold:
                    await self._trigger_alert(threshold.name, AlertLevel.WARNING, current_value, threshold.warning_threshold)
    
    async def _trigger_alert(self, metric_name: str, level: AlertLevel, current_value: float, threshold: float):
        """Trigger an alert."""
        alert_id = f"{metric_name}_{level.value}"
        
        if alert_id in self.active_alerts:
            # Update existing alert
            alert = self.active_alerts[alert_id]
            alert.last_seen = datetime.utcnow()
            alert.current_value = current_value
        else:
            # Create new alert
            alert = Alert(
                id=alert_id,
                metric_name=metric_name,
                level=level,
                message=f"{metric_name} is {current_value:.2f} (threshold: {threshold:.2f})",
                current_value=current_value,
                threshold=threshold,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            self.active_alerts[alert_id] = alert
            
            # Send notification for new alerts
            await self._send_alert_notification(alert)
            
            logger.warning(f"Alert triggered: {alert.message}")
    
    async def _handle_health_alert(self, check_name: str, result: Dict[str, Any]):
        """Handle unhealthy status from health checks."""
        alert_id = f"health_{check_name}"
        
        if alert_id not in self.active_alerts:
            alert = Alert(
                id=alert_id,
                metric_name=f"health_{check_name}",
                level=AlertLevel.ERROR,
                message=f"Health check failed: {check_name} - {result.get('error', 'Unknown error')}",
                current_value=0.0,
                threshold=1.0,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                metadata=result
            )
            self.active_alerts[alert_id] = alert
            
            await self._send_alert_notification(alert)
            
            logger.error(f"Health alert: {alert.message}")
    
    async def _send_alert_notification(self, alert: Alert):
        """Send notification for an alert."""
        context = NotificationContext(
            metadata={
                "alert_id": alert.id,
                "metric_name": alert.metric_name,
                "level": alert.level.value,
                "current_value": alert.current_value,
                "threshold": alert.threshold,
                "message": alert.message
            }
        )
        
        await self.notification_service.send_notification(
            NotificationType.SYSTEM_ALERT,
            context,
            [],  # Channels configured per notification type
            []   # Recipients configured per notification type
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        critical_alerts = [a for a in self.active_alerts.values() if a.level == AlertLevel.CRITICAL and not a.resolved]
        warning_alerts = [a for a in self.active_alerts.values() if a.level == AlertLevel.WARNING and not a.resolved]
        
        if critical_alerts:
            status = "critical"
        elif warning_alerts:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "total_alerts": len(self.active_alerts),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        summary = {}
        
        for metric_name in ["job_success_rate", "error_rate", "proxy_health", "data_quality_score"]:
            stats = self.metric_collector.get_metric_stats(metric_name, 15)  # Last 15 minutes
            if stats:
                summary[metric_name] = stats
        
        return summary


# Global monitoring service instance
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
