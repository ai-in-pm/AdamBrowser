#!/usr/bin/env python3
"""
Travel Booking Patterns for AI Agent Training

This module contains patterns, selectors, and behavioral models specifically
designed for travel booking websites like Expedia, Booking.com, Hotels.com, etc.

Features:
- Website-specific element patterns
- Booking workflow templates
- Common travel form structures
- Error handling patterns
- User behavior simulation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class TravelSite(Enum):
    """Supported travel booking websites."""
    EXPEDIA = "expedia"
    BOOKING = "booking"
    HOTELS = "hotels"
    KAYAK = "kayak"
    PRICELINE = "priceline"
    ORBITZ = "orbitz"


@dataclass
class ElementPattern:
    """Pattern for identifying elements on travel sites."""
    selectors: List[str]
    attributes: Dict[str, str]
    text_patterns: List[str]
    confidence: float
    site_specific: bool = False


class TravelBookingPatterns:
    """Comprehensive patterns for travel booking websites."""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.workflows = self._initialize_workflows()
        self.common_errors = self._initialize_error_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, ElementPattern]]:
        """Initialize element patterns for different travel sites."""
        return {
            'expedia': {
                'search_forms': ElementPattern(
                    selectors=[
                        '[data-testid="flight-search-form"]',
                        '[data-testid="hotel-search-form"]',
                        '[data-testid="car-search-form"]',
                        '.flight-search-form',
                        '.hotel-search-form',
                        '.car-search-form'
                    ],
                    attributes={'role': 'form', 'method': 'post'},
                    text_patterns=['search', 'find', 'book'],
                    confidence=0.9,
                    site_specific=True
                ),
                'location_inputs': ElementPattern(
                    selectors=[
                        '[data-testid="origin-input"]',
                        '[data-testid="destination-input"]',
                        '[placeholder*="From" i]',
                        '[placeholder*="To" i]',
                        '[placeholder*="Where" i]',
                        'input[name*="origin"]',
                        'input[name*="destination"]'
                    ],
                    attributes={'type': 'text', 'autocomplete': 'off'},
                    text_patterns=['from', 'to', 'where', 'destination', 'origin'],
                    confidence=0.85
                ),
                'date_pickers': ElementPattern(
                    selectors=[
                        '[data-testid*="date"]',
                        '.date-picker',
                        'input[type="date"]',
                        '[placeholder*="date" i]'
                    ],
                    attributes={'type': 'date'},
                    text_patterns=['departure', 'return', 'check-in', 'check-out'],
                    confidence=0.8
                ),
                'traveler_selectors': ElementPattern(
                    selectors=[
                        '[data-testid="travelers-selector"]',
                        '[data-testid="guests-selector"]',
                        '.travelers-dropdown',
                        '.guests-dropdown'
                    ],
                    attributes={'role': 'button'},
                    text_patterns=['travelers', 'guests', 'adults', 'children'],
                    confidence=0.75
                ),
                'search_buttons': ElementPattern(
                    selectors=[
                        '[data-testid="search-button"]',
                        'button[type="submit"]',
                        '.search-btn',
                        '.search-button'
                    ],
                    attributes={'type': 'submit'},
                    text_patterns=['search', 'find', 'go'],
                    confidence=0.9
                ),
                'result_items': ElementPattern(
                    selectors=[
                        '[data-testid="result-item"]',
                        '.result-item',
                        '.search-result',
                        '.listing'
                    ],
                    attributes={'role': 'listitem'},
                    text_patterns=['price', 'book', 'select'],
                    confidence=0.8
                ),
                'booking_buttons': ElementPattern(
                    selectors=[
                        '[data-testid*="book"]',
                        '[data-testid*="reserve"]',
                        '.book-button',
                        '.reserve-button',
                        'button:has-text("Book")',
                        'button:has-text("Reserve")'
                    ],
                    attributes={'type': 'button'},
                    text_patterns=['book', 'reserve', 'select', 'choose'],
                    confidence=0.85
                ),
                'price_elements': ElementPattern(
                    selectors=[
                        '[data-testid*="price"]',
                        '.price',
                        '.cost',
                        '.rate',
                        '.amount'
                    ],
                    attributes={'data-currency': 'USD'},
                    text_patterns=['$', 'usd', 'price', 'total'],
                    confidence=0.7
                )
            },
            'booking': {
                'search_forms': ElementPattern(
                    selectors=[
                        '.sb-searchbox',
                        '#frm',
                        '.search-form'
                    ],
                    attributes={'role': 'search'},
                    text_patterns=['search', 'find'],
                    confidence=0.9,
                    site_specific=True
                ),
                'destination_input': ElementPattern(
                    selectors=[
                        '#ss',
                        '[name="ss"]',
                        '.destination-input'
                    ],
                    attributes={'type': 'search'},
                    text_patterns=['where', 'destination'],
                    confidence=0.85
                ),
                'date_inputs': ElementPattern(
                    selectors=[
                        '.sb-date-field',
                        '[data-mode="checkin"]',
                        '[data-mode="checkout"]'
                    ],
                    attributes={'type': 'text'},
                    text_patterns=['check-in', 'check-out'],
                    confidence=0.8
                )
            },
            'generic': {
                'forms': ElementPattern(
                    selectors=['form', '.form', '.search-form'],
                    attributes={'method': 'post'},
                    text_patterns=['search', 'book', 'reserve'],
                    confidence=0.6
                ),
                'inputs': ElementPattern(
                    selectors=['input', 'select', 'textarea'],
                    attributes={'type': 'text'},
                    text_patterns=[],
                    confidence=0.5
                ),
                'buttons': ElementPattern(
                    selectors=['button', 'input[type="submit"]', '.btn'],
                    attributes={'type': 'button'},
                    text_patterns=['search', 'submit', 'book'],
                    confidence=0.6
                )
            }
        }
    
    def _initialize_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize booking workflow templates."""
        return {
            'flight_booking': [
                {
                    'step': 'search_form',
                    'required_fields': ['origin', 'destination', 'departure_date'],
                    'optional_fields': ['return_date', 'travelers', 'class'],
                    'expected_elements': ['search_button'],
                    'next_step': 'results_page'
                },
                {
                    'step': 'results_page',
                    'required_elements': ['result_items', 'filters'],
                    'actions': ['filter', 'sort', 'select'],
                    'next_step': 'details_page'
                },
                {
                    'step': 'details_page',
                    'required_elements': ['booking_button', 'price_display'],
                    'actions': ['review_details', 'book'],
                    'next_step': 'booking_form'
                },
                {
                    'step': 'booking_form',
                    'required_fields': ['passenger_info', 'contact_info'],
                    'optional_fields': ['seat_selection', 'extras'],
                    'next_step': 'payment'
                },
                {
                    'step': 'payment',
                    'required_fields': ['payment_method', 'billing_info'],
                    'actions': ['complete_booking'],
                    'next_step': 'confirmation'
                }
            ],
            'hotel_booking': [
                {
                    'step': 'search_form',
                    'required_fields': ['destination', 'checkin_date', 'checkout_date'],
                    'optional_fields': ['guests', 'rooms'],
                    'next_step': 'results_page'
                },
                {
                    'step': 'results_page',
                    'required_elements': ['hotel_listings', 'filters'],
                    'actions': ['filter_by_price', 'filter_by_rating', 'select_hotel'],
                    'next_step': 'hotel_details'
                },
                {
                    'step': 'hotel_details',
                    'required_elements': ['room_options', 'amenities', 'booking_button'],
                    'actions': ['select_room', 'book'],
                    'next_step': 'booking_form'
                }
            ],
            'car_rental': [
                {
                    'step': 'search_form',
                    'required_fields': ['pickup_location', 'pickup_date', 'dropoff_date'],
                    'optional_fields': ['dropoff_location', 'driver_age'],
                    'next_step': 'results_page'
                },
                {
                    'step': 'results_page',
                    'required_elements': ['car_listings', 'filters'],
                    'actions': ['filter_by_type', 'filter_by_price', 'select_car'],
                    'next_step': 'booking_form'
                }
            ]
        }
    
    def _initialize_error_patterns(self) -> Dict[str, List[str]]:
        """Initialize common error patterns and messages."""
        return {
            'validation_errors': [
                'Please enter a valid destination',
                'Please select a departure date',
                'Please select a return date',
                'Invalid date selection',
                'Departure date cannot be in the past',
                'Return date must be after departure date'
            ],
            'availability_errors': [
                'No flights found for your search',
                'No hotels available for selected dates',
                'No cars available at this location',
                'Limited availability for selected dates'
            ],
            'booking_errors': [
                'Unable to complete booking',
                'Payment processing failed',
                'Session expired',
                'Price has changed',
                'Selected option no longer available'
            ],
            'form_errors': [
                'Please fill in all required fields',
                'Invalid email address',
                'Invalid phone number',
                'Password does not meet requirements',
                'Credit card number is invalid'
            ]
        }
    
    def get_patterns_for_site(self, site: TravelSite) -> Dict[str, ElementPattern]:
        """Get element patterns for a specific travel site."""
        site_patterns = self.patterns.get(site.value, {})
        generic_patterns = self.patterns.get('generic', {})
        
        # Merge site-specific patterns with generic ones
        merged_patterns = {**generic_patterns, **site_patterns}
        return merged_patterns
    
    def get_workflow_for_booking_type(self, booking_type: str) -> List[Dict[str, Any]]:
        """Get workflow steps for a specific booking type."""
        return self.workflows.get(booking_type, [])
    
    def detect_site_from_url(self, url: str) -> TravelSite:
        """Detect travel site from URL."""
        url_lower = url.lower()
        
        if 'expedia' in url_lower:
            return TravelSite.EXPEDIA
        elif 'booking' in url_lower:
            return TravelSite.BOOKING
        elif 'hotels' in url_lower:
            return TravelSite.HOTELS
        elif 'kayak' in url_lower:
            return TravelSite.KAYAK
        elif 'priceline' in url_lower:
            return TravelSite.PRICELINE
        elif 'orbitz' in url_lower:
            return TravelSite.ORBITZ
        else:
            return TravelSite.EXPEDIA  # Default fallback
    
    def get_test_data_for_booking_type(self, booking_type: str) -> Dict[str, Any]:
        """Get test data for different booking types."""
        test_data = {
            'flight_booking': {
                'origin': 'New York, NY (JFK)',
                'destination': 'Los Angeles, CA (LAX)',
                'departure_date': '12/15/2024',
                'return_date': '12/22/2024',
                'travelers': 1,
                'class': 'Economy'
            },
            'hotel_booking': {
                'destination': 'Las Vegas, NV',
                'checkin_date': '12/15/2024',
                'checkout_date': '12/18/2024',
                'guests': 2,
                'rooms': 1
            },
            'car_rental': {
                'pickup_location': 'Los Angeles, CA',
                'dropoff_location': 'Los Angeles, CA',
                'pickup_date': '12/15/2024',
                'dropoff_date': '12/18/2024',
                'driver_age': '25-65'
            }
        }
        
        return test_data.get(booking_type, {})
    
    def save_patterns_to_file(self, filename: str = "travel_patterns.json"):
        """Save patterns to a JSON file for persistence."""
        try:
            # Convert patterns to serializable format
            serializable_patterns = {}
            for site, patterns in self.patterns.items():
                serializable_patterns[site] = {}
                for pattern_name, pattern in patterns.items():
                    serializable_patterns[site][pattern_name] = {
                        'selectors': pattern.selectors,
                        'attributes': pattern.attributes,
                        'text_patterns': pattern.text_patterns,
                        'confidence': pattern.confidence,
                        'site_specific': pattern.site_specific
                    }
            
            data = {
                'patterns': serializable_patterns,
                'workflows': self.workflows,
                'error_patterns': self.common_errors
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"✅ Patterns saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving patterns: {e}")
    
    def load_patterns_from_file(self, filename: str = "travel_patterns.json"):
        """Load patterns from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert back to ElementPattern objects
            loaded_patterns = {}
            for site, patterns in data.get('patterns', {}).items():
                loaded_patterns[site] = {}
                for pattern_name, pattern_data in patterns.items():
                    loaded_patterns[site][pattern_name] = ElementPattern(
                        selectors=pattern_data['selectors'],
                        attributes=pattern_data['attributes'],
                        text_patterns=pattern_data['text_patterns'],
                        confidence=pattern_data['confidence'],
                        site_specific=pattern_data.get('site_specific', False)
                    )
            
            self.patterns = loaded_patterns
            self.workflows = data.get('workflows', {})
            self.common_errors = data.get('error_patterns', {})
            
            print(f"✅ Patterns loaded from {filename}")
            
        except Exception as e:
            print(f"❌ Error loading patterns: {e}")


# Global instance for easy access
travel_patterns = TravelBookingPatterns()
