#!/usr/bin/env python3
"""
Test Chrome Opening - Verify the agent can open Chrome

This script tests if the embedded Chrome can be opened and controlled.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_direct_chrome_opening():
    """Test opening Chrome directly"""
    print("🧪 Testing Direct Chrome Opening...")
    
    try:
        from playwright.async_api import async_playwright
        
        # Chrome path
        chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
        
        if not chrome_path.exists():
            print(f"❌ Chrome not found: {chrome_path}")
            return False
        
        print(f"✅ Chrome found: {chrome_path}")
        
        # Start Playwright
        playwright = await async_playwright().start()
        print("✅ Playwright started")
        
        # Launch Chrome
        browser = await playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=False,  # Visible browser
            slow_mo=1000,    # Slow for visibility
            args=['--no-sandbox']
        )
        print("✅ Chrome launched successfully!")
        
        # Create page
        page = await browser.new_page()
        print("✅ New page created")
        
        # Navigate to Google
        await page.goto("https://www.google.com")
        print("✅ Navigated to Google")
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"📄 Page Title: {title}")
        print(f"🌐 Current URL: {url}")
        
        print("\n🎉 SUCCESS! Chrome opened and navigated to Google!")
        print("The browser window should be visible on your screen.")
        
        # Keep browser open for 10 seconds
        print("⏳ Keeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        
        # Close
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
    print("🤖 Chrome Opening Test")
    print("=" * 40)
    
    success = await test_direct_chrome_opening()
    
    if success:
        print("\n🎉 Test PASSED! Chrome can be opened and controlled.")
        print("The floating agent should now be able to open Chrome when you send commands.")
    else:
        print("\n❌ Test FAILED! Chrome could not be opened.")
    
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
