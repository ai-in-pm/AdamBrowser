@echo off
title Adam Browser Widget Launcher
color 0A
echo.
echo ========================================
echo    🤖 ADAM BROWSER WIDGET LAUNCHER 🤖
echo ========================================
echo.
echo Starting Adam Browser floating widget...
echo Look for the blue robot in bottom-right corner!
echo.

REM Try to run the primary widget (embedded Chrome)
python embedded_chrome_floating_agent.py

REM If that fails, try secondary widget (simple floating agent)
if errorlevel 1 (
    echo.
    echo Primary GUI failed, trying secondary GUI...
    python simple_floating_agent.py
)

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Could not start Adam Browser Widget
    echo.
    echo Possible solutions:
    echo 1. Make sure Python is installed
    echo 2. Install wxPython: pip install wxpython
    echo 3. Check you are in the correct directory
    echo 4. Try running from PyCharm IDE
    echo.
    echo Current directory: %CD%
    echo.
)

echo.
echo Press any key to close this window...
pause >nul
