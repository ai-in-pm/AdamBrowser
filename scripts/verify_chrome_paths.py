#!/usr/bin/env python3
"""
Chrome Path Verification Script

This script verifies that all Chrome paths in the codebase point to the correct
embedded Chrome location: D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe
"""

import os
import sys
from pathlib import Path

def main():
    """Verify Chrome paths configuration"""
    print("🔍 Chrome Path Verification")
    print("=" * 50)
    
    # Expected Chrome path
    expected_chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
    print(f"📍 Expected Chrome Path: {expected_chrome_path}")
    
    # Check if Chrome exists
    if expected_chrome_path.exists():
        print("✅ Chrome executable found!")
        
        # Get file info
        stat = expected_chrome_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        print(f"📊 File size: {size_mb:.1f} MB")
        print(f"📅 Modified: {stat.st_mtime}")
    else:
        print("❌ Chrome executable NOT found!")
        print("⚠️  The agent will not be able to launch Chrome")
        return False
    
    print("\n🔧 Configuration Verification:")
    
    # Check configuration file directly
    config_file = Path(__file__).parent.parent / "config" / "adam.config.toml"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config_content = f.read()
            if str(expected_chrome_path).replace('\\', '\\\\') in config_content:
                print("✅ Configuration file: Correct Chrome path")
            else:
                print("❌ Configuration file: Wrong Chrome path")
                return False
    else:
        print("❌ Configuration file not found")
        return False

    # Check browser manager file
    browser_manager_file = Path(__file__).parent.parent / "adam_browser" / "browser" / "browser_manager.py"
    if browser_manager_file.exists():
        with open(browser_manager_file, 'r') as f:
            manager_content = f.read()
            if str(expected_chrome_path) in manager_content:
                print("✅ BrowserManager: Correct Chrome path")
            else:
                print("❌ BrowserManager: Wrong Chrome path")
                return False
    else:
        print("❌ BrowserManager file not found")
        return False
    
    print("\n🎉 All Chrome paths are correctly configured!")
    print("🚀 The agent should now always use the embedded Chrome browser")
    
    return True

if __name__ == '__main__':
    success = main()
    print(f"\n{'✅ VERIFICATION PASSED' if success else '❌ VERIFICATION FAILED'}")
    sys.exit(0 if success else 1)
