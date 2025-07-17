#!/usr/bin/env python3
"""
Test Enhanced Floating Agent with Physical Browser Control

This script tests the enhanced floating agent that connects to the real Adam Browser
agent for physical command execution.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the enhanced floating agent
from adam_floating_agent import main

if __name__ == '__main__':
    print("🤖 Testing Enhanced Adam Browser Floating Agent")
    print("=" * 60)
    print("Features being tested:")
    print("✅ Physical browser command execution")
    print("✅ Real Adam Agent integration")
    print("✅ Robot icon click to open chat")
    print("✅ Actual browser automation")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Look for the robot icon in the bottom-right corner")
    print("2. Double-click or right-click the robot to open chat")
    print("3. Click 'Start Agent' to initialize the browser")
    print("4. Try commands like:")
    print("   - 'go to google.com'")
    print("   - 'search for Python tutorials'")
    print("   - 'take a screenshot'")
    print("   - 'scroll down'")
    print()
    print("The agent will now physically control your browser!")
    print("=" * 60)
    
    # Launch the enhanced floating agent
    main()
