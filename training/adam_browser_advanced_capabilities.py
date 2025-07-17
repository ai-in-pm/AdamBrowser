#!/usr/bin/env python3
"""
Advanced Capabilities Module for Adam Browser

This module provides sophisticated automation capabilities including:
- Smart form detection and filling
- Natural mouse movement simulation
- Context-aware decision making
- Advanced error recovery strategies
- Learning from user interactions
"""

import asyncio
import random
import math
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class InteractionPattern(Enum):
    """Types of interaction patterns for human-like behavior."""
    CAUTIOUS = "cautious"      # Slow, careful movements
    NORMAL = "normal"          # Average human speed
    CONFIDENT = "confident"    # Fast, direct movements
    DISTRACTED = "distracted"  # Occasional pauses and corrections


@dataclass
class FormField:
    """Represents a detected form field with metadata."""
    element: Any
    field_type: str
    label: str
    placeholder: str
    required: bool
    validation_pattern: Optional[str]
    suggested_value: Optional[str]
    confidence: float


class SmartFormDetector:
    """Advanced form detection with intelligent field analysis."""
    
    def __init__(self, page):
        self.page = page
        self.form_cache = {}
        self.field_patterns = {
            'email': [
                r'email', r'e-mail', r'mail', r'@'
            ],
            'password': [
                r'password', r'pass', r'pwd', r'secret'
            ],
            'name': [
                r'name', r'full.?name', r'first.?name', r'last.?name',
                r'given.?name', r'family.?name', r'surname'
            ],
            'phone': [
                r'phone', r'tel', r'mobile', r'cell', r'number'
            ],
            'address': [
                r'address', r'street', r'location', r'addr'
            ],
            'city': [
                r'city', r'town', r'municipality'
            ],
            'zip': [
                r'zip', r'postal', r'postcode', r'zipcode'
            ],
            'country': [
                r'country', r'nation'
            ],
            'date': [
                r'date', r'birth', r'dob', r'birthday'
            ],
            'company': [
                r'company', r'organization', r'employer', r'business'
            ],
            # Travel-specific fields for Expedia
            'destination': [
                r'where', r'destination', r'going', r'to', r'location'
            ],
            'departure': [
                r'from', r'departure', r'origin', r'leaving'
            ],
            'checkin': [
                r'check.?in', r'arrival', r'start'
            ],
            'checkout': [
                r'check.?out', r'departure', r'end'
            ],
            'travelers': [
                r'travelers', r'guests', r'people', r'adults', r'children'
            ],
            'rooms': [
                r'rooms', r'room'
            ],
            # Enhanced travel patterns
            'flight_class': [
                r'class', r'cabin', r'economy', r'business', r'first'
            ],
            'car_type': [
                r'car.?type', r'vehicle', r'compact', r'sedan', r'suv'
            ],
            'hotel_rating': [
                r'stars', r'rating', r'quality'
            ]
        }
    
    async def detect_forms(self) -> List[Dict[str, Any]]:
        """Detect all forms on the page with detailed analysis."""
        try:
            forms = await self.page.query_selector_all('form')
            detected_forms = []
            
            for i, form in enumerate(forms):
                form_info = await self._analyze_form(form, i)
                if form_info:
                    detected_forms.append(form_info)
            
            return detected_forms
            
        except Exception as e:
            print(f"❌ Error detecting forms: {e}")
            return []
    
    async def _analyze_form(self, form_element, form_index: int) -> Optional[Dict[str, Any]]:
        """Analyze a single form and its fields."""
        try:
            # Get form metadata
            form_action = await form_element.get_attribute('action') or ''
            form_method = await form_element.get_attribute('method') or 'GET'
            form_id = await form_element.get_attribute('id') or f'form_{form_index}'
            
            # Find all input fields within the form
            fields = await self._detect_form_fields(form_element)
            
            if not fields:
                return None
            
            # Determine form purpose
            form_purpose = self._determine_form_purpose(fields, form_action)
            
            return {
                'element': form_element,
                'id': form_id,
                'action': form_action,
                'method': form_method,
                'purpose': form_purpose,
                'fields': fields,
                'field_count': len(fields),
                'confidence': self._calculate_form_confidence(fields)
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing form: {e}")
            return None
    
    async def _detect_form_fields(self, form_element) -> List[FormField]:
        """Detect and analyze all fields within a form."""
        fields = []
        
        # Query for various input types
        input_selectors = [
            'input[type="text"]', 'input[type="email"]', 'input[type="password"]',
            'input[type="tel"]', 'input[type="url"]', 'input[type="search"]',
            'input[type="number"]', 'input[type="date"]', 'input[type="time"]',
            'input:not([type])', 'textarea', 'select'
        ]
        
        for selector in input_selectors:
            try:
                elements = await form_element.query_selector_all(selector)
                for element in elements:
                    field_info = await self._analyze_field(element)
                    if field_info:
                        fields.append(field_info)
            except Exception as e:
                print(f"⚠️ Error finding fields with selector {selector}: {e}")
                continue
        
        return fields
    
    async def _analyze_field(self, element) -> Optional[FormField]:
        """Analyze a single form field."""
        try:
            # Get field attributes
            field_type = await element.get_attribute('type') or 'text'
            name = await element.get_attribute('name') or ''
            placeholder = await element.get_attribute('placeholder') or ''
            required = await element.get_attribute('required') is not None
            pattern = await element.get_attribute('pattern')
            
            # Get associated label
            label = await self._find_field_label(element)
            
            # Determine field purpose and suggested value
            field_purpose = self._classify_field_purpose(name, placeholder, label, field_type)
            suggested_value = self._get_suggested_value(field_purpose, field_type)
            
            # Calculate confidence
            confidence = self._calculate_field_confidence(name, placeholder, label, field_type)
            
            return FormField(
                element=element,
                field_type=field_purpose,
                label=label,
                placeholder=placeholder,
                required=required,
                validation_pattern=pattern,
                suggested_value=suggested_value,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"⚠️ Error analyzing field: {e}")
            return None
    
    async def _find_field_label(self, element) -> str:
        """Find the label associated with a form field."""
        try:
            # Try to find label by 'for' attribute
            element_id = await element.get_attribute('id')
            if element_id:
                label_element = await self.page.query_selector(f'label[for="{element_id}"]')
                if label_element:
                    return await label_element.text_content() or ''
            
            # Try to find parent label
            parent_label = await element.query_selector('xpath=ancestor::label[1]')
            if parent_label:
                return await parent_label.text_content() or ''
            
            # Try to find preceding text
            preceding_text = await element.evaluate('''
                element => {
                    let text = '';
                    let prev = element.previousSibling;
                    while (prev && text.length < 50) {
                        if (prev.nodeType === 3) { // Text node
                            text = prev.textContent.trim() + ' ' + text;
                        } else if (prev.tagName && prev.tagName.toLowerCase() === 'label') {
                            text = prev.textContent.trim() + ' ' + text;
                            break;
                        }
                        prev = prev.previousSibling;
                    }
                    return text.trim();
                }
            ''')
            
            return preceding_text or ''
            
        except Exception as e:
            print(f"⚠️ Error finding field label: {e}")
            return ''
    
    def _classify_field_purpose(self, name: str, placeholder: str, label: str, field_type: str) -> str:
        """Classify the purpose of a form field."""
        combined_text = f"{name} {placeholder} {label}".lower()
        
        # Check against known patterns
        for purpose, patterns in self.field_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    return purpose
        
        # Fallback based on input type
        type_mapping = {
            'email': 'email',
            'password': 'password',
            'tel': 'phone',
            'url': 'website',
            'date': 'date',
            'number': 'number'
        }
        
        return type_mapping.get(field_type, 'text')
    
    def _get_suggested_value(self, field_purpose: str, field_type: str) -> Optional[str]:
        """Get a suggested value for a field based on its purpose."""
        suggestions = {
            'email': 'test.user@example.com',
            'password': 'SecurePass123!',
            'name': 'John Doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1 (555) 123-4567',
            'address': '123 Main Street',
            'city': 'New York',
            'zip': '10001',
            'country': 'United States',
            'company': 'Test Company Inc.',
            'website': 'https://example.com',
            'date': '1990-01-01'
        }
        
        return suggestions.get(field_purpose)
    
    def _calculate_field_confidence(self, name: str, placeholder: str, label: str, field_type: str) -> float:
        """Calculate confidence score for field classification."""
        confidence = 0.5  # Base confidence
        
        # Boost for clear indicators
        combined_text = f"{name} {placeholder} {label}".lower()
        
        if any(keyword in combined_text for keyword in ['email', 'password', 'name', 'phone']):
            confidence += 0.3
        
        if field_type in ['email', 'password', 'tel']:
            confidence += 0.2
        
        if placeholder or label:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _determine_form_purpose(self, fields: List[FormField], action: str) -> str:
        """Determine the overall purpose of a form."""
        field_types = [field.field_type for field in fields]
        
        # Login form
        if 'email' in field_types and 'password' in field_types and len(fields) <= 3:
            return 'login'
        
        # Registration form
        if 'email' in field_types and 'password' in field_types and len(fields) > 3:
            return 'registration'
        
        # Contact form
        if 'email' in field_types and any(t in field_types for t in ['name', 'phone']):
            return 'contact'
        
        # Search form
        if len(fields) == 1 and any(t in field_types for t in ['text', 'search']):
            return 'search'
        
        # Payment form
        if any('card' in field.label.lower() or 'payment' in field.label.lower() for field in fields):
            return 'payment'
        
        return 'general'
    
    def _calculate_form_confidence(self, fields: List[FormField]) -> float:
        """Calculate overall confidence for form detection."""
        if not fields:
            return 0.0
        
        avg_field_confidence = sum(field.confidence for field in fields) / len(fields)
        
        # Boost for forms with clear structure
        if len(fields) >= 2:
            avg_field_confidence += 0.1
        
        if any(field.required for field in fields):
            avg_field_confidence += 0.1
        
        return min(1.0, avg_field_confidence)


class NaturalMouseMovement:
    """Simulates natural human mouse movement patterns."""
    
    def __init__(self):
        self.movement_style = InteractionPattern.NORMAL
        self.error_rate = 0.02  # 2% chance of minor errors
        
    def calculate_bezier_path(self, start: Tuple[float, float], 
                            end: Tuple[float, float], 
                            num_points: int = 20) -> List[Tuple[float, float]]:
        """Calculate a natural Bézier curve path between two points."""
        x1, y1 = start
        x2, y2 = end
        
        # Add some randomness to control points for natural movement
        control_offset = random.uniform(0.2, 0.4)
        
        # Control points for Bézier curve
        cx1 = x1 + (x2 - x1) * control_offset + random.uniform(-50, 50)
        cy1 = y1 + random.uniform(-30, 30)
        cx2 = x1 + (x2 - x1) * (1 - control_offset) + random.uniform(-50, 50)
        cy2 = y2 + random.uniform(-30, 30)
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Cubic Bézier curve formula
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y2
            
            points.append((x, y))
        
        return points
    
    def calculate_movement_timing(self, distance: float) -> List[float]:
        """Calculate realistic timing for mouse movement."""
        base_time = distance / 1000  # Base time in seconds
        
        # Adjust based on movement style
        style_multipliers = {
            InteractionPattern.CAUTIOUS: 1.5,
            InteractionPattern.NORMAL: 1.0,
            InteractionPattern.CONFIDENT: 0.7,
            InteractionPattern.DISTRACTED: 1.3
        }
        
        total_time = base_time * style_multipliers[self.movement_style]
        
        # Add some randomness
        total_time *= random.uniform(0.8, 1.2)
        
        return total_time
    
    async def move_to_element(self, page, element, offset: Optional[Tuple[int, int]] = None):
        """Move mouse to an element with natural movement."""
        try:
            # Get element bounding box
            box = await element.bounding_box()
            if not box:
                return False
            
            # Calculate target position (center of element + offset)
            target_x = box['x'] + box['width'] / 2
            target_y = box['y'] + box['height'] / 2
            
            if offset:
                target_x += offset[0]
                target_y += offset[1]
            
            # Get current mouse position (approximate)
            current_pos = await page.evaluate('() => ({ x: window.mouseX || 0, y: window.mouseY || 0 })')
            start_x = current_pos.get('x', 0)
            start_y = current_pos.get('y', 0)
            
            # Calculate natural movement path
            path = self.calculate_bezier_path((start_x, start_y), (target_x, target_y))
            
            # Calculate timing
            distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
            total_time = self.calculate_movement_timing(distance)
            
            # Execute movement
            for i, (x, y) in enumerate(path):
                await page.mouse.move(x, y)
                await asyncio.sleep(total_time / len(path))
            
            # Store current position for next movement
            await page.evaluate(f'() => {{ window.mouseX = {target_x}; window.mouseY = {target_y}; }}')
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error in natural mouse movement: {e}")
            return False


class ContextAwareDecisionMaker:
    """Makes intelligent decisions based on page context and user goals."""

    def __init__(self):
        self.decision_history = []
        self.success_patterns = {}
        self.failure_patterns = {}

    async def analyze_page_context(self, page) -> Dict[str, Any]:
        """Analyze the current page context to understand available actions."""
        try:
            context = {
                'url': page.url,
                'title': await page.title(),
                'forms': [],
                'buttons': [],
                'links': [],
                'inputs': [],
                'page_type': 'unknown'
            }

            # Detect forms
            form_detector = SmartFormDetector(page)
            context['forms'] = await form_detector.detect_forms()

            # Detect interactive elements
            buttons = await page.query_selector_all('button, input[type="submit"], input[type="button"]')
            context['buttons'] = len(buttons)

            links = await page.query_selector_all('a[href]')
            context['links'] = len(links)

            inputs = await page.query_selector_all('input, textarea, select')
            context['inputs'] = len(inputs)

            # Determine page type
            context['page_type'] = self._classify_page_type(context)

            return context

        except Exception as e:
            print(f"⚠️ Error analyzing page context: {e}")
            return {}

    def _classify_page_type(self, context: Dict[str, Any]) -> str:
        """Classify the type of page based on its content."""
        url = context.get('url', '').lower()
        title = context.get('title', '').lower()
        forms = context.get('forms', [])

        # E-commerce
        if any(keyword in url for keyword in ['shop', 'store', 'buy', 'cart', 'checkout']):
            return 'ecommerce'

        # Social media
        if any(keyword in url for keyword in ['facebook', 'twitter', 'instagram', 'linkedin']):
            return 'social_media'

        # Search engines
        if any(keyword in url for keyword in ['google', 'bing', 'yahoo', 'search']):
            return 'search_engine'

        # Login/Registration
        if forms and any(form['purpose'] in ['login', 'registration'] for form in forms):
            return 'authentication'

        # News/Blog
        if any(keyword in title for keyword in ['news', 'blog', 'article']):
            return 'content'

        # Video platforms
        if any(keyword in url for keyword in ['youtube', 'vimeo', 'video']):
            return 'video_platform'

        # Travel booking sites
        if any(keyword in url for keyword in ['expedia', 'booking', 'hotels', 'kayak']):
            return 'travel_booking'

        return 'general'

    def suggest_next_actions(self, context: Dict[str, Any], user_goal: str) -> List[Dict[str, Any]]:
        """Suggest the next best actions based on context and user goal."""
        suggestions = []
        goal_lower = user_goal.lower()
        page_type = context.get('page_type', 'general')

        # Goal-based suggestions
        if 'search' in goal_lower:
            suggestions.extend(self._suggest_search_actions(context))

        if 'fill' in goal_lower or 'form' in goal_lower:
            suggestions.extend(self._suggest_form_actions(context))

        if 'buy' in goal_lower or 'purchase' in goal_lower:
            suggestions.extend(self._suggest_shopping_actions(context))

        if 'login' in goal_lower or 'sign in' in goal_lower:
            suggestions.extend(self._suggest_login_actions(context))

        if any(keyword in goal_lower for keyword in ['book', 'travel', 'flight', 'hotel', 'car']):
            suggestions.extend(self._suggest_travel_actions(context, goal_lower))

        # Page-type based suggestions
        if page_type == 'ecommerce':
            suggestions.extend(self._suggest_ecommerce_actions(context))
        elif page_type == 'social_media':
            suggestions.extend(self._suggest_social_actions(context))
        elif page_type == 'travel_booking':
            suggestions.extend(self._suggest_travel_booking_actions(context))

        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return suggestions[:5]

    def _suggest_search_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest search-related actions."""
        suggestions = []

        if context.get('page_type') == 'search_engine':
            suggestions.append({
                'action': 'use_search_box',
                'description': 'Use the main search box',
                'confidence': 0.9,
                'selector': 'input[name="q"], input[type="search"]'
            })

        return suggestions

    def _suggest_form_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest form-related actions."""
        suggestions = []
        forms = context.get('forms', [])

        for form in forms:
            if form['purpose'] == 'contact':
                suggestions.append({
                    'action': 'fill_contact_form',
                    'description': f'Fill contact form with {form["field_count"]} fields',
                    'confidence': form['confidence'],
                    'form_data': form
                })
            elif form['purpose'] == 'registration':
                suggestions.append({
                    'action': 'fill_registration_form',
                    'description': f'Complete registration form',
                    'confidence': form['confidence'],
                    'form_data': form
                })

        return suggestions

    def _suggest_shopping_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest shopping-related actions."""
        suggestions = []

        if context.get('page_type') == 'ecommerce':
            suggestions.append({
                'action': 'search_products',
                'description': 'Search for products',
                'confidence': 0.8,
                'selector': 'input[type="search"], .search-input'
            })

            suggestions.append({
                'action': 'browse_categories',
                'description': 'Browse product categories',
                'confidence': 0.7,
                'selector': '.category, .nav-category'
            })

        return suggestions

    def _suggest_login_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest login-related actions."""
        suggestions = []
        forms = context.get('forms', [])

        for form in forms:
            if form['purpose'] == 'login':
                suggestions.append({
                    'action': 'perform_login',
                    'description': 'Fill login form',
                    'confidence': form['confidence'],
                    'form_data': form
                })

        return suggestions

    def _suggest_ecommerce_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest e-commerce specific actions."""
        return [
            {
                'action': 'add_to_cart',
                'description': 'Add item to shopping cart',
                'confidence': 0.6,
                'selector': '.add-to-cart, [data-action="add-to-cart"]'
            },
            {
                'action': 'view_product_details',
                'description': 'View product details',
                'confidence': 0.5,
                'selector': '.product-link, .product-title'
            }
        ]

    def _suggest_social_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest social media specific actions."""
        return [
            {
                'action': 'create_post',
                'description': 'Create a new post',
                'confidence': 0.6,
                'selector': '[data-testid="compose"], .compose-button'
            },
            {
                'action': 'interact_with_content',
                'description': 'Like or comment on content',
                'confidence': 0.5,
                'selector': '.like-button, .comment-button'
            }
        ]

    def _suggest_travel_actions(self, context: Dict[str, Any], goal: str) -> List[Dict[str, Any]]:
        """Suggest travel-specific actions based on user goal."""
        suggestions = []

        if 'flight' in goal:
            suggestions.append({
                'action': 'search_flights',
                'description': 'Search for flights',
                'confidence': 0.9,
                'selector': '[data-testid="flight-search-form"], .flight-search-form'
            })

        if 'hotel' in goal:
            suggestions.append({
                'action': 'search_hotels',
                'description': 'Search for hotels',
                'confidence': 0.9,
                'selector': '[data-testid="hotel-search-form"], .hotel-search-form'
            })

        if 'car' in goal:
            suggestions.append({
                'action': 'search_cars',
                'description': 'Search for car rentals',
                'confidence': 0.9,
                'selector': '[data-testid="car-search-form"], .car-search-form'
            })

        return suggestions

    def _suggest_travel_booking_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest actions specific to travel booking sites."""
        return [
            {
                'action': 'fill_travel_search',
                'description': 'Fill travel search form',
                'confidence': 0.8,
                'selector': '.search-form, [data-testid*="search-form"]'
            },
            {
                'action': 'select_travel_dates',
                'description': 'Select travel dates',
                'confidence': 0.7,
                'selector': '.date-picker, [data-testid*="date"]'
            },
            {
                'action': 'choose_travelers',
                'description': 'Select number of travelers',
                'confidence': 0.6,
                'selector': '.travelers-selector, [data-testid*="travelers"]'
            },
            {
                'action': 'apply_filters',
                'description': 'Apply search filters',
                'confidence': 0.5,
                'selector': '.filter, .facet, [data-testid*="filter"]'
            }
        ]


class LearningSystem:
    """Learns from user interactions and improves performance over time."""

    def __init__(self, storage_path: str = "adam_browser_learning.json"):
        self.storage_path = Path(storage_path)
        self.interaction_history = []
        self.success_patterns = {}
        self.failure_patterns = {}
        self.user_preferences = {}
        self.load_learning_data()

    def record_interaction(self, action: str, context: Dict[str, Any],
                          success: bool, execution_time: float):
        """Record an interaction for learning purposes."""
        interaction = {
            'timestamp': time.time(),
            'action': action,
            'context': context,
            'success': success,
            'execution_time': execution_time
        }

        self.interaction_history.append(interaction)

        # Update patterns
        if success:
            self._update_success_patterns(action, context)
        else:
            self._update_failure_patterns(action, context)

        # Limit history size
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-1000:]

        # Save periodically
        if len(self.interaction_history) % 10 == 0:
            self.save_learning_data()

    def _update_success_patterns(self, action: str, context: Dict[str, Any]):
        """Update successful interaction patterns."""
        if action not in self.success_patterns:
            self.success_patterns[action] = {}

        page_type = context.get('page_type', 'unknown')
        if page_type not in self.success_patterns[action]:
            self.success_patterns[action][page_type] = 0

        self.success_patterns[action][page_type] += 1

    def _update_failure_patterns(self, action: str, context: Dict[str, Any]):
        """Update failed interaction patterns."""
        if action not in self.failure_patterns:
            self.failure_patterns[action] = {}

        page_type = context.get('page_type', 'unknown')
        if page_type not in self.failure_patterns[action]:
            self.failure_patterns[action][page_type] = 0

        self.failure_patterns[action][page_type] += 1

    def get_success_probability(self, action: str, context: Dict[str, Any]) -> float:
        """Calculate the probability of success for an action in given context."""
        page_type = context.get('page_type', 'unknown')

        successes = self.success_patterns.get(action, {}).get(page_type, 0)
        failures = self.failure_patterns.get(action, {}).get(page_type, 0)

        if successes + failures == 0:
            return 0.5  # No data, assume 50% chance

        return successes / (successes + failures)

    def suggest_best_strategy(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest the best strategy for an action based on learning."""
        success_prob = self.get_success_probability(action, context)

        # Get average execution time for successful attempts
        avg_time = self._get_average_execution_time(action, context, success_only=True)

        return {
            'success_probability': success_prob,
            'estimated_time': avg_time,
            'confidence': 'high' if success_prob > 0.8 else 'medium' if success_prob > 0.5 else 'low',
            'recommendation': self._get_strategy_recommendation(success_prob)
        }

    def _get_average_execution_time(self, action: str, context: Dict[str, Any],
                                   success_only: bool = False) -> float:
        """Get average execution time for an action."""
        page_type = context.get('page_type', 'unknown')

        relevant_interactions = [
            i for i in self.interaction_history
            if i['action'] == action and
               i['context'].get('page_type') == page_type and
               (not success_only or i['success'])
        ]

        if not relevant_interactions:
            return 5.0  # Default estimate

        times = [i['execution_time'] for i in relevant_interactions]
        return sum(times) / len(times)

    def _get_strategy_recommendation(self, success_prob: float) -> str:
        """Get strategy recommendation based on success probability."""
        if success_prob > 0.8:
            return "Proceed with confidence - high success rate"
        elif success_prob > 0.5:
            return "Proceed with caution - moderate success rate"
        else:
            return "Consider alternative approach - low success rate"

    def save_learning_data(self):
        """Save learning data to file."""
        try:
            data = {
                'success_patterns': self.success_patterns,
                'failure_patterns': self.failure_patterns,
                'user_preferences': self.user_preferences,
                'interaction_count': len(self.interaction_history)
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Error saving learning data: {e}")

    def load_learning_data(self):
        """Load learning data from file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                self.success_patterns = data.get('success_patterns', {})
                self.failure_patterns = data.get('failure_patterns', {})
                self.user_preferences = data.get('user_preferences', {})

                print(f"✅ Loaded learning data: {data.get('interaction_count', 0)} interactions")

        except Exception as e:
            print(f"⚠️ Error loading learning data: {e}")
            # Initialize with empty data
            self.success_patterns = {}
            self.failure_patterns = {}
            self.user_preferences = {}
