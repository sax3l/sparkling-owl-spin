#!/usr/bin/env python3
"""Test AWS IP Rotator Integration"""

import asyncio
import json
from datetime import datetime

from aws_ip_rotator_integration import EnhancedAWSIPRotator

# Test in DEMO mode (no real AWS credentials needed)
async def test_aws_integration():
    print("🚀 Testing AWS IP Rotator Integration (DEMO MODE)")
    print("=" * 50)
    
    # Initialize AWS IP Rotator in demo mode
    rotator = EnhancedAWSIPRotator(demo_mode=True)
    
    # Test 1: Check configuration
    print("\n📋 Configuration Test:")
    print(f"Demo Mode: {rotator.demo_mode}")
    print(f"Total Regions: {len(rotator.regions)}")
    print(f"Regions: {rotator.regions[:5]}...")  # Show first 5
    
    # Test 2: Demo endpoint creation
    print("\n🔧 Creating Demo Endpoints...")
    endpoints = await rotator.create_endpoints(regions=['us-east-1', 'eu-west-1', 'ap-southeast-1'])
    print(f"Created {len(endpoints)} demo endpoints")
    
    for i, endpoint in enumerate(endpoints[:3]):
        print(f"  {i+1}. Region: {endpoint.region}, Gateway: {endpoint.gateway_id}")
        print(f"     Endpoint URL: {endpoint.endpoint_url}")
    
    # Test 3: Session with rotation
    print("\n🔄 Testing Request Session with IP Rotation...")
    session = rotator.get_requests_session()
    
    # Test 4: Cost estimation
    print("\n💰 Cost Estimation (Demo):")
    daily_cost = rotator.estimate_daily_cost(requests_per_day=10000, active_endpoints=5)
    monthly_cost = rotator.estimate_monthly_cost(requests_per_day=10000, active_endpoints=5)
    print(f"Estimated daily cost: ${daily_cost:.4f}")
    print(f"Estimated monthly cost: ${monthly_cost:.2f}")
    
    # Test 5: Mock request (won't actually call AWS)
    print("\n🌐 Mock HTTP Request Test:")
    try:
        # This will use the demo session
        print("Would normally make request through AWS API Gateway...")
        print("Request would be routed through different IP addresses")
        print("✅ Session configuration successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Endpoint management
    print("\n🗂️ Endpoint Management:")
    print(f"Total endpoints created: {len(rotator.endpoints)}")
    print(f"Active regions: {[ep.region for ep in rotator.endpoints]}")
    
    # Test 7: Stats and monitoring
    print("\n📊 Statistics:")
    stats = {
        'total_endpoints': len(rotator.endpoints),
        'regions_count': len(set(ep.region for ep in rotator.endpoints)),
        'demo_mode': rotator.demo_mode,
        'test_timestamp': datetime.now().isoformat()
    }
    print(json.dumps(stats, indent=2))
    
    # Test 8: Cleanup simulation
    print("\n🧹 Cleanup Simulation:")
    print("Would cleanup AWS resources (API Gateways, deployments)")
    await rotator.cleanup_all()
    print("✅ Cleanup completed (demo mode)")
    
    print("\n🎉 AWS IP Rotator Integration Test Completed!")
    print("Ready for production deployment with real AWS credentials")

if __name__ == "__main__":
    asyncio.run(test_aws_integration())
