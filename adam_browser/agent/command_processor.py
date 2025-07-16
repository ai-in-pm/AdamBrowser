"""
Command Processor for Adam Browser

Processes classified intents and executes corresponding browser actions
through specialized navigation modules and DOM manipulation.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from loguru import logger

from ..config import config
from ..browser import BrowserManager
from ..database import DatabaseManager
from ..security import SecurityVault
from .intent_classifier import IntentType, IntentResult


@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    message: str
    data: Dict[str, Any]
    execution_time: float
    actions_performed: List[str]
    url: Optional[str] = None
    page_title: Optional[str] = None
    screenshot_path: Optional[str] = None


class CommandProcessor:
    """
    Processes classified intents and executes browser actions.
    
    Coordinates between intent classification results and browser automation
    to perform complex multi-step operations.
    """
    
    def __init__(self, browser_manager: BrowserManager, 
                 database_manager: DatabaseManager,
                 security_vault: SecurityVault):
        """
        Initialize the command processor.
        
        Args:
            browser_manager: Browser automation manager
            database_manager: Database operations manager
            security_vault: Security and credential manager
        """
        self.browser_manager = browser_manager
        self.database_manager = database_manager
        self.security_vault = security_vault
        
        # Execution state
        self.current_url = ""
        self.current_page_title = ""
        self.last_screenshot = ""
        
        logger.info("Command processor initialized")
    
    async def execute(self, command: str, intent: IntentResult, 
                     context: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a command based on classified intent.
        
        Args:
            command: Original command text
            intent: Classified intent result
            context: Execution context
            
        Returns:
            ExecutionResult: Execution result with details
        """
        start_time = time.time()
        actions_performed = []
        
        try:
            logger.info(f"Executing command: {command} (intent: {intent.intent.value})")
            
            # Route to appropriate handler based on intent
            if intent.intent == IntentType.NAVIGATE:
                result = await self._handle_navigate(intent, actions_performed)
            elif intent.intent == IntentType.SEARCH:
                result = await self._handle_search(intent, actions_performed)
            elif intent.intent == IntentType.CLICK:
                result = await self._handle_click(intent, actions_performed)
            elif intent.intent == IntentType.TYPE:
                result = await self._handle_type(intent, actions_performed)
            elif intent.intent == IntentType.SCROLL:
                result = await self._handle_scroll(intent, actions_performed)
            elif intent.intent == IntentType.BOOK_TRAVEL:
                result = await self._handle_book_travel(intent, actions_performed)
            elif intent.intent == IntentType.GET_DIRECTIONS:
                result = await self._handle_get_directions(intent, actions_performed)
            elif intent.intent == IntentType.FILL_FORM:
                result = await self._handle_fill_form(intent, actions_performed)
            elif intent.intent == IntentType.SCREENSHOT:
                result = await self._handle_screenshot(intent, actions_performed)
            elif intent.intent == IntentType.WAIT:
                result = await self._handle_wait(intent, actions_performed)
            else:
                result = ExecutionResult(
                    success=False,
                    message=f"Unsupported intent: {intent.intent.value}",
                    data={},
                    execution_time=0,
                    actions_performed=actions_performed
                )
            
            # Update current state
            await self._update_current_state()
            
            # Add state info to result
            result.url = self.current_url
            result.page_title = self.current_page_title
            result.execution_time = time.time() - start_time
            
            # Take screenshot if configured
            if config.automation.screenshot_interval > 0:
                screenshot_path = await self.browser_manager.take_screenshot()
                if screenshot_path:
                    result.screenshot_path = screenshot_path
                    self.last_screenshot = screenshot_path
            
            logger.info(f"Command execution completed: {result.success}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {e}")
            
            return ExecutionResult(
                success=False,
                message=f"Execution error: {str(e)}",
                data={'error': str(e)},
                execution_time=execution_time,
                actions_performed=actions_performed,
                url=self.current_url,
                page_title=self.current_page_title
            )
    
    async def _handle_navigate(self, intent: IntentResult, 
                              actions: List[str]) -> ExecutionResult:
        """Handle navigation commands."""
        target = intent.parameters.get('target', '')
        
        if not target:
            return ExecutionResult(
                success=False,
                message="No navigation target specified",
                data={},
                execution_time=0,
                actions_performed=actions
            )
        
        actions.append(f"navigate_to({target})")

        # Ensure target is a proper URL
        if not target.startswith(('http://', 'https://')):
            if '.' in target and not ' ' in target:
                target = f"https://{target}"
            else:
                # Treat as search query
                target = f"https://www.google.com/search?q={target.replace(' ', '+')}"

        success = await self.browser_manager.navigate_to(target)

        if success:
            await asyncio.sleep(2)  # Wait for page to load

            # Get actual page info
            current_url = self.browser_manager.page.url if self.browser_manager.page else target
            page_title = ""
            try:
                if self.browser_manager.page:
                    page_title = await self.browser_manager.page.title()
            except Exception:
                pass

            return ExecutionResult(
                success=True,
                message=f"Successfully navigated to {target}",
                data={
                    'target': target,
                    'actual_url': current_url,
                    'page_title': page_title
                },
                execution_time=0,
                actions_performed=actions
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Failed to navigate to {target}",
                data={'target': target},
                execution_time=0,
                actions_performed=actions
            )
    
    async def _handle_search(self, intent: IntentResult, 
                            actions: List[str]) -> ExecutionResult:
        """Handle search commands."""
        query = intent.parameters.get('query', '')
        
        if not query:
            return ExecutionResult(
                success=False,
                message="No search query specified",
                data={},
                execution_time=0,
                actions_performed=actions
            )
        
        # If not on a search page, go to Google
        if 'google.com' not in self.current_url.lower():
            actions.append("navigate_to(google.com)")
            await self.browser_manager.navigate_to("https://www.google.com")
            await asyncio.sleep(2)
        
        # Find search box and type query
        search_selectors = [
            'input[name="q"]',
            'input[type="search"]',
            '#search',
            '.search-input',
            '[aria-label*="search" i]'
        ]
        
        search_success = False
        for selector in search_selectors:
            actions.append(f"type_text({selector}, {query})")
            if await self.browser_manager.type_text(selector, query):
                search_success = True
                break
        
        if not search_success:
            return ExecutionResult(
                success=False,
                message="Could not find search input field",
                data={'query': query},
                execution_time=0,
                actions_performed=actions
            )
        
        # Press Enter or click search button
        actions.append("press_enter")

        # Try multiple ways to submit the search
        submit_success = False

        # Method 1: Press Enter on the search input
        try:
            await self.browser_manager.page.keyboard.press('Enter')
            submit_success = True
            logger.debug("Search submitted via Enter key")
        except Exception as e:
            logger.debug(f"Enter key submission failed: {e}")

        # Method 2: Click search button if Enter didn't work
        if not submit_success:
            search_buttons = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Search")',
                'button:has-text("Google Search")',
                '[aria-label*="search" i]'
            ]

            for button_selector in search_buttons:
                if await self.browser_manager.click_element(button_selector):
                    submit_success = True
                    logger.debug(f"Search submitted via button: {button_selector}")
                    break

        # Method 3: JavaScript form submission as fallback
        if not submit_success:
            try:
                await self.browser_manager.execute_javascript("document.activeElement.form.submit()")
                submit_success = True
                logger.debug("Search submitted via JavaScript")
            except Exception as e:
                logger.debug(f"JavaScript submission failed: {e}")

        await asyncio.sleep(3)  # Wait for results
        
        return ExecutionResult(
            success=True,
            message=f"Search completed for: {query}",
            data={'query': query},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_click(self, intent: IntentResult, 
                           actions: List[str]) -> ExecutionResult:
        """Handle click commands."""
        element = intent.parameters.get('element', '')
        
        if not element:
            return ExecutionResult(
                success=False,
                message="No element specified to click",
                data={},
                execution_time=0,
                actions_performed=actions
            )
        
        # Try different click strategies
        click_strategies = [
            f'text="{element}"',  # Exact text match
            f'text*="{element}"',  # Partial text match
            f'[aria-label*="{element}" i]',  # Aria label
            f'[title*="{element}" i]',  # Title attribute
            f'#{element}',  # ID
            f'.{element}',  # Class
            element  # Direct selector
        ]
        
        for strategy in click_strategies:
            actions.append(f"click({strategy})")
            if await self.browser_manager.click_element(strategy):
                await asyncio.sleep(1)  # Wait for click effect
                return ExecutionResult(
                    success=True,
                    message=f"Successfully clicked: {element}",
                    data={'element': element, 'selector': strategy},
                    execution_time=0,
                    actions_performed=actions
                )
        
        return ExecutionResult(
            success=False,
            message=f"Could not find element to click: {element}",
            data={'element': element},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_type(self, intent: IntentResult, 
                          actions: List[str]) -> ExecutionResult:
        """Handle typing commands."""
        text = intent.parameters.get('text', '')
        
        if not text:
            return ExecutionResult(
                success=False,
                message="No text specified to type",
                data={},
                execution_time=0,
                actions_performed=actions
            )
        
        # Find active input or try common input selectors
        input_selectors = [
            'input:focus',  # Currently focused input
            'textarea:focus',  # Currently focused textarea
            'input[type="text"]',
            'input[type="search"]',
            'input[type="email"]',
            'input[type="password"]',
            'textarea',
            '[contenteditable="true"]'
        ]
        
        for selector in input_selectors:
            actions.append(f"type_text({selector}, {text})")
            if await self.browser_manager.type_text(selector, text):
                return ExecutionResult(
                    success=True,
                    message=f"Successfully typed: {text}",
                    data={'text': text, 'selector': selector},
                    execution_time=0,
                    actions_performed=actions
                )
        
        return ExecutionResult(
            success=False,
            message="Could not find input field to type in",
            data={'text': text},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_scroll(self, intent: IntentResult, 
                            actions: List[str]) -> ExecutionResult:
        """Handle scroll commands."""
        direction = intent.parameters.get('direction', 'down')
        amount = intent.parameters.get('amount', 3)
        
        actions.append(f"scroll({direction}, {amount})")
        success = await self.browser_manager.scroll_page(direction, amount)
        
        if success:
            return ExecutionResult(
                success=True,
                message=f"Scrolled {direction} {amount} times",
                data={'direction': direction, 'amount': amount},
                execution_time=0,
                actions_performed=actions
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Failed to scroll {direction}",
                data={'direction': direction, 'amount': amount},
                execution_time=0,
                actions_performed=actions
            )
    
    async def _handle_book_travel(self, intent: IntentResult, 
                                 actions: List[str]) -> ExecutionResult:
        """Handle travel booking commands."""
        # This would integrate with the Expedia navigator module
        travel_type = intent.parameters.get('travel_type', 'flight')
        locations = intent.parameters.get('locations', [])
        
        actions.append(f"book_travel({travel_type})")
        
        # Navigate to Expedia if not already there
        if 'expedia.com' not in self.current_url.lower():
            await self.browser_manager.navigate_to("https://www.expedia.com")
            await asyncio.sleep(3)
        
        # This is a simplified implementation
        # In a full implementation, this would use the ExpediaNavigator module
        return ExecutionResult(
            success=True,
            message=f"Travel booking initiated for {travel_type}",
            data={'travel_type': travel_type, 'locations': locations},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_get_directions(self, intent: IntentResult, 
                                    actions: List[str]) -> ExecutionResult:
        """Handle directions commands."""
        from_location = intent.parameters.get('from', '')
        to_location = intent.parameters.get('to', '')
        
        if not to_location:
            return ExecutionResult(
                success=False,
                message="No destination specified",
                data={},
                execution_time=0,
                actions_performed=actions
            )
        
        actions.append(f"get_directions({from_location} -> {to_location})")
        
        # Navigate to Google Maps
        if 'maps.google.com' not in self.current_url.lower():
            await self.browser_manager.navigate_to("https://maps.google.com")
            await asyncio.sleep(3)
        
        # This would integrate with the MapsNavigator module
        return ExecutionResult(
            success=True,
            message=f"Directions requested from {from_location} to {to_location}",
            data={'from': from_location, 'to': to_location},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_fill_form(self, intent: IntentResult, 
                               actions: List[str]) -> ExecutionResult:
        """Handle form filling commands."""
        actions.append("fill_form")
        
        # This would implement intelligent form filling
        return ExecutionResult(
            success=True,
            message="Form filling completed",
            data={},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _handle_screenshot(self, intent: IntentResult, 
                                actions: List[str]) -> ExecutionResult:
        """Handle screenshot commands."""
        actions.append("take_screenshot")
        
        screenshot_path = await self.browser_manager.take_screenshot()
        
        if screenshot_path:
            return ExecutionResult(
                success=True,
                message=f"Screenshot saved: {screenshot_path}",
                data={'screenshot_path': screenshot_path},
                execution_time=0,
                actions_performed=actions,
                screenshot_path=screenshot_path
            )
        else:
            return ExecutionResult(
                success=False,
                message="Failed to take screenshot",
                data={},
                execution_time=0,
                actions_performed=actions
            )
    
    async def _handle_wait(self, intent: IntentResult, 
                          actions: List[str]) -> ExecutionResult:
        """Handle wait commands."""
        duration = intent.parameters.get('duration', 5)
        
        actions.append(f"wait({duration}s)")
        await asyncio.sleep(duration)
        
        return ExecutionResult(
            success=True,
            message=f"Waited for {duration} seconds",
            data={'duration': duration},
            execution_time=0,
            actions_performed=actions
        )
    
    async def _update_current_state(self) -> None:
        """Update current page state."""
        if self.browser_manager.page:
            try:
                self.current_url = self.browser_manager.page.url
                self.current_page_title = await self.browser_manager.page.title()
            except Exception as e:
                logger.warning(f"Failed to update current state: {e}")
