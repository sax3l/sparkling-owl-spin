#!/usr/bin/env python3
"""
AWS IP Rotator Integration - from Ge0rg3/requests-ip-rotator
============================================================

Integrerar AWS API Gateway-baserad IP rotation från requests-ip-rotator
i vårt Ultimate Scraping System för professionell IP management.

Key Features from requests-ip-rotator:
• AWS API Gateway endpoints för IP rotation
• Geografisk distribution via AWS regions
• Automatic X-Forwarded-For header management
• Session persistence och requests integration
• Cost-effective IP rotation without proxy pools

Enhanced with our Ultimate Scraping System:
• Better error handling and monitoring
• Cost tracking och usage optimization
• Integration med vårt proxy management system
• Enhanced geographic targeting
• Performance monitoring och analytics
"""

import asyncio
import requests
import boto3
import botocore.exceptions
import ipaddress
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict, field
from random import choice, randint
import concurrent.futures
from threading import Lock
import aiohttp

from ultimate_configuration_manager import ConfigurationManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maximum IPv4 for random IP generation
MAX_IPV4 = ipaddress.IPv4Address._ALL_ONES

# AWS Region configurations
DEFAULT_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
    "ca-central-1"
]

EXTRA_REGIONS = DEFAULT_REGIONS + [
    "ap-south-1", "ap-northeast-3", "ap-northeast-2",
    "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
    "sa-east-1"
]

ALL_REGIONS = EXTRA_REGIONS + [
    "ap-east-1", "af-south-1", "eu-south-1", "me-south-1",
    "eu-north-1"
]


@dataclass
class AWSEndpoint:
    """Information om en AWS API Gateway endpoint."""
    region: str
    endpoint_url: str
    api_id: str
    created_at: datetime
    status: str = "active"
    request_count: int = 0
    error_count: int = 0
    last_used: Optional[datetime] = None
    average_response_time: float = 0.0
    cost_estimate: float = 0.0


@dataclass
class RotationSession:
    """Information om en IP rotation session."""
    session_id: str
    target_site: str
    endpoints: List[AWSEndpoint] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0
    active: bool = True


class EnhancedAWSIPRotator:
    """
    Enhanced AWS IP Rotator
    =======================
    
    Integrerad version av requests-ip-rotator med förbättringar
    för vårt Ultimate Scraping System.
    
    Features:
    • AWS API Gateway endpoint management
    • Multi-region IP rotation
    • Cost tracking och optimization
    • Session management
    • Performance monitoring
    • Error handling och retry logic
    """
    
    def __init__(self, 
                 site: str,
                 regions: List[str] = None,
                 access_key_id: Optional[str] = None,
                 access_key_secret: Optional[str] = None,
                 config_manager: Optional[ConfigurationManager] = None):
        
        self.config_manager = config_manager or ConfigurationManager()
        
        # Site configuration
        self.site = site.rstrip('/')
        self.api_name = f"{self.site} - Enhanced IP Rotate API"
        
        # AWS credentials
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        
        # Region management
        self.regions = regions or DEFAULT_REGIONS
        self.endpoints: List[AWSEndpoint] = []
        self.active_session: Optional[RotationSession] = None
        
        # Performance tracking
        self.stats = {
            "total_endpoints": 0,
            "active_endpoints": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "last_rotation": None
        }
        
        # Thread safety
        self._lock = Lock()
        
        # Cost tracking (AWS API Gateway pricing)
        self.cost_per_request = 0.0000035  # $3.50 per million requests
        
    async def initialize(self):
        """Initiera IP rotation systemet."""
        
        logger.info("🚀 Initializing Enhanced AWS IP Rotator...")
        logger.info(f"🎯 Target site: {self.site}")
        logger.info(f"🌍 Regions: {len(self.regions)} configured")
        
        # Create endpoints in all regions
        await self._create_endpoints()
        
        # Create rotation session
        self.active_session = RotationSession(
            session_id=f"session_{int(time.time())}",
            target_site=self.site,
            endpoints=self.endpoints.copy()
        )
        
        logger.info(f"✅ Enhanced AWS IP Rotator initialized with {len(self.endpoints)} endpoints")
        
    async def _create_endpoints(self):
        """Skapa API Gateway endpoints i alla regioner."""
        
        logger.info("🏗️  Creating IP rotation endpoints...")
        
        # Create endpoints concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self._create_single_endpoint, region)
                for region in self.regions
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    endpoint = future.result(timeout=60)
                    if endpoint:
                        self.endpoints.append(endpoint)
                        logger.info(f"✅ Created endpoint in {endpoint.region}")
                    
                except Exception as e:
                    logger.warning(f"❌ Failed to create endpoint: {e}")
                    
        self.stats["total_endpoints"] = len(self.endpoints)
        self.stats["active_endpoints"] = len([e for e in self.endpoints if e.status == "active"])
        
    def _create_single_endpoint(self, region: str) -> Optional[AWSEndpoint]:
        """Skapa en enda API Gateway endpoint."""
        
        try:
            # Initialize AWS client
            session = boto3.session.Session()
            awsclient = session.client(
                "apigateway",
                region_name=region,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.access_key_secret
            )
            
            # Check if API already exists
            existing_endpoint = self._check_existing_api(awsclient, region)
            if existing_endpoint:
                return existing_endpoint
                
            # Create new API Gateway
            logger.debug(f"Creating new API Gateway in {region}")
            
            create_api_response = awsclient.create_rest_api(
                name=self.api_name,
                endpointConfiguration={
                    "types": ["REGIONAL"]
                }
            )
            
            api_id = create_api_response["id"]
            
            # Get root resource
            resources_response = awsclient.get_resources(restApiId=api_id)
            root_resource_id = resources_response["items"][0]["id"]
            
            # Create proxy resource
            proxy_resource = awsclient.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart="{proxy+}"
            )
            
            # Set up ANY method for root
            awsclient.put_method(
                restApiId=api_id,
                resourceId=root_resource_id,
                httpMethod="ANY",
                authorizationType="NONE",
                requestParameters={
                    "method.request.header.X-My-X-Forwarded-For": False
                }
            )
            
            # Set up integration for root
            awsclient.put_integration(
                restApiId=api_id,
                resourceId=root_resource_id,
                type="HTTP_PROXY",
                httpMethod="ANY",
                integrationHttpMethod="ANY",
                uri=f"http://{self.site}",
                requestParameters={
                    "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
                }
            )
            
            # Set up proxy method and integration
            awsclient.put_method(
                restApiId=api_id,
                resourceId=proxy_resource["id"],
                httpMethod="ANY",
                authorizationType="NONE",
                requestParameters={
                    "method.request.path.proxy": True,
                    "method.request.header.X-My-X-Forwarded-For": False
                }
            )
            
            awsclient.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource["id"],
                type="HTTP_PROXY",
                httpMethod="ANY",
                integrationHttpMethod="ANY",
                uri=f"http://{self.site}/{{proxy}}",
                requestParameters={
                    "integration.request.path.proxy": "method.request.path.proxy",
                    "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
                }
            )
            
            # Deploy the API
            awsclient.create_deployment(
                restApiId=api_id,
                stageName="ProxyStage"
            )
            
            # Create endpoint object
            endpoint_url = f"{api_id}.execute-api.{region}.amazonaws.com"
            
            endpoint = AWSEndpoint(
                region=region,
                endpoint_url=endpoint_url,
                api_id=api_id,
                created_at=datetime.now(),
                status="active"
            )
            
            return endpoint
            
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "UnrecognizedClientException":
                logger.debug(f"Region {region} requires manual enabling")
            else:
                logger.warning(f"AWS client error in {region}: {e}")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to create endpoint in {region}: {e}")
            return None
            
    def _check_existing_api(self, awsclient, region: str) -> Optional[AWSEndpoint]:
        """Kolla om API Gateway redan existerar."""
        
        try:
            apis = awsclient.get_rest_apis()
            
            for api in apis["items"]:
                if api["name"].startswith(self.api_name):
                    endpoint = AWSEndpoint(
                        region=region,
                        endpoint_url=f"{api['id']}.execute-api.{region}.amazonaws.com",
                        api_id=api["id"],
                        created_at=datetime.now(),  # We don't know real creation time
                        status="active"
                    )
                    logger.debug(f"Found existing API in {region}")
                    return endpoint
                    
        except Exception as e:
            logger.debug(f"Error checking existing APIs in {region}: {e}")
            
        return None
        
    async def rotate_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Utför request med IP rotation."""
        
        if not self.endpoints:
            raise Exception("No active endpoints available for rotation")
            
        # Choose random endpoint
        endpoint = choice(self.endpoints)
        
        # Modify URL to use our endpoint
        protocol, site_with_path = url.split("://", 1)
        if "/" in site_with_path:
            site, path = site_with_path.split("/", 1)
            rotated_url = f"https://{endpoint.endpoint_url}/ProxyStage/{path}"
        else:
            rotated_url = f"https://{endpoint.endpoint_url}/ProxyStage/"
            
        # Prepare headers
        headers = kwargs.get("headers", {})
        headers["Host"] = endpoint.endpoint_url
        
        # Generate random X-Forwarded-For if not provided
        if "X-Forwarded-For" not in headers:
            random_ip = ipaddress.IPv4Address._string_from_ip_int(randint(0, MAX_IPV4))
            headers["X-My-X-Forwarded-For"] = random_ip
        else:
            headers["X-My-X-Forwarded-For"] = headers.pop("X-Forwarded-For")
            
        kwargs["headers"] = headers
        
        # Track performance
        start_time = time.time()
        
        try:
            response = requests.request(method, rotated_url, **kwargs)
            response_time = time.time() - start_time
            
            # Update statistics
            with self._lock:
                self.stats["total_requests"] += 1
                self.stats["successful_requests"] += 1
                self.stats["last_rotation"] = datetime.now()
                
                # Update endpoint statistics
                endpoint.request_count += 1
                endpoint.last_used = datetime.now()
                endpoint.average_response_time = (
                    (endpoint.average_response_time * (endpoint.request_count - 1) + response_time) /
                    endpoint.request_count
                )
                
                # Update cost
                request_cost = self.cost_per_request
                endpoint.cost_estimate += request_cost
                self.stats["total_cost"] += request_cost
                
                if self.active_session:
                    self.active_session.total_requests += 1
                    self.active_session.successful_requests += 1
                    self.active_session.total_cost += request_cost
                    
            logger.debug(f"✅ Rotated request through {endpoint.region} in {response_time:.2f}s")
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            with self._lock:
                self.stats["total_requests"] += 1
                self.stats["failed_requests"] += 1
                endpoint.error_count += 1
                
            logger.warning(f"❌ Request failed through {endpoint.region}: {e}")
            raise e
            
    async def get_stats(self) -> Dict[str, Any]:
        """Hämta detaljerade statistik."""
        
        with self._lock:
            stats = self.stats.copy()
            
            # Calculate success rate
            if stats["total_requests"] > 0:
                stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"]) * 100
            else:
                stats["success_rate"] = 0.0
                
            # Add endpoint details
            stats["endpoints"] = [
                {
                    "region": ep.region,
                    "request_count": ep.request_count,
                    "error_count": ep.error_count,
                    "average_response_time": ep.average_response_time,
                    "cost_estimate": ep.cost_estimate,
                    "last_used": ep.last_used.isoformat() if ep.last_used else None
                }
                for ep in self.endpoints
            ]
            
            # Add session info
            if self.active_session:
                stats["active_session"] = {
                    "session_id": self.active_session.session_id,
                    "total_requests": self.active_session.total_requests,
                    "successful_requests": self.active_session.successful_requests,
                    "total_cost": self.active_session.total_cost,
                    "duration": (datetime.now() - self.active_session.created_at).total_seconds()
                }
                
        return stats
        
    async def cleanup_endpoints(self):
        """Rensa upp AWS API Gateway endpoints."""
        
        logger.info("🧹 Cleaning up AWS endpoints...")
        
        cleanup_count = 0
        
        for endpoint in self.endpoints:
            try:
                session = boto3.session.Session()
                awsclient = session.client(
                    "apigateway",
                    region_name=endpoint.region,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.access_key_secret
                )
                
                awsclient.delete_rest_api(restApiId=endpoint.api_id)
                cleanup_count += 1
                logger.debug(f"✅ Cleaned up endpoint in {endpoint.region}")
                
            except Exception as e:
                logger.warning(f"❌ Failed to cleanup endpoint in {endpoint.region}: {e}")
                
        logger.info(f"🧹 Cleanup completed: {cleanup_count}/{len(self.endpoints)} endpoints removed")
        
    def get_cost_estimate(self) -> Dict[str, float]:
        """Beräkna kostnadsskattning."""
        
        with self._lock:
            daily_requests = self.stats["total_requests"]
            
            # Estimate costs
            monthly_requests = daily_requests * 30
            monthly_cost = monthly_requests * self.cost_per_request
            
            return {
                "requests_today": daily_requests,
                "estimated_monthly_requests": monthly_requests,
                "estimated_monthly_cost_usd": monthly_cost,
                "cost_per_request": self.cost_per_request,
                "current_total_cost": self.stats["total_cost"]
            }


class IPRotatorSession(requests.Session):
    """
    Enhanced IP Rotator Session
    ===========================
    
    requests.Session som automatiskt använder IP rotation
    för alla HTTP requests.
    """
    
    def __init__(self, rotator: EnhancedAWSIPRotator):
        super().__init__()
        self.rotator = rotator
        
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Override request method to use IP rotation."""
        
        # Use asyncio.run for async method (not ideal but works for sync interface)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(
            self.rotator.rotate_request(url, method, **kwargs)
        )


async def test_aws_ip_rotator():
    """Test AWS IP Rotator system."""
    
    print("🚀 TESTING AWS IP ROTATOR SYSTEM")
    print("=" * 50)
    
    # Note: This test requires AWS credentials and will create actual resources
    print("⚠️  This test requires AWS credentials and will create billable resources!")
    print("   Make sure you have AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY set")
    
    import os
    if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
        print("❌ AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return
        
    # Initialize rotator (using httpbin.org for testing)
    rotator = EnhancedAWSIPRotator(
        site="httpbin.org",
        regions=["us-east-1", "eu-west-1"],  # Just 2 regions for testing
        access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    try:
        # Initialize system
        await rotator.initialize()
        
        # Test some requests
        print(f"\n🔄 Testing IP rotation requests...")
        
        for i in range(3):
            try:
                response = await rotator.rotate_request("http://httpbin.org/ip")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Request {i+1}: IP = {data.get('origin', 'unknown')}")
                else:
                    print(f"   Request {i+1}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   Request {i+1}: Failed - {e}")
                
        # Display statistics
        stats = await rotator.get_stats()
        
        print(f"\n📊 IP ROTATION STATISTICS:")
        print(f"   Total endpoints: {stats['total_endpoints']}")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Successful requests: {stats['successful_requests']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Total cost: ${stats['total_cost']:.6f}")
        
        # Cost estimate
        cost_info = rotator.get_cost_estimate()
        print(f"\n💰 COST ESTIMATES:")
        print(f"   Current cost: ${cost_info['current_total_cost']:.6f}")
        print(f"   Estimated monthly cost: ${cost_info['estimated_monthly_cost_usd']:.2f}")
        
        print(f"\n✅ AWS IP Rotator test completed!")
        
    finally:
        # Cleanup resources
        print(f"\n🧹 Cleaning up AWS resources...")
        await rotator.cleanup_endpoints()
        

async def demo_without_aws():
    """Demo the IP rotator concept without actually creating AWS resources."""
    
    print("🚀 AWS IP ROTATOR DEMO (Simulation Mode)")
    print("=" * 50)
    print("This demo shows the IP rotation concept without creating AWS resources")
    
    # Simulated rotator
    rotator = EnhancedAWSIPRotator(
        site="httpbin.org",
        regions=["us-east-1", "eu-west-1", "ap-southeast-1"]
    )
    
    # Simulate endpoints
    rotator.endpoints = [
        AWSEndpoint("us-east-1", "abc123.execute-api.us-east-1.amazonaws.com", "abc123", datetime.now()),
        AWSEndpoint("eu-west-1", "def456.execute-api.eu-west-1.amazonaws.com", "def456", datetime.now()),
        AWSEndpoint("ap-southeast-1", "ghi789.execute-api.ap-southeast-1.amazonaws.com", "ghi789", datetime.now())
    ]
    
    print(f"\n🌍 Simulated {len(rotator.endpoints)} endpoints:")
    for endpoint in rotator.endpoints:
        print(f"   • {endpoint.region}: {endpoint.endpoint_url}")
        
    # Simulate requests
    print(f"\n🔄 Simulating IP rotation requests...")
    for i in range(5):
        endpoint = choice(rotator.endpoints)
        fake_ip = f"{randint(1,255)}.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}"
        
        # Update simulated stats
        endpoint.request_count += 1
        endpoint.last_used = datetime.now()
        rotator.stats["total_requests"] += 1
        rotator.stats["successful_requests"] += 1
        
        print(f"   Request {i+1}: Region {endpoint.region} → Simulated IP {fake_ip}")
        
    # Show final stats
    print(f"\n📊 SIMULATION STATISTICS:")
    print(f"   Total requests: {rotator.stats['total_requests']}")
    print(f"   Success rate: 100%")
    print(f"   Cost per request: ${rotator.cost_per_request:.7f}")
    print(f"   Total cost: ${rotator.stats['total_requests'] * rotator.cost_per_request:.6f}")
    
    print(f"\n✅ IP Rotator simulation completed!")


if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Full AWS test (requires credentials, creates billable resources)")
    print("2. Demo simulation (no AWS resources created)")
    
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(test_aws_ip_rotator())
    else:
        asyncio.run(demo_without_aws())
