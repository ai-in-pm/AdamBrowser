"""
DOM Manipulator for Adam Browser

Provides advanced DOM interaction capabilities with smart element detection,
fuzzy matching, and fallback strategies for robust web automation.
"""

import asyncio
import re
from typing import Optional, List, Dict, Any, Union
from playwright.async_api import Page, ElementHandle, TimeoutError as PlaywrightTimeoutError
from loguru import logger

from ..config import config


class DOMManipulator:
    """
    Advanced DOM manipulation with intelligent element detection.
    
    Provides robust element interaction with multiple selector strategies,
    fuzzy matching, and automatic fallback mechanisms.
    """
    
    def __init__(self, page: Page):
        """
        Initialize DOM manipulator.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        
        # Selector strategies in priority order
        self.selector_strategies = [
            'id',
            'name', 
            'aria-label',
            'placeholder',
            'text',
            'css',
            'xpath'
        ]
        
        logger.info("DOM manipulator initialized")
    
    async def click_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Click an element using smart selector strategies.
        
        Args:
            selector: Element selector or description
            timeout: Optional timeout override
            
        Returns:
            bool: True if click successful
        """
        timeout = timeout or config.browser.timeout
        
        try:
            # Try direct selector first
            if await self._try_click_direct(selector, timeout):
                return True
            
            # Try smart selector strategies
            element = await self._find_element_smart(selector, timeout)
            if element:
                await element.click(timeout=timeout)
                logger.debug(f"Clicked element: {selector}")
                return True
            
            logger.warning(f"Could not find element to click: {selector}")
            return False
            
        except Exception as e:
            logger.error(f"Click failed for {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, text: str, clear: bool = True, 
                       timeout: Optional[int] = None) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: Element selector
            text: Text to type
            clear: Whether to clear existing text
            timeout: Optional timeout override
            
        Returns:
            bool: True if typing successful
        """
        timeout = timeout or config.browser.timeout
        
        try:
            # Find input element
            element = await self._find_input_element(selector, timeout)
            if not element:
                return False
            
            # Clear existing text if requested
            if clear:
                await element.clear(timeout=timeout)
            
            # Type text with delay
            await element.type(text, delay=config.automation.type_delay, timeout=timeout)
            
            logger.debug(f"Typed text into {selector}: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Type failed for {selector}: {e}")
            return False
    
    async def get_element_text(self, selector: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get text content of an element.
        
        Args:
            selector: Element selector
            timeout: Optional timeout override
            
        Returns:
            str: Element text content, or None if not found
        """
        timeout = timeout or config.browser.timeout
        
        try:
            element = await self._find_element_smart(selector, timeout)
            if element:
                text = await element.text_content()
                return text
            
            return None
            
        except Exception as e:
            logger.error(f"Get text failed for {selector}: {e}")
            return None
    
    async def get_element_attribute(self, selector: str, attribute: str, 
                                   timeout: Optional[int] = None) -> Optional[str]:
        """
        Get attribute value of an element.
        
        Args:
            selector: Element selector
            attribute: Attribute name
            timeout: Optional timeout override
            
        Returns:
            str: Attribute value, or None if not found
        """
        timeout = timeout or config.browser.timeout
        
        try:
            element = await self._find_element_smart(selector, timeout)
            if element:
                value = await element.get_attribute(attribute)
                return value
            
            return None
            
        except Exception as e:
            logger.error(f"Get attribute failed for {selector}.{attribute}: {e}")
            return None
    
    async def is_element_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible.
        
        Args:
            selector: Element selector
            timeout: Optional timeout override
            
        Returns:
            bool: True if element is visible
        """
        timeout = timeout or config.browser.timeout
        
        try:
            element = await self._find_element_smart(selector, timeout)
            if element:
                return await element.is_visible()
            
            return False
            
        except Exception as e:
            logger.error(f"Visibility check failed for {selector}: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: Element selector
            timeout: Optional timeout override
            
        Returns:
            bool: True if element appeared
        """
        timeout = timeout or config.browser.timeout
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
        except Exception as e:
            logger.error(f"Wait for element failed for {selector}: {e}")
            return False
    
    async def _try_click_direct(self, selector: str, timeout: int) -> bool:
        """Try clicking with direct selector."""
        try:
            await self.page.click(selector, timeout=timeout)
            return True
        except Exception:
            return False
    
    async def _find_element_smart(self, selector: str, timeout: int) -> Optional[ElementHandle]:
        """Find element using smart strategies."""
        # Try direct selector first
        try:
            element = await self.page.wait_for_selector(selector, timeout=1000)
            if element:
                return element
        except Exception:
            pass
        
        # Try different selector strategies
        strategies = [
            lambda s: f'#{s}',  # ID
            lambda s: f'[name="{s}"]',  # Name attribute
            lambda s: f'[aria-label*="{s}" i]',  # Aria label
            lambda s: f'[placeholder*="{s}" i]',  # Placeholder
            lambda s: f'text="{s}"',  # Exact text
            lambda s: f'text*="{s}"',  # Partial text
            lambda s: f'[title*="{s}" i]',  # Title attribute
            lambda s: f'.{s}',  # Class name
        ]
        
        for strategy in strategies:
            try:
                test_selector = strategy(selector)
                element = await self.page.wait_for_selector(test_selector, timeout=1000)
                if element:
                    logger.debug(f"Found element with strategy: {test_selector}")
                    return element
            except Exception:
                continue
        
        # Try fuzzy text matching
        return await self._find_by_fuzzy_text(selector, timeout)
    
    async def _find_input_element(self, selector: str, timeout: int) -> Optional[ElementHandle]:
        """Find input element with specialized strategies."""
        input_strategies = [
            lambda s: f'input[name="{s}"]',
            lambda s: f'input[id="{s}"]',
            lambda s: f'input[placeholder*="{s}" i]',
            lambda s: f'textarea[name="{s}"]',
            lambda s: f'textarea[id="{s}"]',
            lambda s: f'textarea[placeholder*="{s}" i]',
            lambda s: f'[contenteditable="true"]',
            lambda s: 'input:focus',  # Currently focused input
            lambda s: 'textarea:focus',  # Currently focused textarea
        ]
        
        for strategy in input_strategies:
            try:
                test_selector = strategy(selector)
                element = await self.page.wait_for_selector(test_selector, timeout=1000)
                if element:
                    logger.debug(f"Found input element: {test_selector}")
                    return element
            except Exception:
                continue
        
        # Fallback to general element finding
        return await self._find_element_smart(selector, timeout)
    
    async def _find_by_fuzzy_text(self, text: str, timeout: int) -> Optional[ElementHandle]:
        """Find element by fuzzy text matching."""
        try:
            # Get all text-containing elements
            elements = await self.page.query_selector_all('*')
            
            best_match = None
            best_score = 0
            
            for element in elements:
                try:
                    element_text = await element.text_content()
                    if element_text:
                        # Calculate similarity score
                        score = self._calculate_similarity(text.lower(), element_text.lower())
                        if score > best_score and score > 0.6:  # Minimum similarity threshold
                            best_score = score
                            best_match = element
                except Exception:
                    continue
            
            if best_match:
                logger.debug(f"Found element by fuzzy matching: {text} (score: {best_score:.2f})")
                return best_match
            
            return None
            
        except Exception as e:
            logger.error(f"Fuzzy text search failed: {e}")
            return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Simple similarity calculation
        if text1 in text2 or text2 in text1:
            return 0.8
        
        # Word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def get_all_links(self) -> List[Dict[str, str]]:
        """Get all links on the page."""
        try:
            links = await self.page.query_selector_all('a[href]')
            result = []
            
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                
                if href:
                    result.append({
                        'href': href,
                        'text': text or '',
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get links: {e}")
            return []
    
    async def get_all_forms(self) -> List[Dict[str, Any]]:
        """Get all forms on the page."""
        try:
            forms = await self.page.query_selector_all('form')
            result = []
            
            for form in forms:
                form_data = {
                    'action': await form.get_attribute('action') or '',
                    'method': await form.get_attribute('method') or 'GET',
                    'inputs': []
                }
                
                # Get form inputs
                inputs = await form.query_selector_all('input, textarea, select')
                for input_elem in inputs:
                    input_data = {
                        'type': await input_elem.get_attribute('type') or 'text',
                        'name': await input_elem.get_attribute('name') or '',
                        'id': await input_elem.get_attribute('id') or '',
                        'placeholder': await input_elem.get_attribute('placeholder') or '',
                        'required': await input_elem.get_attribute('required') is not None,
                    }
                    form_data['inputs'].append(input_data)
                
                result.append(form_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get forms: {e}")
            return []
    
    async def fill_form_smart(self, form_data: Dict[str, str]) -> bool:
        """
        Fill a form intelligently based on field names and labels.
        
        Args:
            form_data: Dictionary of field names/labels to values
            
        Returns:
            bool: True if form filling successful
        """
        try:
            success_count = 0
            
            for field_identifier, value in form_data.items():
                # Try multiple strategies to find the field
                field_selectors = [
                    f'input[name="{field_identifier}"]',
                    f'input[id="{field_identifier}"]',
                    f'textarea[name="{field_identifier}"]',
                    f'textarea[id="{field_identifier}"]',
                    f'select[name="{field_identifier}"]',
                    f'select[id="{field_identifier}"]',
                    f'input[placeholder*="{field_identifier}" i]',
                    f'textarea[placeholder*="{field_identifier}" i]',
                ]
                
                filled = False
                for selector in field_selectors:
                    if await self.type_text(selector, str(value)):
                        success_count += 1
                        filled = True
                        break
                
                if not filled:
                    logger.warning(f"Could not fill field: {field_identifier}")
            
            logger.info(f"Form filling completed: {success_count}/{len(form_data)} fields filled")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return False
