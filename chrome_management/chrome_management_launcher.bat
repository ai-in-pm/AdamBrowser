@echo off
title Chrome Management Suite
echo Chrome Management Suite - Adam Browser
echo ========================================
echo.

REM Set environment
set CHROME_MGMT_ROOT=D:\science_projects\adam_browser
set PYTHONPATH=%CHROME_MGMT_ROOT%;%PYTHONPATH%

REM Show menu
echo Available commands:
echo   1. Build distribution packages
echo   2. Update Chrome
echo   3. Optimize installation
echo   4. Run tests
echo   5. Start auto-updater
echo   6. Show status
echo   7. Run complete cycle
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" build
) else if "%choice%"=="2" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" update
) else if "%choice%"=="3" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" optimize
) else if "%choice%"=="4" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" test
) else if "%choice%"=="5" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" auto-update
) else if "%choice%"=="6" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" status
) else if "%choice%"=="7" (
    python "D:\science_projects\adam_browser/chrome_management_suite.py" all
) else (
    echo Invalid choice
)

pause
