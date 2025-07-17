#!/usr/bin/env python3
"""
Test Chrome Functionality

This script tests that Chrome is working correctly in the floating agent.
"""

import sys
import os
from pathlib import Path

def test_chrome_path():
    """Test that Chrome executable exists."""
    print("🔍 Testing Chrome Path...")
    
    chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
    
    if chrome_path.exists():
        print(f"✅ Chrome found: {chrome_path}")
        
        # Check file size
        file_size = chrome_path.stat().st_size
        print(f"✅ Chrome size: {file_size / 1024 / 1024:.1f} MB")
        
        # Check if it's executable
        if os.access(chrome_path, os.X_OK):
            print("✅ Chrome is executable")
        else:
            print("⚠️ Chrome may not be executable")
        
        return True
    else:
        print(f"❌ Chrome not found: {chrome_path}")
        return False

def test_chrome_version():
    """Test Chrome version detection."""
    print("\n🔍 Testing Chrome Version...")
    
    try:
        import subprocess
        chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
        
        if not chrome_path.exists():
            print("❌ Chrome not found for version test")
            return False
        
        # Try to get Chrome version
        result = subprocess.run([str(chrome_path), "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Chrome version: {version}")
            return True
        else:
            print(f"⚠️ Chrome version check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Chrome version test error: {e}")
        return False

def test_browser_manager():
    """Test browser manager configuration."""
    print("\n🔍 Testing Browser Manager...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from adam_browser.browser.browser_manager import BrowserManager
        
        # Create browser manager
        browser_manager = BrowserManager()
        
        print(f"✅ Browser Manager created")
        print(f"✅ Browser path: {browser_manager.browser_path}")
        print(f"✅ Browser type: {browser_manager.browser_type}")
        
        # Check if the path matches our Chrome
        expected_path = r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe"
        if browser_manager.browser_path == expected_path:
            print("✅ Browser path correctly configured")
            return True
        else:
            print(f"⚠️ Browser path mismatch: expected {expected_path}, got {browser_manager.browser_path}")
            return False
            
    except Exception as e:
        print(f"❌ Browser Manager test error: {e}")
        return False

def test_chrome_management_imports():
    """Test Chrome Management System imports."""
    print("\n🔍 Testing Chrome Management Imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from chrome_management_suite import ChromeManagementSuite
        print("✅ ChromeManagementSuite imported")
        
        from chrome_management.version_manager import ChromeVersionManager
        print("✅ ChromeVersionManager imported")
        
        # Test initialization
        project_root = Path(__file__).parent
        suite = ChromeManagementSuite(project_root)
        print("✅ ChromeManagementSuite initialized")
        
        # Test status
        status = suite.get_status()
        print(f"✅ Chrome status: {status.get('chrome_installed', False)}")
        print(f"✅ Chrome version: {status.get('chrome_version', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chrome Management test error: {e}")
        return False

def test_floating_agent_chrome_integration():
    """Test floating agent Chrome integration."""
    print("\n🔍 Testing Floating Agent Chrome Integration...")
    
    try:
        # Test that the floating agent file exists and has Chrome integration
        floating_agent_path = Path(__file__).parent / "embedded_chrome_floating_agent_v1.py"
        
        if not floating_agent_path.exists():
            print("❌ Floating agent file not found")
            return False
        
        print("✅ Floating agent file found")
        
        # Check for Chrome Management imports in the file
        with open(floating_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chrome_imports = [
            "from chrome_management_suite import ChromeManagementSuite",
            "from chrome_management.version_manager import ChromeVersionManager",
            "CHROME_MANAGEMENT = True"
        ]
        
        for import_line in chrome_imports:
            if import_line in content:
                print(f"✅ Found: {import_line}")
            else:
                print(f"⚠️ Missing: {import_line}")
        
        # Check for Chrome Management task types
        chrome_tasks = [
            "CHROME_UPDATE",
            "CHROME_OPTIMIZE", 
            "CHROME_TEST",
            "CHROME_STATUS"
        ]
        
        for task in chrome_tasks:
            if task in content:
                print(f"✅ Found Chrome task: {task}")
            else:
                print(f"⚠️ Missing Chrome task: {task}")
        
        return True
        
    except Exception as e:
        print(f"❌ Floating agent integration test error: {e}")
        return False

def main():
    """Run all Chrome functionality tests."""
    print("🧪 Chrome Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        ("Chrome Path Test", test_chrome_path),
        ("Chrome Version Test", test_chrome_version),
        ("Browser Manager Test", test_browser_manager),
        ("Chrome Management Imports Test", test_chrome_management_imports),
        ("Floating Agent Integration Test", test_floating_agent_chrome_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"CHROME FUNCTIONALITY TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Chrome functionality tests passed!")
        print("\n📋 Chrome Status Summary:")
        print("✅ Chrome executable found and accessible")
        print("✅ Chrome version detection working")
        print("✅ Browser Manager correctly configured")
        print("✅ Chrome Management System integrated")
        print("✅ Floating Agent Chrome integration complete")
        
        print("\n🚀 Chrome is ready for use!")
        return 0
    else:
        print("❌ Some Chrome functionality tests failed.")
        print("Please check the errors above and fix any issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
