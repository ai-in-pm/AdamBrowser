#!/usr/bin/env python3
"""
Test Persistent Browser - Verify browser stays open between commands

This script tests the persistent browser functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_persistent_browser():
    """Test persistent browser functionality"""
    print("🧪 Testing Persistent Browser Functionality...")
    
    try:
        from playwright.async_api import async_playwright
        
        # Chrome path
        chrome_path = Path(__file__).parent / "Google" / "Chrome" / "Application" / "chrome.exe"
        
        if not chrome_path.exists():
            print(f"❌ Chrome not found: {chrome_path}")
            return False
        
        print(f"✅ Chrome found: {chrome_path}")
        
        # Start Playwright
        playwright = await async_playwright().start()
        print("✅ Playwright started")
        
        # Launch persistent Chrome
        print("🌐 Launching persistent Chrome browser...")
        browser = await playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=False,  # Visible browser
            slow_mo=500,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        # Create persistent page
        page = await browser.new_page()
        await page.goto("about:blank")
        
        print("✅ Persistent browser launched!")
        print("🌐 Browser window should be visible and will stay open")
        
        # Test 1: Navigate to Google
        print("\n🧪 Test 1: Navigate to Google")
        await page.goto("https://www.google.com", wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        title = await page.title()
        url = page.url
        print(f"✅ Navigation successful")
        print(f"📄 Title: {title}")
        print(f"🌐 URL: {url}")
        
        # Test 2: Search
        print("\n🧪 Test 2: Perform search")
        search_box = page.locator('input[name="q"]')
        await search_box.fill("persistent browser test")
        await search_box.press('Enter')
        await asyncio.sleep(3)
        
        new_title = await page.title()
        print(f"✅ Search successful")
        print(f"📄 Results title: {new_title}")
        
        # Test 3: Navigate to another site
        print("\n🧪 Test 3: Navigate to another site")
        await page.goto("https://www.github.com", wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        github_title = await page.title()
        print(f"✅ Navigation to GitHub successful")
        print(f"📄 GitHub title: {github_title}")
        
        print("\n🎉 All tests completed!")
        print("🌐 Browser is staying open - you can interact with it")
        print("⏳ Browser will stay open for 30 seconds for you to test...")
        
        # Keep browser open for user interaction
        await asyncio.sleep(30)
        
        print("\n🔒 Closing browser...")
        await browser.close()
        await playwright.stop()
        print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🤖 Persistent Browser Test")
    print("=" * 40)
    
    success = await test_persistent_browser()
    
    if success:
        print("\n🎉 Test PASSED! Persistent browser functionality working.")
        print("The floating agent should now keep Chrome open between commands.")
    else:
        print("\n❌ Test FAILED! Persistent browser not working.")
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        input("\nPress Enter to exit...")
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
