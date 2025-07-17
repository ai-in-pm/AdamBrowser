#!/usr/bin/env python3
"""
Test Script for Advanced Adam Browser Agent

This script tests the enhanced capabilities of the Adam Browser agent
including complex task execution, form filling, and AI-powered automation.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import wx
        print("✅ wxPython imported successfully")
        
        # Test Playwright
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
        
        # Test advanced capabilities
        from adam_browser_advanced_capabilities import (
            SmartFormDetector, NaturalMouseMovement, ContextAwareDecisionMaker, 
            LearningSystem, InteractionPattern, FormField
        )
        print("✅ Advanced capabilities imported successfully")
        
        # Test main agent
        from embedded_chrome_floating_agent_v1 import (
            TaskOrchestrator, TaskType, TaskPriority, TaskStatus,
            EmbeddedChromeFloatingApp
        )
        print("✅ Main agent components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_task_creation():
    """Test task creation and analysis."""
    print("\n🧪 Testing task creation...")
    
    try:
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator, TaskType
        
        # Create a mock chat window
        class MockChatWindow:
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[{sender}] {message}")
        
        # Create orchestrator
        orchestrator = TaskOrchestrator(None, MockChatWindow())
        
        # Test task analysis
        test_commands = [
            "Fill out the contact form",
            "Search for Python tutorials and click the first video",
            "Navigate to Google and search for AI news",
            "Complete the signup form with test data"
        ]
        
        for command in test_commands:
            is_complex = orchestrator._is_complex_task(command)
            task_type = orchestrator._determine_task_type(command)
            print(f"✅ '{command}' -> Complex: {is_complex}, Type: {task_type.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task creation test failed: {e}")
        return False

def test_form_detection():
    """Test form detection capabilities."""
    print("\n🧪 Testing form detection...")
    
    try:
        from adam_browser_advanced_capabilities import SmartFormDetector
        
        # Create a mock page object
        class MockPage:
            def __init__(self):
                self.url = "https://example.com/contact"
            
            async def query_selector_all(self, selector):
                # Mock form elements
                if selector == 'form':
                    return [MockFormElement()]
                elif 'input' in selector:
                    return [MockInputElement('email'), MockInputElement('password')]
                return []
        
        class MockFormElement:
            async def get_attribute(self, attr):
                if attr == 'action':
                    return '/submit'
                elif attr == 'method':
                    return 'POST'
                return ''
            
            async def query_selector_all(self, selector):
                return [MockInputElement('email'), MockInputElement('password')]
        
        class MockInputElement:
            def __init__(self, field_type):
                self.field_type = field_type
            
            async def get_attribute(self, attr):
                if attr == 'type':
                    return self.field_type
                elif attr == 'name':
                    return self.field_type
                elif attr == 'placeholder':
                    return f"Enter your {self.field_type}"
                return ''
            
            async def evaluate(self, script):
                return ''
        
        # Test form detection
        detector = SmartFormDetector(MockPage())
        
        # Test field classification
        purpose = detector._classify_field_purpose('email', 'enter email', 'Email Address', 'email')
        print(f"✅ Field classification: {purpose}")
        
        suggested_value = detector._get_suggested_value('email', 'email')
        print(f"✅ Suggested value: {suggested_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Form detection test failed: {e}")
        return False

def test_mouse_movement():
    """Test natural mouse movement calculations."""
    print("\n🧪 Testing mouse movement...")
    
    try:
        from adam_browser_advanced_capabilities import NaturalMouseMovement, InteractionPattern
        
        mouse = NaturalMouseMovement()
        
        # Test path calculation
        start = (100, 100)
        end = (500, 300)
        path = mouse.calculate_bezier_path(start, end, 10)
        
        print(f"✅ Generated path with {len(path)} points")
        print(f"   Start: {path[0]}, End: {path[-1]}")
        
        # Test timing calculation
        distance = 400  # pixels
        timing = mouse.calculate_movement_timing(distance)
        print(f"✅ Movement timing: {timing:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Mouse movement test failed: {e}")
        return False

def test_decision_making():
    """Test context-aware decision making."""
    print("\n🧪 Testing decision making...")
    
    try:
        from adam_browser_advanced_capabilities import ContextAwareDecisionMaker
        
        decision_maker = ContextAwareDecisionMaker()
        
        # Test page classification
        test_contexts = [
            {'url': 'https://amazon.com/product', 'title': 'Buy iPhone'},
            {'url': 'https://google.com', 'title': 'Google Search'},
            {'url': 'https://facebook.com', 'title': 'Facebook'},
            {'url': 'https://example.com/login', 'title': 'Login Page', 'forms': [{'purpose': 'login'}]}
        ]
        
        for context in test_contexts:
            page_type = decision_maker._classify_page_type(context)
            print(f"✅ Page classification: {context['url']} -> {page_type}")
        
        # Test action suggestions
        suggestions = decision_maker.suggest_next_actions(
            {'page_type': 'ecommerce', 'forms': []}, 
            'buy a product'
        )
        print(f"✅ Generated {len(suggestions)} action suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Decision making test failed: {e}")
        return False

def test_learning_system():
    """Test learning system functionality."""
    print("\n🧪 Testing learning system...")
    
    try:
        from adam_browser_advanced_capabilities import LearningSystem
        
        # Use a temporary file for testing
        learning = LearningSystem("test_learning.json")
        
        # Test recording interactions
        context = {'page_type': 'ecommerce', 'url': 'https://example.com'}
        learning.record_interaction('click', context, True, 2.5)
        learning.record_interaction('form_filling', context, True, 5.0)
        learning.record_interaction('click', context, False, 1.0)
        
        # Test success probability calculation
        success_prob = learning.get_success_probability('click', context)
        print(f"✅ Success probability for 'click': {success_prob:.2f}")
        
        # Test strategy suggestion
        strategy = learning.suggest_best_strategy('form_filling', context)
        print(f"✅ Strategy suggestion: {strategy}")
        
        # Clean up test file
        test_file = Path("test_learning.json")
        if test_file.exists():
            test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Learning system test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Advanced Adam Browser Agent Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_task_creation,
        test_form_detection,
        test_mouse_movement,
        test_decision_making,
        test_learning_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The advanced agent is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
