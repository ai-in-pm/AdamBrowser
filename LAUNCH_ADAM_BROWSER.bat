@echo off
title Adam Browser Launcher
echo.
echo ========================================
echo    ADAM BROWSER GUI LAUNCHER
echo ========================================
echo.
echo Starting Adam Browser GUI...
echo.

python start_adam_browser.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Adam Browser GUI
    echo.
    echo Trying alternative launcher...
    python run_adam_gui.py
)

if errorlevel 1 (
    echo.
    echo ERROR: GUI launch failed
    echo.
    echo Please check:
    echo 1. Python is installed
    echo 2. wxPython is installed: pip install wxpython
    echo 3. You are in the correct directory
    echo.
)

echo.
echo Press any key to close...
pause >nul
