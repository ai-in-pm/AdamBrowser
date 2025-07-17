#!/usr/bin/env python3
"""
Test Script for Expedia Training System

This script tests the integration of the Expedia training modules
with the main floating agent system.
"""

import asyncio
import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Expedia Training System Imports...")
    
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
        
        # Test Expedia training modules
        from expedia_training_module import (
            ExpediaTrainingAgent, TravelSearchCriteria, TravelBookingType,
            BookingStep, ExpediaElementDetector
        )
        print("✅ Expedia training module imported successfully")
        
        from expedia_element_detector import (
            AdvancedExpediaDetector, ExpediaPageType, DetectedElement
        )
        print("✅ Advanced Expedia detector imported successfully")
        
        from travel_booking_patterns import (
            travel_patterns, TravelSite, ElementPattern
        )
        print("✅ Travel booking patterns imported successfully")
        
        # Test main agent with Expedia integration
        from embedded_chrome_floating_agent_v1 import (
            TaskOrchestrator, TaskType, TaskPriority, TaskStatus
        )
        print("✅ Enhanced main agent imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_training_data():
    """Test that training data files are accessible."""
    print("\n🧪 Testing Training Data Files...")
    
    try:
        # Test training data file
        import json
        with open('expedia_training_data.json', 'r') as f:
            data = json.load(f)
        
        print("✅ Expedia training data loaded successfully")
        print(f"  - {len(data.get('common_destinations', []))} destinations")
        print(f"  - {len(data.get('test_scenarios', []))} test scenarios")
        print(f"  - {len(data.get('booking_patterns', {}))} booking patterns")
        
        return True
        
    except FileNotFoundError:
        print("❌ Training data file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in training data: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        return False


def test_pattern_loading():
    """Test travel booking pattern loading."""
    print("\n🧪 Testing Travel Booking Patterns...")
    
    try:
        from travel_booking_patterns import travel_patterns, TravelSite
        
        # Test pattern retrieval
        expedia_patterns = travel_patterns.get_patterns_for_site(TravelSite.EXPEDIA)
        print(f"✅ Loaded {len(expedia_patterns)} Expedia patterns")
        
        # Test workflow retrieval
        flight_workflow = travel_patterns.get_workflow_for_booking_type('flight_booking')
        print(f"✅ Loaded flight workflow with {len(flight_workflow)} steps")
        
        # Test site detection
        site = travel_patterns.detect_site_from_url('https://www.expedia.com')
        print(f"✅ Site detection works: {site.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern loading failed: {e}")
        return False


async def test_browser_integration():
    """Test browser integration with training modules."""
    print("\n🧪 Testing Browser Integration...")
    
    try:
        from playwright.async_api import async_playwright
        from expedia_training_module import ExpediaTrainingAgent
        from expedia_element_detector import AdvancedExpediaDetector
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("✅ Browser launched successfully")
        
        # Test navigation to Expedia
        await page.goto('https://www.expedia.com', timeout=30000)
        print("✅ Navigation to Expedia successful")
        
        # Test training agent initialization
        class MockChatWindow:
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[MOCK] {sender}: {message}")
        
        mock_chat = MockChatWindow()
        training_agent = ExpediaTrainingAgent(page, mock_chat)
        print("✅ Training agent initialized")
        
        # Test element detector
        detector = AdvancedExpediaDetector(page)
        page_type = await detector.detect_page_type()
        print(f"✅ Page type detected: {page_type.value}")
        
        # Test element detection
        elements = await detector.detect_all_interactive_elements()
        total_elements = sum(len(element_list) for element_list in elements.values())
        print(f"✅ Detected {total_elements} interactive elements")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Browser integration test failed: {e}")
        return False


def test_training_scenarios():
    """Test training scenario creation."""
    print("\n🧪 Testing Training Scenarios...")
    
    try:
        from expedia_training_module import TravelSearchCriteria, TravelBookingType
        
        # Test flight criteria
        flight_criteria = TravelSearchCriteria(
            booking_type=TravelBookingType.FLIGHT,
            departure_location="New York, NY",
            destination_location="Los Angeles, CA"
        )
        print("✅ Flight search criteria created")
        print(f"  - Departure: {flight_criteria.departure_location}")
        print(f"  - Destination: {flight_criteria.destination_location}")
        print(f"  - Departure date: {flight_criteria.departure_date}")
        
        # Test hotel criteria
        hotel_criteria = TravelSearchCriteria(
            booking_type=TravelBookingType.HOTEL,
            destination_location="Las Vegas, NV",
            travelers=2,
            rooms=1
        )
        print("✅ Hotel search criteria created")
        print(f"  - Destination: {hotel_criteria.destination_location}")
        print(f"  - Travelers: {hotel_criteria.travelers}")
        print(f"  - Rooms: {hotel_criteria.rooms}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training scenario test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Expedia Training System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Training Data Tests", test_training_data),
        ("Pattern Loading Tests", test_pattern_loading),
        ("Training Scenario Tests", test_training_scenarios),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run async browser test separately
    print(f"\n📋 Running Browser Integration Tests...")
    try:
        browser_result = asyncio.run(test_browser_integration())
        results.append(("Browser Integration Tests", browser_result))
    except Exception as e:
        print(f"❌ Browser Integration Tests crashed: {e}")
        results.append(("Browser Integration Tests", False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Expedia training system is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
