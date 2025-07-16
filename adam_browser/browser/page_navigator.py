"""
Page Navigator for Adam Browser

Provides intelligent page navigation, scrolling, and interaction utilities
with smooth animations and smart positioning.
"""

import asyncio
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import Page
from loguru import logger

from ..config import config


class PageNavigator:
    """
    Intelligent page navigation and scrolling manager.
    
    Provides smooth scrolling, smart positioning, and navigation
    utilities with configurable behavior and error handling.
    """
    
    def __init__(self, page: Page):
        """
        Initialize page navigator.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.current_scroll_position = 0
        self.page_height = 0
        self.viewport_height = 0
        
        logger.info("Page navigator initialized")
    
    async def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """
        Scroll the page in the specified direction.
        
        Args:
            direction: "up", "down", "top", "bottom"
            amount: Number of scroll steps (for up/down)
            
        Returns:
            bool: True if scroll successful
        """
        try:
            await self._update_page_info()
            
            if direction.lower() == "down":
                return await self._scroll_down(amount)
            elif direction.lower() == "up":
                return await self._scroll_up(amount)
            elif direction.lower() == "top":
                return await self._scroll_to_top()
            elif direction.lower() == "bottom":
                return await self._scroll_to_bottom()
            else:
                logger.warning(f"Unknown scroll direction: {direction}")
                return False
                
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    async def scroll_to_element(self, selector: str, 
                               offset: int = 0, smooth: bool = True) -> bool:
        """
        Scroll to bring an element into view.
        
        Args:
            selector: Element selector
            offset: Additional offset from element position
            smooth: Whether to use smooth scrolling
            
        Returns:
            bool: True if scroll successful
        """
        try:
            # Wait for element
            element = await self.page.wait_for_selector(selector, timeout=5000)
            if not element:
                logger.warning(f"Element not found for scroll: {selector}")
                return False
            
            # Scroll to element
            await element.scroll_into_view_if_needed()
            
            # Apply additional offset if specified
            if offset != 0:
                await self.page.evaluate(f"window.scrollBy(0, {offset})")
            
            # Add smooth scrolling effect if requested
            if smooth:
                await asyncio.sleep(0.5)  # Allow scroll animation
            
            logger.debug(f"Scrolled to element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Scroll to element failed for {selector}: {e}")
            return False
    
    async def scroll_by_pixels(self, x: int = 0, y: int = 0, smooth: bool = True) -> bool:
        """
        Scroll by specific pixel amounts.
        
        Args:
            x: Horizontal scroll amount (positive = right)
            y: Vertical scroll amount (positive = down)
            smooth: Whether to use smooth scrolling
            
        Returns:
            bool: True if scroll successful
        """
        try:
            if smooth:
                # Smooth scrolling with animation
                await self.page.evaluate(f"""
                    window.scrollBy({{
                        left: {x},
                        top: {y},
                        behavior: 'smooth'
                    }});
                """)
                await asyncio.sleep(1)  # Wait for animation
            else:
                # Instant scrolling
                await self.page.evaluate(f"window.scrollBy({x}, {y})")
            
            await self._update_scroll_position()
            logger.debug(f"Scrolled by pixels: x={x}, y={y}")
            return True
            
        except Exception as e:
            logger.error(f"Scroll by pixels failed: {e}")
            return False
    
    async def get_scroll_position(self) -> Tuple[int, int]:
        """
        Get current scroll position.
        
        Returns:
            Tuple of (x, y) scroll position
        """
        try:
            position = await self.page.evaluate("""
                () => ({
                    x: window.pageXOffset || document.documentElement.scrollLeft,
                    y: window.pageYOffset || document.documentElement.scrollTop
                })
            """)
            
            return (position['x'], position['y'])
            
        except Exception as e:
            logger.error(f"Failed to get scroll position: {e}")
            return (0, 0)
    
    async def get_page_dimensions(self) -> Dict[str, int]:
        """
        Get page dimensions and viewport info.
        
        Returns:
            Dict containing page and viewport dimensions
        """
        try:
            dimensions = await self.page.evaluate("""
                () => ({
                    pageWidth: document.documentElement.scrollWidth,
                    pageHeight: document.documentElement.scrollHeight,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    scrollX: window.pageXOffset || document.documentElement.scrollLeft,
                    scrollY: window.pageYOffset || document.documentElement.scrollTop
                })
            """)
            
            return dimensions
            
        except Exception as e:
            logger.error(f"Failed to get page dimensions: {e}")
            return {}
    
    async def is_at_top(self) -> bool:
        """Check if page is scrolled to the top."""
        try:
            scroll_y = await self.page.evaluate("window.pageYOffset || document.documentElement.scrollTop")
            return scroll_y <= 10  # Allow small tolerance
        except Exception:
            return False
    
    async def is_at_bottom(self) -> bool:
        """Check if page is scrolled to the bottom."""
        try:
            result = await self.page.evaluate("""
                () => {
                    const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                    const windowHeight = window.innerHeight;
                    const documentHeight = document.documentElement.scrollHeight;
                    return scrollY + windowHeight >= documentHeight - 10;
                }
            """)
            return result
        except Exception:
            return False
    
    async def _scroll_down(self, amount: int) -> bool:
        """Scroll down by specified amount."""
        scroll_distance = config.automation.scroll_speed * amount
        
        for i in range(amount):
            await self.page.evaluate(f"""
                window.scrollBy({{
                    top: {config.automation.scroll_speed},
                    behavior: 'smooth'
                }});
            """)
            await asyncio.sleep(0.3)  # Pause between scrolls
        
        await self._update_scroll_position()
        logger.debug(f"Scrolled down {amount} steps")
        return True
    
    async def _scroll_up(self, amount: int) -> bool:
        """Scroll up by specified amount."""
        scroll_distance = -config.automation.scroll_speed * amount
        
        for i in range(amount):
            await self.page.evaluate(f"""
                window.scrollBy({{
                    top: {-config.automation.scroll_speed},
                    behavior: 'smooth'
                }});
            """)
            await asyncio.sleep(0.3)  # Pause between scrolls
        
        await self._update_scroll_position()
        logger.debug(f"Scrolled up {amount} steps")
        return True
    
    async def _scroll_to_top(self) -> bool:
        """Scroll to the top of the page."""
        await self.page.evaluate("""
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        """)
        await asyncio.sleep(1)  # Wait for animation
        
        await self._update_scroll_position()
        logger.debug("Scrolled to top")
        return True
    
    async def _scroll_to_bottom(self) -> bool:
        """Scroll to the bottom of the page."""
        await self.page.evaluate("""
            window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: 'smooth'
            });
        """)
        await asyncio.sleep(1)  # Wait for animation
        
        await self._update_scroll_position()
        logger.debug("Scrolled to bottom")
        return True
    
    async def _update_page_info(self):
        """Update cached page information."""
        try:
            dimensions = await self.get_page_dimensions()
            self.page_height = dimensions.get('pageHeight', 0)
            self.viewport_height = dimensions.get('viewportHeight', 0)
        except Exception as e:
            logger.warning(f"Failed to update page info: {e}")
    
    async def _update_scroll_position(self):
        """Update cached scroll position."""
        try:
            _, y = await self.get_scroll_position()
            self.current_scroll_position = y
        except Exception as e:
            logger.warning(f"Failed to update scroll position: {e}")
    
    async def smooth_scroll_to_position(self, x: int, y: int, duration: float = 1.0) -> bool:
        """
        Smoothly scroll to a specific position over time.
        
        Args:
            x: Target X position
            y: Target Y position
            duration: Animation duration in seconds
            
        Returns:
            bool: True if scroll successful
        """
        try:
            # Get current position
            current_x, current_y = await self.get_scroll_position()
            
            # Calculate steps
            steps = max(10, int(duration * 30))  # 30 FPS
            step_duration = duration / steps
            
            x_step = (x - current_x) / steps
            y_step = (y - current_y) / steps
            
            # Animate scroll
            for i in range(steps):
                target_x = current_x + (x_step * (i + 1))
                target_y = current_y + (y_step * (i + 1))
                
                await self.page.evaluate(f"window.scrollTo({target_x}, {target_y})")
                await asyncio.sleep(step_duration)
            
            # Ensure final position
            await self.page.evaluate(f"window.scrollTo({x}, {y})")
            
            logger.debug(f"Smooth scrolled to position: ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Smooth scroll failed: {e}")
            return False
    
    async def auto_scroll_page(self, direction: str = "down", 
                              max_scrolls: int = 10, delay: float = 2.0) -> int:
        """
        Automatically scroll the page with delays.
        
        Args:
            direction: Scroll direction ("up" or "down")
            max_scrolls: Maximum number of scrolls
            delay: Delay between scrolls in seconds
            
        Returns:
            int: Number of scrolls performed
        """
        try:
            scroll_count = 0
            
            for i in range(max_scrolls):
                # Check if we can scroll further
                if direction == "down" and await self.is_at_bottom():
                    break
                elif direction == "up" and await self.is_at_top():
                    break
                
                # Perform scroll
                if await self.scroll_page(direction, 1):
                    scroll_count += 1
                    await asyncio.sleep(delay)
                else:
                    break
            
            logger.info(f"Auto-scroll completed: {scroll_count} scrolls")
            return scroll_count
            
        except Exception as e:
            logger.error(f"Auto-scroll failed: {e}")
            return 0
