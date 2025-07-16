"""
GUI Module for Adam Browser

Provides wxPython-based graphical user interface with real-time logging,
agent control, configuration management, and system tray integration.

Components:
- AdamMainWindow: Main application window
- LogViewer: Real-time log display with filtering
- ConfigPanel: Configuration management interface
- TrayIcon: System tray integration
- SplashScreen: Application startup screen
"""

from .main_window import AdamMainWindow
from .log_viewer import LogViewer
from .config_panel import ConfigPanel
from .tray_icon import TrayIcon
from .splash_screen import SplashScreen

__all__ = [
    "AdamMainWindow",
    "LogViewer",
    "ConfigPanel",
    "TrayIcon",
    "SplashScreen",
]
