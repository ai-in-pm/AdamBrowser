"""
Adam Browser - Main Entry Point

This is the main entry point for the Adam Browser application.
It provides a simple interface to launch the application.
"""

import sys
from pathlib import Path

# Add the adam_browser package to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from adam_browser.main import main

if __name__ == '__main__':
    sys.exit(main())
