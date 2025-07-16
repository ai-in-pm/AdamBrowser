#!/usr/bin/env python3
"""
Direct Chrome Launcher for Adam Browser

This script directly launches Chrome and performs browser automation
to ensure physical browser control is working.
"""

import asyncio
import subprocess
import time
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Chrome path
CHROME_PATH = Path(__file__).parent / "Google" / "Chrome" / "Application" / "chrome.exe"

async def launch_chrome_directly():
    """Launch Chrome directly and perform automation"""
    print("🚀 Direct Chrome Launcher Starting...")
    print(f"🌐 Chrome Path: {CHROME_PATH}")
    
    if not CHROME_PATH.exists():
        print(f"❌ Chrome not found at: {CHROME_PATH}")
        return False
    
    print("✅ Chrome found! Starting Playwright...")
    
    try:
        # Start Playwright
        playwright = await async_playwright().start()
        print("✅ Playwright started")
        
        # Launch Chrome with custom executable
        browser = await playwright.chromium.launch(
            executable_path=str(CHROME_PATH),
            headless=False,  # Make sure it's visible
            slow_mo=1000,    # Slow down for visibility
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
            ]
        )
        print("✅ Chrome browser launched!")
        
        # Create a new page
        page = await browser.new_page()
        print("✅ New page created")
        
        # Navigate to Google
        print("🌐 Navigating to Google...")
        await page.goto("https://www.google.com")
        print("✅ Navigation completed!")
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"📄 Page Title: {title}")
        print(f"🌐 Current URL: {url}")
        
        # Take a screenshot
        print("📸 Taking screenshot...")
        screenshot_path = "chrome_test_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Try to search
        print("🔍 Attempting search...")
        try:
            # Find search box and type
            search_box = page.locator('input[name="q"]')
            await search_box.fill("Adam Browser Test")
            print("✅ Text entered in search box")
            
            # Press Enter
            await search_box.press('Enter')
            print("✅ Search submitted")
            
            # Wait for results
            await asyncio.sleep(3)
            
            # Get new page info
            new_title = await page.title()
            new_url = page.url
            print(f"📄 Search Results Title: {new_title}")
            print(f"🌐 Search Results URL: {new_url}")
            
        except Exception as e:
            print(f"⚠️ Search failed: {e}")
        
        # Keep browser open for a moment
        print("⏳ Keeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        
        # Close browser
        print("🔒 Closing browser...")
        await browser.close()
        await playwright.stop()
        
        print("✅ Direct Chrome test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Chrome automation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🤖 Adam Browser - Direct Chrome Test")
    print("=" * 50)
    
    success = await launch_chrome_directly()
    
    if success:
        print("\n🎉 Chrome automation working! The browser should have opened and performed actions.")
    else:
        print("\n❌ Chrome automation failed. Check the errors above.")
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        input("\nPress Enter to exit...")
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
