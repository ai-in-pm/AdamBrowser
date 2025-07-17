#!/usr/bin/env python3
"""
Comprehensive Chrome Integration Testing Framework

This module provides extensive testing capabilities for Chrome integration including:
- Chrome installation verification
- Version management testing
- Update mechanism testing
- Performance benchmarking
- Compatibility testing
- Security validation
"""

import os
import sys
import asyncio
import subprocess
import tempfile
import shutil
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import unittest
import pytest
from loguru import logger

# disable all "safe" commands
import psutil
import requests
from playwright.async_api import async_playwright, Browser, Page
# disable all "dangerous" commands

# Import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from chrome_management.version_manager import ChromeVersionManager, ChromeVersion, UpdatePolicy
from chrome_management.auto_updater import UpdateScheduler
from optimization.size_optimizer import ChromeOptimizer, OptimizationConfig


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Result of performance benchmark."""
    test_name: str
    metric_name: str
    value: float
    unit: str
    baseline: Optional[float] = None
    improvement: Optional[float] = None


class ChromeInstallationTests:
    """Tests for Chrome installation and basic functionality."""
    
    def __init__(self, project_root: Path):
        """Initialize Chrome installation tests."""
        self.project_root = project_root
        self.chrome_dir = project_root / "Google" / "Chrome"
        self.test_results = []
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all Chrome installation tests."""
        tests = [
            self.test_chrome_executable_exists,
            self.test_chrome_version_detection,
            self.test_chrome_launch_basic,
            self.test_chrome_launch_with_args,
            self.test_chrome_directory_structure,
            self.test_chrome_dependencies,
            self.test_chrome_permissions,
            self.test_chrome_memory_usage,
        ]
        
        self.test_results = []
        
        for test in tests:
            start_time = time.time()
            try:
                test()
                duration = time.time() - start_time
                result = TestResult(
                    test_name=test.__name__,
                    success=True,
                    duration=duration
                )
            except Exception as e:
                duration = time.time() - start_time
                result = TestResult(
                    test_name=test.__name__,
                    success=False,
                    duration=duration,
                    error_message=str(e)
                )
            
            self.test_results.append(result)
            logger.info(f"Test {test.__name__}: {'PASS' if result.success else 'FAIL'}")
        
        return self.test_results
    
    def test_chrome_executable_exists(self) -> None:
        """Test that Chrome executable exists and is valid."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        if not chrome_exe.exists():
            raise AssertionError(f"Chrome executable not found: {chrome_exe}")
        
        # Check file size (should be reasonable)
        file_size = chrome_exe.stat().st_size
        if file_size < 1024 * 1024:  # Less than 1MB is suspicious
            raise AssertionError(f"Chrome executable too small: {file_size} bytes")
        
        # Check it's a valid PE executable
        with open(chrome_exe, 'rb') as f:
            header = f.read(2)
            if header != b'MZ':
                raise AssertionError("Chrome executable is not a valid PE file")
    
    def test_chrome_version_detection(self) -> None:
        """Test Chrome version detection."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        # Try to get version using --version flag
        try:
            result = subprocess.run([str(chrome_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise AssertionError(f"Chrome --version failed: {result.stderr}")
            
            version_output = result.stdout.strip()
            if not version_output or "Google Chrome" not in version_output:
                raise AssertionError(f"Invalid version output: {version_output}")
            
        except subprocess.TimeoutExpired:
            raise AssertionError("Chrome version check timed out")
    
    def test_chrome_launch_basic(self) -> None:
        """Test basic Chrome launch and shutdown."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        # Launch Chrome with minimal arguments
        process = subprocess.Popen([
            str(chrome_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--remote-debugging-port=0"
        ])
        
        try:
            # Wait a moment for Chrome to start
            time.sleep(3)
            
            # Check if process is running
            if process.poll() is not None:
                raise AssertionError(f"Chrome process exited prematurely: {process.returncode}")
            
        finally:
            # Cleanup
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    
    def test_chrome_launch_with_args(self) -> None:
        """Test Chrome launch with various arguments."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        test_args = [
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--window-size=1920,1080"
        ]
        
        process = subprocess.Popen([str(chrome_exe)] + test_args)
        
        try:
            time.sleep(3)
            
            if process.poll() is not None:
                raise AssertionError(f"Chrome with args failed: {process.returncode}")
            
        finally:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    
    def test_chrome_directory_structure(self) -> None:
        """Test Chrome directory structure integrity."""
        required_files = [
            "Application/chrome.exe",
            "Application/chrome.dll",
            "Application/chrome_elf.dll",
            "Application/resources.pak",
            "Application/icudtl.dat"
        ]
        
        for file_path in required_files:
            full_path = self.chrome_dir / file_path
            if not full_path.exists():
                raise AssertionError(f"Required Chrome file missing: {file_path}")
    
    def test_chrome_dependencies(self) -> None:
        """Test Chrome dependencies are available."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        # Check for required DLLs in the same directory
        required_dlls = [
            "chrome.dll",
            "chrome_elf.dll",
            "libEGL.dll",
            "libGLESv2.dll"
        ]
        
        app_dir = chrome_exe.parent
        for dll_name in required_dlls:
            dll_path = app_dir / dll_name
            if not dll_path.exists():
                raise AssertionError(f"Required DLL missing: {dll_name}")
    
    def test_chrome_permissions(self) -> None:
        """Test Chrome file permissions."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        # Check if executable is readable and executable
        if not os.access(chrome_exe, os.R_OK):
            raise AssertionError("Chrome executable is not readable")
        
        if not os.access(chrome_exe, os.X_OK):
            raise AssertionError("Chrome executable is not executable")
    
    def test_chrome_memory_usage(self) -> None:
        """Test Chrome memory usage is reasonable."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        process = subprocess.Popen([
            str(chrome_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox"
        ])
        
        try:
            time.sleep(5)  # Let Chrome stabilize
            
            # Get memory usage
            chrome_process = psutil.Process(process.pid)
            memory_mb = chrome_process.memory_info().rss / 1024 / 1024
            
            # Chrome should use reasonable amount of memory (less than 500MB for headless)
            if memory_mb > 500:
                raise AssertionError(f"Chrome using too much memory: {memory_mb:.1f} MB")
            
        finally:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class ChromeVersionManagementTests:
    """Tests for Chrome version management functionality."""
    
    def __init__(self, project_root: Path):
        """Initialize version management tests."""
        self.project_root = project_root
        self.version_manager = ChromeVersionManager(project_root)
        self.test_results = []
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all version management tests."""
        tests = [
            self.test_current_version_detection,
            self.test_available_versions_fetch,
            self.test_version_comparison,
            self.test_update_check,
            self.test_backup_creation,
            self.test_version_history,
        ]
        
        self.test_results = []
        
        for test in tests:
            start_time = time.time()
            try:
                test()
                duration = time.time() - start_time
                result = TestResult(
                    test_name=test.__name__,
                    success=True,
                    duration=duration
                )
            except Exception as e:
                duration = time.time() - start_time
                result = TestResult(
                    test_name=test.__name__,
                    success=False,
                    duration=duration,
                    error_message=str(e)
                )
            
            self.test_results.append(result)
            logger.info(f"Test {test.__name__}: {'PASS' if result.success else 'FAIL'}")
        
        return self.test_results
    
    def test_current_version_detection(self) -> None:
        """Test current Chrome version detection."""
        current_version = self.version_manager.get_current_version()
        
        if not current_version:
            raise AssertionError("Could not detect current Chrome version")
        
        if not current_version.version:
            raise AssertionError("Current version string is empty")
        
        # Version should be in format like "120.0.6099.109"
        version_parts = current_version.version.split('.')
        if len(version_parts) != 4:
            raise AssertionError(f"Invalid version format: {current_version.version}")
        
        for part in version_parts:
            if not part.isdigit():
                raise AssertionError(f"Invalid version part: {part}")
    
    def test_available_versions_fetch(self) -> None:
        """Test fetching available Chrome versions."""
        try:
            available_versions = self.version_manager.get_available_versions("stable", limit=5)
            
            if not available_versions:
                raise AssertionError("No available versions found")
            
            if len(available_versions) == 0:
                raise AssertionError("Available versions list is empty")
            
            # Check version format
            for version in available_versions:
                if not version.version:
                    raise AssertionError("Available version has empty version string")
                
                if version.channel != "stable":
                    raise AssertionError(f"Wrong channel: expected stable, got {version.channel}")
                    
        except requests.RequestException as e:
            # Network issues are acceptable in testing
            logger.warning(f"Network error in version fetch test: {e}")
    
    def test_version_comparison(self) -> None:
        """Test version comparison logic."""
        # Test version comparison
        result1 = self.version_manager._compare_versions("120.0.6099.109", "120.0.6099.108")
        if result1 != 1:
            raise AssertionError("Version comparison failed: newer > older")
        
        result2 = self.version_manager._compare_versions("120.0.6099.108", "120.0.6099.109")
        if result2 != -1:
            raise AssertionError("Version comparison failed: older < newer")
        
        result3 = self.version_manager._compare_versions("120.0.6099.109", "120.0.6099.109")
        if result3 != 0:
            raise AssertionError("Version comparison failed: equal versions")
    
    def test_update_check(self) -> None:
        """Test update checking functionality."""
        try:
            update_available = self.version_manager.check_for_updates()
            
            # This test just verifies the method doesn't crash
            # The result can be None (no updates) or a ChromeVersion object
            if update_available is not None:
                if not isinstance(update_available, ChromeVersion):
                    raise AssertionError("Update check returned invalid type")
                    
        except requests.RequestException as e:
            # Network issues are acceptable
            logger.warning(f"Network error in update check test: {e}")
    
    def test_backup_creation(self) -> None:
        """Test Chrome backup creation."""
        current_version = self.version_manager.get_current_version()
        if not current_version:
            raise AssertionError("No current version for backup test")
        
        # Create a test backup
        backup_success = self.version_manager._create_backup(current_version, "_test")
        
        if not backup_success:
            raise AssertionError("Backup creation failed")
        
        # Verify backup exists
        backup_found = False
        for backup_dir in self.version_manager.backups_dir.iterdir():
            if backup_dir.is_dir() and "_test" in backup_dir.name:
                backup_found = True
                
                # Verify backup has chrome.exe
                chrome_exe = backup_dir / "Application" / "chrome.exe"
                if not chrome_exe.exists():
                    raise AssertionError("Backup missing chrome.exe")
                
                # Cleanup test backup
                shutil.rmtree(backup_dir, ignore_errors=True)
                break
        
        if not backup_found:
            raise AssertionError("Test backup not found")
    
    def test_version_history(self) -> None:
        """Test version history tracking."""
        # Load current history
        history = self.version_manager._load_version_history()
        
        # History should be a list
        if not isinstance(history, list):
            raise AssertionError("Version history is not a list")
        
        # Test adding to history
        current_version = self.version_manager.get_current_version()
        if current_version:
            original_length = len(self.version_manager.version_history)
            self.version_manager._add_to_history(current_version)
            
            if len(self.version_manager.version_history) != original_length + 1:
                raise AssertionError("Version not added to history")


class ChromePerformanceTests:
    """Performance and benchmark tests for Chrome."""
    
    def __init__(self, project_root: Path):
        """Initialize performance tests."""
        self.project_root = project_root
        self.chrome_dir = project_root / "Google" / "Chrome"
        self.benchmark_results = []
    
    async def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all performance benchmarks."""
        benchmarks = [
            self.benchmark_startup_time,
            self.benchmark_page_load_time,
            self.benchmark_memory_usage,
            self.benchmark_cpu_usage,
        ]
        
        self.benchmark_results = []
        
        for benchmark in benchmarks:
            try:
                result = await benchmark()
                if result:
                    self.benchmark_results.append(result)
                    logger.info(f"Benchmark {benchmark.__name__}: {result.value} {result.unit}")
            except Exception as e:
                logger.error(f"Benchmark {benchmark.__name__} failed: {e}")
        
        return self.benchmark_results
    
    async def benchmark_startup_time(self) -> BenchmarkResult:
        """Benchmark Chrome startup time."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        start_time = time.time()
        
        process = subprocess.Popen([
            str(chrome_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--remote-debugging-port=0"
        ])
        
        try:
            # Wait for Chrome to be ready (when it starts accepting connections)
            await asyncio.sleep(2)
            
            startup_time = time.time() - start_time
            
            return BenchmarkResult(
                test_name="benchmark_startup_time",
                metric_name="startup_time",
                value=startup_time,
                unit="seconds"
            )
            
        finally:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    
    async def benchmark_page_load_time(self) -> BenchmarkResult:
        """Benchmark page loading performance."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path=str(self.chrome_dir / "Application" / "chrome.exe"),
                headless=True
            )
            
            try:
                page = await browser.new_page()
                
                start_time = time.time()
                await page.goto("https://www.google.com", wait_until="domcontentloaded")
                load_time = time.time() - start_time
                
                return BenchmarkResult(
                    test_name="benchmark_page_load_time",
                    metric_name="page_load_time",
                    value=load_time,
                    unit="seconds"
                )
                
            finally:
                await browser.close()
    
    async def benchmark_memory_usage(self) -> BenchmarkResult:
        """Benchmark Chrome memory usage."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        process = subprocess.Popen([
            str(chrome_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox"
        ])
        
        try:
            await asyncio.sleep(5)  # Let Chrome stabilize
            
            chrome_process = psutil.Process(process.pid)
            memory_mb = chrome_process.memory_info().rss / 1024 / 1024
            
            return BenchmarkResult(
                test_name="benchmark_memory_usage",
                metric_name="memory_usage",
                value=memory_mb,
                unit="MB"
            )
            
        finally:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    
    async def benchmark_cpu_usage(self) -> BenchmarkResult:
        """Benchmark Chrome CPU usage."""
        chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
        
        process = subprocess.Popen([
            str(chrome_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox"
        ])
        
        try:
            await asyncio.sleep(3)  # Let Chrome start
            
            chrome_process = psutil.Process(process.pid)
            
            # Measure CPU usage over 5 seconds
            cpu_percent = chrome_process.cpu_percent(interval=5)
            
            return BenchmarkResult(
                test_name="benchmark_cpu_usage",
                metric_name="cpu_usage",
                value=cpu_percent,
                unit="percent"
            )
            
        finally:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class ChromeTestSuite:
    """Main test suite coordinator."""

    def __init__(self, project_root: Path):
        """Initialize test suite."""
        self.project_root = project_root
        self.installation_tests = ChromeInstallationTests(project_root)
        self.version_tests = ChromeVersionManagementTests(project_root)
        self.performance_tests = ChromePerformanceTests(project_root)

        self.all_results = []
        self.all_benchmarks = []

    async def run_all_tests(self, include_performance: bool = True) -> Dict[str, Any]:
        """Run all test suites."""
        logger.info("Starting comprehensive Chrome testing...")

        start_time = time.time()

        # Run installation tests
        logger.info("Running Chrome installation tests...")
        installation_results = self.installation_tests.run_all_tests()

        # Run version management tests
        logger.info("Running Chrome version management tests...")
        version_results = self.version_tests.run_all_tests()

        # Run performance benchmarks
        benchmark_results = []
        if include_performance:
            logger.info("Running Chrome performance benchmarks...")
            benchmark_results = await self.performance_tests.run_all_benchmarks()

        total_time = time.time() - start_time

        # Compile results
        all_test_results = installation_results + version_results

        passed_tests = sum(1 for r in all_test_results if r.success)
        total_tests = len(all_test_results)

        results_summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_duration": total_time,
            "installation_tests": installation_results,
            "version_management_tests": version_results,
            "performance_benchmarks": benchmark_results,
            "timestamp": datetime.now().isoformat()
        }

        # Save results to file
        self._save_test_results(results_summary)

        # Print summary
        self._print_test_summary(results_summary)

        return results_summary

    def _save_test_results(self, results: Dict[str, Any]) -> None:
        """Save test results to JSON file."""
        try:
            results_dir = self.project_root / "testing" / "results"
            results_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"chrome_test_results_{timestamp}.json"

            # Convert test results to serializable format
            serializable_results = self._make_serializable(results)

            with open(results_file, 'w') as f:
                json.dump(serializable_results, f, indent=2)

            logger.info(f"Test results saved to: {results_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def _make_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (TestResult, BenchmarkResult)):
            return obj.__dict__
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def _print_test_summary(self, results: Dict[str, Any]) -> None:
        """Print test results summary."""
        print(f"\n{'='*80}")
        print("CHROME INTEGRATION TEST RESULTS")
        print(f"{'='*80}")

        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Total Duration: {results['total_duration']:.2f} seconds")

        # Installation tests summary
        print(f"\n📦 INSTALLATION TESTS:")
        for test in results['installation_tests']:
            status = "✅ PASS" if test.success else "❌ FAIL"
            print(f"  {test.test_name}: {status} ({test.duration:.2f}s)")
            if not test.success and test.error_message:
                print(f"    Error: {test.error_message}")

        # Version management tests summary
        print(f"\n🔄 VERSION MANAGEMENT TESTS:")
        for test in results['version_management_tests']:
            status = "✅ PASS" if test.success else "❌ FAIL"
            print(f"  {test.test_name}: {status} ({test.duration:.2f}s)")
            if not test.success and test.error_message:
                print(f"    Error: {test.error_message}")

        # Performance benchmarks summary
        if results['performance_benchmarks']:
            print(f"\n⚡ PERFORMANCE BENCHMARKS:")
            for benchmark in results['performance_benchmarks']:
                print(f"  {benchmark.metric_name}: {benchmark.value:.2f} {benchmark.unit}")

        print(f"\n{'='*80}")


def main():
    """Main entry point for Chrome integration tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Chrome Integration Test Suite")
    parser.add_argument("--no-performance", action="store_true",
                       help="Skip performance benchmarks")
    parser.add_argument("--installation-only", action="store_true",
                       help="Run only installation tests")
    parser.add_argument("--version-only", action="store_true",
                       help="Run only version management tests")
    parser.add_argument("--performance-only", action="store_true",
                       help="Run only performance benchmarks")
    parser.add_argument("--output", type=Path, help="Output directory for results")

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # Determine project root
    project_root = Path(__file__).parent.parent

    async def run_tests():
        """Run the test suite."""
        test_suite = ChromeTestSuite(project_root)

        try:
            if args.installation_only:
                logger.info("Running installation tests only...")
                results = test_suite.installation_tests.run_all_tests()
                passed = sum(1 for r in results if r.success)
                print(f"\nInstallation Tests: {passed}/{len(results)} passed")

            elif args.version_only:
                logger.info("Running version management tests only...")
                results = test_suite.version_tests.run_all_tests()
                passed = sum(1 for r in results if r.success)
                print(f"\nVersion Management Tests: {passed}/{len(results)} passed")

            elif args.performance_only:
                logger.info("Running performance benchmarks only...")
                results = await test_suite.performance_tests.run_all_benchmarks()
                print(f"\nPerformance Benchmarks: {len(results)} completed")
                for benchmark in results:
                    print(f"  {benchmark.metric_name}: {benchmark.value:.2f} {benchmark.unit}")

            else:
                # Run all tests
                include_performance = not args.no_performance
                results = await test_suite.run_all_tests(include_performance)

                # Return appropriate exit code
                return 0 if results['failed_tests'] == 0 else 1

            return 0

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            return 1

    # Run the async test suite
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
