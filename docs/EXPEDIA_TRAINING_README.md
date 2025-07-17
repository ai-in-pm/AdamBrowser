# 🎯 AI Agent Training System

## Overview

This comprehensive training system enhances the Adam Browser AI agent with both specialized and general webpage training capabilities. It includes:

- **Expedia-Specific Training**: Specialized capabilities for travel booking interfaces
- **General Webpage Training**: Universal training for any website
- **Intelligent Analysis**: Comprehensive page structure and element detection
- **Adaptive Learning**: Continuous improvement through interaction patterns

## 🚀 Features

### Core Training Capabilities
- **Intelligent Form Detection**: Automatically identifies and analyzes forms on any webpage
- **Natural Interaction Simulation**: Human-like typing, mouse movements, and interaction patterns
- **Adaptive Learning**: Learns from successful interactions and improves over time
- **Multi-Step Workflow Management**: Handles complex processes from analysis to interaction
- **Error Recovery**: Intelligent retry mechanisms and alternative approaches

### General Webpage Training
- **Universal Element Detection**: Identifies buttons, forms, links, and interactive elements on any site
- **Page Structure Analysis**: Comprehensive analysis of content, navigation, and accessibility
- **Safe Interaction Practice**: Practices interactions without causing destructive actions
- **Content Pattern Recognition**: Learns common webpage patterns and structures
- **Performance Metrics**: Gathers page load times and element counts

### Expedia-Specific Intelligence
- **Travel Form Recognition**: Specialized detection for flight, hotel, and car rental forms
- **Dynamic Content Handling**: Manages loading states, autocomplete, and dynamic pricing
- **Booking Step Detection**: Automatically identifies current page type and appropriate actions
- **Travel Pattern Learning**: Understands common travel booking patterns and user preferences

## 📁 File Structure

```
# General Training System
general_webpage_trainer.py          # Universal webpage training for any site
test_general_training.py           # Test suite for general training

# Expedia-Specific Training
expedia_training_module.py          # Main training agent and logic
expedia_element_detector.py         # Advanced element detection for Expedia
travel_booking_patterns.py          # Travel-specific patterns and workflows
expedia_training_data.json          # Training data and scenarios
train_expedia_agent.py             # Standalone training script
test_expedia_training.py           # Test suite for training system

# Enhanced Main System
embedded_chrome_floating_agent_v1.py # Enhanced main agent with training integration
adam_browser_advanced_capabilities.py # Enhanced with travel booking intelligence
```

## 🛠️ Installation & Setup

### Prerequisites
```bash
pip install playwright wxpython pillow pytesseract numpy loguru
playwright install chromium
```

### Quick Start
1. **Run the test suites** to verify everything is working:
   ```bash
   python test_general_training.py    # Test general training
   python test_expedia_training.py    # Test Expedia-specific training
   ```

2. **Start the enhanced floating agent**:
   ```bash
   python embedded_chrome_floating_agent_v1.py
   ```

3. **Navigate to any webpage** and click the **"🎯 Train on this page"** button
   - For Expedia.com: Specialized travel booking training activates
   - For other sites: General webpage training activates

## 🎮 Usage

### Interactive Training Mode

1. **Launch the floating agent** and navigate to any webpage
2. **Click the "🎯 Train on this page" button** for instant training
3. **Or use chat commands**:
   - `"Train on this page"` - Comprehensive page analysis and learning
   - `"Analyze this website"` - Detailed structure analysis
   - `"Practice interactions"` - Safe interaction practice
   - `"Learn this form"` - Specific form analysis

   **For Expedia.com specifically**:
   - `"Practice booking a flight"` - Flight search form practice
   - `"Learn hotel booking"` - Hotel search interface training
   - `"Practice travel search"` - Travel form practice

### Standalone Training Session

Run a comprehensive training session:
```bash
python train_expedia_agent.py
```

This will:
- Launch a browser and navigate to Expedia
- Run multiple training scenarios
- Generate a detailed performance report
- Save learning data for future sessions

### Training Commands in Chat

When the floating agent is active on Expedia.com, you can use these commands:

- **"Train me on Expedia"** - Start comprehensive training
- **"Practice flight search from NYC to LAX"** - Specific scenario training
- **"Learn this form"** - Analyze current form structure
- **"Show me what you learned"** - Display training statistics

## 🧠 How It Works

### 1. Page Analysis
The system automatically detects:
- Current page type (homepage, search results, details, booking)
- Available forms and their purposes
- Interactive elements and their functions
- Dynamic content loading states

### 2. Element Detection
Advanced selectors identify:
- Location input fields (origin/destination)
- Date picker elements
- Traveler/guest selectors
- Search and booking buttons
- Result items and filters

### 3. Intelligent Interaction
The agent simulates human behavior:
- Natural typing speeds with variations
- Realistic mouse movement patterns
- Appropriate delays between actions
- Error correction and retry logic

### 4. Learning & Adaptation
The system continuously improves:
- Records successful interaction patterns
- Learns from failed attempts
- Adapts to UI changes and A/B tests
- Builds user preference profiles

## 📊 Training Scenarios

### Built-in Scenarios

1. **Basic Flight Search**
   - Origin: New York, NY → Destination: Los Angeles, CA
   - Tests: Form filling, date selection, traveler options

2. **Hotel Booking**
   - Destination: Las Vegas, NV
   - Tests: Check-in/out dates, guest selection, room options

3. **Car Rental**
   - Location: Miami, FL
   - Tests: Pickup/dropoff locations and dates

4. **International Flight**
   - Origin: New York, NY → Destination: London, UK
   - Tests: International booking patterns, class selection

### Custom Scenarios

Create custom training scenarios by modifying `expedia_training_data.json`:

```json
{
  "name": "Custom Scenario",
  "type": "flight",
  "data": {
    "origin": "Your Origin",
    "destination": "Your Destination",
    "departure_date": "MM/DD/YYYY",
    "return_date": "MM/DD/YYYY",
    "travelers": 2,
    "class": "Business"
  }
}
```

## 📈 Performance Monitoring

### Training Reports

After each session, the system generates detailed reports:

```json
{
  "session_summary": {
    "duration_minutes": 15.2,
    "pages_trained": 3,
    "successful_interactions": 12,
    "failed_interactions": 2,
    "forms_completed": 4,
    "success_rate": 85.7
  },
  "recommendations": [
    "Consider increasing training duration for better learning",
    "Focus on form filling training scenarios"
  ]
}
```

### Learning Metrics

Track improvement over time:
- Form completion success rate
- Average interaction time
- Error recovery effectiveness
- Pattern recognition accuracy

## 🔧 Configuration

### Training Parameters

Modify training behavior in `expedia_training_module.py`:

```python
# Typing speed simulation
typing_speed_wpm = random.randint(35, 65)

# Mouse movement patterns
mouse_movement_speed = random.uniform(0.8, 1.5)

# Error simulation for realism
error_probability = 0.02  # 2% chance
```

### Element Selectors

Update selectors in `expedia_element_detector.py` for UI changes:

```python
'search_forms': [
    '[data-testid="flight-search-form"]',  # Primary
    '.flight-search-form',                 # Fallback
    '#flight-search'                       # Legacy
]
```

## 🐛 Troubleshooting

### Common Issues

1. **Training not activating**
   - Ensure you're on expedia.com
   - Check console for import errors
   - Verify all dependencies are installed

2. **Element detection failing**
   - UI may have changed - update selectors
   - Check for loading states
   - Verify page is fully loaded

3. **Form filling errors**
   - Check for CAPTCHA or bot detection
   - Verify field selectors are current
   - Ensure proper timing delays

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Adding New Travel Sites

1. Create site-specific patterns in `travel_booking_patterns.py`
2. Add detection logic in element detector
3. Update training scenarios
4. Test with new site workflows

### Improving Detection

1. Monitor failed interactions
2. Update selectors for UI changes
3. Add new interaction patterns
4. Enhance error recovery logic

## 📞 Support

For issues or questions:
1. Run the test suite: `python test_expedia_training.py`
2. Check the training reports for insights
3. Review console output for error details
4. Update selectors if UI has changed

## 🎉 Success Indicators

The training system is working correctly when you see:

- ✅ "Expedia training mode activated!" message
- 🎯 Successful form detection and filling
- 📊 Improving success rates over time
- 🧠 Adaptive behavior based on learned patterns

The AI agent will become increasingly proficient at Expedia interactions as it learns from each training session, ultimately providing seamless travel booking assistance.
