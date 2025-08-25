#!/usr/bin/env python3
"""
Core Orchestration Utilities

Provides orchestration utilities for managing pyramid services:
- Service lifecycle management
- Health monitoring
- Performance metrics
- Service discovery
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from pathlib import Path

from shared.models.base import ServiceStatus, BaseService, ServiceHealthCheck


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    uptime: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_id': self.service_id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'request_count': self.request_count,
            'error_count': self.error_count,
            'avg_response_time': self.avg_response_time,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'uptime': self.uptime
        }


class ServiceRegistry:
    """Registry for managing services in the pyramid architecture"""
    
    def __init__(self):
        self._services: Dict[str, BaseService] = {}
        self._service_dependencies: Dict[str, Set[str]] = {}
        self._service_metadata: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_service(self, 
                        service: BaseService,
                        dependencies: Optional[List[str]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a service with optional dependencies and metadata"""
        
        service_id = service.service_id
        
        if service_id in self._services:
            self._logger.warning(f"Service {service_id} already registered, overwriting")
        
        self._services[service_id] = service
        self._service_dependencies[service_id] = set(dependencies or [])
        self._service_metadata[service_id] = metadata or {}
        
        self._logger.info(f"Registered service: {service_id}")
    
    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        if service_id not in self._services:
            return False
        
        # Remove from all structures
        del self._services[service_id]
        self._service_dependencies.pop(service_id, None)
        self._service_metadata.pop(service_id, None)
        
        # Remove from other services' dependencies
        for deps in self._service_dependencies.values():
            deps.discard(service_id)
        
        self._logger.info(f"Unregistered service: {service_id}")
        return True
    
    def get_service(self, service_id: str) -> Optional[BaseService]:
        """Get service by ID"""
        return self._services.get(service_id)
    
    def list_services(self) -> List[str]:
        """List all registered service IDs"""
        return list(self._services.keys())
    
    def get_dependencies(self, service_id: str) -> Set[str]:
        """Get dependencies for a service"""
        return self._service_dependencies.get(service_id, set())
    
    def get_dependents(self, service_id: str) -> Set[str]:
        """Get services that depend on the given service"""
        dependents = set()
        for sid, deps in self._service_dependencies.items():
            if service_id in deps:
                dependents.add(sid)
        return dependents
    
    def get_startup_order(self) -> List[str]:
        """Get services in dependency-resolved startup order"""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_id: str):
            if service_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {service_id}")
            if service_id in visited:
                return
            
            temp_visited.add(service_id)
            
            # Visit dependencies first
            for dep in self._service_dependencies.get(service_id, set()):
                if dep in self._services:  # Only consider registered services
                    visit(dep)
            
            temp_visited.remove(service_id)
            visited.add(service_id)
            result.append(service_id)
        
        # Visit all services
        for service_id in self._services:
            if service_id not in visited:
                visit(service_id)
        
        return result
    
    def get_shutdown_order(self) -> List[str]:
        """Get services in reverse dependency order for shutdown"""
        return list(reversed(self.get_startup_order()))


class ServiceHealthChecker:
    """Health checker for pyramid services"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._health_cache: Dict[str, ServiceHealthCheck] = {}
        self._metrics: Dict[str, ServiceMetrics] = {}
        self._logger = logging.getLogger(__name__)
    
    async def check_service_health(self, service_id: str) -> ServiceHealthCheck:
        """Check health of a specific service"""
        service = self.registry.get_service(service_id)
        
        if not service:
            return ServiceHealthCheck(
                service_id=service_id,
                status=HealthStatus.UNKNOWN.value,
                message="Service not found",
                timestamp=datetime.now()
            )
        
        try:
            # Call service's health check method
            if hasattr(service, 'health_check'):
                health_result = await service.health_check()
            else:
                # Basic health check based on service status
                if service.status == ServiceStatus.RUNNING:
                    health_result = ServiceHealthCheck(
                        service_id=service_id,
                        status=HealthStatus.HEALTHY.value,
                        message="Service is running",
                        timestamp=datetime.now()
                    )
                else:
                    health_result = ServiceHealthCheck(
                        service_id=service_id,
                        status=HealthStatus.UNHEALTHY.value,
                        message=f"Service status: {service.status.value}",
                        timestamp=datetime.now()
                    )
            
            # Cache result
            self._health_cache[service_id] = health_result
            
            # Update metrics
            if service_id not in self._metrics:
                self._metrics[service_id] = ServiceMetrics(service_id)
            self._metrics[service_id].last_health_check = health_result.timestamp
            
            return health_result
            
        except Exception as e:
            self._logger.error(f"Health check failed for {service_id}: {e}")
            
            error_result = ServiceHealthCheck(
                service_id=service_id,
                status=HealthStatus.UNHEALTHY.value,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now()
            )
            
            self._health_cache[service_id] = error_result
            return error_result
    
    async def check_all_services(self) -> Dict[str, ServiceHealthCheck]:
        """Check health of all registered services"""
        results = {}
        
        for service_id in self.registry.list_services():
            results[service_id] = await self.check_service_health(service_id)
        
        return results
    
    def get_cached_health(self, service_id: str, max_age: int = 60) -> Optional[ServiceHealthCheck]:
        """Get cached health check result if recent enough"""
        if service_id not in self._health_cache:
            return None
        
        health_check = self._health_cache[service_id]
        age = (datetime.now() - health_check.timestamp).total_seconds()
        
        if age <= max_age:
            return health_check
        
        return None
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        services = self.registry.list_services()
        total_services = len(services)
        
        if total_services == 0:
            return {
                'status': 'unknown',
                'total_services': 0,
                'healthy_services': 0,
                'degraded_services': 0,
                'unhealthy_services': 0,
                'unknown_services': 0
            }
        
        health_counts = {
            HealthStatus.HEALTHY.value: 0,
            HealthStatus.DEGRADED.value: 0,
            HealthStatus.UNHEALTHY.value: 0,
            HealthStatus.UNKNOWN.value: 0
        }
        
        for service_id in services:
            cached_health = self.get_cached_health(service_id, max_age=300)  # 5 min cache
            if cached_health:
                health_counts[cached_health.status] += 1
            else:
                health_counts[HealthStatus.UNKNOWN.value] += 1
        
        # Determine overall system status
        if health_counts[HealthStatus.UNHEALTHY.value] > 0:
            overall_status = 'unhealthy'
        elif health_counts[HealthStatus.DEGRADED.value] > 0:
            overall_status = 'degraded'
        elif health_counts[HealthStatus.HEALTHY.value] == total_services:
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        return {
            'status': overall_status,
            'total_services': total_services,
            'healthy_services': health_counts[HealthStatus.HEALTHY.value],
            'degraded_services': health_counts[HealthStatus.DEGRADED.value],
            'unhealthy_services': health_counts[HealthStatus.UNHEALTHY.value],
            'unknown_services': health_counts[HealthStatus.UNKNOWN.value],
            'last_check': datetime.now().isoformat()
        }
    
    def get_service_metrics(self, service_id: str) -> Optional[ServiceMetrics]:
        """Get metrics for a specific service"""
        return self._metrics.get(service_id)
    
    def update_service_metrics(self, service_id: str, **kwargs) -> None:
        """Update metrics for a service"""
        if service_id not in self._metrics:
            self._metrics[service_id] = ServiceMetrics(service_id)
        
        metrics = self._metrics[service_id]
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)


class ServiceOrchestrator:
    """Main orchestrator for managing pyramid services"""
    
    def __init__(self, registry: ServiceRegistry, health_checker: ServiceHealthChecker):
        self.registry = registry
        self.health_checker = health_checker
        self._startup_callbacks: List[Callable] = []
        self._shutdown_callbacks: List[Callable] = []
        self._background_tasks: Set[asyncio.Task] = set()
        self._logger = logging.getLogger(__name__)
        self._is_shutting_down = False
    
    def add_startup_callback(self, callback: Callable) -> None:
        """Add callback to run on startup"""
        self._startup_callbacks.append(callback)
    
    def add_shutdown_callback(self, callback: Callable) -> None:
        """Add callback to run on shutdown"""
        self._shutdown_callbacks.append(callback)
    
    async def startup(self) -> None:
        """Start all services in dependency order"""
        self._logger.info("Starting service orchestrator...")
        
        # Run startup callbacks
        for callback in self._startup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                self._logger.error(f"Startup callback failed: {e}")
        
        # Start services in dependency order
        startup_order = self.registry.get_startup_order()
        
        for service_id in startup_order:
            if self._is_shutting_down:
                break
                
            service = self.registry.get_service(service_id)
            if service:
                try:
                    self._logger.info(f"Starting service: {service_id}")
                    await service.start()
                    self._logger.info(f"Service started: {service_id}")
                except Exception as e:
                    self._logger.error(f"Failed to start service {service_id}: {e}")
                    # Continue with other services for now
        
        # Start background health monitoring
        task = asyncio.create_task(self._health_monitor_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        self._logger.info("Service orchestrator startup complete")
    
    async def shutdown(self) -> None:
        """Stop all services in reverse dependency order"""
        self._logger.info("Shutting down service orchestrator...")
        self._is_shutting_down = True
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Stop services in reverse dependency order
        shutdown_order = self.registry.get_shutdown_order()
        
        for service_id in shutdown_order:
            service = self.registry.get_service(service_id)
            if service:
                try:
                    self._logger.info(f"Stopping service: {service_id}")
                    await service.stop()
                    self._logger.info(f"Service stopped: {service_id}")
                except Exception as e:
                    self._logger.error(f"Failed to stop service {service_id}: {e}")
        
        # Run shutdown callbacks
        for callback in self._shutdown_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                self._logger.error(f"Shutdown callback failed: {e}")
        
        self._logger.info("Service orchestrator shutdown complete")
    
    async def restart_service(self, service_id: str) -> bool:
        """Restart a specific service"""
        service = self.registry.get_service(service_id)
        if not service:
            return False
        
        try:
            self._logger.info(f"Restarting service: {service_id}")
            await service.stop()
            await service.start()
            self._logger.info(f"Service restarted: {service_id}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to restart service {service_id}: {e}")
            return False
    
    async def _health_monitor_loop(self):
        """Background health monitoring loop"""
        while not self._is_shutting_down:
            try:
                await self.health_checker.check_all_services()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        services = {}
        
        for service_id in self.registry.list_services():
            service = self.registry.get_service(service_id)
            health = self.health_checker.get_cached_health(service_id)
            metrics = self.health_checker.get_service_metrics(service_id)
            
            services[service_id] = {
                'status': service.status.value if service else 'unknown',
                'health': health.status if health else 'unknown',
                'last_health_check': health.timestamp.isoformat() if health else None,
                'metrics': metrics.to_dict() if metrics else None,
                'dependencies': list(self.registry.get_dependencies(service_id)),
                'dependents': list(self.registry.get_dependents(service_id))
            }
        
        return services
