#!/usr/bin/env python3
"""
Expedia Training Module for Advanced AI Agent

This module provides specialized training capabilities for Expedia.com interactions,
including intelligent form detection, travel booking workflows, and adaptive learning
for travel-specific user interfaces.

Features:
- Travel booking form detection and completion
- Dynamic pricing element tracking
- Multi-step booking workflow management
- Expedia-specific element pattern recognition
- Adaptive learning for UI changes
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

# Import advanced capabilities
try:
    from adam_browser_advanced_capabilities import (
        SmartFormDetector, NaturalMouseMovement, ContextAwareDecisionMaker,
        LearningSystem, InteractionPattern, FormField
    )
    ADVANCED_CAPABILITIES = True
except ImportError:
    ADVANCED_CAPABILITIES = False


class TravelBookingType(Enum):
    """Types of travel bookings on Expedia."""
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"
    PACKAGE = "package"
    CRUISE = "cruise"
    ACTIVITY = "activity"


class BookingStep(Enum):
    """Steps in the travel booking process."""
    SEARCH_FORM = "search_form"
    RESULTS_PAGE = "results_page"
    DETAILS_PAGE = "details_page"
    BOOKING_FORM = "booking_form"
    PAYMENT_PAGE = "payment_page"
    CONFIRMATION = "confirmation"


@dataclass
class TravelSearchCriteria:
    """Travel search criteria for form filling."""
    booking_type: TravelBookingType
    departure_location: str = "New York, NY"
    destination_location: str = "Los Angeles, CA"
    departure_date: str = ""
    return_date: str = ""
    travelers: int = 1
    rooms: int = 1
    children: int = 0
    class_preference: str = "economy"
    
    def __post_init__(self):
        if not self.departure_date:
            # Default to 30 days from now
            future_date = datetime.now() + timedelta(days=30)
            self.departure_date = future_date.strftime("%m/%d/%Y")
        
        if not self.return_date and self.booking_type in [TravelBookingType.FLIGHT, TravelBookingType.PACKAGE]:
            # Default return 7 days after departure
            dep_date = datetime.strptime(self.departure_date, "%m/%d/%Y")
            return_date = dep_date + timedelta(days=7)
            self.return_date = return_date.strftime("%m/%d/%Y")


class ExpediaElementDetector:
    """Specialized element detector for Expedia.com interfaces."""
    
    def __init__(self, page):
        self.page = page
        self.element_cache = {}
        
        # Expedia-specific selectors
        self.expedia_selectors = {
            'search_forms': {
                'flight_form': [
                    '[data-testid="flight-search-form"]',
                    '.flight-search-form',
                    '#flight-search',
                    'form[action*="flight"]'
                ],
                'hotel_form': [
                    '[data-testid="hotel-search-form"]',
                    '.hotel-search-form',
                    '#hotel-search',
                    'form[action*="hotel"]'
                ],
                'car_form': [
                    '[data-testid="car-search-form"]',
                    '.car-search-form',
                    '#car-search',
                    'form[action*="car"]'
                ]
            },
            'location_inputs': [
                '[data-testid="origin-input"]',
                '[data-testid="destination-input"]',
                '[placeholder*="From" i]',
                '[placeholder*="To" i]',
                '[placeholder*="Where" i]',
                '[aria-label*="origin" i]',
                '[aria-label*="destination" i]',
                'input[name*="origin"]',
                'input[name*="destination"]'
            ],
            'date_inputs': [
                '[data-testid="departure-date"]',
                '[data-testid="return-date"]',
                '[data-testid="checkin-date"]',
                '[data-testid="checkout-date"]',
                'input[type="date"]',
                '[placeholder*="date" i]',
                '.date-picker-input'
            ],
            'traveler_selectors': [
                '[data-testid="travelers-selector"]',
                '[data-testid="guests-selector"]',
                '.travelers-dropdown',
                '.guests-dropdown',
                '[aria-label*="travelers" i]',
                '[aria-label*="guests" i]'
            ],
            'search_buttons': [
                '[data-testid="search-button"]',
                'button[type="submit"]',
                '.search-btn',
                '.search-button',
                'button:has-text("Search")',
                '[aria-label*="search" i]'
            ]
        }
    
    async def detect_booking_step(self) -> BookingStep:
        """Detect which step of the booking process we're currently on."""
        try:
            url = self.page.url.lower()
            page_content = await self.page.content()
            
            # Check URL patterns
            if 'search' in url or 'flights' in url or 'hotels' in url:
                # Check if we have search forms
                search_forms = await self._find_search_forms()
                if search_forms:
                    return BookingStep.SEARCH_FORM
                else:
                    return BookingStep.RESULTS_PAGE
            
            elif 'details' in url or 'book' in url:
                return BookingStep.DETAILS_PAGE
            
            elif 'checkout' in url or 'payment' in url:
                return BookingStep.PAYMENT_PAGE
            
            elif 'confirmation' in url or 'receipt' in url:
                return BookingStep.CONFIRMATION
            
            # Fallback to content analysis
            if 'search' in page_content.lower() and await self._find_search_forms():
                return BookingStep.SEARCH_FORM
            elif 'results' in page_content.lower():
                return BookingStep.RESULTS_PAGE
            else:
                return BookingStep.SEARCH_FORM  # Default assumption
                
        except Exception as e:
            print(f"⚠️ Error detecting booking step: {e}")
            return BookingStep.SEARCH_FORM
    
    async def _find_search_forms(self) -> List[Dict[str, Any]]:
        """Find all search forms on the current page."""
        forms = []
        
        for form_type, selectors in self.expedia_selectors['search_forms'].items():
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            forms.append({
                                'type': form_type,
                                'element': element,
                                'selector': selector
                            })
                except:
                    continue
        
        return forms
    
    async def find_location_inputs(self) -> List[Dict[str, Any]]:
        """Find location input fields (origin/destination)."""
        location_inputs = []
        
        for selector in self.expedia_selectors['location_inputs']:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        placeholder = await element.get_attribute('placeholder') or ''
                        aria_label = await element.get_attribute('aria-label') or ''
                        name = await element.get_attribute('name') or ''
                        
                        # Determine if this is origin or destination
                        field_type = self._classify_location_field(placeholder, aria_label, name)
                        
                        location_inputs.append({
                            'element': element,
                            'type': field_type,
                            'placeholder': placeholder,
                            'aria_label': aria_label,
                            'selector': selector
                        })
            except:
                continue
        
        return location_inputs
    
    def _classify_location_field(self, placeholder: str, aria_label: str, name: str) -> str:
        """Classify whether a location field is origin or destination."""
        combined = f"{placeholder} {aria_label} {name}".lower()
        
        origin_keywords = ['from', 'origin', 'departure', 'leaving']
        destination_keywords = ['to', 'destination', 'arrival', 'going']
        
        if any(keyword in combined for keyword in origin_keywords):
            return 'origin'
        elif any(keyword in combined for keyword in destination_keywords):
            return 'destination'
        else:
            return 'location'  # Generic location field
    
    async def find_date_inputs(self) -> List[Dict[str, Any]]:
        """Find date input fields."""
        date_inputs = []
        
        for selector in self.expedia_selectors['date_inputs']:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        placeholder = await element.get_attribute('placeholder') or ''
                        aria_label = await element.get_attribute('aria-label') or ''
                        data_testid = await element.get_attribute('data-testid') or ''
                        
                        # Determine date type
                        date_type = self._classify_date_field(placeholder, aria_label, data_testid)
                        
                        date_inputs.append({
                            'element': element,
                            'type': date_type,
                            'placeholder': placeholder,
                            'aria_label': aria_label,
                            'selector': selector
                        })
            except:
                continue
        
        return date_inputs
    
    def _classify_date_field(self, placeholder: str, aria_label: str, data_testid: str) -> str:
        """Classify the type of date field."""
        combined = f"{placeholder} {aria_label} {data_testid}".lower()
        
        if any(keyword in combined for keyword in ['departure', 'depart', 'leaving']):
            return 'departure'
        elif any(keyword in combined for keyword in ['return', 'returning']):
            return 'return'
        elif any(keyword in combined for keyword in ['checkin', 'check-in', 'arrival']):
            return 'checkin'
        elif any(keyword in combined for keyword in ['checkout', 'check-out']):
            return 'checkout'
        else:
            return 'date'  # Generic date field


class ExpediaTrainingAgent:
    """Advanced AI agent specifically trained for Expedia.com interactions."""
    
    def __init__(self, page, chat_window=None):
        self.page = page
        self.chat_window = chat_window
        self.element_detector = ExpediaElementDetector(page)
        self.current_booking_step = BookingStep.SEARCH_FORM
        self.booking_context = {}
        
        # Initialize advanced capabilities if available
        if ADVANCED_CAPABILITIES:
            self.form_detector = SmartFormDetector(page)
            self.mouse_movement = NaturalMouseMovement()
            self.decision_maker = ContextAwareDecisionMaker()
            self.learning_system = LearningSystem("expedia_learning.json")
        
        # Load Expedia-specific training data
        self.training_data = self._load_training_data()
        
        print("🎯 Expedia Training Agent initialized")
    
    def _load_training_data(self) -> Dict[str, Any]:
        """Load Expedia-specific training data."""
        try:
            training_file = Path("expedia_training_data.json")
            if training_file.exists():
                with open(training_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load training data: {e}")
        
        # Return default training data
        return {
            'common_destinations': [
                'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Miami, FL',
                'Las Vegas, NV', 'San Francisco, CA', 'Orlando, FL', 'Boston, MA'
            ],
            'booking_patterns': {
                'flight': ['origin', 'destination', 'departure_date', 'return_date', 'travelers'],
                'hotel': ['destination', 'checkin_date', 'checkout_date', 'guests', 'rooms'],
                'car': ['pickup_location', 'dropoff_location', 'pickup_date', 'dropoff_date']
            }
        }

    async def train_on_current_page(self) -> Dict[str, Any]:
        """Train the AI agent on the current Expedia page."""
        try:
            start_time = time.time()

            # Detect current booking step
            self.current_booking_step = await self.element_detector.detect_booking_step()

            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    f"🎯 Training on Expedia page - Step: {self.current_booking_step.value}",
                    is_bot=True)

            # Perform step-specific training
            training_result = await self._train_for_booking_step()

            # Record training session
            execution_time = time.time() - start_time
            if ADVANCED_CAPABILITIES and self.learning_system:
                context = await self.decision_maker.analyze_page_context(self.page)
                context['booking_step'] = self.current_booking_step.value
                self.learning_system.record_interaction(
                    'expedia_training', context, training_result['success'], execution_time
                )

            training_result['execution_time'] = execution_time
            return training_result

        except Exception as e:
            print(f"❌ Training failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _train_for_booking_step(self) -> Dict[str, Any]:
        """Perform training specific to the current booking step."""
        if self.current_booking_step == BookingStep.SEARCH_FORM:
            return await self._train_search_form()
        elif self.current_booking_step == BookingStep.RESULTS_PAGE:
            return await self._train_results_page()
        elif self.current_booking_step == BookingStep.DETAILS_PAGE:
            return await self._train_details_page()
        elif self.current_booking_step == BookingStep.BOOKING_FORM:
            return await self._train_booking_form()
        else:
            return await self._train_general_page()

    async def _train_search_form(self) -> Dict[str, Any]:
        """Train on Expedia search forms."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    "📋 Training on search form interactions...", is_bot=True)

            # Find and analyze search forms
            search_forms = await self.element_detector._find_search_forms()

            if not search_forms:
                return {'success': False, 'error': 'No search forms found'}

            trained_forms = 0
            for form_info in search_forms:
                form_result = await self._train_single_search_form(form_info)
                if form_result['success']:
                    trained_forms += 1

            # Practice filling a complete search form
            if trained_forms > 0:
                practice_result = await self._practice_search_form_filling()

                if self.chat_window:
                    self.chat_window.add_chat_message("Adam",
                        f"✅ Trained on {trained_forms} search forms. Practice result: {practice_result['success']}",
                        is_bot=True)

                return {
                    'success': True,
                    'trained_forms': trained_forms,
                    'practice_success': practice_result['success']
                }

            return {'success': False, 'error': 'No forms could be trained'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _train_single_search_form(self, form_info: Dict[str, Any]) -> Dict[str, Any]:
        """Train on a single search form."""
        try:
            form_type = form_info['type']
            form_element = form_info['element']

            # Find location inputs
            location_inputs = await self.element_detector.find_location_inputs()

            # Find date inputs
            date_inputs = await self.element_detector.find_date_inputs()

            # Find traveler selectors
            traveler_selectors = []
            for selector in self.element_detector.expedia_selectors['traveler_selectors']:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            traveler_selectors.append(element)
                except:
                    continue

            # Store form structure for learning
            form_structure = {
                'type': form_type,
                'location_inputs': len(location_inputs),
                'date_inputs': len(date_inputs),
                'traveler_selectors': len(traveler_selectors),
                'timestamp': time.time()
            }

            # Save form structure to training data
            self._save_form_structure(form_structure)

            return {
                'success': True,
                'form_type': form_type,
                'elements_found': {
                    'locations': len(location_inputs),
                    'dates': len(date_inputs),
                    'travelers': len(traveler_selectors)
                }
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _practice_search_form_filling(self) -> Dict[str, Any]:
        """Practice filling out a search form with test data."""
        try:
            # Create test search criteria
            test_criteria = TravelSearchCriteria(
                booking_type=TravelBookingType.FLIGHT,
                departure_location=random.choice(self.training_data['common_destinations']),
                destination_location=random.choice(self.training_data['common_destinations'])
            )

            # Ensure different origin and destination
            while test_criteria.destination_location == test_criteria.departure_location:
                test_criteria.destination_location = random.choice(self.training_data['common_destinations'])

            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    f"🧪 Practicing with: {test_criteria.departure_location} → {test_criteria.destination_location}",
                    is_bot=True)

            # Fill the form
            fill_result = await self.fill_search_form(test_criteria)

            return fill_result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _save_form_structure(self, form_structure: Dict[str, Any]):
        """Save discovered form structure to training data."""
        try:
            if 'discovered_forms' not in self.training_data:
                self.training_data['discovered_forms'] = []

            self.training_data['discovered_forms'].append(form_structure)

            # Save to file
            with open("expedia_training_data.json", 'w') as f:
                json.dump(self.training_data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Could not save form structure: {e}")

    async def fill_search_form(self, criteria: TravelSearchCriteria) -> Dict[str, Any]:
        """Fill a search form with the provided criteria."""
        try:
            filled_fields = 0

            # Fill location inputs
            location_inputs = await self.element_detector.find_location_inputs()
            for location_input in location_inputs:
                if location_input['type'] == 'origin':
                    await self._fill_location_field(location_input['element'], criteria.departure_location)
                    filled_fields += 1
                elif location_input['type'] == 'destination':
                    await self._fill_location_field(location_input['element'], criteria.destination_location)
                    filled_fields += 1

            # Fill date inputs
            date_inputs = await self.element_detector.find_date_inputs()
            for date_input in date_inputs:
                if date_input['type'] == 'departure':
                    await self._fill_date_field(date_input['element'], criteria.departure_date)
                    filled_fields += 1
                elif date_input['type'] == 'return' and criteria.return_date:
                    await self._fill_date_field(date_input['element'], criteria.return_date)
                    filled_fields += 1

            return {'success': True, 'filled_fields': filled_fields}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _fill_location_field(self, element, location: str):
        """Fill a location field with natural typing."""
        try:
            # Use natural mouse movement if available
            if ADVANCED_CAPABILITIES and self.mouse_movement:
                await self.mouse_movement.move_to_element(self.page, element)
                await asyncio.sleep(0.2)

            # Clear and fill the field
            await element.click()
            await asyncio.sleep(0.3)
            await element.clear()
            await asyncio.sleep(0.2)

            # Type with human-like speed
            for char in location:
                await element.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))

            # Wait for autocomplete and press Enter
            await asyncio.sleep(1)
            await element.press('Enter')
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Error filling location field: {e}")

    async def _fill_date_field(self, element, date: str):
        """Fill a date field with the provided date."""
        try:
            # Use natural mouse movement if available
            if ADVANCED_CAPABILITIES and self.mouse_movement:
                await self.mouse_movement.move_to_element(self.page, element)
                await asyncio.sleep(0.2)

            await element.click()
            await asyncio.sleep(0.3)
            await element.clear()
            await asyncio.sleep(0.2)
            await element.fill(date)
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Error filling date field: {e}")

    async def _train_results_page(self) -> Dict[str, Any]:
        """Train on Expedia results page interactions."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    "📊 Training on results page interactions...", is_bot=True)

            # Find result items
            result_selectors = [
                '[data-testid="result-item"]',
                '.result-item',
                '.search-result',
                '.listing',
                '.offer-listing'
            ]

            results_found = 0
            for selector in result_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    results_found += len(elements)

                    # Analyze first few results
                    for i, element in enumerate(elements[:3]):
                        await self._analyze_result_item(element, i)

                except:
                    continue

            # Find and analyze filters
            filter_elements = await self._find_filter_elements()

            # Find sort options
            sort_elements = await self._find_sort_elements()

            return {
                'success': True,
                'results_found': results_found,
                'filters_found': len(filter_elements),
                'sort_options': len(sort_elements)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _analyze_result_item(self, element, index: int):
        """Analyze a single result item to understand its structure."""
        try:
            # Extract key information
            price_selectors = ['.price', '[data-testid="price"]', '.cost', '.rate']
            title_selectors = ['.title', '.name', '.hotel-name', '.airline-name']

            item_info = {
                'index': index,
                'has_price': False,
                'has_title': False,
                'has_image': False,
                'clickable': False
            }

            # Check for price
            for selector in price_selectors:
                try:
                    price_element = await element.query_selector(selector)
                    if price_element:
                        item_info['has_price'] = True
                        break
                except:
                    continue

            # Check for title
            for selector in title_selectors:
                try:
                    title_element = await element.query_selector(selector)
                    if title_element:
                        item_info['has_title'] = True
                        break
                except:
                    continue

            # Check for image
            try:
                img_element = await element.query_selector('img')
                if img_element:
                    item_info['has_image'] = True
            except:
                pass

            # Check if clickable
            try:
                await element.hover()
                item_info['clickable'] = True
            except:
                pass

            # Store analysis
            if 'result_analysis' not in self.training_data:
                self.training_data['result_analysis'] = []

            self.training_data['result_analysis'].append(item_info)

        except Exception as e:
            print(f"⚠️ Error analyzing result item: {e}")

    async def _find_filter_elements(self) -> List[Any]:
        """Find filter elements on the results page."""
        filter_selectors = [
            '[data-testid*="filter"]',
            '.filter',
            '.facet',
            '.refinement',
            'input[type="checkbox"]',
            'input[type="radio"]'
        ]

        filters = []
        for selector in filter_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                filters.extend(elements)
            except:
                continue

        return filters

    async def _find_sort_elements(self) -> List[Any]:
        """Find sort/ordering elements on the results page."""
        sort_selectors = [
            '[data-testid*="sort"]',
            '.sort',
            '.order',
            'select[name*="sort"]',
            '.dropdown-sort'
        ]

        sort_elements = []
        for selector in sort_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                sort_elements.extend(elements)
            except:
                continue

        return sort_elements

    async def _train_details_page(self) -> Dict[str, Any]:
        """Train on product/service details page."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    "🔍 Training on details page interactions...", is_bot=True)

            # Find booking buttons
            booking_buttons = await self._find_booking_buttons()

            # Find image galleries
            image_galleries = await self._find_image_galleries()

            # Find amenities/features lists
            amenities = await self._find_amenities()

            # Find reviews section
            reviews = await self._find_reviews_section()

            return {
                'success': True,
                'booking_buttons': len(booking_buttons),
                'image_galleries': len(image_galleries),
                'amenities_found': len(amenities),
                'reviews_section': len(reviews) > 0
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _find_booking_buttons(self) -> List[Any]:
        """Find booking/reservation buttons."""
        button_selectors = [
            '[data-testid*="book"]',
            '[data-testid*="reserve"]',
            '.book-button',
            '.reserve-button',
            '.cta-button',
            'button:has-text("Book")',
            'button:has-text("Reserve")',
            'button:has-text("Select")'
        ]

        buttons = []
        for selector in button_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                buttons.extend(elements)
            except:
                continue

        return buttons

    async def _find_image_galleries(self) -> List[Any]:
        """Find image gallery elements."""
        gallery_selectors = [
            '.gallery',
            '.image-gallery',
            '.photos',
            '.carousel',
            '[data-testid*="gallery"]'
        ]

        galleries = []
        for selector in gallery_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                galleries.extend(elements)
            except:
                continue

        return galleries

    async def _find_amenities(self) -> List[Any]:
        """Find amenities or features lists."""
        amenity_selectors = [
            '.amenities',
            '.features',
            '.facilities',
            '.services',
            '[data-testid*="amenity"]'
        ]

        amenities = []
        for selector in amenity_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                amenities.extend(elements)
            except:
                continue

        return amenities

    async def _find_reviews_section(self) -> List[Any]:
        """Find reviews section."""
        review_selectors = [
            '.reviews',
            '.ratings',
            '.feedback',
            '[data-testid*="review"]'
        ]

        reviews = []
        for selector in review_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                reviews.extend(elements)
            except:
                continue

        return reviews

    async def _train_booking_form(self) -> Dict[str, Any]:
        """Train on booking/checkout forms."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    "💳 Training on booking form interactions...", is_bot=True)

            # Use advanced form detection if available
            if ADVANCED_CAPABILITIES and self.form_detector:
                forms = await self.form_detector.detect_forms()

                booking_forms = [f for f in forms if f['purpose'] in ['payment', 'booking', 'checkout']]

                return {
                    'success': True,
                    'forms_detected': len(forms),
                    'booking_forms': len(booking_forms)
                }
            else:
                # Basic form detection
                forms = await self.page.query_selector_all('form')
                return {
                    'success': True,
                    'forms_detected': len(forms),
                    'booking_forms': len(forms)
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _train_general_page(self) -> Dict[str, Any]:
        """Train on general page elements."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam",
                    "🔧 Training on general page elements...", is_bot=True)

            # Count interactive elements
            buttons = await self.page.query_selector_all('button')
            links = await self.page.query_selector_all('a[href]')
            inputs = await self.page.query_selector_all('input')

            return {
                'success': True,
                'buttons': len(buttons),
                'links': len(links),
                'inputs': len(inputs)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
