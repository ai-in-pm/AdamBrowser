#!/usr/bin/env python3
"""
General Webpage Training Module

This module provides comprehensive training capabilities for any webpage,
not limited to specific sites like Expedia. It analyzes page structure,
identifies interactive elements, and learns interaction patterns.

Features:
- Universal element detection and analysis
- Form structure learning
- Interactive element mapping
- Content pattern recognition
- Navigation flow understanding
- Accessibility feature detection
"""

import asyncio
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
from urllib.parse import urlparse


class PageType(Enum):
    """General page types for any website."""
    HOMEPAGE = "homepage"
    SEARCH_RESULTS = "search_results"
    PRODUCT_DETAIL = "product_detail"
    FORM_PAGE = "form_page"
    ARTICLE = "article"
    NAVIGATION = "navigation"
    LOGIN = "login"
    CHECKOUT = "checkout"
    PROFILE = "profile"
    SETTINGS = "settings"
    UNKNOWN = "unknown"


class ElementType(Enum):
    """Types of interactive elements."""
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FORM = "form"
    IMAGE = "image"
    VIDEO = "video"
    NAVIGATION = "navigation"


@dataclass
class InteractiveElement:
    """Represents an interactive element with comprehensive metadata."""
    element: Any
    element_type: ElementType
    tag_name: str
    text_content: str
    attributes: Dict[str, str]
    position: Dict[str, float]
    confidence: float
    accessibility_score: float
    interaction_methods: List[str]
    context: str
    parent_context: str


class GeneralWebpageTrainer:
    """Universal webpage training system for any website."""
    
    def __init__(self, page, chat_window=None):
        self.page = page
        self.chat_window = chat_window
        self.training_data = {}
        self.discovered_patterns = {}
        self.interaction_history = []
        
        # Universal selectors for common elements
        self.universal_selectors = {
            'forms': [
                'form',
                '[role="form"]',
                '.form',
                '.contact-form',
                '.search-form',
                '.login-form',
                '.signup-form'
            ],
            'buttons': [
                'button',
                'input[type="button"]',
                'input[type="submit"]',
                '[role="button"]',
                '.btn',
                '.button',
                'a.button'
            ],
            'inputs': [
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'input[type="search"]',
                'input[type="tel"]',
                'input[type="url"]',
                'textarea',
                'select'
            ],
            'navigation': [
                'nav',
                '[role="navigation"]',
                '.nav',
                '.navigation',
                '.menu',
                '.navbar',
                'header nav',
                'footer nav'
            ],
            'content_areas': [
                'main',
                '[role="main"]',
                '.main',
                '.content',
                '.main-content',
                'article',
                '.article'
            ]
        }
        
        print("🎯 General Webpage Trainer initialized")
    
    async def analyze_page_structure(self, url_context: str = None, training_type: str = None) -> Dict[str, Any]:
        """Analyze the overall structure and content of the current page with enhanced context."""
        try:
            # Check if page is still valid
            if not self.page:
                return {'error': 'Page context not available'}

            # Safely get page information
            try:
                current_url = self.page.url
                if not current_url or current_url == 'about:blank':
                    return {'error': 'No webpage loaded - please navigate to a page first'}

                page_title = await self.page.title()
                detected_page_type = await self._detect_page_type()
            except Exception as e:
                return {'error': f'Page context unavailable: {str(e)}'}

            analysis = {
                'url': current_url,
                'url_context': url_context or current_url,
                'title': page_title,
                'page_type': detected_page_type,
                'training_type': training_type or self._classify_site_type(current_url),
                'domain_info': self._analyze_domain(current_url),
                'elements': {},
                'forms': [],
                'navigation': [],
                'content_structure': {},
                'accessibility_features': {},
                'performance_metrics': {},
                'url_analysis': self._analyze_url_structure(current_url),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.chat_window:
                domain_name = analysis['domain_info']['domain']
                site_type = analysis['training_type']
                self.chat_window.add_chat_message("Adam",
                    f"🔍 Analyzing page structure for: {analysis['title']}\n"
                    f"🌐 Domain: {domain_name}\n"
                    f"🏷️ Site type: {site_type}\n"
                    f"📄 Page type: {detected_page_type.value}", is_bot=True)
            
            # Analyze different element types
            for element_category, selectors in self.universal_selectors.items():
                analysis['elements'][element_category] = await self._analyze_element_category(
                    element_category, selectors
                )
            
            # Detailed form analysis
            analysis['forms'] = await self._analyze_forms()
            
            # Navigation structure
            analysis['navigation'] = await self._analyze_navigation()
            
            # Content structure
            analysis['content_structure'] = await self._analyze_content_structure()
            
            # Accessibility features
            analysis['accessibility_features'] = await self._analyze_accessibility()
            
            # Performance metrics
            analysis['performance_metrics'] = await self._gather_performance_metrics()
            
            # Save analysis
            self._save_page_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing page structure: {e}")
            return {'error': str(e)}
    
    async def _detect_page_type(self) -> PageType:
        """Detect the type of page based on content and structure."""
        try:
            url = self.page.url.lower()
            title = await self.page.title()
            title_lower = title.lower()
            
            # URL-based detection
            if any(keyword in url for keyword in ['search', 'results']):
                return PageType.SEARCH_RESULTS
            elif any(keyword in url for keyword in ['product', 'item', 'detail']):
                return PageType.PRODUCT_DETAIL
            elif any(keyword in url for keyword in ['login', 'signin', 'auth']):
                return PageType.LOGIN
            elif any(keyword in url for keyword in ['checkout', 'cart', 'payment']):
                return PageType.CHECKOUT
            elif any(keyword in url for keyword in ['profile', 'account', 'user']):
                return PageType.PROFILE
            elif any(keyword in url for keyword in ['settings', 'preferences', 'config']):
                return PageType.SETTINGS
            
            # Content-based detection
            page_content = await self.page.content()
            content_lower = page_content.lower()
            
            # Check for forms
            forms = await self.page.query_selector_all('form')
            if len(forms) > 0:
                form_purposes = []
                for form in forms:
                    action = await form.get_attribute('action') or ''
                    if 'search' in action.lower():
                        return PageType.SEARCH_RESULTS
                    elif any(keyword in action.lower() for keyword in ['login', 'auth']):
                        return PageType.LOGIN
                    elif any(keyword in action.lower() for keyword in ['contact', 'form']):
                        return PageType.FORM_PAGE
            
            # Check for article content
            articles = await self.page.query_selector_all('article, .article, .post')
            if len(articles) > 0:
                return PageType.ARTICLE
            
            # Check if it's likely a homepage
            if url.count('/') <= 3 and not any(char in url for char in ['?', '&', '=']):
                return PageType.HOMEPAGE
            
            return PageType.UNKNOWN
            
        except Exception as e:
            print(f"⚠️ Error detecting page type: {e}")
            return PageType.UNKNOWN
    
    async def _analyze_element_category(self, category: str, selectors: List[str]) -> Dict[str, Any]:
        """Analyze a category of elements."""
        try:
            elements_found = []
            total_elements = 0
            
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    total_elements += len(elements)
                    
                    for element in elements[:5]:  # Analyze first 5 of each type
                        element_data = await self._analyze_single_element(element, category)
                        if element_data:
                            elements_found.append(element_data)
                            
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue
            
            return {
                'count': total_elements,
                'analyzed_samples': len(elements_found),
                'elements': elements_found,
                'patterns': self._extract_patterns(elements_found)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {category}: {e}")
            return {'count': 0, 'analyzed_samples': 0, 'elements': [], 'patterns': {}}
    
    async def _analyze_single_element(self, element, category: str) -> Optional[Dict[str, Any]]:
        """Analyze a single element in detail."""
        try:
            # Get basic properties
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text_content = await element.evaluate('el => el.textContent?.trim() || ""')
            
            # Get attributes
            attributes = {}
            for attr in ['id', 'class', 'name', 'type', 'placeholder', 'aria-label', 
                        'title', 'role', 'href', 'action', 'method']:
                value = await element.get_attribute(attr)
                if value:
                    attributes[attr] = value
            
            # Get position and visibility
            bounding_box = await element.bounding_box()
            is_visible = await element.is_visible()
            
            # Calculate accessibility score
            accessibility_score = self._calculate_accessibility_score(attributes, text_content)
            
            # Determine interaction methods
            interaction_methods = await self._determine_interaction_methods(element, tag_name, attributes)
            
            # Get context
            context = await self._get_element_context(element)
            
            return {
                'tag_name': tag_name,
                'text_content': text_content[:100],  # Limit text length
                'attributes': attributes,
                'position': bounding_box if bounding_box else {},
                'is_visible': is_visible,
                'accessibility_score': accessibility_score,
                'interaction_methods': interaction_methods,
                'context': context,
                'category': category
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing element: {e}")
            return None
    
    def _calculate_accessibility_score(self, attributes: Dict[str, str], text_content: str) -> float:
        """Calculate accessibility score for an element."""
        score = 0.0
        
        # Check for accessibility attributes
        if 'aria-label' in attributes:
            score += 0.3
        if 'title' in attributes:
            score += 0.2
        if 'role' in attributes:
            score += 0.2
        if 'id' in attributes:
            score += 0.1
        
        # Check for meaningful text
        if text_content and len(text_content.strip()) > 0:
            score += 0.2
        
        return min(1.0, score)
    
    async def _determine_interaction_methods(self, element, tag_name: str, attributes: Dict[str, str]) -> List[str]:
        """Determine possible interaction methods for an element."""
        methods = []
        
        # Basic interactions based on tag
        if tag_name in ['button', 'a']:
            methods.append('click')
        elif tag_name == 'input':
            input_type = attributes.get('type', 'text')
            if input_type in ['text', 'email', 'password', 'search']:
                methods.extend(['click', 'type', 'clear'])
            elif input_type in ['submit', 'button']:
                methods.append('click')
            elif input_type in ['checkbox', 'radio']:
                methods.extend(['click', 'check', 'uncheck'])
        elif tag_name == 'select':
            methods.extend(['click', 'select_option'])
        elif tag_name == 'textarea':
            methods.extend(['click', 'type', 'clear'])
        
        # Check for hover interactions
        try:
            has_hover = await element.evaluate('''
                el => {
                    const style = window.getComputedStyle(el);
                    return style.cursor === 'pointer' || 
                           el.onmouseover !== null ||
                           el.getAttribute('onmouseover') !== null;
                }
            ''')
            if has_hover:
                methods.append('hover')
        except:
            pass
        
        return methods
    
    async def _get_element_context(self, element) -> str:
        """Get contextual information about an element."""
        try:
            # Get parent context
            parent_info = await element.evaluate('''
                el => {
                    const parent = el.parentElement;
                    if (parent) {
                        return {
                            tagName: parent.tagName.toLowerCase(),
                            className: parent.className || '',
                            id: parent.id || ''
                        };
                    }
                    return null;
                }
            ''')
            
            # Get sibling context
            sibling_info = await element.evaluate('''
                el => {
                    const siblings = Array.from(el.parentElement?.children || []);
                    return {
                        position: siblings.indexOf(el),
                        total: siblings.length
                    };
                }
            ''')
            
            context_parts = []
            if parent_info:
                context_parts.append(f"parent: {parent_info['tagName']}")
                if parent_info['className']:
                    context_parts.append(f"parent_class: {parent_info['className'][:50]}")
            
            if sibling_info:
                context_parts.append(f"position: {sibling_info['position']}/{sibling_info['total']}")
            
            return ", ".join(context_parts)
            
        except Exception as e:
            return f"context_error: {str(e)[:50]}"
    
    def _extract_patterns(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common patterns from analyzed elements."""
        if not elements:
            return {}
        
        patterns = {
            'common_classes': {},
            'common_attributes': {},
            'text_patterns': [],
            'interaction_patterns': {}
        }
        
        # Analyze common classes
        for element in elements:
            class_attr = element['attributes'].get('class', '')
            if class_attr:
                classes = class_attr.split()
                for cls in classes:
                    patterns['common_classes'][cls] = patterns['common_classes'].get(cls, 0) + 1
        
        # Analyze common attributes
        for element in elements:
            for attr, value in element['attributes'].items():
                if attr not in patterns['common_attributes']:
                    patterns['common_attributes'][attr] = {}
                patterns['common_attributes'][attr][value] = patterns['common_attributes'][attr].get(value, 0) + 1
        
        # Analyze interaction patterns
        for element in elements:
            for method in element['interaction_methods']:
                patterns['interaction_patterns'][method] = patterns['interaction_patterns'].get(method, 0) + 1
        
        return patterns
    
    async def _analyze_forms(self) -> List[Dict[str, Any]]:
        """Analyze all forms on the page."""
        try:
            forms = await self.page.query_selector_all('form')
            form_analysis = []
            
            for i, form in enumerate(forms):
                form_data = {
                    'index': i,
                    'action': await form.get_attribute('action') or '',
                    'method': await form.get_attribute('method') or 'GET',
                    'fields': [],
                    'buttons': [],
                    'purpose': 'unknown'
                }
                
                # Analyze form fields
                fields = await form.query_selector_all('input, select, textarea')
                for field in fields:
                    field_data = await self._analyze_single_element(field, 'form_field')
                    if field_data:
                        form_data['fields'].append(field_data)
                
                # Analyze form buttons
                buttons = await form.query_selector_all('button, input[type="submit"], input[type="button"]')
                for button in buttons:
                    button_data = await self._analyze_single_element(button, 'form_button')
                    if button_data:
                        form_data['buttons'].append(button_data)
                
                # Determine form purpose
                form_data['purpose'] = self._determine_form_purpose(form_data)
                
                form_analysis.append(form_data)
            
            return form_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing forms: {e}")
            return []
    
    def _determine_form_purpose(self, form_data: Dict[str, Any]) -> str:
        """Determine the purpose of a form based on its fields and attributes."""
        action = form_data['action'].lower()
        fields = form_data['fields']
        
        # Check action URL
        if 'search' in action:
            return 'search'
        elif any(keyword in action for keyword in ['login', 'signin', 'auth']):
            return 'login'
        elif any(keyword in action for keyword in ['contact', 'feedback', 'support']):
            return 'contact'
        elif any(keyword in action for keyword in ['register', 'signup', 'join']):
            return 'registration'
        
        # Check field types
        field_types = [field['attributes'].get('type', '') for field in fields]
        field_names = [field['attributes'].get('name', '').lower() for field in fields]
        
        if 'password' in field_types and 'email' in field_types:
            if len(fields) <= 3:
                return 'login'
            else:
                return 'registration'
        elif any('search' in name for name in field_names):
            return 'search'
        elif any(name in ['email', 'message', 'subject'] for name in field_names):
            return 'contact'
        
        return 'general'
    
    async def _analyze_navigation(self) -> List[Dict[str, Any]]:
        """Analyze navigation elements."""
        try:
            nav_elements = []
            
            for selector in self.universal_selectors['navigation']:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        nav_data = await self._analyze_single_element(element, 'navigation')
                        if nav_data:
                            # Get navigation links
                            links = await element.query_selector_all('a')
                            nav_data['links'] = []
                            
                            for link in links[:10]:  # Limit to first 10 links
                                href = await link.get_attribute('href')
                                text = await link.evaluate('el => el.textContent?.trim() || ""')
                                if href and text:
                                    nav_data['links'].append({
                                        'href': href,
                                        'text': text[:50]
                                    })
                            
                            nav_elements.append(nav_data)
                            
                except Exception as e:
                    print(f"⚠️ Error analyzing navigation with {selector}: {e}")
                    continue
            
            return nav_elements
            
        except Exception as e:
            print(f"❌ Error analyzing navigation: {e}")
            return []
    
    async def _analyze_content_structure(self) -> Dict[str, Any]:
        """Analyze the content structure of the page."""
        try:
            structure = {
                'headings': {},
                'paragraphs': 0,
                'images': 0,
                'videos': 0,
                'lists': 0,
                'tables': 0
            }
            
            # Analyze headings
            for level in range(1, 7):
                headings = await self.page.query_selector_all(f'h{level}')
                structure['headings'][f'h{level}'] = len(headings)
            
            # Count other content elements
            structure['paragraphs'] = len(await self.page.query_selector_all('p'))
            structure['images'] = len(await self.page.query_selector_all('img'))
            structure['videos'] = len(await self.page.query_selector_all('video'))
            structure['lists'] = len(await self.page.query_selector_all('ul, ol'))
            structure['tables'] = len(await self.page.query_selector_all('table'))
            
            return structure
            
        except Exception as e:
            print(f"❌ Error analyzing content structure: {e}")
            return {}
    
    async def _analyze_accessibility(self) -> Dict[str, Any]:
        """Analyze accessibility features of the page."""
        try:
            accessibility = {
                'aria_labels': 0,
                'alt_texts': 0,
                'skip_links': 0,
                'landmarks': 0,
                'focus_indicators': 0
            }
            
            # Count accessibility features
            accessibility['aria_labels'] = len(await self.page.query_selector_all('[aria-label]'))
            accessibility['alt_texts'] = len(await self.page.query_selector_all('img[alt]'))
            accessibility['skip_links'] = len(await self.page.query_selector_all('a[href^="#"]'))
            accessibility['landmarks'] = len(await self.page.query_selector_all('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"]'))
            
            return accessibility
            
        except Exception as e:
            print(f"❌ Error analyzing accessibility: {e}")
            return {}
    
    async def _gather_performance_metrics(self) -> Dict[str, Any]:
        """Gather basic performance metrics."""
        try:
            metrics = await self.page.evaluate('''
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        load_time: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
                        dom_content_loaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
                        page_size: document.documentElement.outerHTML.length,
                        element_count: document.querySelectorAll('*').length
                    };
                }
            ''')
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error gathering performance metrics: {e}")
            return {}
    
    def _save_page_analysis(self, analysis: Dict[str, Any]):
        """Save page analysis to file."""
        try:
            # Create filename based on URL
            url_parts = urlparse(analysis['url'])
            domain = url_parts.netloc.replace('.', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_analysis_{domain}_{timestamp}.json"
            
            # Remove non-serializable elements
            serializable_analysis = self._make_serializable(analysis)
            
            with open(filename, 'w') as f:
                json.dump(serializable_analysis, f, indent=2)
            
            print(f"📊 Page analysis saved to {filename}")
            
        except Exception as e:
            print(f"⚠️ Could not save analysis: {e}")
    
    def _make_serializable(self, data: Any) -> Any:
        """Make data serializable by removing non-JSON compatible elements."""
        if isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items() if k != 'element'}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif hasattr(data, '__dict__'):
            return str(data)
        else:
            return data
    
    async def practice_interactions(self) -> Dict[str, Any]:
        """Practice interactions with discovered elements."""
        try:
            if self.chat_window:
                self.chat_window.add_chat_message("Adam", 
                    "🎮 Starting practice interactions...", is_bot=True)
            
            practice_results = {
                'attempted_interactions': 0,
                'successful_interactions': 0,
                'failed_interactions': 0,
                'interaction_log': []
            }
            
            # Get safe elements to practice with (avoid forms and destructive actions)
            safe_selectors = [
                'button:not([type="submit"])',
                'a[href^="#"]',  # Internal links
                '.tab',
                '.accordion',
                '.dropdown'
            ]
            
            for selector in safe_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements[:2]:  # Practice with first 2 of each type
                        if await element.is_visible():
                            interaction_result = await self._practice_single_interaction(element)
                            practice_results['interaction_log'].append(interaction_result)
                            practice_results['attempted_interactions'] += 1
                            
                            if interaction_result['success']:
                                practice_results['successful_interactions'] += 1
                            else:
                                practice_results['failed_interactions'] += 1
                            
                            # Small delay between interactions
                            await asyncio.sleep(0.5)
                            
                except Exception as e:
                    print(f"⚠️ Error practicing with {selector}: {e}")
                    continue
            
            success_rate = (practice_results['successful_interactions'] / 
                          max(1, practice_results['attempted_interactions'])) * 100
            
            if self.chat_window:
                self.chat_window.add_chat_message("Adam", 
                    f"🎯 Practice complete! Success rate: {success_rate:.1f}% "
                    f"({practice_results['successful_interactions']}/{practice_results['attempted_interactions']})", 
                    is_bot=True)
            
            return practice_results
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _practice_single_interaction(self, element) -> Dict[str, Any]:
        """Practice a single interaction with an element."""
        try:
            # Get element info
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text_content = await element.evaluate('el => el.textContent?.trim() || ""')
            
            # Try safe interactions
            if tag_name in ['button', 'a']:
                # Try hover first
                await element.hover()
                await asyncio.sleep(0.2)
                
                # For internal links or safe buttons, try clicking
                href = await element.get_attribute('href')
                if href and href.startswith('#'):
                    await element.click()
                    await asyncio.sleep(0.3)
                
                return {
                    'element_type': tag_name,
                    'text': text_content[:50],
                    'interaction': 'hover_and_click',
                    'success': True
                }
            else:
                # Just hover for other elements
                await element.hover()
                await asyncio.sleep(0.2)
                
                return {
                    'element_type': tag_name,
                    'text': text_content[:50],
                    'interaction': 'hover',
                    'success': True
                }
                
        except Exception as e:
            return {
                'element_type': 'unknown',
                'text': '',
                'interaction': 'failed',
                'success': False,
                'error': str(e)
            }

    def _classify_site_type(self, url: str) -> str:
        """Classify the type of website based on URL."""
        url_lower = url.lower()

        # E-commerce
        if any(keyword in url_lower for keyword in ['shop', 'store', 'buy', 'cart', 'amazon', 'ebay']):
            return "E-commerce"

        # Social media
        elif any(keyword in url_lower for keyword in ['facebook', 'twitter', 'instagram', 'linkedin', 'social']):
            return "Social Media"

        # News/Media
        elif any(keyword in url_lower for keyword in ['news', 'blog', 'article', 'media', 'press']):
            return "News/Media"

        # Travel
        elif any(keyword in url_lower for keyword in ['travel', 'hotel', 'flight', 'booking', 'expedia']):
            return "Travel"

        # Tech/Developer
        elif any(keyword in url_lower for keyword in ['github', 'stackoverflow', 'developer', 'api', 'docs']):
            return "Tech/Developer"

        # Education
        elif any(keyword in url_lower for keyword in ['edu', 'university', 'school', 'course', 'learn']):
            return "Education"

        # Government
        elif any(keyword in url_lower for keyword in ['.gov', 'government', 'official']):
            return "Government"

        # Business/Corporate
        elif any(keyword in url_lower for keyword in ['company', 'corp', 'business', 'about', 'contact']):
            return "Business/Corporate"

        return "General Website"

    def _analyze_domain(self, url: str) -> Dict[str, str]:
        """Analyze domain information from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)

            domain = parsed.netloc.lower()
            subdomain = ""
            main_domain = domain

            # Extract subdomain if present
            parts = domain.split('.')
            if len(parts) > 2:
                subdomain = parts[0]
                main_domain = '.'.join(parts[1:])

            # Determine domain type
            domain_type = "Commercial"
            if domain.endswith('.edu'):
                domain_type = "Educational"
            elif domain.endswith('.gov'):
                domain_type = "Government"
            elif domain.endswith('.org'):
                domain_type = "Organization"
            elif domain.endswith('.mil'):
                domain_type = "Military"

            return {
                'domain': domain,
                'main_domain': main_domain,
                'subdomain': subdomain,
                'domain_type': domain_type,
                'tld': parts[-1] if parts else ""
            }

        except Exception as e:
            return {
                'domain': url,
                'main_domain': url,
                'subdomain': "",
                'domain_type': "Unknown",
                'tld': "",
                'error': str(e)
            }

    def _analyze_url_structure(self, url: str) -> Dict[str, Any]:
        """Analyze URL structure for insights."""
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)

            # Analyze path
            path_segments = [seg for seg in parsed.path.split('/') if seg]

            # Analyze query parameters
            query_params = parse_qs(parsed.query)

            # Determine URL patterns
            url_patterns = []
            if 'search' in url.lower():
                url_patterns.append('search')
            if any(param in query_params for param in ['q', 'query', 'search']):
                url_patterns.append('search_query')
            if 'login' in url.lower() or 'signin' in url.lower():
                url_patterns.append('authentication')
            if any(seg.isdigit() for seg in path_segments):
                url_patterns.append('id_based')
            if len(path_segments) > 3:
                url_patterns.append('deep_path')

            return {
                'scheme': parsed.scheme,
                'path': parsed.path,
                'path_segments': path_segments,
                'path_depth': len(path_segments),
                'query_params': list(query_params.keys()),
                'query_param_count': len(query_params),
                'fragment': parsed.fragment,
                'url_patterns': url_patterns,
                'is_secure': parsed.scheme == 'https'
            }

        except Exception as e:
            return {
                'error': str(e),
                'scheme': 'unknown',
                'path': '',
                'path_segments': [],
                'path_depth': 0,
                'query_params': [],
                'query_param_count': 0,
                'fragment': '',
                'url_patterns': [],
                'is_secure': False
            }
