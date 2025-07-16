"""
Browser Automation Module for Adam Browser

Provides Playwright-based browser automation with support for multiple
browsers, custom Chrome integration, and advanced DOM manipulation.

Components:
- BrowserManager: Main browser control interface
- DOMManipulator: Advanced DOM interaction utilities
- ScreenshotManager: Screenshot capture and management
- PageNavigator: Navigation and page loading utilities
"""

from .browser_manager import BrowserManager
from .dom_manipulator import DOMManipulator
from .screenshot_manager import ScreenshotManager
from .page_navigator import PageNavigator

__all__ = [
    "BrowserManager",
    "DOMManipulator",
    "ScreenshotManager", 
    "PageNavigator",
]
