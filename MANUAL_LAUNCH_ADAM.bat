@echo off
title Adam Browser Manual Launcher
color 0B
cls

echo.
echo ================================================================
echo                🤖 ADAM BROWSER MANUAL LAUNCHER 🤖
echo ================================================================
echo.
echo This script will help you launch Adam Browser manually.
echo.
echo Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python is available
python --version

echo.
echo Checking for required files...

if exist "adam_floating_agent.py" (
    echo ✅ adam_floating_agent.py found
) else (
    echo ❌ adam_floating_agent.py not found
)

if exist "run_adam_gui.py" (
    echo ✅ run_adam_gui.py found
) else (
    echo ❌ run_adam_gui.py not found
)

if exist "start_adam_browser.py" (
    echo ✅ start_adam_browser.py found
) else (
    echo ❌ start_adam_browser.py not found
)

echo.
echo ================================================================
echo                    LAUNCH OPTIONS
echo ================================================================
echo.
echo 1. Launch Floating Robot Widget (adam_floating_agent.py)
echo 2. Launch Main GUI (run_adam_gui.py)
echo 3. Launch Simple Browser (start_adam_browser.py)
echo 4. Test wxPython Installation
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto launch_robot
if "%choice%"=="2" goto launch_gui
if "%choice%"=="3" goto launch_browser
if "%choice%"=="4" goto test_wx
if "%choice%"=="5" goto exit
goto invalid_choice

:launch_robot
echo.
echo 🤖 Launching Adam Floating Robot Widget...
echo Look for a blue robot in the bottom-right corner of your screen!
echo.
python adam_floating_agent.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to launch robot widget
    echo Error code: %errorlevel%
    echo.
    echo Trying alternative method...
    python -c "exec(open('adam_floating_agent.py').read())"
)
goto end

:launch_gui
echo.
echo 🖥️ Launching Adam Main GUI...
echo.
python run_adam_gui.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to launch main GUI
    echo Error code: %errorlevel%
)
goto end

:launch_browser
echo.
echo 🌐 Launching Adam Simple Browser...
echo.
python start_adam_browser.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to launch browser
    echo Error code: %errorlevel%
)
goto end

:test_wx
echo.
echo 🧪 Testing wxPython installation...
echo.
python -c "import wx; print('✅ wxPython is working!'); app = wx.App(); frame = wx.Frame(None, title='wxPython Test', size=(300, 200)); frame.Show(); app.MainLoop()"
if errorlevel 1 (
    echo.
    echo ❌ wxPython test failed
    echo.
    echo Installing wxPython...
    pip install wxpython
)
goto end

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.
echo.
pause
goto start

:exit
echo.
echo 👋 Goodbye!
goto end

:end
echo.
echo ================================================================
echo.
echo Press any key to close this window...
pause >nul
