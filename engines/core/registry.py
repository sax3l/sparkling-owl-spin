"""
Unified Service Registry for Sparkling Owl Spin
Sammanfogad registry från core, agents och tools
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Set
from collections import defaultdict
from .base_classes import BaseService, BaseAgent, BaseEngine, ServiceStatus, ServiceInfo
import weakref
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """
    Unified service registry for managing all services, agents, and engines
    Sammanfogad från core/registry.py, agents/registry.py och tools/registry.py
    """
    
    def __init__(self):
        self._services: Dict[str, BaseService] = {}
        self._agents: Dict[str, BaseAgent] = {}
        self._engines: Dict[str, BaseEngine] = {}
        self._service_types: Dict[str, Type[BaseService]] = {}
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._startup_order: List[str] = []
        self._shutdown_order: List[str] = []
        self._health_monitoring = True
        self._lock = asyncio.Lock()
        
    async def register_service(self, service: BaseService, dependencies: List[str] = None) -> bool:
        """Register a service in the registry"""
        async with self._lock:
            service_name = service.name
            
            if service_name in self._services:
                logger.warning(f"Service {service_name} already registered, updating...")
                
            self._services[service_name] = service
            self._service_types[service_name] = type(service)
            
            # Handle dependencies
            if dependencies:
                self._dependencies[service_name] = set(dependencies)
                service.dependencies.extend(dependencies)
                
            # Categorize service
            if isinstance(service, BaseAgent):
                self._agents[service_name] = service
                logger.info(f"Registered agent: {service_name} with capabilities: {service.capabilities}")
            elif isinstance(service, BaseEngine):
                self._engines[service_name] = service
                logger.info(f"Registered engine: {service_name} of type: {service.engine_type}")
            else:
                logger.info(f"Registered service: {service_name}")
                
            await self._update_startup_order()
            return True
            
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service"""
        async with self._lock:
            if service_name not in self._services:
                logger.warning(f"Service {service_name} not found for unregistration")
                return False
                
            service = self._services[service_name]
            
            # Stop service if running
            if service.status == ServiceStatus.RUNNING:
                await service.stop()
                
            # Remove from all registries
            del self._services[service_name]
            self._service_types.pop(service_name, None)
            self._dependencies.pop(service_name, None)
            self._agents.pop(service_name, None)
            self._engines.pop(service_name, None)
            
            # Update startup order
            await self._update_startup_order()
            
            logger.info(f"Unregistered service: {service_name}")
            return True
            
    async def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return self._services.get(service_name)
        
    async def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self._agents.get(agent_name)
        
    async def get_engine(self, engine_name: str) -> Optional[BaseEngine]:
        """Get an engine by name"""
        return self._engines.get(engine_name)
        
    async def get_services_by_type(self, service_type: Type[BaseService]) -> List[BaseService]:
        """Get all services of a specific type"""
        return [service for service in self._services.values() 
                if isinstance(service, service_type)]
                
    async def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Get agents that have a specific capability"""
        return [agent for agent in self._agents.values() 
                if capability in agent.capabilities]
                
    async def get_engines_by_type(self, engine_type: str) -> List[BaseEngine]:
        """Get engines of a specific type"""
        return [engine for engine in self._engines.values() 
                if engine.engine_type == engine_type]
                
    async def start_all_services(self) -> Dict[str, bool]:
        """Start all services in dependency order"""
        results = {}
        
        for service_name in self._startup_order:
            service = self._services.get(service_name)
            if service:
                try:
                    logger.info(f"Starting service: {service_name}")
                    result = await service.start()
                    results[service_name] = result
                    if not result:
                        logger.error(f"Failed to start service: {service_name}")
                        # Continue with other services
                except Exception as e:
                    logger.error(f"Exception starting service {service_name}: {e}")
                    results[service_name] = False
                    
        return results
        
    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all services in reverse dependency order"""
        results = {}
        
        for service_name in reversed(self._shutdown_order):
            service = self._services.get(service_name)
            if service and service.status == ServiceStatus.RUNNING:
                try:
                    logger.info(f"Stopping service: {service_name}")
                    result = await service.stop()
                    results[service_name] = result
                except Exception as e:
                    logger.error(f"Exception stopping service {service_name}: {e}")
                    results[service_name] = False
                    
        return results
        
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all services"""
        health_results = {}
        
        for service_name, service in self._services.items():
            try:
                health = await service.health_check()
                health_results[service_name] = {
                    'status': 'healthy',
                    'details': health,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_results[service_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        return health_results
        
    async def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get detailed service information"""
        service = self._services.get(service_name)
        if service:
            return await service.get_info()
        return None
        
    async def get_all_services_info(self) -> Dict[str, ServiceInfo]:
        """Get information for all services"""
        info = {}
        for service_name, service in self._services.items():
            try:
                info[service_name] = await service.get_info()
            except Exception as e:
                logger.error(f"Failed to get info for service {service_name}: {e}")
                
        return info
        
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        running_services = sum(1 for s in self._services.values() 
                             if s.status == ServiceStatus.RUNNING)
        
        return {
            'total_services': len(self._services),
            'total_agents': len(self._agents),
            'total_engines': len(self._engines),
            'running_services': running_services,
            'startup_order': self._startup_order.copy(),
            'dependencies': dict(self._dependencies),
            'health_monitoring': self._health_monitoring
        }
        
    async def _update_startup_order(self):
        """Update the startup order based on dependencies"""
        # Topological sort for dependency resolution
        def topological_sort(services, dependencies):
            in_degree = {service: 0 for service in services}
            
            # Calculate in-degrees
            for service in services:
                for dep in dependencies.get(service, set()):
                    if dep in in_degree:
                        in_degree[service] += 1
                        
            # Process services with no dependencies first
            queue = [service for service, degree in in_degree.items() if degree == 0]
            result = []
            
            while queue:
                service = queue.pop(0)
                result.append(service)
                
                # Update in-degrees for dependent services
                for dependent in services:
                    if service in dependencies.get(dependent, set()):
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)
                            
            return result
            
        self._startup_order = topological_sort(
            list(self._services.keys()), 
            self._dependencies
        )
        self._shutdown_order = self._startup_order.copy()
        
    async def find_service_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Find the first available agent with a specific capability"""
        for agent in self._agents.values():
            if (capability in agent.capabilities and 
                agent.status == ServiceStatus.RUNNING):
                return agent
        return None
        
    async def find_engine_by_type_and_availability(self, engine_type: str) -> Optional[BaseEngine]:
        """Find the first available engine of a specific type"""
        for engine in self._engines.values():
            if (engine.engine_type == engine_type and 
                engine.is_available and 
                engine.status == ServiceStatus.RUNNING):
                return engine
        return None
        
    async def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the service dependency graph"""
        return {service: list(deps) for service, deps in self._dependencies.items()}
        
    async def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate that all dependencies are satisfied"""
        missing_deps = {}
        
        for service_name, deps in self._dependencies.items():
            missing = [dep for dep in deps if dep not in self._services]
            if missing:
                missing_deps[service_name] = missing
                
        return missing_deps

# Global registry instance
_global_registry: Optional[ServiceRegistry] = None

async def get_registry() -> ServiceRegistry:
    """Get the global service registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ServiceRegistry()
    return _global_registry

async def register_service(service: BaseService, dependencies: List[str] = None) -> bool:
    """Convenience function to register a service"""
    registry = await get_registry()
    return await registry.register_service(service, dependencies)

async def get_service(service_name: str) -> Optional[BaseService]:
    """Convenience function to get a service"""
    registry = await get_registry()
    return await registry.get_service(service_name)

async def get_agent(agent_name: str) -> Optional[BaseAgent]:
    """Convenience function to get an agent"""
    registry = await get_registry()
    return await registry.get_agent(agent_name)

async def get_engine(engine_name: str) -> Optional[BaseEngine]:
    """Convenience function to get an engine"""
    registry = await get_registry()
    return await registry.get_engine(engine_name)
