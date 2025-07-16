"""
Adam Browser - Autonomous AI Agent Browser Application

A sophisticated browser automation system that uses AI/NLP to understand
natural language commands and execute complex web interactions including
form filling, navigation, travel booking, and map directions.

Key Features:
- Natural language command processing using BERT
- Playwright-based browser automation
- Specialized modules for Expedia and Google Maps
- wxPython GUI with real-time logging
- Encrypted credential storage
- SQLite-based session logging
- Windows installer generation

Author: Adam Browser Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Adam Browser Team"
__email__ = "team@adambrowser.ai"
__license__ = "MIT"

# Core imports for easy access
from .config import Config
from .agent import AdamAgent
from .browser import BrowserManager
from .gui import AdamMainWindow

__all__ = [
    "Config",
    "AdamAgent", 
    "BrowserManager",
    "AdamMainWindow",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
