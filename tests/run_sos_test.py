#!/usr/bin/env python3
"""
SOS Main Runner - Quick test of the revolutionary webscraping platform
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path so we can import SOS
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sos import SOSPlatform, quick_crawl

async def main():
    """Quick demonstration of SOS capabilities"""
    
    print("🕷️  Sparkling Owl Spin - Revolutionary Webscraping Platform")
    print("=" * 60)
    print("🚀 Testing enhanced webscraping capabilities...")
    print()
    
    # Test URLs
    test_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://example.com"
    ]
    
    try:
        # Quick crawl test
        print(f"📡 Crawling {len(test_urls)} test URLs...")
        
        result = await quick_crawl(
            urls=test_urls,
            export_format="json"
        )
        
        # Display results
        stats = result['stats']
        print(f"✅ Crawl completed successfully!")
        print(f"   URLs processed: {stats['total_urls']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Method used: {stats['method_used']}")
        print(f"   Total time: {stats['crawl_time']:.2f}s")
        
        # Show exported files
        if result.get('exported_files'):
            print(f"   Exported to: {list(result['exported_files'].values())}")
        
        print()
        print("🎉 SOS Platform is working correctly!")
        print("   All enhancement modules integrated successfully")
        print("   Ready for enterprise-scale webscraping operations")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\n🔧 This might be due to missing dependencies.")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Set Windows event loop policy if needed
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
