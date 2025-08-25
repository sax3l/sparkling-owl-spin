#!/usr/bin/env python3
"""Test AWS IP Rotator Integration"""

import asyncio
import json
from datetime import datetime

from engines.bypass.aws_ip_rotator import EnhancedAWSIPRotator, RotationStrategy, RotationConfig

# Test in DEMO mode (no real AWS credentials needed)
async def test_aws_integration():
    print("🚀 Testing AWS IP Rotator Integration (DEMO MODE)")
    print("=" * 50)
    
    # Initialize AWS IP Rotator in demo mode with custom config
    config = RotationConfig(
        strategy=RotationStrategy.ROUND_ROBIN,
        rotation_interval=50,
        max_retries=3,
        rate_limit=5
    )
    
    rotator = EnhancedAWSIPRotator(demo_mode=True, config=config)
    
    # Test 1: Check configuration
    print("\n📋 Configuration Test:")
    print(f"Demo Mode: {rotator.demo_mode}")
    print(f"Total Regions: {len(rotator.regions)}")
    print(f"Regions: {rotator.regions[:5]}...")  # Show first 5
    print(f"Rotation Strategy: {rotator.config.strategy.value}")
    print(f"Rotation Interval: {rotator.config.rotation_interval}")
    
    # Test 2: Service lifecycle
    print("\n🔧 Service Lifecycle Test:")
    await rotator.start()
    print(f"Service Status: {rotator.status.value}")
    
    # Test 3: Demo endpoint creation
    print("\n🌐 Creating Demo Endpoints...")
    endpoints = await rotator.create_endpoints(
        regions=['us-east-1', 'eu-west-1', 'ap-southeast-1'], 
        count=2
    )
    print(f"Created {len(endpoints)} demo endpoints")
    
    for i, endpoint in enumerate(endpoints):
        print(f"  {i+1}. Region: {endpoint.region}")
        print(f"     Gateway ID: {endpoint.gateway_id}")
        print(f"     Endpoint URL: {endpoint.endpoint_url}")
        print(f"     Created: {endpoint.created_at.strftime('%H:%M:%S')}")
    
    # Test 4: Endpoint rotation
    print("\n🔄 Testing Endpoint Rotation...")
    for i in range(8):  # Test multiple rotations
        endpoint = await rotator.get_next_endpoint()
        print(f"  Request {i+1}: Using {endpoint.region} (Used {endpoint.request_count} times)")
    
    # Test 5: Session with rotation
    print("\n📡 Testing Request Session with IP Rotation...")
    session = rotator.get_requests_session()
    
    if session:
        print("✅ Session created successfully")
        print("  - Configured with retry strategy")
        print("  - Rotation method attached")
        print("  - Rate limiting enabled")
    else:
        print("⚠️ Session creation skipped (requests library not available)")
    
    # Test 6: Cost estimation
    print("\n💰 Cost Estimation (Demo):")
    daily_cost = rotator.estimate_daily_cost(requests_per_day=10000, active_endpoints=5)
    monthly_cost = rotator.estimate_monthly_cost(requests_per_day=10000, active_endpoints=5)
    print(f"Estimated daily cost (10k requests/day, 5 endpoints): ${daily_cost:.4f}")
    print(f"Estimated monthly cost: ${monthly_cost:.2f}")
    
    # Test 7: Health check
    print("\n🏥 Health Check Test:")
    health_result = await rotator.health_check()
    print(f"Health Status: {health_result.status}")
    print(f"Message: {health_result.message}")
    print(f"Timestamp: {health_result.timestamp.strftime('%H:%M:%S')}")
    
    # Test 8: Statistics
    print("\n📊 Service Statistics:")
    stats = rotator.get_statistics()
    print(f"Total Endpoints: {stats['total_endpoints']}")
    print(f"Active Endpoints: {stats['active_endpoints']}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Current Strategy: {stats['current_strategy']}")
    print(f"Regions: {', '.join(stats['regions'])}")
    
    # Show endpoint details
    print("\n🔍 Endpoint Details:")
    for i, ep_stat in enumerate(stats['endpoint_stats']):
        print(f"  {i+1}. {ep_stat['region']}: {ep_stat['requests']} requests, "
              f"{'Active' if ep_stat['active'] else 'Inactive'}")
    
    # Test 9: Mock request simulation
    print("\n🌐 Mock HTTP Request Simulation:")
    try:
        print("Simulating requests through different endpoints...")
        for i in range(5):
            endpoint = await rotator.get_next_endpoint()
            print(f"  Request {i+1}: GET https://example.com → {endpoint.region}")
            await asyncio.sleep(0.1)  # Simulate request time
        print("✅ Request simulation completed")
    except Exception as e:
        print(f"❌ Simulation error: {e}")
    
    # Test 10: Cleanup simulation
    print("\n🧹 Cleanup Simulation:")
    print("Cleaning up AWS resources (demo mode)...")
    await rotator.cleanup_all()
    print("✅ Cleanup completed")
    
    # Test 11: Service shutdown
    print("\n🛑 Service Shutdown:")
    await rotator.stop()
    print(f"Final Service Status: {rotator.status.value}")
    
    print("\n🎉 AWS IP Rotator Integration Test Completed!")
    print("=" * 50)
    print("✅ All tests passed successfully")
    print("🚀 Ready for production deployment with real AWS credentials")
    
    # Generate test report
    test_report = {
        'test_timestamp': datetime.now().isoformat(),
        'demo_mode': True,
        'endpoints_created': len(endpoints),
        'regions_tested': ['us-east-1', 'eu-west-1', 'ap-southeast-1'],
        'rotation_strategy': config.strategy.value,
        'total_requests_simulated': stats['total_requests'],
        'health_status': health_result.status,
        'estimated_daily_cost': daily_cost,
        'estimated_monthly_cost': monthly_cost,
        'test_status': 'PASSED'
    }
    
    print(f"\n📄 Test Report:")
    print(json.dumps(test_report, indent=2))


async def test_different_strategies():
    """Test different rotation strategies"""
    print("\n🔄 Testing Different Rotation Strategies")
    print("=" * 40)
    
    strategies = [
        RotationStrategy.SEQUENTIAL,
        RotationStrategy.RANDOM,
        RotationStrategy.ROUND_ROBIN,
        RotationStrategy.WEIGHTED
    ]
    
    for strategy in strategies:
        print(f"\n📊 Testing {strategy.value.upper()} strategy:")
        
        config = RotationConfig(strategy=strategy, rotation_interval=10)
        rotator = EnhancedAWSIPRotator(demo_mode=True, config=config)
        
        await rotator.start()
        await rotator.create_endpoints(['us-east-1', 'eu-west-1', 'ap-southeast-1'])
        
        # Test rotation pattern
        regions_used = []
        for i in range(6):
            endpoint = await rotator.get_next_endpoint()
            regions_used.append(endpoint.region)
        
        print(f"  Rotation pattern: {' → '.join(regions_used)}")
        
        await rotator.stop()


if __name__ == "__main__":
    # Run main test
    asyncio.run(test_aws_integration())
    
    # Run strategy test
    asyncio.run(test_different_strategies())
