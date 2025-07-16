"""
Main entry point for Adam Browser

Provides both GUI and CLI interfaces for the Adam Browser AI Agent.
Handles application initialization, configuration loading, and startup.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
from typing import Optional
import wx
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adam_browser.config import config
from adam_browser.gui import AdamMainWindow, SplashScreen
from adam_browser.agent import AdamAgent
from adam_browser.cli import AdamCLI


class AdamBrowserApp(wx.App):
    """
    Main wxPython application class for Adam Browser.
    
    Handles application initialization, splash screen, and main window creation.
    """
    
    def __init__(self, show_splash: bool = True):
        """
        Initialize the application.
        
        Args:
            show_splash: Whether to show splash screen
        """
        self.show_splash = show_splash
        self.splash: Optional[SplashScreen] = None
        self.main_window: Optional[AdamMainWindow] = None
        
        super().__init__(False)  # Don't redirect stdout/stderr
    
    def OnInit(self) -> bool:
        """Initialize the application."""
        try:
            # Set application name
            self.SetAppName(config.app_name)
            self.SetAppDisplayName(f"{config.app_name} v{config.version}")
            
            # Show splash screen if enabled
            if self.show_splash and config.gui.show_splash:
                self.splash = SplashScreen()
                self.splash.Show()
                wx.Yield()  # Process splash screen events
            
            # Create main window
            self.main_window = AdamMainWindow()
            
            # Hide splash and show main window
            if self.splash:
                self.splash.Destroy()
                self.splash = None
            
            self.main_window.Show()
            self.SetTopWindow(self.main_window)
            
            logger.info(f"{config.app_name} GUI started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GUI application: {e}")
            
            # Show error dialog
            wx.MessageBox(
                f"Failed to start {config.app_name}:\n\n{str(e)}",
                "Startup Error",
                wx.OK | wx.ICON_ERROR
            )
            
            return False
    
    def OnExit(self) -> int:
        """Handle application exit."""
        logger.info(f"{config.app_name} GUI shutting down")
        return 0


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        debug: Enable debug logging
        log_file: Optional log file path
    """
    # Remove default logger
    logger.remove()
    
    # Set log level
    log_level = "DEBUG" if debug else config.log_level
    
    # Console logging
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logging
    if log_file or config.logging.get('log_to_file', False):
        log_path = log_file or config.logging.get('log_file_path', 'logs/adam.log')
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        logger.add(
            log_path,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )
        
        logger.info(f"Logging to file: {log_path}")


def check_dependencies() -> bool:
    """
    Check if all required dependencies are available.
    
    Returns:
        bool: True if all dependencies are available
    """
    missing_deps = []
    
    try:
        import playwright
    except ImportError:
        missing_deps.append("playwright")
    
    try:
        import torch
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import transformers
    except ImportError:
        missing_deps.append("transformers")
    
    try:
        import wx
    except ImportError:
        missing_deps.append("wxPython")
    
    if missing_deps:
        logger.error(f"Missing required dependencies: {', '.join(missing_deps)}")
        logger.info("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    
    return True


def install_playwright_browsers() -> bool:
    """
    Install Playwright browsers if needed.
    
    Returns:
        bool: True if browsers are available
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Check if Chromium is available
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                return True
            except Exception:
                logger.info("Installing Playwright browsers...")
                os.system("playwright install chromium")
                return True
                
    except Exception as e:
        logger.error(f"Failed to check/install Playwright browsers: {e}")
        return False


def main() -> int:
    """
    Main entry point for Adam Browser.
    
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(
        description="Adam Browser - Autonomous AI Agent Browser Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  adam-browser                    # Start GUI application
  adam-browser --cli              # Start CLI interface
  adam-browser --debug            # Start with debug logging
  adam-browser --config custom.toml  # Use custom config file
  adam-browser --headless         # Start in headless mode
        """
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true",
        help="Start CLI interface instead of GUI"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true", 
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: adam.config.toml)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Disable splash screen"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {config.version}"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(debug=args.debug, log_file=args.log_file)
    
    logger.info(f"Starting {config.app_name} v{config.version}")
    
    # Load custom config if specified
    if args.config:
        config.config_path = args.config
        config.load_config()
    
    # Apply command line overrides
    if args.headless:
        config.browser.headless = True
    
    if args.debug:
        config.debug_mode = True
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Install Playwright browsers if needed
    if not install_playwright_browsers():
        logger.warning("Playwright browsers may not be available")
    
    try:
        if args.cli:
            # Start CLI interface
            logger.info("Starting CLI interface...")
            cli = AdamCLI()
            return asyncio.run(cli.run())
        else:
            # Start GUI application
            logger.info("Starting GUI interface...")
            app = AdamBrowserApp(show_splash=not args.no_splash)
            return app.MainLoop()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
