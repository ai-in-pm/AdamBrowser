@echo off
title Adam Browser - Embedded Chrome Agent v1
echo.
echo ===============================================
echo    Adam Browser - Embedded Chrome Agent v1
echo ===============================================
echo.
echo Starting AI-powered browser automation...
echo Loading embedded Chrome integration...
echo Initializing floating robot interface...
echo.

cd /d "D:\science_projects\adam_browser"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH. Trying specific Python installation...
    "C:\Program Files\Python311\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo Python not found. Please install Python or check your installation.
        echo.
        pause
        exit /b 1
    ) else (
        echo Using Python from: C:\Program Files\Python311\python.exe
        "C:\Program Files\Python311\python.exe" "embedded_chrome_floating_agent_v1.py"
    )
) else (
    echo Using Python from PATH
    python "embedded_chrome_floating_agent_v1.py"
)

echo.
echo ===============================================
echo    Application closed
echo ===============================================
echo.
echo Tips:
echo - Look for the floating robot icon in bottom-right corner
echo - Single-click the robot to open the chat interface
echo - Use natural language commands like "go to google.com"
echo.
echo Press any key to exit...
pause >nul
