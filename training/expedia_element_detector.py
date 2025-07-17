#!/usr/bin/env python3
"""
Advanced Expedia Element Detector

This module provides sophisticated element detection specifically optimized
for Expedia.com's dynamic interface, including handling of:
- Dynamic content loading
- A/B testing variations
- Mobile vs desktop layouts
- Seasonal interface changes
- Multi-language support
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re

try:
    from travel_booking_patterns import travel_patterns, TravelSite
    PATTERNS_AVAILABLE = True
except ImportError:
    PATTERNS_AVAILABLE = False


class ExpediaPageType(Enum):
    """Types of pages on Expedia."""
    HOMEPAGE = "homepage"
    SEARCH_RESULTS = "search_results"
    HOTEL_DETAILS = "hotel_details"
    FLIGHT_DETAILS = "flight_details"
    BOOKING_FORM = "booking_form"
    PAYMENT = "payment"
    CONFIRMATION = "confirmation"
    ACCOUNT = "account"
    UNKNOWN = "unknown"


@dataclass
class DetectedElement:
    """Represents a detected element with metadata."""
    element: Any
    element_type: str
    confidence: float
    selector_used: str
    attributes: Dict[str, str]
    text_content: str
    position: Dict[str, float]
    is_visible: bool
    is_interactive: bool


class AdvancedExpediaDetector:
    """Advanced element detector specifically for Expedia.com."""
    
    def __init__(self, page):
        self.page = page
        self.detection_cache = {}
        self.page_analysis = {}
        self.last_analysis_time = 0
        
        # Expedia-specific selectors with priority
        self.priority_selectors = {
            'search_forms': [
                # High priority - data-testid selectors
                '[data-testid="flight-search-form"]',
                '[data-testid="hotel-search-form"]',
                '[data-testid="car-search-form"]',
                '[data-testid="package-search-form"]',
                # Medium priority - class-based
                '.flight-search-form',
                '.hotel-search-form',
                '.car-search-form',
                '.search-form',
                # Low priority - generic
                'form[action*="search"]',
                'form[action*="flight"]',
                'form[action*="hotel"]'
            ],
            'location_inputs': [
                # Expedia-specific
                '[data-testid="origin-input"]',
                '[data-testid="destination-input"]',
                '[data-testid="location-input"]',
                # Generic travel site patterns
                'input[placeholder*="From" i]',
                'input[placeholder*="To" i]',
                'input[placeholder*="Where" i]',
                'input[placeholder*="Going" i]',
                'input[name*="origin"]',
                'input[name*="destination"]',
                'input[name*="location"]',
                # Aria labels
                '[aria-label*="origin" i]',
                '[aria-label*="destination" i]',
                '[aria-label*="location" i]'
            ],
            'date_inputs': [
                '[data-testid*="date"]',
                '[data-testid="departure-date"]',
                '[data-testid="return-date"]',
                '[data-testid="checkin-date"]',
                '[data-testid="checkout-date"]',
                '.date-picker-input',
                '.date-input',
                'input[type="date"]',
                'input[placeholder*="date" i]',
                '[aria-label*="date" i]'
            ],
            'traveler_controls': [
                '[data-testid="travelers-selector"]',
                '[data-testid="guests-selector"]',
                '[data-testid="rooms-selector"]',
                '.travelers-dropdown',
                '.guests-dropdown',
                '.rooms-dropdown',
                '[aria-label*="travelers" i]',
                '[aria-label*="guests" i]',
                '[aria-label*="rooms" i]'
            ],
            'search_buttons': [
                '[data-testid="search-button"]',
                '[data-testid="submit-button"]',
                'button[type="submit"]',
                '.search-btn',
                '.search-button',
                '.submit-btn',
                'button:has-text("Search")',
                'button:has-text("Find")',
                '[aria-label*="search" i]'
            ]
        }
        
        # Dynamic content indicators
        self.loading_indicators = [
            '.loading',
            '.spinner',
            '.skeleton',
            '[data-testid*="loading"]',
            '[aria-label*="loading" i]'
        ]
    
    async def detect_page_type(self) -> ExpediaPageType:
        """Detect the current page type on Expedia."""
        try:
            url = self.page.url.lower()
            title = await self.page.title()
            title_lower = title.lower()
            
            # URL-based detection
            if 'expedia.com' not in url:
                return ExpediaPageType.UNKNOWN
            
            if '/flights/' in url or 'flight' in url:
                if 'details' in url or 'book' in url:
                    return ExpediaPageType.FLIGHT_DETAILS
                else:
                    return ExpediaPageType.SEARCH_RESULTS
            
            elif '/hotels/' in url or 'hotel' in url:
                if 'details' in url or 'book' in url:
                    return ExpediaPageType.HOTEL_DETAILS
                else:
                    return ExpediaPageType.SEARCH_RESULTS
            
            elif '/checkout' in url or '/payment' in url:
                return ExpediaPageType.PAYMENT
            
            elif '/confirmation' in url or '/receipt' in url:
                return ExpediaPageType.CONFIRMATION
            
            elif '/account' in url or '/profile' in url:
                return ExpediaPageType.ACCOUNT
            
            # Content-based detection
            page_content = await self.page.content()
            content_lower = page_content.lower()
            
            # Check for search forms (homepage)
            search_forms = await self._quick_find_search_forms()
            if search_forms and len(search_forms) > 1:
                return ExpediaPageType.HOMEPAGE
            
            # Check for search results
            if 'search results' in content_lower or 'results found' in content_lower:
                return ExpediaPageType.SEARCH_RESULTS
            
            # Check for booking forms
            if 'booking' in content_lower and 'form' in content_lower:
                return ExpediaPageType.BOOKING_FORM
            
            return ExpediaPageType.HOMEPAGE  # Default fallback
            
        except Exception as e:
            print(f"⚠️ Error detecting page type: {e}")
            return ExpediaPageType.UNKNOWN
    
    async def _quick_find_search_forms(self) -> List[Any]:
        """Quick search for forms without detailed analysis."""
        forms = []
        for selector in self.priority_selectors['search_forms'][:3]:  # Check top 3 only
            try:
                elements = await self.page.query_selector_all(selector)
                forms.extend(elements)
                if forms:  # Found some, no need to continue
                    break
            except:
                continue
        return forms
    
    async def wait_for_page_load(self, timeout: int = 10) -> bool:
        """Wait for dynamic content to load."""
        try:
            # Wait for loading indicators to disappear
            for indicator in self.loading_indicators:
                try:
                    await self.page.wait_for_selector(indicator, state='detached', timeout=timeout * 1000)
                except:
                    continue  # Indicator might not exist
            
            # Wait for network to be idle
            await self.page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Page load wait timeout: {e}")
            return False
    
    async def detect_all_interactive_elements(self) -> Dict[str, List[DetectedElement]]:
        """Detect all interactive elements on the current page."""
        try:
            # Wait for page to load
            await self.wait_for_page_load()
            
            detected_elements = {
                'search_forms': [],
                'location_inputs': [],
                'date_inputs': [],
                'traveler_controls': [],
                'search_buttons': [],
                'result_items': [],
                'booking_buttons': [],
                'navigation_links': []
            }
            
            # Detect each type of element
            for element_type, selectors in self.priority_selectors.items():
                detected_elements[element_type] = await self._detect_elements_by_type(
                    element_type, selectors
                )
            
            # Detect additional elements based on page type
            page_type = await self.detect_page_type()
            if page_type == ExpediaPageType.SEARCH_RESULTS:
                detected_elements['result_items'] = await self._detect_result_items()
                detected_elements['filters'] = await self._detect_filters()
            
            elif page_type in [ExpediaPageType.HOTEL_DETAILS, ExpediaPageType.FLIGHT_DETAILS]:
                detected_elements['booking_buttons'] = await self._detect_booking_buttons()
                detected_elements['price_elements'] = await self._detect_price_elements()
            
            # Cache results
            self.detection_cache = detected_elements
            self.last_analysis_time = time.time()
            
            return detected_elements
            
        except Exception as e:
            print(f"❌ Error detecting interactive elements: {e}")
            return {}
    
    async def _detect_elements_by_type(self, element_type: str, selectors: List[str]) -> List[DetectedElement]:
        """Detect elements of a specific type using priority selectors."""
        detected = []
        
        for i, selector in enumerate(selectors):
            try:
                elements = await self.page.query_selector_all(selector)
                
                for element in elements:
                    # Check if element is visible and interactive
                    is_visible = await element.is_visible()
                    if not is_visible:
                        continue
                    
                    # Get element details
                    element_details = await self._analyze_element(element, selector, i)
                    if element_details:
                        detected.append(element_details)
                
                # If we found elements with high-priority selectors, we can stop
                if detected and i < 3:  # Top 3 selectors are high priority
                    break
                    
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
                continue
        
        # Sort by confidence
        detected.sort(key=lambda x: x.confidence, reverse=True)
        return detected
    
    async def _analyze_element(self, element, selector: str, selector_priority: int) -> Optional[DetectedElement]:
        """Analyze a single element and create DetectedElement object."""
        try:
            # Get element attributes
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text_content = await element.evaluate('el => el.textContent?.trim() || ""')
            
            # Get common attributes
            attributes = {}
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'aria-label', 'data-testid']:
                value = await element.get_attribute(attr)
                if value:
                    attributes[attr] = value
            
            # Get position
            bounding_box = await element.bounding_box()
            position = bounding_box if bounding_box else {'x': 0, 'y': 0, 'width': 0, 'height': 0}
            
            # Calculate confidence based on selector priority and element characteristics
            confidence = self._calculate_element_confidence(
                tag_name, attributes, text_content, selector_priority
            )
            
            # Determine if element is interactive
            is_interactive = await self._is_element_interactive(element, tag_name)
            
            return DetectedElement(
                element=element,
                element_type=self._classify_element_type(tag_name, attributes, text_content),
                confidence=confidence,
                selector_used=selector,
                attributes=attributes,
                text_content=text_content,
                position=position,
                is_visible=True,  # Already checked
                is_interactive=is_interactive
            )
            
        except Exception as e:
            print(f"⚠️ Error analyzing element: {e}")
            return None
    
    def _calculate_element_confidence(self, tag_name: str, attributes: Dict[str, str], 
                                    text_content: str, selector_priority: int) -> float:
        """Calculate confidence score for element detection."""
        confidence = 0.5  # Base confidence
        
        # Boost for high-priority selectors
        if selector_priority == 0:
            confidence += 0.3  # data-testid selectors
        elif selector_priority <= 2:
            confidence += 0.2  # class-based selectors
        elif selector_priority <= 5:
            confidence += 0.1  # generic selectors
        
        # Boost for interactive tags
        if tag_name in ['button', 'input', 'select', 'a']:
            confidence += 0.2
        
        # Boost for meaningful attributes
        if 'data-testid' in attributes:
            confidence += 0.2
        if 'aria-label' in attributes:
            confidence += 0.1
        if 'placeholder' in attributes:
            confidence += 0.1
        
        # Boost for meaningful text content
        if text_content and len(text_content.strip()) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    async def _is_element_interactive(self, element, tag_name: str) -> bool:
        """Check if an element is interactive."""
        try:
            # Check tag type
            if tag_name in ['button', 'input', 'select', 'textarea', 'a']:
                return True
            
            # Check for click handlers
            has_click = await element.evaluate('''
                el => {
                    return el.onclick !== null || 
                           el.getAttribute('onclick') !== null ||
                           window.getComputedStyle(el).cursor === 'pointer';
                }
            ''')
            
            return has_click
            
        except:
            return False
    
    def _classify_element_type(self, tag_name: str, attributes: Dict[str, str], text_content: str) -> str:
        """Classify the type/purpose of an element."""
        # Check data-testid first
        testid = attributes.get('data-testid', '').lower()
        if 'search' in testid:
            return 'search'
        elif 'date' in testid:
            return 'date'
        elif 'location' in testid or 'origin' in testid or 'destination' in testid:
            return 'location'
        elif 'traveler' in testid or 'guest' in testid:
            return 'traveler'
        
        # Check placeholder
        placeholder = attributes.get('placeholder', '').lower()
        if any(word in placeholder for word in ['from', 'to', 'where', 'destination']):
            return 'location'
        elif 'date' in placeholder:
            return 'date'
        
        # Check text content
        text_lower = text_content.lower()
        if any(word in text_lower for word in ['search', 'find']):
            return 'search'
        elif any(word in text_lower for word in ['book', 'reserve', 'select']):
            return 'booking'
        
        # Fallback to tag name
        return tag_name
    
    async def _detect_result_items(self) -> List[DetectedElement]:
        """Detect search result items."""
        result_selectors = [
            '[data-testid*="result"]',
            '.result-item',
            '.search-result',
            '.listing',
            '.offer-listing',
            '.hotel-listing',
            '.flight-listing'
        ]
        
        return await self._detect_elements_by_type('result_item', result_selectors)
    
    async def _detect_filters(self) -> List[DetectedElement]:
        """Detect filter elements."""
        filter_selectors = [
            '[data-testid*="filter"]',
            '.filter',
            '.facet',
            '.refinement',
            '.sidebar-filter'
        ]
        
        return await self._detect_elements_by_type('filter', filter_selectors)
    
    async def _detect_booking_buttons(self) -> List[DetectedElement]:
        """Detect booking/reservation buttons."""
        booking_selectors = [
            '[data-testid*="book"]',
            '[data-testid*="reserve"]',
            '.book-button',
            '.reserve-button',
            '.cta-button',
            'button:has-text("Book")',
            'button:has-text("Reserve")',
            'button:has-text("Select")'
        ]
        
        return await self._detect_elements_by_type('booking_button', booking_selectors)
    
    async def _detect_price_elements(self) -> List[DetectedElement]:
        """Detect price display elements."""
        price_selectors = [
            '[data-testid*="price"]',
            '.price',
            '.cost',
            '.rate',
            '.amount',
            '.total-price'
        ]
        
        return await self._detect_elements_by_type('price', price_selectors)
    
    def get_cached_elements(self, element_type: str = None) -> Dict[str, List[DetectedElement]]:
        """Get cached element detection results."""
        if element_type:
            return {element_type: self.detection_cache.get(element_type, [])}
        return self.detection_cache
    
    def is_cache_valid(self, max_age_seconds: int = 30) -> bool:
        """Check if cached results are still valid."""
        return (time.time() - self.last_analysis_time) < max_age_seconds
