#!/usr/bin/env python3
"""
SOS Platform Example - Demonstration of revolutionary webscraping capabilities
Shows integration of all enhancement modules
"""

import asyncio
import logging
from typing import List

# Import SOS components
from src.sos import (
    SOSPlatform,
    quick_crawl, 
    stealth_crawl,
    distributed_crawl,
    get_settings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sos_example")

async def example_basic_crawling():
    """Example 1: Basic HTTP crawling with enhanced features"""
    
    logger.info("🚀 Example 1: Basic Enhanced Crawling")
    
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers", 
        "https://httpbin.org/user-agent",
        "https://example.com",
        "https://httpbin.org/delay/2"
    ]
    
    # Quick crawl with auto method selection
    result = await quick_crawl(
        urls=urls,
        export_format="json",
        max_concurrency=3,
        delay_ms=1000
    )
    
    logger.info(f"✅ Crawled {result['stats']['total_urls']} URLs")
    logger.info(f"   Success rate: {result['stats']['success_rate']:.1%}")
    logger.info(f"   Total time: {result['stats']['crawl_time']:.2f}s")
    
    return result

async def example_stealth_crawling():
    """Example 2: Stealth browser automation for JavaScript-heavy sites"""
    
    logger.info("🥷 Example 2: Stealth Browser Crawling")
    
    # URLs that might need JavaScript rendering
    js_urls = [
        "https://httpbin.org/get",  # Simple test
        "https://example.com",      # Static content
    ]
    
    try:
        result = await stealth_crawl(
            urls=js_urls,
            export_formats=["json"],
            headless=True,
            wait_time=3000  # Wait 3 seconds for JS
        )
        
        logger.info(f"✅ Stealth crawled {result['stats']['total_urls']} URLs")
        logger.info(f"   Success rate: {result['stats']['success_rate']:.1%}")
        logger.info(f"   Method used: {result['stats']['method_used']}")
        
        return result
        
    except Exception as e:
        logger.warning(f"⚠️  Stealth crawling failed (likely browser deps missing): {str(e)}")
        return None

async def example_comprehensive_platform():
    """Example 3: Full platform with all components"""
    
    logger.info("🌟 Example 3: Comprehensive SOS Platform")
    
    # Initialize platform with all components
    platform = SOSPlatform()
    
    # Enable components based on what's available
    components = ['base_crawler', 'enhanced_crawler']
    
    # Add optional components if configured
    settings = get_settings()
    if getattr(settings, 'STEALTH_BROWSER_ENABLED', False):
        components.append('stealth_browser')
    if getattr(settings, 'ANTI_DETECTION_ENABLED', False):
        components.append('anti_detection')
    if getattr(settings, 'DISTRIBUTED_ENABLED', False):
        components.append('distributed')
    
    await platform.initialize(components)
    
    try:
        # Test URLs for different scenarios
        test_urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/json",
            "https://httpbin.org/html",
            "https://example.com"
        ]
        
        # Crawl with auto method selection
        result = await platform.crawl(
            urls=test_urls,
            method="auto",
            export_formats=["json", "csv"],
            priority=5
        )
        
        # Display comprehensive results
        logger.info("📊 Comprehensive Crawl Results:")
        logger.info(f"   Platform components: {platform.stats['components_initialized']}")
        logger.info(f"   URLs processed: {result['stats']['total_urls']}")
        logger.info(f"   Success rate: {result['stats']['success_rate']:.1%}")
        logger.info(f"   Method used: {result['stats']['method_used']}")
        logger.info(f"   Exported formats: {list(result['exported_files'].keys())}")
        
        # Get platform statistics
        platform_stats = platform.get_platform_stats()
        logger.info(f"   Platform uptime: {platform_stats['platform']['uptime_seconds']:.1f}s")
        logger.info(f"   Total platform crawls: {platform_stats['crawling']['total_crawls']}")
        
        # Health check
        health = await platform.health_check()
        logger.info(f"   Platform health: {health['status']}")
        logger.info(f"   Component health: {list(health['components'].keys())}")
        
        return result
        
    finally:
        await platform.shutdown()

async def example_batch_processing():
    """Example 4: Batch processing with different strategies"""
    
    logger.info("📦 Example 4: Batch Processing")
    
    # Large batch of URLs for testing scalability
    large_batch = [
        f"https://httpbin.org/get?page={i}" 
        for i in range(1, 21)  # 20 URLs
    ]
    
    platform = SOSPlatform()
    await platform.initialize(['base_crawler', 'enhanced_crawler'])
    
    try:
        # Test different crawling strategies
        strategies = ['basic', 'enhanced']
        
        results = {}
        for strategy in strategies:
            logger.info(f"   Testing {strategy} strategy...")
            
            start_time = asyncio.get_event_loop().time()
            
            result = await platform.crawl(
                urls=large_batch,
                method=strategy,
                max_concurrency=5,
                delay_ms=500
            )
            
            end_time = asyncio.get_event_loop().time()
            
            results[strategy] = {
                'success_rate': result['stats']['success_rate'],
                'total_time': end_time - start_time,
                'successful': result['stats']['successful']
            }
            
            logger.info(f"     ✅ {strategy}: {result['stats']['successful']}/{result['stats']['total_urls']} "
                       f"({result['stats']['success_rate']:.1%}) in {results[strategy]['total_time']:.2f}s")
        
        # Compare strategies
        logger.info("📊 Strategy Comparison:")
        for strategy, stats in results.items():
            logger.info(f"   {strategy.capitalize()}: "
                       f"{stats['success_rate']:.1%} success, "
                       f"{stats['total_time']:.2f}s total")
        
        return results
        
    finally:
        await platform.shutdown()

async def example_export_formats():
    """Example 5: Multiple export formats"""
    
    logger.info("📁 Example 5: Export Format Testing")
    
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json", 
        "https://example.com"
    ]
    
    # Test all export formats
    export_formats = ["json", "csv"]
    
    result = await quick_crawl(
        urls=urls,
        export_formats=export_formats,
        output_dir="data/exports"
    )
    
    logger.info("📁 Export Results:")
    for format_name, file_path in result['exported_files'].items():
        logger.info(f"   {format_name.upper()}: {file_path}")
    
    return result

async def example_error_handling():
    """Example 6: Error handling and resilience"""
    
    logger.info("🛡️  Example 6: Error Handling")
    
    # Mix of valid and invalid URLs
    test_urls = [
        "https://httpbin.org/get",           # Valid
        "https://httpbin.org/status/404",    # 404 error
        "https://httpbin.org/status/500",    # 500 error
        "https://invalid-domain-xyz.com",    # DNS error
        "https://httpbin.org/delay/10",      # Timeout (if configured)
        "https://example.com"                 # Valid
    ]
    
    result = await quick_crawl(
        urls=test_urls,
        max_retries=2,
        timeout=5
    )
    
    # Analyze error patterns
    successful = sum(1 for r in result['results'] if not r.error)
    failed = len(result['results']) - successful
    
    logger.info(f"🛡️  Error Handling Results:")
    logger.info(f"   Total URLs: {len(test_urls)}")
    logger.info(f"   Successful: {successful}")
    logger.info(f"   Failed: {failed}")
    logger.info(f"   Success rate: {successful/len(test_urls):.1%}")
    
    # Show error types
    error_types = {}
    for r in result['results']:
        if r.error:
            error_type = type(r.error).__name__ if hasattr(r.error, '__class__') else 'Unknown'
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    if error_types:
        logger.info("   Error breakdown:")
        for error_type, count in error_types.items():
            logger.info(f"     {error_type}: {count}")
    
    return result

async def main():
    """Run all examples"""
    
    logger.info("🎯 Starting SOS Platform Examples")
    logger.info("=" * 60)
    
    examples = [
        ("Basic Enhanced Crawling", example_basic_crawling),
        ("Stealth Browser Crawling", example_stealth_crawling), 
        ("Comprehensive Platform", example_comprehensive_platform),
        ("Batch Processing", example_batch_processing),
        ("Export Formats", example_export_formats),
        ("Error Handling", example_error_handling),
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            logger.info(f"\n🔄 Running: {name}")
            logger.info("-" * 40)
            
            result = await example_func()
            results[name] = result
            
            logger.info(f"✅ Completed: {name}")
            
        except Exception as e:
            logger.error(f"❌ Failed: {name} - {str(e)}")
            results[name] = {"error": str(e)}
        
        # Small delay between examples
        await asyncio.sleep(1)
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("🎉 SOS Platform Examples Summary")
    logger.info("=" * 60)
    
    successful_examples = sum(1 for r in results.values() if "error" not in r)
    total_examples = len(examples)
    
    logger.info(f"Examples completed: {successful_examples}/{total_examples}")
    
    for name, result in results.items():
        if "error" in result:
            logger.info(f"❌ {name}: {result['error']}")
        else:
            logger.info(f"✅ {name}: Success")
    
    logger.info("\n🚀 SOS Platform demonstration completed!")
    logger.info("   Revolutionary webscraping capabilities successfully demonstrated")

if __name__ == "__main__":
    # Set up event loop policy for Windows if needed
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
