#!/usr/bin/env python3
"""
Comprehensive Expedia AI Agent Training Script

This script provides a complete training environment for the AI agent to learn
Expedia.com interactions. It includes:
- Automated training sessions
- Performance monitoring
- Learning analytics
- Interactive training mode
- Batch training scenarios
"""

import asyncio
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import our training modules
try:
    from expedia_training_module import ExpediaTrainingAgent, TravelSearchCriteria, TravelBookingType
    from expedia_element_detector import AdvancedExpediaDetector, ExpediaPageType
    from travel_booking_patterns import travel_patterns, TravelSite
    TRAINING_MODULES_AVAILABLE = True
    print("✅ All training modules imported successfully")
except ImportError as e:
    print(f"❌ Training modules not available: {e}")
    TRAINING_MODULES_AVAILABLE = False

# Import browser automation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ExpediaTrainingSession:
    """Manages a complete training session for the Expedia AI agent."""
    
    def __init__(self, headless: bool = False, slow_mo: int = 500):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.page = None
        self.training_agent = None
        self.element_detector = None
        
        # Training metrics
        self.session_stats = {
            'start_time': None,
            'end_time': None,
            'pages_trained': 0,
            'successful_interactions': 0,
            'failed_interactions': 0,
            'forms_completed': 0,
            'errors_encountered': [],
            'learning_points': []
        }
        
        # Load training scenarios
        self.training_scenarios = self._load_training_scenarios()
    
    def _load_training_scenarios(self) -> List[Dict[str, Any]]:
        """Load training scenarios from the data file."""
        try:
            with open('expedia_training_data.json', 'r') as f:
                data = json.load(f)
            return data.get('test_scenarios', [])
        except Exception as e:
            print(f"⚠️ Could not load training scenarios: {e}")
            return self._get_default_scenarios()
    
    def _get_default_scenarios(self) -> List[Dict[str, Any]]:
        """Get default training scenarios if file is not available."""
        return [
            {
                "name": "Basic Flight Search",
                "type": "flight",
                "data": {
                    "origin": "New York, NY",
                    "destination": "Los Angeles, CA",
                    "departure_date": "03/15/2024",
                    "return_date": "03/22/2024",
                    "travelers": 1,
                    "class": "Economy"
                }
            },
            {
                "name": "Hotel Search",
                "type": "hotel",
                "data": {
                    "destination": "Las Vegas, NV",
                    "checkin_date": "04/10/2024",
                    "checkout_date": "04/13/2024",
                    "guests": 2,
                    "rooms": 1
                }
            }
        ]
    
    async def start_training_session(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """Start a comprehensive training session."""
        try:
            print("🚀 Starting Expedia AI Agent Training Session")
            print(f"⏱️ Duration: {duration_minutes} minutes")
            print(f"🎭 Headless mode: {self.headless}")
            
            self.session_stats['start_time'] = datetime.now()
            
            # Initialize browser
            await self._initialize_browser()
            
            # Navigate to Expedia
            await self._navigate_to_expedia()
            
            # Initialize training components
            await self._initialize_training_components()
            
            # Run training scenarios
            end_time = time.time() + (duration_minutes * 60)
            scenario_index = 0
            
            while time.time() < end_time and scenario_index < len(self.training_scenarios):
                scenario = self.training_scenarios[scenario_index]
                print(f"\n📋 Training Scenario {scenario_index + 1}: {scenario['name']}")
                
                result = await self._run_training_scenario(scenario)
                self._update_session_stats(result)
                
                scenario_index += 1
                
                # Wait between scenarios
                await asyncio.sleep(2)
            
            # Run general page exploration
            if time.time() < end_time:
                await self._explore_page_elements()
            
            # Finalize session
            self.session_stats['end_time'] = datetime.now()
            session_report = await self._generate_session_report()
            
            await self._cleanup()
            
            return session_report
            
        except Exception as e:
            print(f"❌ Training session failed: {e}")
            await self._cleanup()
            return {'success': False, 'error': str(e)}
    
    async def _initialize_browser(self):
        """Initialize the browser for training."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")
        
        playwright = await async_playwright().start()
        
        # Use system Chrome if available
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if Path(chrome_path).exists():
            self.browser = await playwright.chromium.launch(
                executable_path=chrome_path,
                headless=self.headless,
                slow_mo=self.slow_mo
            )
        else:
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
        
        # Create page with realistic viewport
        self.page = await self.browser.new_page(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Set user agent to appear more human
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("✅ Browser initialized successfully")
    
    async def _navigate_to_expedia(self):
        """Navigate to Expedia homepage."""
        try:
            print("🌐 Navigating to Expedia.com...")
            await self.page.goto('https://www.expedia.com', wait_until='domcontentloaded')
            await asyncio.sleep(3)  # Wait for dynamic content
            
            # Handle cookie consent if present
            await self._handle_cookie_consent()
            
            print("✅ Successfully navigated to Expedia")
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            raise
    
    async def _handle_cookie_consent(self):
        """Handle cookie consent popup if present."""
        try:
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                '[data-testid="accept-cookies"]',
                '.cookie-accept',
                '#accept-cookies'
            ]
            
            for selector in cookie_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        await element.click()
                        await asyncio.sleep(1)
                        print("✅ Cookie consent handled")
                        return
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Cookie consent handling: {e}")
    
    async def _initialize_training_components(self):
        """Initialize training agent and element detector."""
        if not TRAINING_MODULES_AVAILABLE:
            raise RuntimeError("Training modules not available")
        
        # Create a mock chat window for logging
        class MockChatWindow:
            def add_chat_message(self, sender, message, is_bot=False):
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {sender}: {message}")
        
        mock_chat = MockChatWindow()
        
        # Initialize training components
        self.training_agent = ExpediaTrainingAgent(self.page, mock_chat)
        self.element_detector = AdvancedExpediaDetector(self.page)
        
        print("✅ Training components initialized")
    
    async def _run_training_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single training scenario."""
        try:
            scenario_name = scenario['name']
            scenario_type = scenario['type']
            scenario_data = scenario['data']
            
            print(f"🎯 Running scenario: {scenario_name}")
            
            # Create search criteria from scenario data
            if scenario_type == 'flight':
                criteria = TravelSearchCriteria(
                    booking_type=TravelBookingType.FLIGHT,
                    departure_location=scenario_data.get('origin', 'New York, NY'),
                    destination_location=scenario_data.get('destination', 'Los Angeles, CA'),
                    departure_date=scenario_data.get('departure_date', ''),
                    return_date=scenario_data.get('return_date', ''),
                    travelers=scenario_data.get('travelers', 1)
                )
            elif scenario_type == 'hotel':
                criteria = TravelSearchCriteria(
                    booking_type=TravelBookingType.HOTEL,
                    destination_location=scenario_data.get('destination', 'Las Vegas, NV'),
                    departure_date=scenario_data.get('checkin_date', ''),
                    return_date=scenario_data.get('checkout_date', ''),
                    travelers=scenario_data.get('guests', 2),
                    rooms=scenario_data.get('rooms', 1)
                )
            else:
                # Generic criteria
                criteria = TravelSearchCriteria(
                    booking_type=TravelBookingType.FLIGHT
                )
            
            # Train on current page
            training_result = await self.training_agent.train_on_current_page()
            
            if training_result['success']:
                # Try to fill the search form
                fill_result = await self.training_agent.fill_search_form(criteria)
                
                return {
                    'scenario': scenario_name,
                    'success': fill_result['success'],
                    'training_result': training_result,
                    'fill_result': fill_result
                }
            else:
                return {
                    'scenario': scenario_name,
                    'success': False,
                    'error': training_result.get('error', 'Training failed')
                }
                
        except Exception as e:
            return {
                'scenario': scenario.get('name', 'Unknown'),
                'success': False,
                'error': str(e)
            }
    
    async def _explore_page_elements(self):
        """Explore and analyze page elements for learning."""
        try:
            print("🔍 Exploring page elements...")
            
            # Detect page type
            page_type = await self.element_detector.detect_page_type()
            print(f"📄 Page type detected: {page_type.value}")
            
            # Detect all interactive elements
            elements = await self.element_detector.detect_all_interactive_elements()
            
            total_elements = sum(len(element_list) for element_list in elements.values())
            print(f"🎯 Found {total_elements} interactive elements")
            
            for element_type, element_list in elements.items():
                if element_list:
                    print(f"  - {element_type}: {len(element_list)} elements")
            
            self.session_stats['pages_trained'] += 1
            
        except Exception as e:
            print(f"⚠️ Page exploration error: {e}")
    
    def _update_session_stats(self, result: Dict[str, Any]):
        """Update session statistics based on training result."""
        if result['success']:
            self.session_stats['successful_interactions'] += 1
            if 'fill_result' in result and result['fill_result'].get('success'):
                self.session_stats['forms_completed'] += 1
        else:
            self.session_stats['failed_interactions'] += 1
            if 'error' in result:
                self.session_stats['errors_encountered'].append(result['error'])
    
    async def _generate_session_report(self) -> Dict[str, Any]:
        """Generate a comprehensive session report."""
        duration = self.session_stats['end_time'] - self.session_stats['start_time']
        
        report = {
            'session_summary': {
                'duration_minutes': duration.total_seconds() / 60,
                'pages_trained': self.session_stats['pages_trained'],
                'successful_interactions': self.session_stats['successful_interactions'],
                'failed_interactions': self.session_stats['failed_interactions'],
                'forms_completed': self.session_stats['forms_completed'],
                'success_rate': self._calculate_success_rate(),
                'errors_count': len(self.session_stats['errors_encountered'])
            },
            'detailed_stats': self.session_stats,
            'recommendations': self._generate_recommendations()
        }
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"training_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📊 Training report saved to {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        return report
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        total = self.session_stats['successful_interactions'] + self.session_stats['failed_interactions']
        if total == 0:
            return 0.0
        return (self.session_stats['successful_interactions'] / total) * 100
    
    def _generate_recommendations(self) -> List[str]:
        """Generate training recommendations based on session results."""
        recommendations = []
        
        success_rate = self._calculate_success_rate()
        
        if success_rate < 50:
            recommendations.append("Consider increasing training duration for better learning")
            recommendations.append("Review element detection patterns for accuracy")
        
        if self.session_stats['forms_completed'] == 0:
            recommendations.append("Focus on form filling training scenarios")
        
        if len(self.session_stats['errors_encountered']) > 5:
            recommendations.append("Implement better error handling and recovery")
        
        if self.session_stats['pages_trained'] < 3:
            recommendations.append("Explore more page types for comprehensive training")
        
        return recommendations
    
    async def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            print("✅ Browser cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


async def main():
    """Main training function."""
    print("🤖 Expedia AI Agent Training System")
    print("=" * 50)
    
    if not TRAINING_MODULES_AVAILABLE:
        print("❌ Training modules not available. Please ensure all files are present.")
        return
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available. Please install: pip install playwright")
        return
    
    # Create training session
    training_session = ExpediaTrainingSession(
        headless=False,  # Set to True for headless mode
        slow_mo=300      # Slow down for better observation
    )
    
    # Start training
    try:
        report = await training_session.start_training_session(duration_minutes=15)
        
        print("\n" + "=" * 50)
        print("📊 TRAINING SESSION COMPLETE")
        print("=" * 50)
        
        if report.get('success', True):
            summary = report['session_summary']
            print(f"⏱️ Duration: {summary['duration_minutes']:.1f} minutes")
            print(f"📄 Pages trained: {summary['pages_trained']}")
            print(f"✅ Successful interactions: {summary['successful_interactions']}")
            print(f"❌ Failed interactions: {summary['failed_interactions']}")
            print(f"📋 Forms completed: {summary['forms_completed']}")
            print(f"📈 Success rate: {summary['success_rate']:.1f}%")
            
            if report['recommendations']:
                print("\n💡 Recommendations:")
                for rec in report['recommendations']:
                    print(f"  - {rec}")
        else:
            print(f"❌ Training session failed: {report.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
    except Exception as e:
        print(f"❌ Training error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
