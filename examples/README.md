# Adam Browser - Embedded Chrome Agent v1 - Desktop Shortcuts

This folder contains desktop shortcuts for the **Embedded Chrome Floating Agent v1** that allow you to run the application without opening an IDE.

## 🚀 Available Shortcuts

### 1. Adam Browser - Embedded Chrome Agent v1.bat (RECOMMENDED)
- **Type**: Enhanced Batch File (.bat file)
- **Usage**: Double-click to launch the floating agent v1
- **Features**:
  - ✅ Enhanced console interface with colors and progress
  - ✅ Automatic Python detection and fallback
  - ✅ Detailed startup messages and tips
  - ✅ Better error handling and user guidance
  - ✅ Shows application status and instructions

### 2. Adam Browser Agent.bat (Updated)
- **Type**: Updated Batch File (.bat file)
- **Usage**: Double-click to launch the floating agent v1
- **Features**:
  - ✅ Updated to point to v1 script
  - ✅ Shows console window during startup
  - ✅ Displays any error messages
  - ✅ Pauses after execution for debugging

### 3. Adam Browser Agent.lnk (Original)
- **Type**: Windows Shortcut (.lnk file)
- **Usage**: Double-click to launch the floating agent
- **Features**:
  - ⚠️ Points to original version (not v1)
  - Native Windows shortcut with proper icon
  - Can be copied to desktop or pinned to taskbar

## How to Use

1. **Quick Launch**: Double-click either shortcut file to start the agent
2. **Desktop Access**: Copy either file to your desktop for easy access
3. **Taskbar Pin**: Right-click the .lnk file and select "Pin to taskbar"
4. **Start Menu**: Copy to your Start Menu folder for quick access

## What the Agent Does

When launched, the **Embedded Chrome Floating Agent** will:

- 🤖 Display a floating robot icon in the bottom-right corner of your screen
- 🌐 Use the embedded Chrome browser for automation
- 💬 Open a chat interface when you click the robot icon
- 🔧 Provide browser automation capabilities with OCR support
- 📸 Take screenshots and perform web automation tasks

## Features

- **Embedded Chrome Integration**: Uses the Chrome browser located at `D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe`
- **OCR Capabilities**: Extract text from web pages and images
- **Floating UI**: Always-on-top robot icon for quick access
- **Browser Automation**: Navigate, search, click, and interact with web pages
- **Persistent Browser**: Browser stays open between commands for faster execution

## Troubleshooting

### If the shortcut doesn't work:
1. Make sure Python is properly installed
2. Verify the embedded Chrome browser exists at the expected path
3. Check that all required dependencies are installed
4. Try running the .bat file to see any error messages

### If you see import errors:
1. Open a command prompt in the project directory
2. Run: `pip install -r requirements.txt` (if requirements file exists)
3. Install missing packages: `pip install wx playwright loguru pillow opencv-python pytesseract`

### If Chrome browser is not found:
1. Check if Chrome exists at: `D:\science_projects\adam_browser\Google\Chrome\Application\chrome.exe`
2. The agent will fall back to system Chrome if embedded version is not found
3. Install Playwright browsers: `playwright install chromium`

## 📁 File Locations

- **Main Script v1**: `../embedded_chrome_floating_agent_v1.py`
- **Original Script**: `../embedded_chrome_floating_agent.py`
- **Project Root**: `D:/science_projects/adam_browser/`
- **Shortcuts**: `D:/science_projects/adam_browser/examples/`
- **Chrome Browser**: `D:/science_projects/adam_browser/Google/Chrome/Application/chrome.exe`

## Support

For issues or questions:
1. Check the console output when using the .bat file
2. Review the main script documentation
3. Ensure all dependencies are properly installed
4. Verify Python and Chrome paths are correct

---

**Note**: These shortcuts are configured to run with your current Python environment and project setup. If you move the project folder, you'll need to recreate the shortcuts using the `create_shortcut.py` script.
