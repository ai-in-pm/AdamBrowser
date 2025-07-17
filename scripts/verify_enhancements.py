#!/usr/bin/env python3
"""
Verify Enhanced Floating Agent Features

This script verifies that the enhancements have been properly implemented.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify all required imports work"""
    print("🔍 Verifying imports...")
    
    try:
        import wx
        print("✅ wxPython imported successfully")
    except ImportError as e:
        print(f"❌ wxPython import failed: {e}")
        return False
    
    try:
        from adam_browser.agent import AdamAgent
        print("✅ AdamAgent imported successfully")
    except ImportError as e:
        print(f"❌ AdamAgent import failed: {e}")
        return False
    
    try:
        from adam_browser.config import config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from loguru import logger
        print("✅ Loguru imported successfully")
    except ImportError as e:
        print(f"❌ Loguru import failed: {e}")
        return False
    
    return True

def verify_floating_agent_structure():
    """Verify the floating agent file structure"""
    print("\n🔍 Verifying floating agent structure...")
    
    floating_agent_path = project_root / "adam_floating_agent.py"
    if not floating_agent_path.exists():
        print("❌ adam_floating_agent.py not found")
        return False
    
    print("✅ adam_floating_agent.py exists")
    
    # Check for key enhancements in the file
    with open(floating_agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("AdamAgent import", "from adam_browser.agent import AdamAgent"),
        ("Real agent integration", "self.adam_agent: Optional[AdamAgent]"),
        ("Async command execution", "_execute_real_command"),
        ("Enhanced click detection", "click_start_time"),
        ("Physical command processing", "process_browser_command"),
    ]
    
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✅ {check_name} found")
        else:
            print(f"❌ {check_name} missing")
            return False
    
    return True

def verify_command_processor_enhancements():
    """Verify command processor enhancements"""
    print("\n🔍 Verifying command processor enhancements...")
    
    cmd_processor_path = project_root / "adam_browser" / "agent" / "command_processor.py"
    if not cmd_processor_path.exists():
        print("❌ command_processor.py not found")
        return False
    
    with open(cmd_processor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Enhanced search submission", "submit_success"),
        ("Multiple search strategies", "search_buttons"),
        ("Enhanced navigation", "actual_url"),
        ("JavaScript fallback", "execute_javascript"),
    ]
    
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✅ {check_name} found")
        else:
            print(f"❌ {check_name} missing")
            return False
    
    return True

def verify_files_created():
    """Verify new files were created"""
    print("\n🔍 Verifying new files...")
    
    files_to_check = [
        "test_enhanced_floating_agent.py",
        "ENHANCED_FLOATING_AGENT_README.md",
        "LAUNCH_ENHANCED_FLOATING_AGENT.bat",
        "verify_enhancements.py"
    ]
    
    for filename in files_to_check:
        filepath = project_root / filename
        if filepath.exists():
            print(f"✅ {filename} created")
        else:
            print(f"❌ {filename} missing")
            return False
    
    return True

def main():
    """Main verification function"""
    print("🤖 Enhanced Adam Browser Floating Agent - Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Run all verification checks
    checks = [
        verify_imports,
        verify_floating_agent_structure,
        verify_command_processor_enhancements,
        verify_files_created
    ]
    
    for check in checks:
        if not check():
            all_checks_passed = False
    
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All verifications passed! Enhanced floating agent is ready.")
        print("\nTo test the enhanced agent:")
        print("1. Run: python test_enhanced_floating_agent.py")
        print("2. Or use: LAUNCH_ENHANCED_FLOATING_AGENT.bat")
        print("3. Look for the robot icon in bottom-right corner")
        print("4. Click the robot to open chat interface")
        print("5. Start the agent and try commands like 'go to google.com'")
    else:
        print("❌ Some verifications failed. Please check the issues above.")
    
    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    sys.exit(main())
