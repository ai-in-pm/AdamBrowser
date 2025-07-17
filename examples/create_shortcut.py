#!/usr/bin/env python3
"""
Create Desktop Shortcut for Embedded Chrome Floating Agent

This script creates a Windows shortcut (.lnk file) for the embedded_chrome_floating_agent.py
that can be accessed without an IDE.
"""

import os
import sys
from pathlib import Path
import subprocess

def create_windows_shortcut():
    """Create a Windows shortcut using PowerShell"""
    
    # Get the absolute path to the Python script
    script_dir = Path(__file__).parent.parent
    target_script = script_dir / "embedded_chrome_floating_agent.py"
    
    # Get Python executable path
    python_exe = sys.executable
    
    # Shortcut details
    shortcut_name = "Adam Browser Agent"
    shortcut_path = script_dir / "examples" / f"{shortcut_name}.lnk"
    
    # Create PowerShell command to create shortcut
    powershell_cmd = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{python_exe}"
$Shortcut.Arguments = '"{target_script}"'
$Shortcut.WorkingDirectory = "{script_dir}"
$Shortcut.Description = "Adam Browser - Embedded Chrome Floating Agent"
$Shortcut.IconLocation = "{python_exe},0"
$Shortcut.Save()
'''
    
    try:
        # Execute PowerShell command
        result = subprocess.run([
            "powershell", "-Command", powershell_cmd
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ Shortcut created successfully!")
        print(f"📁 Location: {shortcut_path}")
        print(f"🎯 Target: {target_script}")
        print(f"🐍 Python: {python_exe}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating shortcut: {e}")
        print(f"PowerShell output: {e.stdout}")
        print(f"PowerShell error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_batch_file():
    """Create a batch file as an alternative launcher"""
    
    script_dir = Path(__file__).parent.parent
    target_script = script_dir / "embedded_chrome_floating_agent.py"
    python_exe = sys.executable
    
    batch_content = f'''@echo off
title Adam Browser Agent
echo Starting Adam Browser - Embedded Chrome Floating Agent...
echo.
cd /d "{script_dir}"
"{python_exe}" "{target_script}"
pause
'''
    
    batch_path = script_dir / "examples" / "Adam Browser Agent.bat"
    
    try:
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Batch file created successfully!")
        print(f"📁 Location: {batch_path}")
        print(f"💡 Double-click the .bat file to run the agent")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating batch file: {e}")
        return False

def main():
    """Main function to create shortcuts"""
    print("🚀 Creating desktop shortcuts for Adam Browser Agent...")
    print("=" * 60)
    
    # Check if target script exists
    script_dir = Path(__file__).parent.parent
    target_script = script_dir / "embedded_chrome_floating_agent.py"
    
    if not target_script.exists():
        print(f"❌ Target script not found: {target_script}")
        return False
    
    print(f"✅ Target script found: {target_script}")
    print(f"🐍 Python executable: {sys.executable}")
    print()
    
    # Create Windows shortcut
    print("Creating Windows shortcut (.lnk)...")
    shortcut_success = create_windows_shortcut()
    print()
    
    # Create batch file as alternative
    print("Creating batch file launcher (.bat)...")
    batch_success = create_batch_file()
    print()
    
    if shortcut_success or batch_success:
        print("🎉 SUCCESS! Shortcuts created in the examples folder.")
        print()
        print("📋 How to use:")
        if shortcut_success:
            print("   • Double-click 'Adam Browser Agent.lnk' to launch")
        if batch_success:
            print("   • Double-click 'Adam Browser Agent.bat' to launch")
        print()
        print("💡 You can copy these files to your desktop or any other location")
        print("   for easy access without opening an IDE!")
        
        return True
    else:
        print("❌ Failed to create shortcuts")
        return False

if __name__ == "__main__":
    main()
