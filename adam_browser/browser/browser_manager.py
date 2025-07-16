"""
Browser Manager for Adam Browser

Manages Playwright browser instances with support for custom Chrome,
multiple contexts, and advanced automation features.
"""

import asyncio
import os
from typing import Optional, Dict, List, Any
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from loguru import logger

from ..config import config
from .dom_manipulator import DOMManipulator
from .screenshot_manager import ScreenshotManager
from .page_navigator import PageNavigator


class BrowserManager:
    """
    Manages browser instances and provides high-level automation interface.
    
    Supports multiple browsers, custom Chrome integration, and context management
    for isolated browsing sessions.
    """
    
    def __init__(self):
        """Initialize the browser manager."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Component managers
        self.dom_manipulator: Optional[DOMManipulator] = None
        self.screenshot_manager: Optional[ScreenshotManager] = None
        self.page_navigator: Optional[PageNavigator] = None
        
        # State tracking
        self.is_initialized = False
        self.current_url = ""
        self.page_title = ""
        
        # Browser configuration
        self.browser_type = config.browser.default_browser

        # Use embedded Chrome browser from Google directory
        embedded_chrome_path = Path(__file__).parent.parent.parent / "Google" / "Chrome" / "Application" / "chrome.exe"
        if embedded_chrome_path.exists():
            self.browser_path = str(embedded_chrome_path)
            logger.info(f"Using embedded Chrome browser: {self.browser_path}")
        else:
            self.browser_path = config.browser.browser_path
            logger.warning(f"Embedded Chrome not found, using configured path: {self.browser_path}")

        self.headless = config.browser.headless
        self.viewport = {
            'width': config.browser.viewport_width,
            'height': config.browser.viewport_height
        }
        
        logger.info("Browser manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Playwright and browser instance.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing browser manager...")
            
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser based on configuration
            if self.browser_type == "chromium":
                await self._launch_chromium()
            elif self.browser_type == "firefox":
                await self._launch_firefox()
            elif self.browser_type == "webkit":
                await self._launch_webkit()
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Create browser context
            await self._create_context()
            
            # Create initial page
            await self._create_page()
            
            # Initialize component managers
            self.dom_manipulator = DOMManipulator(self.page)
            self.screenshot_manager = ScreenshotManager(self.page)
            self.page_navigator = PageNavigator(self.page)
            
            self.is_initialized = True
            logger.info("Browser manager initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser manager: {e}")
            await self.cleanup()
            return False
    
    async def _launch_chromium(self) -> None:
        """Launch Chromium/Chrome browser."""

        # Calculate browser window position (maximized like in user's image)
        try:
            import wx
            app = wx.App(False)  # Create wx app if not exists
            display_size = wx.GetDisplaySize()
            browser_width = display_size.width  # Full width browser (maximized)
            browser_height = display_size.height - 80  # Leave minimal space for taskbar
            browser_x = 0  # Left edge of screen
            browser_y = 0  # Top of screen
            app.Destroy()
        except:
            # Fallback if wx not available
            browser_width = 1920  # Default full width for 1920px screen
            browser_height = 1000
            browser_x = 0
            browser_y = 0

        launch_options = {
            'headless': self.headless,
            'slow_mo': config.browser.slow_mo,
            'devtools': config.browser.devtools,
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                f'--user-agent={config.browser.user_agent}',
                f'--window-size={browser_width},{browser_height}',
                f'--window-position={browser_x},{browser_y}',
                '--disable-infobars',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-hang-monitor',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--no-default-browser-check',
                '--disable-domain-reliability',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
                '--disable-prompt-on-repost'
            ]
        }
        
        # Use custom Chrome if path is specified and exists
        if self.browser_path and os.path.exists(self.browser_path):
            launch_options['executable_path'] = self.browser_path
            logger.info(f"Using custom Chrome at: {self.browser_path}")
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        logger.info("Chromium browser launched")
    
    async def _launch_firefox(self) -> None:
        """Launch Firefox browser."""
        launch_options = {
            'headless': self.headless,
            'slow_mo': config.browser.slow_mo,
            'devtools': config.browser.devtools,
        }
        
        self.browser = await self.playwright.firefox.launch(**launch_options)
        logger.info("Firefox browser launched")
    
    async def _launch_webkit(self) -> None:
        """Launch WebKit browser."""
        launch_options = {
            'headless': self.headless,
            'slow_mo': config.browser.slow_mo,
        }
        
        self.browser = await self.playwright.webkit.launch(**launch_options)
        logger.info("WebKit browser launched")
    
    async def _create_context(self) -> None:
        """Create browser context with configuration."""
        context_options = {
            'viewport': self.viewport,
            'user_agent': config.browser.user_agent,
            'accept_downloads': True,
            'ignore_https_errors': True,
        }
        
        # Set download path if configured
        if hasattr(config.browser, 'downloads') and config.browser.downloads.get('download_path'):
            download_path = Path(config.browser.downloads['download_path'])
            download_path.mkdir(parents=True, exist_ok=True)
            context_options['accept_downloads'] = True
        
        self.context = await self.browser.new_context(**context_options)
        
        # Set default timeout
        self.context.set_default_timeout(config.browser.timeout)
        
        logger.info("Browser context created")
    
    async def _create_page(self) -> None:
        """Create initial page."""
        self.page = await self.context.new_page()
        
        # Set up page event listeners
        self.page.on("load", self._on_page_load)
        self.page.on("domcontentloaded", self._on_dom_ready)
        self.page.on("response", self._on_response)
        self.page.on("console", self._on_console)
        
        logger.info("Initial page created")
    
    async def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not initialized")
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                if '.' in url:
                    url = f"https://{url}"
                else:
                    # Treat as search query
                    url = f"https://www.google.com/search?q={url}"
            
            logger.info(f"Navigating to: {url}")
            
            response = await self.page.goto(url, wait_until='domcontentloaded')
            
            if response and response.ok:
                self.current_url = self.page.url
                self.page_title = await self.page.title()
                logger.info(f"Navigation successful: {self.page_title}")
                return True
            else:
                logger.error(f"Navigation failed: {response.status if response else 'No response'}")
                return False
                
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    async def click_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Click an element by selector.
        
        Args:
            selector: CSS selector or text to click
            timeout: Optional timeout override
            
        Returns:
            bool: True if click successful
        """
        if not self.dom_manipulator:
            logger.error("DOM manipulator not initialized")
            return False
        
        return await self.dom_manipulator.click_element(selector, timeout)
    
    async def type_text(self, selector: str, text: str, clear: bool = True) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: CSS selector for input element
            text: Text to type
            clear: Whether to clear existing text first
            
        Returns:
            bool: True if typing successful
        """
        if not self.dom_manipulator:
            logger.error("DOM manipulator not initialized")
            return False
        
        return await self.dom_manipulator.type_text(selector, text, clear)
    
    async def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """
        Scroll the page.
        
        Args:
            direction: "up" or "down"
            amount: Number of scroll steps
            
        Returns:
            bool: True if scroll successful
        """
        if not self.page_navigator:
            logger.error("Page navigator not initialized")
            return False
        
        return await self.page_navigator.scroll_page(direction, amount)
    
    async def take_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            str: Path to saved screenshot, or None if failed
        """
        if not self.screenshot_manager:
            logger.error("Screenshot manager not initialized")
            return None
        
        return await self.screenshot_manager.take_screenshot(filename)
    
    async def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector to wait for
            timeout: Optional timeout override
            
        Returns:
            bool: True if element appeared
        """
        try:
            if not self.page:
                return False
            
            timeout = timeout or config.browser.timeout
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
            
        except Exception as e:
            logger.error(f"Wait for element failed: {e}")
            return False
    
    async def get_page_content(self) -> str:
        """Get the current page's HTML content."""
        if not self.page:
            return ""
        
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return ""
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript on the current page.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Any: Result of script execution
        """
        if not self.page:
            return None
        
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return None
    
    async def new_page(self) -> Optional[Page]:
        """Create a new page in the current context."""
        if not self.context:
            return None
        
        try:
            new_page = await self.context.new_page()
            logger.info("New page created")
            return new_page
        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            return None
    
    async def close_page(self, page: Optional[Page] = None) -> None:
        """Close a page (current page if none specified)."""
        target_page = page or self.page
        
        if target_page:
            try:
                await target_page.close()
                if target_page == self.page:
                    self.page = None
                logger.info("Page closed")
            except Exception as e:
                logger.error(f"Failed to close page: {e}")
    
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        logger.info("Cleaning up browser resources...")
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.is_initialized = False
            logger.info("Browser cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    def _on_page_load(self, page: Page) -> None:
        """Handle page load event."""
        logger.debug(f"Page loaded: {page.url}")
        self.current_url = page.url
    
    def _on_dom_ready(self, page: Page) -> None:
        """Handle DOM content loaded event."""
        logger.debug(f"DOM ready: {page.url}")
    
    def _on_response(self, response) -> None:
        """Handle HTTP response event."""
        if response.status >= 400:
            logger.warning(f"HTTP {response.status}: {response.url}")
    
    def _on_console(self, msg) -> None:
        """Handle browser console messages."""
        if msg.type == "error":
            logger.warning(f"Browser console error: {msg.text}")
        elif config.debug_mode:
            logger.debug(f"Browser console: {msg.text}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current browser status."""
        return {
            'initialized': self.is_initialized,
            'browser_type': self.browser_type,
            'current_url': self.current_url,
            'page_title': self.page_title,
            'headless': self.headless,
            'viewport': self.viewport,
            'has_page': self.page is not None,
            'has_context': self.context is not None,
            'has_browser': self.browser is not None,
        }
