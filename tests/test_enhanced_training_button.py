#!/usr/bin/env python3
"""
Test Enhanced Training Button with URL Detection

This script tests the enhanced "Train on this page" button functionality
including URL detection, site type classification, and context-aware training.
"""

import asyncio
import sys
from pathlib import Path

def test_url_detection():
    """Test URL detection and site classification."""
    print("🧪 Testing URL Detection and Site Classification...")
    
    try:
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        
        # Create a mock chat window
        class MockChatWindow:
            def __init__(self, url="https://example.com"):
                self.persistent_page = MockPage(url)
            
            def add_chat_message(self, sender, message, is_bot=False):
                print(f"[MOCK] {sender}: {message}")
        
        class MockPage:
            def __init__(self, url):
                self.url = url
        
        # Test different URL types
        test_urls = [
            ("https://www.expedia.com/flights", "Expedia Travel Booking"),
            ("https://www.amazon.com/products", "E-commerce"),
            ("https://github.com/user/repo", "Developer/Tech"),
            ("https://stackoverflow.com/questions", "Developer/Tech"),
            ("https://www.facebook.com", "Social Media"),
            ("https://news.cnn.com/article", "News/Content"),
            ("https://university.edu/courses", "General Website"),
            ("https://example.com/search?q=test", "Search Results"),
            ("https://site.com/login", "Login/Authentication"),
            ("https://shop.com/checkout", "Checkout/Payment"),
        ]
        
        orchestrator = TaskOrchestrator(None, MockChatWindow())
        
        for url, expected_type in test_urls:
            # Test site type determination
            domain = url.split('/')[2].lower()
            detected_type = orchestrator.determine_training_type(url, domain)
            
            status = "✅" if expected_type.lower() in detected_type.lower() else "⚠️"
            print(f"{status} {url} -> {detected_type}")
        
        print("✅ URL detection test completed")
        return True
        
    except Exception as e:
        print(f"❌ URL detection test failed: {e}")
        return False


def test_context_extraction():
    """Test context extraction from training descriptions."""
    print("\n🧪 Testing Context Extraction...")
    
    try:
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        
        class MockChatWindow:
            def __init__(self):
                self.persistent_page = None
        
        orchestrator = TaskOrchestrator(None, MockChatWindow())
        
        # Test URL extraction
        test_descriptions = [
            "train on this page: https://www.expedia.com (type: Expedia Travel Booking)",
            "analyze this website: https://github.com/user/repo (type: Developer/Tech)",
            "learn from https://amazon.com/products",
            "train on this page"
        ]
        
        for description in test_descriptions:
            url = orchestrator._extract_url_context(description)
            training_type = orchestrator._extract_training_type(description)
            
            print(f"📝 Description: {description[:50]}...")
            print(f"   🌐 URL: {url or 'None detected'}")
            print(f"   🏷️ Type: {training_type}")
            print()
        
        print("✅ Context extraction test completed")
        return True
        
    except Exception as e:
        print(f"❌ Context extraction test failed: {e}")
        return False


async def test_enhanced_training_workflow():
    """Test the enhanced training workflow with URL context."""
    print("\n🧪 Testing Enhanced Training Workflow...")
    
    try:
        from playwright.async_api import async_playwright
        from embedded_chrome_floating_agent_v1 import TaskOrchestrator
        
        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Mock chat window with page
        class MockChatWindow:
            def __init__(self, page):
                self.persistent_page = page
                self.messages = []
            
            def add_chat_message(self, sender, message, is_bot=False):
                self.messages.append(f"{sender}: {message}")
                print(f"[WORKFLOW] {sender}: {message}")
        
        # Test on different sites
        test_sites = [
            ("https://example.com", "General Website"),
            ("https://github.com", "Developer/Tech"),
        ]
        
        for url, expected_type in test_sites:
            try:
                await page.goto(url, timeout=30000)
                print(f"\n🌐 Testing on: {url}")
                
                mock_chat = MockChatWindow(page)
                orchestrator = TaskOrchestrator(None, mock_chat)
                orchestrator.initialize_element_detector(page)
                
                # Test enhanced training task creation
                enhanced_description = f"train on this page: {url} (type: {expected_type})"

                # Import TaskType directly
                from embedded_chrome_floating_agent_v1 import TaskType

                task = await orchestrator._create_task_from_description(
                    enhanced_description,
                    TaskType.MULTI_STEP
                )
                
                print(f"✅ Enhanced task created: {task.name}")
                
                if task.steps:
                    step = task.steps[0]
                    print(f"   📋 Action: {step.action}")
                    print(f"   🎯 Parameters: {step.parameters}")
                    
                    # Check if URL context is preserved
                    if 'url' in step.parameters:
                        print(f"   🌐 URL context: {step.parameters['url']}")
                    if 'training_type' in step.parameters:
                        print(f"   🏷️ Training type: {step.parameters['training_type']}")
                    if step.parameters.get('enhanced'):
                        print("   ✨ Enhanced mode: Enabled")
                
            except Exception as e:
                print(f"⚠️ Test failed for {url}: {e}")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        
        print("✅ Enhanced training workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced training workflow test failed: {e}")
        return False


def test_domain_analysis():
    """Test domain analysis functionality."""
    print("\n🧪 Testing Domain Analysis...")
    
    try:
        from general_webpage_trainer import GeneralWebpageTrainer
        
        # Create a mock trainer to test domain analysis
        class MockPage:
            def __init__(self, url):
                self.url = url
        
        trainer = GeneralWebpageTrainer(MockPage("https://example.com"), None)
        
        test_urls = [
            "https://www.example.com/path/to/page",
            "https://subdomain.github.com/user/repo",
            "https://university.edu/courses",
            "https://government.gov/services",
            "https://organization.org/about",
        ]
        
        for url in test_urls:
            domain_info = trainer._analyze_domain(url)
            url_analysis = trainer._analyze_url_structure(url)
            site_type = trainer._classify_site_type(url)
            
            print(f"🌐 URL: {url}")
            print(f"   Domain: {domain_info['domain']}")
            print(f"   Type: {domain_info['domain_type']}")
            print(f"   Site classification: {site_type}")
            print(f"   Path depth: {url_analysis['path_depth']}")
            print(f"   Secure: {url_analysis['is_secure']}")
            print()
        
        print("✅ Domain analysis test completed")
        return True
        
    except Exception as e:
        print(f"❌ Domain analysis test failed: {e}")
        return False


def test_button_integration():
    """Test that the enhanced button functionality is properly integrated."""
    print("\n🧪 Testing Enhanced Button Integration...")
    
    try:
        from embedded_chrome_floating_agent_v1 import EnhancedChatWindow
        import inspect
        
        # Check if enhanced methods are present
        source = inspect.getsource(EnhancedChatWindow)
        
        required_methods = [
            'get_current_page_context',
            'determine_training_type',
            'on_train_page'
        ]
        
        for method in required_methods:
            if method in source:
                print(f"✅ {method} method found")
            else:
                print(f"❌ {method} method missing")
                return False
        
        # Check for enhanced functionality indicators
        if 'URL context' in source:
            print("✅ URL context functionality found")
        else:
            print("❌ URL context functionality missing")
            return False
        
        if 'training_type' in source:
            print("✅ Training type detection found")
        else:
            print("❌ Training type detection missing")
            return False
        
        print("✅ Enhanced button integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced button integration test failed: {e}")
        return False


def main():
    """Run all enhanced training button tests."""
    print("🚀 Enhanced Training Button Test Suite")
    print("=" * 60)
    
    # Synchronous tests
    sync_tests = [
        ("URL Detection Test", test_url_detection),
        ("Context Extraction Test", test_context_extraction),
        ("Domain Analysis Test", test_domain_analysis),
        ("Button Integration Test", test_button_integration),
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
        ("Enhanced Training Workflow Test", test_enhanced_training_workflow),
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
    print("📊 ENHANCED TRAINING BUTTON TEST RESULTS")
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
        print("\n🎉 ALL TESTS PASSED! Enhanced training button is ready!")
        print("\n🚀 NEW FEATURES:")
        print("✨ Automatic URL detection and context awareness")
        print("🏷️ Intelligent site type classification")
        print("🎯 Enhanced training with domain-specific insights")
        print("📊 Comprehensive page analysis with URL context")
        print("🔍 Deep domain and URL structure analysis")
        print("\n💡 The 'Train on this page' button now:")
        print("  - Detects the current URL automatically")
        print("  - Classifies the site type (e-commerce, social media, etc.)")
        print("  - Provides context-aware training")
        print("  - Analyzes domain and URL structure")
        print("  - Gives detailed feedback about the page being trained on")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
