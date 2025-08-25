#!/usr/bin/env python3
"""
Health API - Health monitoring and status endpoints

Provides REST endpoints for:
- Service health checks
- System status monitoring
- Performance metrics
- Service discovery
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import logging

from core.utils.orchestration import ServiceOrchestrator, ServiceRegistry, ServiceHealthChecker
from shared.models.base import ServiceHealthCheck, ServiceStatus

logger = logging.getLogger(__name__)

class HealthAPI:
    """Health monitoring API endpoints"""
    
    def __init__(self, orchestrator: ServiceOrchestrator):
        self.orchestrator = orchestrator
        self.registry = orchestrator.registry
        self.health_checker = orchestrator.health_checker
        self.router = APIRouter(prefix="/health", tags=["health"])
        
        # Register routes
        self.router.add_api_route("/", self.get_system_health, methods=["GET"])
        self.router.add_api_route("/services", self.get_all_services_health, methods=["GET"])
        self.router.add_api_route("/services/{service_id}", self.get_service_health, methods=["GET"])
        self.router.add_api_route("/services/{service_id}/restart", self.restart_service, methods=["POST"])
        self.router.add_api_route("/metrics", self.get_system_metrics, methods=["GET"])
        self.router.add_api_route("/metrics/{service_id}", self.get_service_metrics, methods=["GET"])
        self.router.add_api_route("/status", self.get_service_status, methods=["GET"])
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            health_summary = self.health_checker.get_system_health_summary()
            
            return {
                "status": "success",
                "data": health_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve system health: {str(e)}"
            )
    
    async def get_all_services_health(self) -> Dict[str, Any]:
        """Get health status of all services"""
        try:
            health_results = await self.health_checker.check_all_services()
            
            # Convert to JSON-serializable format
            services_health = {}
            for service_id, health_check in health_results.items():
                services_health[service_id] = {
                    "service_id": health_check.service_id,
                    "status": health_check.status,
                    "message": health_check.message,
                    "timestamp": health_check.timestamp.isoformat(),
                    "details": health_check.details or {}
                }
            
            return {
                "status": "success",
                "data": services_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get all services health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve services health: {str(e)}"
            )
    
    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Get health status of a specific service"""
        try:
            # Check if service exists
            if not self.registry.get_service(service_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{service_id}' not found"
                )
            
            health_check = await self.health_checker.check_service_health(service_id)
            
            return {
                "status": "success",
                "data": {
                    "service_id": health_check.service_id,
                    "status": health_check.status,
                    "message": health_check.message,
                    "timestamp": health_check.timestamp.isoformat(),
                    "details": health_check.details or {}
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get service health for {service_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve service health: {str(e)}"
            )
    
    async def restart_service(self, service_id: str) -> Dict[str, Any]:
        """Restart a specific service"""
        try:
            # Check if service exists
            if not self.registry.get_service(service_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{service_id}' not found"
                )
            
            success = await self.orchestrator.restart_service(service_id)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Service '{service_id}' restarted successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to restart service '{service_id}'"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to restart service {service_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to restart service: {str(e)}"
            )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide performance metrics"""
        try:
            services = self.registry.list_services()
            all_metrics = {}
            
            for service_id in services:
                metrics = self.health_checker.get_service_metrics(service_id)
                if metrics:
                    all_metrics[service_id] = metrics.to_dict()
            
            # Calculate aggregate metrics
            total_requests = sum(m.get('request_count', 0) for m in all_metrics.values())
            total_errors = sum(m.get('error_count', 0) for m in all_metrics.values())
            avg_cpu = sum(m.get('cpu_usage', 0) for m in all_metrics.values()) / len(all_metrics) if all_metrics else 0
            avg_memory = sum(m.get('memory_usage', 0) for m in all_metrics.values()) / len(all_metrics) if all_metrics else 0
            
            return {
                "status": "success",
                "data": {
                    "services": all_metrics,
                    "aggregate": {
                        "total_services": len(services),
                        "total_requests": total_requests,
                        "total_errors": total_errors,
                        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                        "avg_cpu_usage": avg_cpu,
                        "avg_memory_usage": avg_memory
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve system metrics: {str(e)}"
            )
    
    async def get_service_metrics(self, service_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific service"""
        try:
            # Check if service exists
            if not self.registry.get_service(service_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service '{service_id}' not found"
                )
            
            metrics = self.health_checker.get_service_metrics(service_id)
            
            if not metrics:
                return {
                    "status": "success",
                    "data": {
                        "service_id": service_id,
                        "message": "No metrics available for this service"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "status": "success",
                "data": metrics.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get service metrics for {service_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve service metrics: {str(e)}"
            )
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status overview of all services"""
        try:
            service_status = self.orchestrator.get_service_status()
            
            return {
                "status": "success",
                "data": service_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve service status: {str(e)}"
            )


def create_health_router(orchestrator: ServiceOrchestrator) -> APIRouter:
    """Create and return health API router"""
    health_api = HealthAPI(orchestrator)
    return health_api.router
