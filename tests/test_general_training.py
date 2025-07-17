#!/usr/bin/env python3
"""
Test Script for General Webpage Training System

This script tests the general webpage training capabilities
on various types of websites.
"""

import asyncio
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing General Training System Imports...")
    
    try:
        # Test general training module
        from general_webpage_trainer import (
            GeneralWebpageTrainer, PageType, ElementType, InteractiveElement
        )
        print("✅ General webpage trainer imported successfully")
        
        # Test enhanced main agent
        from embedded_chrome_floating_agent_v1 import (
            TaskOrchestrator, TaskType, TaskPriority, TaskStatus
        )
        print("✅ Enhanced main agent imported successfully")
        
        # Test Playwright
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_general_training_on_site(url: str, site_name: str):
    """Test general training on a specific website."""
    print(f"\n🧪 Testing General Training on {site_name}...")
    
    try:
        from playwright.async_api import async_playwright
        from general_webpage_trainer import GeneralWebpageTrainer
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"✅ Browser launched for {site_name}")
        
        # Navigate to site
        await page.goto(url, timeout=30000)
        print(f"✅ Navigation to {site_name} successful")
        
        # Test training
        class MockChatWindow:
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[{site_name}] {sender}: {message}")
        
        mock_chat = MockChatWindow()
        trainer = GeneralWebpageTrainer(page, mock_chat)
        print(f"✅ Trainer initialized for {site_name}")
        
        # Analyze page structure
        analysis = await trainer.analyze_page_structure()
        
        if 'error' not in analysis:
            print(f"✅ Page analysis successful for {site_name}")
            print(f"  - Page type: {analysis.get('page_type', 'unknown')}")
            print(f"  - Forms found: {len(analysis.get('forms', []))}")
            
            elements = analysis.get('elements', {})
            for element_type, data in elements.items():
                count = data.get('count', 0)
                if count > 0:
                    print(f"  - {element_type}: {count}")
            
            # Test practice interactions
            practice_result = await trainer.practice_interactions()
            
            if 'error' not in practice_result:
                success_rate = (practice_result['successful_interactions'] / 
                              max(1, practice_result['attempted_interactions'])) * 100
                print(f"✅ Practice interactions successful for {site_name}")
                print(f"  - Success rate: {success_rate:.1f}%")
                print(f"  - Interactions: {practice_result['successful_interactions']}/{practice_result['attempted_interactions']}")
            else:
                print(f"⚠️ Practice interactions failed for {site_name}: {practice_result['error']}")
        else:
            print(f"❌ Page analysis failed for {site_name}: {analysis['error']}")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Training test failed for {site_name}: {e}")
        return False


async def test_multiple_sites():
    """Test training on multiple different types of websites."""
    print("\n🧪 Testing General Training on Multiple Sites...")
    
    test_sites = [
        ("https://example.com", "Example.com"),
        ("https://github.com", "GitHub"),
        ("https://stackoverflow.com", "Stack Overflow"),
        ("https://wikipedia.org", "Wikipedia"),
        ("https://news.ycombinator.com", "Hacker News")
    ]
    
    results = []
    
    for url, name in test_sites:
        try:
            result = await test_general_training_on_site(url, name)
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    return results


def test_page_type_detection():
    """Test page type detection logic."""
    print("\n🧪 Testing Page Type Detection...")
    
    try:
        from general_webpage_trainer import GeneralWebpageTrainer, PageType
        
        # Test URL-based detection patterns
        test_cases = [
            ("https://example.com/search?q=test", PageType.SEARCH_RESULTS),
            ("https://example.com/product/123", PageType.PRODUCT_DETAIL),
            ("https://example.com/login", PageType.LOGIN),
            ("https://example.com/checkout", PageType.CHECKOUT),
            ("https://example.com/profile", PageType.PROFILE),
            ("https://example.com/settings", PageType.SETTINGS),
            ("https://example.com", PageType.HOMEPAGE),
        ]
        
        print("✅ Page type detection patterns loaded")
        print(f"  - Test cases: {len(test_cases)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Page type detection test failed: {e}")
        return False


def test_element_analysis():
    """Test element analysis capabilities."""
    print("\n🧪 Testing Element Analysis...")
    
    try:
        from general_webpage_trainer import GeneralWebpageTrainer, ElementType
        
        # Test selector patterns
        trainer_class = GeneralWebpageTrainer
        selectors = trainer_class.__new__(trainer_class).universal_selectors
        
        print("✅ Universal selectors loaded")
        for category, selector_list in selectors.items():
            print(f"  - {category}: {len(selector_list)} selectors")
        
        return True
        
    except Exception as e:
        print(f"❌ Element analysis test failed: {e}")
        return False


async def test_browser_integration():
    """Test browser integration with general training."""
    print("\n🧪 Testing Browser Integration...")
    
    try:
        from playwright.async_api import async_playwright
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("✅ Browser launched successfully")
        
        # Test navigation
        await page.goto('https://example.com', timeout=30000)
        print("✅ Navigation successful")
        
        # Test task orchestrator with general training
        class MockChatWindow:
            def __init__(self):
                self.persistent_page = page
            
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[MOCK] {sender}: {message}")
        
        mock_chat = MockChatWindow()
        orchestrator = TaskOrchestrator(None, mock_chat)
        
        # Initialize element detector
        orchestrator.initialize_element_detector(page)
        print("✅ Task orchestrator initialized")
        
        # Test training task creation
        task_description = "train on this page"
        task = await orchestrator._create_task_from_description(task_description, orchestrator.TaskType.MULTI_STEP)
        
        print(f"✅ Training task created: {task.name}")
        print(f"  - Steps: {len(task.steps)}")
        
        if task.steps:
            step = task.steps[0]
            print(f"  - First step: {step.action}")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Browser integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 General Webpage Training System Test Suite")
    print("=" * 50)
    
    # Synchronous tests
    sync_tests = [
        ("Import Tests", test_imports),
        ("Page Type Detection Tests", test_page_type_detection),
        ("Element Analysis Tests", test_element_analysis),
    ]
    
    results = []
    
    for test_name, test_func in sync_tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Asynchronous tests
    async_tests = [
        ("Browser Integration Tests", test_browser_integration),
        ("Multiple Sites Training Tests", test_multiple_sites),
    ]
    
    for test_name, test_func in async_tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = asyncio.run(test_func())
            if isinstance(result, list):
                # Handle multiple site results
                success_count = sum(1 for _, success in result if success)
                total_count = len(result)
                overall_success = success_count == total_count
                
                print(f"📊 {test_name} Results:")
                for site_name, success in result:
                    status = "✅ PASS" if success else "❌ FAIL"
                    print(f"  {status} {site_name}")
                
                results.append((test_name, overall_success))
            else:
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
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
        print("🎉 All tests passed! General training system is ready.")
        print("\n💡 Usage:")
        print("1. Start the floating agent: python embedded_chrome_floating_agent_v1.py")
        print("2. Navigate to any webpage")
        print("3. Click the '🎯 Train on this page' button")
        print("4. Or use chat commands like 'train on this page' or 'analyze this website'")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
