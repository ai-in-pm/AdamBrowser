#!/usr/bin/env python3
"""
Chrome Management Setup Script

This script sets up the Chrome management system with all necessary dependencies,
configurations, and initial setup tasks.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json
from loguru import logger


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        logger.error("Python 3.11 or higher is required")
        logger.info(f"Current version: {sys.version}")
        return False
    
    logger.info(f"✅ Python version OK: {sys.version}")
    return True


def install_dependencies() -> bool:
    """Install required Python dependencies."""
    try:
        logger.info("Installing Python dependencies...")
        
        dependencies = [
            "loguru>=0.7.0",
            "requests>=2.31.0",
            "playwright>=1.40.0",
            "psutil>=5.9.0",
            "schedule>=1.2.0",
            "pefile>=2023.2.7",
            "Pillow>=10.0.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0"
        ]
        
        # Install dependencies
        cmd = [sys.executable, "-m", "pip", "install"] + dependencies
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to install dependencies: {result.stderr}")
            return False
        
        logger.info("✅ Dependencies installed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def install_playwright_browsers() -> bool:
    """Install Playwright browsers."""
    try:
        logger.info("Installing Playwright browsers...")
        
        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"Playwright browser installation warning: {result.stderr}")
            # Don't fail on this as it's not critical
        
        logger.info("✅ Playwright browsers installed")
        return True
        
    except Exception as e:
        logger.warning(f"Playwright browser installation failed: {e}")
        return True  # Don't fail setup for this


def check_system_tools() -> Dict[str, bool]:
    """Check for optional system tools."""
    tools = {
        "git": shutil.which("git") is not None,
        "7z": shutil.which("7z") is not None,
        "upx": shutil.which("upx") is not None,
        "makensis": shutil.which("makensis") is not None,
        "candle": shutil.which("candle") is not None,
        "optipng": shutil.which("optipng") is not None,
        "jpegoptim": shutil.which("jpegoptim") is not None
    }
    
    logger.info("System tools availability:")
    for tool, available in tools.items():
        status = "✅" if available else "❌"
        logger.info(f"  {tool}: {status}")
    
    return tools


def create_directory_structure(project_root: Path) -> bool:
    """Create necessary directory structure."""
    try:
        directories = [
            "chrome_management",
            "chrome_management/versions",
            "chrome_management/backups",
            "chrome_management/cache",
            "distribution",
            "distribution/packages",
            "distribution/build",
            "optimization",
            "testing",
            "testing/results",
            "scripts",
            "docs"
        ]
        
        for dir_name in directories:
            dir_path = project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Directory structure created")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create directory structure: {e}")
        return False


def create_default_configs(project_root: Path) -> bool:
    """Create default configuration files."""
    try:
        # Chrome management suite config
        suite_config = {
            "package": {
                "name": "AdamBrowser",
                "version": "1.0.0",
                "include_chrome": True,
                "optimize_size": True,
                "build_all_formats": True
            },
            "chrome": {
                "channel": "stable",
                "auto_update": True,
                "backup_versions": 3,
                "update_window_start": 2,
                "update_window_end": 6
            },
            "optimization": {
                "remove_debug_symbols": True,
                "remove_dev_tools": True,
                "compress_resources": True,
                "aggressive_optimization": False
            },
            "testing": {
                "run_on_build": True,
                "include_performance": True,
                "fail_on_test_failure": True
            }
        }
        
        config_file = project_root / "chrome_management" / "suite_config.json"
        with open(config_file, 'w') as f:
            json.dump(suite_config, f, indent=2)
        
        # Update policy config
        update_policy = {
            "auto_update": True,
            "check_interval_hours": 24,
            "allowed_channels": ["stable"],
            "security_updates_only": False,
            "rollback_enabled": True,
            "backup_versions": 3,
            "update_window_start": 2,
            "update_window_end": 6,
            "require_confirmation": False
        }
        
        policy_file = project_root / "chrome_management" / "update_policy.json"
        with open(policy_file, 'w') as f:
            json.dump(update_policy, f, indent=2)
        
        logger.info("✅ Default configurations created")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create configurations: {e}")
        return False


def create_launcher_scripts(project_root: Path) -> bool:
    """Create launcher scripts for easy access."""
    try:
        # Windows batch script
        batch_content = f'''@echo off
title Chrome Management Suite
echo Chrome Management Suite - Adam Browser
echo ========================================
echo.

REM Set environment
set CHROME_MGMT_ROOT={project_root}
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
    python "{project_root}/chrome_management_suite.py" build
) else if "%choice%"=="2" (
    python "{project_root}/chrome_management_suite.py" update
) else if "%choice%"=="3" (
    python "{project_root}/chrome_management_suite.py" optimize
) else if "%choice%"=="4" (
    python "{project_root}/chrome_management_suite.py" test
) else if "%choice%"=="5" (
    python "{project_root}/chrome_management_suite.py" auto-update
) else if "%choice%"=="6" (
    python "{project_root}/chrome_management_suite.py" status
) else if "%choice%"=="7" (
    python "{project_root}/chrome_management_suite.py" all
) else (
    echo Invalid choice
)

pause
'''
        
        batch_file = project_root / "chrome_management_launcher.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # PowerShell script
        ps_content = f'''# Chrome Management Suite PowerShell Launcher
Write-Host "Chrome Management Suite - Adam Browser" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$env:CHROME_MGMT_ROOT = "{project_root}"
$env:PYTHONPATH = "$env:CHROME_MGMT_ROOT;$env:PYTHONPATH"

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Green
Write-Host "  1. Build distribution packages"
Write-Host "  2. Update Chrome"
Write-Host "  3. Optimize installation"
Write-Host "  4. Run tests"
Write-Host "  5. Start auto-updater"
Write-Host "  6. Show status"
Write-Host "  7. Run complete cycle"
Write-Host ""

$choice = Read-Host "Enter your choice (1-7)"

switch ($choice) {{
    "1" {{ & python "{project_root}/chrome_management_suite.py" build }}
    "2" {{ & python "{project_root}/chrome_management_suite.py" update }}
    "3" {{ & python "{project_root}/chrome_management_suite.py" optimize }}
    "4" {{ & python "{project_root}/chrome_management_suite.py" test }}
    "5" {{ & python "{project_root}/chrome_management_suite.py" auto-update }}
    "6" {{ & python "{project_root}/chrome_management_suite.py" status }}
    "7" {{ & python "{project_root}/chrome_management_suite.py" all }}
    default {{ Write-Host "Invalid choice" -ForegroundColor Red }}
}}

Read-Host "Press Enter to exit"
'''
        
        ps_file = project_root / "chrome_management_launcher.ps1"
        with open(ps_file, 'w') as f:
            f.write(ps_content)
        
        logger.info("✅ Launcher scripts created")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create launcher scripts: {e}")
        return False


def verify_chrome_installation(project_root: Path) -> bool:
    """Verify existing Chrome installation."""
    chrome_exe = project_root / "Google" / "Chrome" / "Application" / "chrome.exe"
    
    if chrome_exe.exists():
        logger.info("✅ Chrome installation found")
        
        # Get Chrome version
        try:
            result = subprocess.run([str(chrome_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"  Chrome version: {version}")
            else:
                logger.warning("  Could not determine Chrome version")
        except Exception as e:
            logger.warning(f"  Chrome version check failed: {e}")
        
        return True
    else:
        logger.warning("❌ Chrome installation not found")
        logger.info(f"  Expected location: {chrome_exe}")
        return False


def run_initial_tests(project_root: Path) -> bool:
    """Run basic tests to verify setup."""
    try:
        logger.info("Running initial verification tests...")
        
        # Test imports
        sys.path.insert(0, str(project_root))
        
        try:
            from chrome_management.version_manager import ChromeVersionManager
            from distribution.package_builder import DistributionBuilder
            from optimization.size_optimizer import PackageOptimizer
            logger.info("✅ Module imports successful")
        except ImportError as e:
            logger.error(f"❌ Module import failed: {e}")
            return False
        
        # Test Chrome version detection
        try:
            version_manager = ChromeVersionManager(project_root)
            current_version = version_manager.get_current_version()
            if current_version:
                logger.info(f"✅ Chrome version detection: {current_version.version}")
            else:
                logger.warning("⚠️ Chrome version detection failed")
        except Exception as e:
            logger.warning(f"⚠️ Chrome version detection error: {e}")
        
        logger.info("✅ Initial tests completed")
        return True
        
    except Exception as e:
        logger.error(f"Initial tests failed: {e}")
        return False


def main():
    """Main setup function."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    logger.info("🚀 Chrome Management System Setup")
    logger.info("=" * 50)
    
    project_root = Path(__file__).parent.parent
    logger.info(f"Project root: {project_root}")
    
    setup_steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Installing Playwright browsers", install_playwright_browsers),
        ("Creating directory structure", lambda: create_directory_structure(project_root)),
        ("Creating default configurations", lambda: create_default_configs(project_root)),
        ("Creating launcher scripts", lambda: create_launcher_scripts(project_root)),
        ("Verifying Chrome installation", lambda: verify_chrome_installation(project_root)),
        ("Running initial tests", lambda: run_initial_tests(project_root))
    ]
    
    failed_steps = []
    
    for step_name, step_func in setup_steps:
        logger.info(f"\n📋 {step_name}...")
        try:
            success = step_func()
            if not success:
                failed_steps.append(step_name)
                logger.error(f"❌ {step_name} failed")
            else:
                logger.info(f"✅ {step_name} completed")
        except Exception as e:
            failed_steps.append(step_name)
            logger.error(f"❌ {step_name} failed: {e}")
    
    # Check system tools
    logger.info(f"\n📋 Checking system tools...")
    tools = check_system_tools()
    
    # Final summary
    logger.info(f"\n{'='*50}")
    logger.info("SETUP SUMMARY")
    logger.info(f"{'='*50}")
    
    if not failed_steps:
        logger.info("🎉 Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Run 'python chrome_management_suite.py status' to check system status")
        logger.info("2. Run 'python chrome_management_suite.py test' to run comprehensive tests")
        logger.info("3. Use 'chrome_management_launcher.bat' for interactive menu")
        
        return 0
    else:
        logger.error(f"❌ Setup completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            logger.error(f"  - {step}")
        
        logger.info("\nYou may still be able to use some features.")
        logger.info("Check the logs above for specific error details.")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
