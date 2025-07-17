#!/usr/bin/env python3
"""
Simple Launcher for Adam Browser Agent

This script provides a simple way to launch the embedded Chrome floating agent
with proper error handling and user feedback.
"""

import sys
import os
from pathlib import Path
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'wx',
        'playwright', 
        'loguru',
        'PIL',
        'cv2',
        'pytesseract'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - MISSING")
    
    return missing_modules

def check_chrome_browser():
    """Check if embedded Chrome browser exists"""
    chrome_path = Path(r"D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe")
    
    if chrome_path.exists():
        print(f"✅ Embedded Chrome found: {chrome_path}")
        return True
    else:
        print(f"⚠️ Embedded Chrome not found: {chrome_path}")
        print("   Agent will use system Chrome as fallback")
        return False

def launch_agent():
    """Launch the embedded Chrome floating agent"""
    
    # Get the script path
    script_dir = Path(__file__).parent.parent
    agent_script = script_dir / "embedded_chrome_floating_agent.py"
    
    if not agent_script.exists():
        print(f"❌ Agent script not found: {agent_script}")
        return False
    
    print(f"🚀 Launching agent: {agent_script}")
    
    try:
        # Change to the project directory
        os.chdir(script_dir)
        
        # Launch the agent
        subprocess.run([sys.executable, str(agent_script)], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching agent: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Launch cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main launcher function"""
    print("🤖 Adam Browser Agent Launcher")
    print("=" * 40)
    print()
    
    print("📋 Checking dependencies...")
    missing_deps = check_dependencies()
    print()
    
    print("🌐 Checking Chrome browser...")
    chrome_available = check_chrome_browser()
    print()
    
    if missing_deps:
        print("⚠️ Missing dependencies detected:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print()
        print("💡 To install missing dependencies, run:")
        print("   pip install wx-python playwright loguru pillow opencv-python pytesseract")
        print()
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Launch cancelled")
            return False
    
    print("🚀 Starting Adam Browser Agent...")
    print("   (Close this window or press Ctrl+C to stop)")
    print()
    
    # Small delay for user to read messages
    time.sleep(2)
    
    success = launch_agent()
    
    if success:
        print("✅ Agent launched successfully!")
    else:
        print("❌ Failed to launch agent")
        input("Press Enter to exit...")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        input("Press Enter to exit...")
