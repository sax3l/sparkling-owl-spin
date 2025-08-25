#!/usr/bin/env python3
"""
Enhanced AWS IP Rotator Integration for Pyramid Architecture

Provides IP rotation capabilities through AWS API Gateway for anti-detection:
- Multi-region endpoint rotation
- Cost estimation and monitoring
- Session management with automatic rotation
- Production and demo modes
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from shared.models.base import BaseService, ServiceStatus
from shared.utils.helpers import get_logger, generate_uuid, RateLimiter

logger = get_logger(__name__)


class RotationStrategy(Enum):
    """IP rotation strategies"""
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


@dataclass
class AWSEndpoint:
    """AWS API Gateway endpoint configuration"""
    region: str
    gateway_id: str
    deployment_id: str
    endpoint_url: str
    created_at: datetime
    is_active: bool = True
    request_count: int = 0
    error_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class RotationConfig:
    """IP rotation configuration"""
    strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    rotation_interval: int = 100  # Requests before rotation
    max_retries: int = 3
    timeout: int = 30
    rate_limit: int = 10  # Requests per second per endpoint
    health_check_interval: int = 300  # Seconds


class EnhancedAWSIPRotator(BaseService):
    """Enhanced AWS IP Rotator with pyramid architecture integration"""
    
    def __init__(self, demo_mode: bool = False, config: Optional[RotationConfig] = None):
        super().__init__("aws_ip_rotator", "AWS IP Rotation Service")
        
        self.demo_mode = demo_mode
        self.config = config or RotationConfig()
        self.endpoints: List[AWSEndpoint] = []
        self.current_endpoint_index = 0
        self.request_count = 0
        self.total_requests = 0
        self.rate_limiter = RateLimiter(calls=self.config.rate_limit, period=1.0)
        
        # AWS regions for global coverage
        self.regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
            'ap-south-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 
            'ap-southeast-2', 'ca-central-1', 'sa-east-1'
        ]
        
        if demo_mode:
            logger.info("🎭 AWS IP Rotator initialized in DEMO mode")
        else:
            logger.info("🚀 AWS IP Rotator initialized for production")
    
    async def start(self) -> None:
        """Start the AWS IP Rotator service"""
        self.status = ServiceStatus.STARTING
        logger.info("Starting AWS IP Rotator service...")
        
        try:
            if not self.demo_mode:
                # Initialize AWS clients
                await self._initialize_aws_clients()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor_loop())
            
            self.status = ServiceStatus.RUNNING
            logger.info("✅ AWS IP Rotator service started successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            logger.error(f"❌ Failed to start AWS IP Rotator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the AWS IP Rotator service"""
        self.status = ServiceStatus.STOPPING
        logger.info("Stopping AWS IP Rotator service...")
        
        try:
            # Cleanup all endpoints
            await self.cleanup_all()
            
            self.status = ServiceStatus.STOPPED
            logger.info("✅ AWS IP Rotator service stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            logger.error(f"❌ Failed to stop AWS IP Rotator: {e}")
            raise
    
    async def _initialize_aws_clients(self) -> None:
        """Initialize AWS clients (production mode only)"""
        try:
            import boto3
            from botocore.config import Config
            
            # Initialize AWS clients for each region
            self.aws_clients = {}
            
            config = Config(
                region_name='us-east-1',
                retries={'max_attempts': 3},
                max_pool_connections=50
            )
            
            for region in self.regions:
                self.aws_clients[region] = boto3.client(
                    'apigateway',
                    region_name=region,
                    config=config
                )
            
            logger.info(f"✅ Initialized AWS clients for {len(self.regions)} regions")
            
        except ImportError:
            logger.warning("⚠️ boto3 not available, running in demo mode")
            self.demo_mode = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS clients: {e}")
            raise
    
    async def create_endpoints(self, regions: List[str], count: int = 1) -> List[AWSEndpoint]:
        """Create API Gateway endpoints in specified regions"""
        endpoints = []
        
        for region in regions:
            for i in range(count):
                if self.demo_mode:
                    endpoint = self._create_demo_endpoint(region, i)
                else:
                    endpoint = await self._create_real_endpoint(region)
                
                endpoints.append(endpoint)
                self.endpoints.append(endpoint)
        
        logger.info(f"✅ Created {len(endpoints)} endpoints across {len(regions)} regions")
        return endpoints
    
    def _create_demo_endpoint(self, region: str, index: int) -> AWSEndpoint:
        """Create a demo endpoint (no real AWS resources)"""
        gateway_id = f"demo-gw-{generate_uuid()[:8]}"
        deployment_id = f"demo-dep-{generate_uuid()[:8]}"
        
        return AWSEndpoint(
            region=region,
            gateway_id=gateway_id,
            deployment_id=deployment_id,
            endpoint_url=f"https://{gateway_id}.execute-api.{region}.amazonaws.com/prod",
            created_at=datetime.now()
        )
    
    async def _create_real_endpoint(self, region: str) -> AWSEndpoint:
        """Create a real AWS API Gateway endpoint"""
        try:
            client = self.aws_clients[region]
            
            # Create API Gateway
            api_response = await asyncio.to_thread(
                client.create_rest_api,
                name=f'ip-rotator-{generate_uuid()[:8]}',
                description='IP Rotation Gateway for Web Scraping',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            
            gateway_id = api_response['id']
            
            # Get root resource
            resources_response = await asyncio.to_thread(
                client.get_resources,
                restApiId=gateway_id
            )
            
            root_resource_id = next(
                resource['id'] for resource in resources_response['items']
                if resource['path'] == '/'
            )
            
            # Create proxy resource
            proxy_resource = await asyncio.to_thread(
                client.create_resource,
                restApiId=gateway_id,
                parentId=root_resource_id,
                pathPart='{proxy+}'
            )
            
            # Create ANY method
            await asyncio.to_thread(
                client.put_method,
                restApiId=gateway_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                authorizationType='NONE',
                requestParameters={'method.request.path.proxy': True}
            )
            
            # Create integration
            await asyncio.to_thread(
                client.put_integration,
                restApiId=gateway_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                type='HTTP_PROXY',
                integrationHttpMethod='ANY',
                uri='http://httpbin.org/{proxy}',
                requestParameters={'integration.request.path.proxy': 'method.request.path.proxy'}
            )
            
            # Deploy API
            deployment = await asyncio.to_thread(
                client.create_deployment,
                restApiId=gateway_id,
                stageName='prod'
            )
            
            endpoint_url = f"https://{gateway_id}.execute-api.{region}.amazonaws.com/prod"
            
            return AWSEndpoint(
                region=region,
                gateway_id=gateway_id,
                deployment_id=deployment['id'],
                endpoint_url=endpoint_url,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create endpoint in {region}: {e}")
            raise
    
    async def get_next_endpoint(self) -> AWSEndpoint:
        """Get next endpoint based on rotation strategy"""
        if not self.endpoints:
            raise ValueError("No endpoints available")
        
        active_endpoints = [ep for ep in self.endpoints if ep.is_active]
        
        if not active_endpoints:
            raise ValueError("No active endpoints available")
        
        if self.config.strategy == RotationStrategy.SEQUENTIAL:
            endpoint = active_endpoints[self.current_endpoint_index % len(active_endpoints)]
            self.current_endpoint_index += 1
            
        elif self.config.strategy == RotationStrategy.RANDOM:
            endpoint = random.choice(active_endpoints)
            
        elif self.config.strategy == RotationStrategy.ROUND_ROBIN:
            endpoint = active_endpoints[self.current_endpoint_index % len(active_endpoints)]
            self.current_endpoint_index += 1
            
        elif self.config.strategy == RotationStrategy.WEIGHTED:
            # Weight by inverse of error rate
            weights = []
            for ep in active_endpoints:
                error_rate = ep.error_count / max(ep.request_count, 1)
                weight = 1.0 / (1.0 + error_rate)
                weights.append(weight)
            
            endpoint = random.choices(active_endpoints, weights=weights)[0]
        
        else:
            endpoint = active_endpoints[0]
        
        # Check if rotation is needed
        if self.request_count >= self.config.rotation_interval:
            self.request_count = 0
            logger.debug(f"🔄 Rotating to endpoint: {endpoint.region}")
        
        endpoint.last_used = datetime.now()
        endpoint.request_count += 1
        self.request_count += 1
        self.total_requests += 1
        
        return endpoint
    
    def get_requests_session(self):
        """Get requests session configured for IP rotation"""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            
            # Configure retries
            retry_strategy = Retry(
                total=self.config.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Add custom request method that uses rotation
            original_request = session.request
            
            async def rotated_request(method, url, **kwargs):
                await self.rate_limiter.acquire()
                endpoint = await self.get_next_endpoint()
                
                if self.demo_mode:
                    # In demo mode, just log the rotation
                    logger.debug(f"🎭 DEMO: Would route {method} {url} through {endpoint.endpoint_url}")
                    return original_request(method, url, **kwargs)
                else:
                    # Route through AWS API Gateway
                    proxy_url = f"{endpoint.endpoint_url}/{url.lstrip('/')}"
                    return original_request(method, proxy_url, **kwargs)
            
            session.rotated_request = rotated_request
            return session
            
        except ImportError:
            logger.warning("⚠️ requests library not available")
            return None
    
    async def _health_monitor_loop(self) -> None:
        """Background health monitoring for endpoints"""
        while self.status == ServiceStatus.RUNNING:
            try:
                await self._check_endpoint_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_endpoint_health(self) -> None:
        """Check health of all endpoints"""
        if self.demo_mode:
            logger.debug("🎭 DEMO: Skipping health checks")
            return
        
        for endpoint in self.endpoints:
            try:
                # Simple health check - could be enhanced
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{endpoint.endpoint_url}/health",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        endpoint.is_active = response.status == 200
                        
            except Exception as e:
                logger.warning(f"Health check failed for {endpoint.region}: {e}")
                endpoint.is_active = False
                endpoint.error_count += 1
    
    def estimate_daily_cost(self, requests_per_day: int, active_endpoints: int = 5) -> float:
        """Estimate daily AWS costs"""
        # AWS API Gateway pricing (approximate)
        cost_per_million_requests = 3.50
        cost_per_request = cost_per_million_requests / 1_000_000
        
        # Data transfer costs (approximate)
        data_transfer_per_gb = 0.09
        avg_response_size_kb = 50
        daily_data_gb = (requests_per_day * avg_response_size_kb) / (1024 * 1024)
        
        request_cost = requests_per_day * cost_per_request * active_endpoints
        data_cost = daily_data_gb * data_transfer_per_gb
        
        return request_cost + data_cost
    
    def estimate_monthly_cost(self, requests_per_day: int, active_endpoints: int = 5) -> float:
        """Estimate monthly AWS costs"""
        daily_cost = self.estimate_daily_cost(requests_per_day, active_endpoints)
        return daily_cost * 30
    
    async def cleanup_all(self) -> None:
        """Cleanup all AWS resources"""
        logger.info("🧹 Cleaning up AWS resources...")
        
        for endpoint in self.endpoints:
            await self._cleanup_endpoint(endpoint)
        
        self.endpoints.clear()
        logger.info("✅ Cleanup completed")
    
    async def _cleanup_endpoint(self, endpoint: AWSEndpoint) -> None:
        """Cleanup a specific endpoint"""
        try:
            if self.demo_mode:
                logger.debug(f"🎭 DEMO: Would cleanup {endpoint.gateway_id} in {endpoint.region}")
                return
            
            client = self.aws_clients[endpoint.region]
            
            # Delete API Gateway
            await asyncio.to_thread(
                client.delete_rest_api,
                restApiId=endpoint.gateway_id
            )
            
            logger.info(f"✅ Cleaned up endpoint in {endpoint.region}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup endpoint {endpoint.gateway_id}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rotation statistics"""
        active_endpoints = [ep for ep in self.endpoints if ep.is_active]
        
        return {
            'total_endpoints': len(self.endpoints),
            'active_endpoints': len(active_endpoints),
            'total_requests': self.total_requests,
            'current_strategy': self.config.strategy.value,
            'demo_mode': self.demo_mode,
            'regions': list(set(ep.region for ep in self.endpoints)),
            'endpoint_stats': [
                {
                    'region': ep.region,
                    'requests': ep.request_count,
                    'errors': ep.error_count,
                    'active': ep.is_active,
                    'last_used': ep.last_used.isoformat() if ep.last_used else None
                }
                for ep in self.endpoints
            ]
        }
    
    async def health_check(self):
        """Service health check"""
        from shared.models.base import ServiceHealthCheck
        
        active_endpoints = len([ep for ep in self.endpoints if ep.is_active])
        total_endpoints = len(self.endpoints)
        
        if total_endpoints == 0:
            status = "healthy" if self.demo_mode else "degraded"
            message = "No endpoints created yet"
        elif active_endpoints == 0:
            status = "unhealthy"
            message = "No active endpoints available"
        elif active_endpoints < total_endpoints * 0.5:
            status = "degraded"
            message = f"Only {active_endpoints}/{total_endpoints} endpoints active"
        else:
            status = "healthy"
            message = f"All systems operational ({active_endpoints}/{total_endpoints} endpoints active)"
        
        return ServiceHealthCheck(
            service_id=self.service_id,
            status=status,
            message=message,
            timestamp=datetime.now(),
            details=self.get_statistics()
        )
