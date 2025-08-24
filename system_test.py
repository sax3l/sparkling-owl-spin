#!/usr/bin/env python3
"""
🧪 Kontinuerlig systemtest för Sparkling Owl Spin
"""
import asyncio
from stealth_browser_manager import StealthBrowserManager, BrowserType

async def test_system():
    print("🧪 Testing Sparkling Owl Spin System...")
    
    # Test stealth browser
    manager = StealthBrowserManager(BrowserType.CHROMIUM)
    browser = await manager.launch_browser(headless=True)
    context = await manager.create_stealth_context()
    page = await manager.create_stealth_page(context)
    
    # Test navigation
    result = await manager.navigate_stealthily(page, "https://httpbin.org/headers")
    print(f"Navigation result: {result}")
    
    await manager.close()
    print("✅ System test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_system())
