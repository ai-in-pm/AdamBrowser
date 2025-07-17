#!/usr/bin/env python3
"""
Adam Browser GUI Launcher

Simple launcher that starts the primary GUI (embedded Chrome floating agent)
with fallback to secondary GUI (simple floating agent).
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Adam Browser GUI"""
    project_root = Path(__file__).parent
    
    print("🤖 Adam Browser GUI Launcher")
    print("=" * 40)
    
    # Try primary GUI first (embedded Chrome floating agent)
    primary_gui = project_root / "embedded_chrome_floating_agent.py"
    secondary_gui = project_root / "simple_floating_agent.py"
    
    if primary_gui.exists():
        print("🚀 Launching Primary GUI: Embedded Chrome Floating Agent")
        try:
            subprocess.run([sys.executable, str(primary_gui)], check=True)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Primary GUI failed: {e}")
            print("🔄 Trying secondary GUI...")
    
    # Fallback to secondary GUI
    if secondary_gui.exists():
        print("🚀 Launching Secondary GUI: Simple Floating Agent")
        try:
            subprocess.run([sys.executable, str(secondary_gui)], check=True)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Secondary GUI failed: {e}")
    
    print("❌ No GUI available to launch")
    return 1

if __name__ == '__main__':
    sys.exit(main())
