#!/usr/bin/env python3
"""
Test Chrome Launch

This script tests if Chrome can be launched successfully.
"""

import asyncio
import sys
from pathlib import Path

async def test_chrome_launch():
    """Test Chrome launch with Playwright."""
    print("🧪 Testing Chrome Launch...")
    
    try:
        from playwright.async_api import async_playwright
        
        chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
        
        if not chrome_path.exists():
            print(f"❌ Chrome not found: {chrome_path}")
            return False
        
        print(f"✅ Chrome found: {chrome_path}")
        
        # Test basic Chrome launch
        print("🚀 Launching Chrome with minimal arguments...")
        
        playwright = await async_playwright().start()
        
        # Try with minimal arguments first
        browser = await playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        print("✅ Chrome launched successfully!")
        
        # Create a page
        page = await browser.new_page()
        print("✅ Page created successfully!")
        
        # Navigate to a simple page
        await page.goto("about:blank")
        print("✅ Navigation successful!")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Close browser
        await browser.close()
        await playwright.stop()
        
        print("✅ Chrome test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Chrome launch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chrome_with_full_args():
    """Test Chrome launch with full arguments from floating agent."""
    print("\n🧪 Testing Chrome Launch with Full Arguments...")
    
    try:
        from playwright.async_api import async_playwright
        
        chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
        
        playwright = await async_playwright().start()
        
        # Use the same arguments as in the floating agent
        browser = await playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=False,
            slow_mo=500,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--window-size=1920,1080',
                '--window-position=0,0',
                '--disable-infobars',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--no-default-browser-check',
                '--disable-domain-reliability',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
                '--disable-prompt-on-repost',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        print("✅ Chrome launched with full arguments!")
        
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("about:blank")
        
        print("✅ Full arguments test successful!")
        
        await asyncio.sleep(2)
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Full arguments test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chrome_executable():
    """Test Chrome executable directly."""
    print("\n🧪 Testing Chrome Executable Directly...")
    
    try:
        import subprocess
        
        chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
        
        # Test Chrome version
        result = subprocess.run([str(chrome_path), "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Chrome version: {result.stdout.strip()}")
        else:
            print(f"❌ Chrome version check failed: {result.stderr}")
            return False
        
        # Test Chrome help
        result = subprocess.run([str(chrome_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Chrome help command successful")
        else:
            print(f"⚠️ Chrome help command failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chrome executable test failed: {e}")
        return False

async def main():
    """Run all Chrome launch tests."""
    print("🧪 Chrome Launch Test Suite")
    print("=" * 50)
    
    # Test 1: Chrome executable
    print("Test 1: Chrome Executable")
    test1_result = test_chrome_executable()
    
    # Test 2: Basic Chrome launch
    print("\nTest 2: Basic Chrome Launch")
    test2_result = await test_chrome_launch()
    
    # Test 3: Full arguments Chrome launch
    print("\nTest 3: Full Arguments Chrome Launch")
    test3_result = await test_chrome_with_full_args()
    
    print(f"\n{'='*50}")
    print("CHROME LAUNCH TEST RESULTS:")
    print(f"Chrome Executable Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Basic Chrome Launch Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"Full Arguments Test: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 All Chrome launch tests passed!")
        print("Chrome should work correctly in the floating agent.")
        return 0
    else:
        print("\n❌ Some Chrome launch tests failed.")
        print("This explains why the floating agent Chrome initialization is failing.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
