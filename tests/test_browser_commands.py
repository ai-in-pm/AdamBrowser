#!/usr/bin/env python3
"""
Test Browser Commands - Diagnostic Script

This script tests the browser manager directly to verify command execution.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from adam_browser.browser.browser_manager import BrowserManager
    print("✅ BrowserManager imported successfully")
except ImportError as e:
    print(f"❌ Failed to import BrowserManager: {e}")
    sys.exit(1)

async def test_browser_commands():
    """Test browser commands directly"""
    print("🚀 Starting browser command test...")
    
    # Initialize browser manager
    browser_manager = BrowserManager()
    
    try:
        print("🔧 Initializing browser...")
        success = await browser_manager.initialize()
        
        if not success:
            print("❌ Failed to initialize browser")
            return False
        
        print("✅ Browser initialized successfully")
        print(f"✅ Browser ready: {browser_manager.is_initialized}")
        print(f"✅ Page available: {browser_manager.page is not None}")
        
        # Test 1: Navigate to Google
        print("\n🧪 Test 1: Navigate to Google")
        nav_success = await browser_manager.navigate_to("https://www.google.com")
        print(f"Navigation result: {nav_success}")
        
        if nav_success:
            await asyncio.sleep(3)  # Wait for page to load
            current_url = browser_manager.page.url
            page_title = await browser_manager.page.title()
            print(f"✅ Current URL: {current_url}")
            print(f"✅ Page title: {page_title}")
        
        # Test 2: Take screenshot
        print("\n🧪 Test 2: Take screenshot")
        screenshot_path = await browser_manager.take_screenshot()
        print(f"Screenshot result: {screenshot_path}")
        
        # Test 3: Search
        print("\n🧪 Test 3: Search test")
        if nav_success:
            search_success = await browser_manager.type_text('input[name="q"]', 'test search')
            print(f"Search typing result: {search_success}")
            
            if search_success:
                await browser_manager.page.keyboard.press('Enter')
                await asyncio.sleep(3)
                print("✅ Search completed")
        
        # Test 4: Scroll
        print("\n🧪 Test 4: Scroll test")
        try:
            await browser_manager.page.keyboard.press('PageDown')
            print("✅ Scroll completed")
        except Exception as e:
            print(f"❌ Scroll failed: {e}")
        
        print("\n✅ All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("🧹 Cleaning up...")
        await browser_manager.cleanup()

async def main():
    """Main test function"""
    print("🤖 Browser Command Test Suite")
    print("=" * 50)
    
    success = await test_browser_commands()
    
    if success:
        print("\n🎉 All tests passed! Browser commands are working.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
