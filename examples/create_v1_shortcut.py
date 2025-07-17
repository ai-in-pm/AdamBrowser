#!/usr/bin/env python3
"""
Create Desktop Shortcut for Adam Browser Embedded Chrome Agent v1
This script creates a Windows shortcut (.lnk) file for easy access to the v1 application.
"""

import os
import sys
from pathlib import Path

def create_shortcut_with_powershell():
    """Create shortcut using PowerShell (works without additional dependencies)"""
    
    # Paths
    script_path = Path(r"D:\science_projects\adam_browser\embedded_chrome_floating_agent_v1.py")
    shortcut_dir = Path(r"D:\science_projects\adam_browser\examples")
    shortcut_path = shortcut_dir / "Adam Browser - Embedded Chrome Agent v1.lnk"
    
    # Get Python executable path
    python_exe = sys.executable
    
    # PowerShell script to create shortcut
    powershell_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{python_exe}"
$Shortcut.Arguments = '"{script_path}"'
$Shortcut.WorkingDirectory = "{script_path.parent}"
$Shortcut.Description = "Adam Browser - Embedded Chrome Agent v1 - AI-powered browser automation"
$Shortcut.Save()
'''
    
    try:
        # Execute PowerShell script
        import subprocess
        result = subprocess.run([
            "powershell", "-Command", powershell_script
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"✅ Shortcut created successfully!")
            print(f"📁 Location: {shortcut_path}")
            print(f"🎯 Target: {script_path}")
            print(f"🐍 Python: {python_exe}")
            return True
        else:
            print(f"❌ PowerShell error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False

def create_desktop_shortcut():
    """Create a shortcut on the desktop as well"""
    
    # Paths
    script_path = Path(r"D:\science_projects\adam_browser\embedded_chrome_floating_agent_v1.py")
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / "Adam Browser - Embedded Chrome Agent v1.lnk"
    
    # Get Python executable path
    python_exe = sys.executable
    
    # PowerShell script to create shortcut
    powershell_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{python_exe}"
$Shortcut.Arguments = '"{script_path}"'
$Shortcut.WorkingDirectory = "{script_path.parent}"
$Shortcut.Description = "Adam Browser - Embedded Chrome Agent v1 - AI-powered browser automation"
$Shortcut.Save()
'''
    
    try:
        # Execute PowerShell script
        import subprocess
        result = subprocess.run([
            "powershell", "-Command", powershell_script
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"✅ Desktop shortcut created successfully!")
            print(f"📁 Location: {shortcut_path}")
            return True
        else:
            print(f"❌ PowerShell error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating desktop shortcut: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Creating shortcuts for Adam Browser - Embedded Chrome Agent v1")
    print("=" * 70)
    
    # Create shortcut in examples folder
    examples_success = create_shortcut_with_powershell()
    
    # Ask if user wants desktop shortcut too
    if examples_success:
        print("\n" + "=" * 70)
        print("📋 Shortcut created in examples folder!")
        print("\n🖥️ Would you like to create a desktop shortcut as well? (y/n)")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes']:
                desktop_success = create_desktop_shortcut()
                if desktop_success:
                    print("✅ Desktop shortcut created!")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("🎉 Setup complete!")
    print("\n📋 How to use:")
    print("• Double-click the .lnk file to run the application")
    print("• Or use the .bat file for a console version")
    print("• The floating robot icon will appear in the bottom-right corner")
    print("• Single-click the robot to open the Chrome chat interface")
    print("• Use natural language commands like 'go to google.com'")
    print("\n🚀 Ready to automate your browsing experience!")
