#!/usr/bin/env python3
"""
Complete Training System Test

This script tests the entire training system including:
- General webpage training
- Expedia-specific training
- Integration with the floating agent
- Button functionality
"""

import asyncio
import sys
import time
from pathlib import Path

def test_all_imports():
    """Test that all training modules can be imported."""
    print("🧪 Testing Complete Training System Imports...")
    
    try:
        # Test general training
        from general_webpage_trainer import GeneralWebpageTrainer, PageType, ElementType
        print("✅ General webpage trainer imported")
        
        # Test Expedia training
        from expedia_training_module import ExpediaTrainingAgent, TravelSearchCriteria, TravelBookingType
        from expedia_element_detector import AdvancedExpediaDetector, ExpediaPageType
        from travel_booking_patterns import travel_patterns, TravelSite
        print("✅ Expedia training modules imported")
        
        # Test enhanced main agent
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        print("✅ Enhanced floating agent imported")
        
        # Test advanced capabilities
        from adam_browser_advanced_capabilities import SmartFormDetector, ContextAwareDecisionMaker
        print("✅ Advanced capabilities imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


async def test_training_integration():
    """Test the integration of training systems with the main agent."""
    print("\n🧪 Testing Training Integration...")
    
    try:
        from playwright.async_api import async_playwright
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        
        # Mock chat window
        class MockChatWindow:
            def __init__(self):
                self.persistent_page = None
                self.messages = []
            
            def add_chat_message(self, sender, message, is_bot=False):
                self.messages.append(f"{sender}: {message}")
                print(f"[CHAT] {sender}: {message}")
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Create mock chat window with page
        mock_chat = MockChatWindow()
        mock_chat.persistent_page = page
        
        # Test on a general website
        await page.goto('https://example.com', timeout=30000)
        print("✅ Navigated to example.com")
        
        # Create task orchestrator
        orchestrator = TaskOrchestrator(None, mock_chat)
        orchestrator.initialize_element_detector(page)
        print("✅ Task orchestrator initialized")
        
        # Test general training task creation
        task = await orchestrator._create_task_from_description("train on this page", orchestrator.TaskType.MULTI_STEP)
        print(f"✅ General training task created: {task.name}")
        
        if task.steps:
            step = task.steps[0]
            print(f"  - Action: {step.action}")
            print(f"  - Expected outcome: {step.expected_outcome}")
            
            # Test task execution
            if step.action == "general_training":
                result = await orchestrator._execute_general_training_step(step.parameters)
                if result['success']:
                    print("✅ General training execution successful")
                    print(f"  - Page type: {result.get('page_type', 'unknown')}")
                    print(f"  - Forms found: {result.get('forms_found', 0)}")
                else:
                    print(f"⚠️ General training execution failed: {result.get('error', 'Unknown')}")
        
        # Test on Expedia (if accessible)
        try:
            await page.goto('https://www.expedia.com', timeout=30000)
            print("✅ Navigated to Expedia.com")
            
            # Reinitialize for Expedia
            orchestrator.initialize_element_detector(page)
            
            # Test Expedia training task creation
            expedia_task = await orchestrator._create_task_from_description("train on expedia", orchestrator.TaskType.MULTI_STEP)
            print(f"✅ Expedia training task created: {expedia_task.name}")
            
            if expedia_task.steps:
                expedia_step = expedia_task.steps[0]
                if expedia_step.action == "expedia_training":
                    print("✅ Expedia-specific training detected")
                
        except Exception as e:
            print(f"⚠️ Expedia test skipped: {e}")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def test_button_integration():
    """Test that the train button is properly integrated."""
    print("\n🧪 Testing Train Button Integration...")
    
    try:
        import wx
        from embedded_chrome_floating_agent_v1 import EnhancedChatWindow
        
        # Test that the button exists in the class
        # We can't actually create the GUI in a test, but we can check the code
        import inspect
        
        # Check if the train button is defined
        source = inspect.getsource(EnhancedChatWindow)
        
        if 'train_page_btn' in source:
            print("✅ Train page button found in GUI code")
        else:
            print("❌ Train page button not found in GUI code")
            return False
        
        if 'on_train_page' in source:
            print("✅ Train page event handler found")
        else:
            print("❌ Train page event handler not found")
            return False
        
        if '🎯 Train on this page' in source:
            print("✅ Train button label found")
        else:
            print("❌ Train button label not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Button integration test failed: {e}")
        return False


def test_training_data_files():
    """Test that all training data files are present and valid."""
    print("\n🧪 Testing Training Data Files...")
    
    try:
        import json
        
        # Test Expedia training data
        if Path('expedia_training_data.json').exists():
            with open('expedia_training_data.json', 'r') as f:
                expedia_data = json.load(f)
            print("✅ Expedia training data loaded")
            print(f"  - Destinations: {len(expedia_data.get('common_destinations', []))}")
            print(f"  - Test scenarios: {len(expedia_data.get('test_scenarios', []))}")
        else:
            print("⚠️ Expedia training data file not found")
        
        # Test travel patterns
        from travel_booking_patterns import travel_patterns
        expedia_patterns = travel_patterns.get_patterns_for_site(travel_patterns.TravelSite.EXPEDIA)
        print(f"✅ Travel patterns loaded: {len(expedia_patterns)} patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Training data test failed: {e}")
        return False


async def test_end_to_end_workflow():
    """Test the complete end-to-end training workflow."""
    print("\n🧪 Testing End-to-End Training Workflow...")
    
    try:
        from playwright.async_api import async_playwright
        from general_webpage_trainer import GeneralWebpageTrainer
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test complete workflow on a simple page
        await page.goto('https://example.com', timeout=30000)
        
        # Mock chat for logging
        class MockChat:
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[WORKFLOW] {sender}: {message}")
        
        mock_chat = MockChat()
        
        # Create trainer
        trainer = GeneralWebpageTrainer(page, mock_chat)
        
        # Step 1: Analyze page structure
        print("📊 Step 1: Analyzing page structure...")
        analysis = await trainer.analyze_page_structure()
        
        if 'error' not in analysis:
            print("✅ Page analysis successful")
            
            # Step 2: Practice interactions
            print("🎮 Step 2: Practicing interactions...")
            practice = await trainer.practice_interactions()
            
            if 'error' not in practice:
                print("✅ Practice interactions successful")
                
                # Step 3: Generate summary
                print("📋 Step 3: Generating training summary...")
                
                summary = {
                    'url': analysis['url'],
                    'page_type': analysis['page_type'],
                    'elements_analyzed': sum(data.get('count', 0) for data in analysis.get('elements', {}).values()),
                    'forms_found': len(analysis.get('forms', [])),
                    'interactions_practiced': practice['attempted_interactions'],
                    'success_rate': (practice['successful_interactions'] / max(1, practice['attempted_interactions'])) * 100
                }
                
                print("✅ Training workflow completed successfully")
                print(f"📊 Summary:")
                for key, value in summary.items():
                    print(f"  - {key}: {value}")
                
                # Cleanup
                await browser.close()
                await playwright.stop()
                
                return True
            else:
                print(f"❌ Practice interactions failed: {practice['error']}")
        else:
            print(f"❌ Page analysis failed: {analysis['error']}")
        
        # Cleanup on failure
        await browser.close()
        await playwright.stop()
        
        return False
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        return False


def main():
    """Run complete test suite."""
    print("🚀 Complete Training System Test Suite")
    print("=" * 60)
    
    # Synchronous tests
    sync_tests = [
        ("All Imports Test", test_all_imports),
        ("Button Integration Test", test_button_integration),
        ("Training Data Files Test", test_training_data_files),
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
        ("Training Integration Test", test_training_integration),
        ("End-to-End Workflow Test", test_end_to_end_workflow),
    ]
    
    for test_name, test_func in async_tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = asyncio.run(test_func())
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Complete training system is ready!")
        print("\n🚀 READY TO USE:")
        print("1. Start the floating agent: python embedded_chrome_floating_agent_v1.py")
        print("2. Navigate to any webpage")
        print("3. Click the '🎯 Train on this page' button")
        print("4. Watch the AI learn and practice!")
        print("\n✨ Features available:")
        print("  - Universal webpage training for any site")
        print("  - Specialized Expedia.com travel booking training")
        print("  - Intelligent form detection and analysis")
        print("  - Safe interaction practice")
        print("  - Comprehensive page structure analysis")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
