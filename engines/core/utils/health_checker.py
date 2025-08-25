#!/usr/bin/env python3
"""
Health Checker - Service health monitoring utilities

Provides health checking capabilities:
- Service health validation
- Health check scheduling
- Health metrics collection
- Alert generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import time

from shared.models.base import ServiceHealthCheck, ServiceStatus


class HealthCheckType(Enum):
    """Types of health checks"""
    HTTP = "http"
    TCP = "tcp"
    CUSTOM = "custom"
    PING = "ping"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health alert representation"""
    service_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    service_id: str
    check_type: HealthCheckType
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    retries: int = 3
    enabled: bool = True
    custom_check: Optional[Callable] = None
    endpoint: Optional[str] = None
    expected_status: int = 200


class ServiceHealthChecker:
    """Advanced health checker for services"""
    
    def __init__(self):
        self._health_checks: Dict[str, HealthCheckConfig] = {}
        self._health_history: Dict[str, List[ServiceHealthCheck]] = {}
        self._alerts: List[HealthAlert] = []
        self._alert_callbacks: List[Callable] = []
        self._running_checks: Dict[str, asyncio.Task] = {}
        self._logger = logging.getLogger(__name__)
        self._is_running = False
    
    def add_health_check(self, config: HealthCheckConfig) -> None:
        """Add a health check configuration"""
        self._health_checks[config.service_id] = config
        self._logger.info(f"Added health check for service: {config.service_id}")
    
    def remove_health_check(self, service_id: str) -> bool:
        """Remove a health check configuration"""
        if service_id in self._health_checks:
            del self._health_checks[service_id]
            
            # Cancel running check
            if service_id in self._running_checks:
                self._running_checks[service_id].cancel()
                del self._running_checks[service_id]
            
            self._logger.info(f"Removed health check for service: {service_id}")
            return True
        
        return False
    
    async def check_service_health(self, service_id: str) -> ServiceHealthCheck:
        """Perform health check for a specific service"""
        config = self._health_checks.get(service_id)
        
        if not config:
            return ServiceHealthCheck(
                service_id=service_id,
                status="unknown",
                message="No health check configuration found",
                timestamp=datetime.now()
            )
        
        if not config.enabled:
            return ServiceHealthCheck(
                service_id=service_id,
                status="disabled",
                message="Health check disabled",
                timestamp=datetime.now()
            )
        
        # Perform the actual health check
        try:
            if config.check_type == HealthCheckType.HTTP:
                result = await self._check_http_health(config)
            elif config.check_type == HealthCheckType.TCP:
                result = await self._check_tcp_health(config)
            elif config.check_type == HealthCheckType.CUSTOM:
                result = await self._check_custom_health(config)
            elif config.check_type == HealthCheckType.PING:
                result = await self._check_ping_health(config)
            else:
                result = ServiceHealthCheck(
                    service_id=service_id,
                    status="unknown",
                    message=f"Unknown health check type: {config.check_type}",
                    timestamp=datetime.now()
                )
            
            # Store in history
            if service_id not in self._health_history:
                self._health_history[service_id] = []
            
            self._health_history[service_id].append(result)
            
            # Keep only last 100 results
            self._health_history[service_id] = self._health_history[service_id][-100:]
            
            # Check for alerts
            self._check_for_alerts(result)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Health check failed for {service_id}: {e}")
            
            error_result = ServiceHealthCheck(
                service_id=service_id,
                status="unhealthy",
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now()
            )
            
            self._check_for_alerts(error_result)
            return error_result
    
    async def _check_http_health(self, config: HealthCheckConfig) -> ServiceHealthCheck:
        """Perform HTTP health check"""
        import aiohttp
        
        if not config.endpoint:
            raise ValueError("HTTP health check requires endpoint")
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(config.endpoint) as response:
                status = "healthy" if response.status == config.expected_status else "unhealthy"
                
                return ServiceHealthCheck(
                    service_id=config.service_id,
                    status=status,
                    message=f"HTTP {response.status}",
                    timestamp=datetime.now(),
                    details={
                        "status_code": response.status,
                        "response_time": time.time(),  # Would need to measure properly
                        "endpoint": config.endpoint
                    }
                )
    
    async def _check_tcp_health(self, config: HealthCheckConfig) -> ServiceHealthCheck:
        """Perform TCP health check"""
        # Extract host and port from endpoint
        if not config.endpoint:
            raise ValueError("TCP health check requires endpoint (host:port)")
        
        host, port = config.endpoint.split(':')
        port = int(port)
        
        try:
            # Try to establish TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=config.timeout
            )
            
            writer.close()
            await writer.wait_closed()
            
            return ServiceHealthCheck(
                service_id=config.service_id,
                status="healthy",
                message="TCP connection successful",
                timestamp=datetime.now(),
                details={
                    "host": host,
                    "port": port
                }
            )
            
        except (asyncio.TimeoutError, ConnectionError, OSError) as e:
            return ServiceHealthCheck(
                service_id=config.service_id,
                status="unhealthy",
                message=f"TCP connection failed: {str(e)}",
                timestamp=datetime.now(),
                details={
                    "host": host,
                    "port": port,
                    "error": str(e)
                }
            )
    
    async def _check_custom_health(self, config: HealthCheckConfig) -> ServiceHealthCheck:
        """Perform custom health check"""
        if not config.custom_check:
            raise ValueError("Custom health check requires custom_check function")
        
        try:
            if asyncio.iscoroutinefunction(config.custom_check):
                result = await config.custom_check(config.service_id)
            else:
                result = config.custom_check(config.service_id)
            
            if isinstance(result, ServiceHealthCheck):
                return result
            elif isinstance(result, dict):
                return ServiceHealthCheck(**result)
            else:
                # Assume boolean result
                status = "healthy" if result else "unhealthy"
                return ServiceHealthCheck(
                    service_id=config.service_id,
                    status=status,
                    message="Custom health check result",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return ServiceHealthCheck(
                service_id=config.service_id,
                status="unhealthy",
                message=f"Custom health check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _check_ping_health(self, config: HealthCheckConfig) -> ServiceHealthCheck:
        """Perform ping health check"""
        import subprocess
        import platform
        
        if not config.endpoint:
            raise ValueError("Ping health check requires endpoint (host)")
        
        # Determine ping command based on OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', config.endpoint]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=config.timeout
            )
            
            status = "healthy" if result.returncode == 0 else "unhealthy"
            
            return ServiceHealthCheck(
                service_id=config.service_id,
                status=status,
                message=f"Ping result: {result.returncode}",
                timestamp=datetime.now(),
                details={
                    "host": config.endpoint,
                    "return_code": result.returncode,
                    "output": result.stdout[:200]  # Limit output
                }
            )
            
        except subprocess.TimeoutExpired:
            return ServiceHealthCheck(
                service_id=config.service_id,
                status="unhealthy",
                message="Ping timeout",
                timestamp=datetime.now(),
                details={
                    "host": config.endpoint,
                    "error": "timeout"
                }
            )
    
    def _check_for_alerts(self, health_check: ServiceHealthCheck) -> None:
        """Check if alert should be generated"""
        service_id = health_check.service_id
        
        # Get recent health checks
        recent_checks = self._health_history.get(service_id, [])[-5:]  # Last 5 checks
        
        # Check for consecutive failures
        if len(recent_checks) >= 3:
            recent_statuses = [check.status for check in recent_checks[-3:]]
            
            if all(status == "unhealthy" for status in recent_statuses):
                # Generate error alert
                self._generate_alert(
                    service_id=service_id,
                    severity=AlertSeverity.ERROR,
                    message=f"Service {service_id} has been unhealthy for 3 consecutive checks"
                )
            elif all(status in ["unhealthy", "degraded"] for status in recent_statuses):
                # Generate warning alert
                self._generate_alert(
                    service_id=service_id,
                    severity=AlertSeverity.WARNING,
                    message=f"Service {service_id} has been degraded/unhealthy"
                )
    
    def _generate_alert(self, service_id: str, severity: AlertSeverity, message: str) -> None:
        """Generate health alert"""
        
        # Check if similar alert already exists
        existing_alert = next(
            (alert for alert in self._alerts 
             if alert.service_id == service_id 
             and alert.severity == severity 
             and not alert.resolved),
            None
        )
        
        if existing_alert:
            return  # Don't duplicate alerts
        
        alert = HealthAlert(
            service_id=service_id,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        
        self._alerts.append(alert)
        self._logger.warning(f"Health alert generated: {alert}")
        
        # Notify alert callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self._logger.error(f"Alert callback error: {e}")
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        self._is_running = True
        self._logger.info("Starting health monitoring")
        
        # Start health check tasks for each configured service
        for service_id, config in self._health_checks.items():
            if config.enabled:
                task = asyncio.create_task(self._monitor_service(service_id))
                self._running_checks[service_id] = task
        
        self._logger.info(f"Started monitoring {len(self._running_checks)} services")
    
    async def stop_monitoring(self) -> None:
        """Stop continuous health monitoring"""
        self._is_running = False
        self._logger.info("Stopping health monitoring")
        
        # Cancel all running checks
        for task in self._running_checks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._running_checks:
            await asyncio.gather(*self._running_checks.values(), return_exceptions=True)
        
        self._running_checks.clear()
        self._logger.info("Health monitoring stopped")
    
    async def _monitor_service(self, service_id: str) -> None:
        """Monitor a specific service continuously"""
        config = self._health_checks[service_id]
        
        while self._is_running and config.enabled:
            try:
                await self.check_service_health(service_id)
                await asyncio.sleep(config.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error monitoring {service_id}: {e}")
                await asyncio.sleep(config.interval)
    
    def get_health_history(self, service_id: str, limit: int = 10) -> List[ServiceHealthCheck]:
        """Get health check history for a service"""
        history = self._health_history.get(service_id, [])
        return history[-limit:] if limit else history
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[HealthAlert]:
        """Get health alerts"""
        if resolved is None:
            return self._alerts.copy()
        
        return [alert for alert in self._alerts if alert.resolved == resolved]
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        if 0 <= alert_id < len(self._alerts):
            self._alerts[alert_id].resolved = True
            self._alerts[alert_id].resolution_time = datetime.now()
            return True
        
        return False
    
    def add_alert_callback(self, callback: Callable[[HealthAlert], None]) -> None:
        """Add callback for alert notifications"""
        self._alert_callbacks.append(callback)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_services = len(self._health_checks)
        monitored_services = len([c for c in self._health_checks.values() if c.enabled])
        
        # Get latest health status for each service
        service_statuses = {}
        for service_id in self._health_checks:
            history = self._health_history.get(service_id, [])
            if history:
                service_statuses[service_id] = history[-1].status
            else:
                service_statuses[service_id] = "unknown"
        
        # Count by status
        status_counts = {}
        for status in service_statuses.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count alerts
        active_alerts = len([a for a in self._alerts if not a.resolved])
        
        return {
            "total_services": total_services,
            "monitored_services": monitored_services,
            "status_counts": status_counts,
            "active_alerts": active_alerts,
            "last_update": datetime.now().isoformat()
        }
