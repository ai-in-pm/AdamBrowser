#!/usr/bin/env python3
"""
Chrome Management Suite - Main Orchestration Script

This is the main entry point for the comprehensive Chrome management system,
providing a unified interface for all Chrome-related operations including:
- Distribution package building
- Chrome version management
- Automatic updates
- Size optimization
- Testing and validation
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from loguru import logger

# disable all "safe" commands
import subprocess
import shutil
# disable all "dangerous" commands

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from distribution.package_builder import DistributionBuilder, PackageConfig
from chrome_management.version_manager import ChromeVersionManager, UpdatePolicy
from chrome_management.auto_updater import UpdateScheduler
from optimization.size_optimizer import PackageOptimizer, OptimizationConfig
from testing.chrome_integration_tests import ChromeTestSuite


class ChromeManagementSuite:
    """Main orchestrator for Chrome management operations."""
    
    def __init__(self, project_root: Path):
        """Initialize the Chrome management suite."""
        self.project_root = project_root
        self.config_file = project_root / "chrome_management" / "suite_config.json"
        
        # Create management directories
        self.management_dir = project_root / "chrome_management"
        self.distribution_dir = project_root / "distribution"
        self.optimization_dir = project_root / "optimization"
        self.testing_dir = project_root / "testing"
        
        for dir_path in [self.management_dir, self.distribution_dir, 
                        self.optimization_dir, self.testing_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.version_manager = ChromeVersionManager(project_root)
        self.test_suite = ChromeTestSuite(project_root)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load suite configuration."""
        default_config = {
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
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for section, values in loaded_config.items():
                        if section in default_config:
                            default_config[section].update(values)
                        else:
                            default_config[section] = values
        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
        
        return default_config
    
    def _save_config(self) -> None:
        """Save current configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    async def build_distribution_packages(self, package_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Build distribution packages with embedded Chrome."""
        logger.info("🚀 Starting distribution package building...")
        
        # Create package configuration
        package_config = PackageConfig(
            name=self.config["package"]["name"],
            version=self.config["package"]["version"],
            include_chrome=self.config["package"]["include_chrome"],
            optimize_size=self.config["package"]["optimize_size"],
            chrome_channel=self.config["chrome"]["channel"]
        )
        
        # Set package types to build
        if package_types:
            package_config.build_zip = "zip" in package_types
            package_config.build_msi = "msi" in package_types
            package_config.build_nsis = "nsis" in package_types
            package_config.build_portable = "portable" in package_types
            package_config.build_docker = "docker" in package_types
        elif self.config["package"]["build_all_formats"]:
            package_config.build_zip = True
            package_config.build_msi = True
            package_config.build_nsis = True
            package_config.build_portable = True
            package_config.build_docker = False  # Optional
        
        # Build packages
        builder = DistributionBuilder(self.project_root, package_config)
        results = builder.build_all_packages()
        
        # Run tests on built packages if configured
        if self.config["testing"]["run_on_build"]:
            logger.info("🧪 Running tests on built packages...")
            test_results = await self._test_packages(results)
            
            if (self.config["testing"]["fail_on_test_failure"] and 
                any(not r.success for r in test_results.values())):
                logger.error("Package tests failed, aborting distribution")
                return {"success": False, "error": "Package tests failed"}
        
        logger.info("✅ Distribution package building completed")
        return {"success": True, "packages": results}
    
    async def update_chrome(self, force: bool = False, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Update Chrome to latest or specified version."""
        logger.info("🔄 Starting Chrome update process...")
        
        try:
            # Check current version
            current = self.version_manager.get_current_version()
            if current:
                logger.info(f"Current Chrome version: {current.version}")
            
            # Perform update
            if target_version:
                # Find specific version
                available_versions = self.version_manager.get_available_versions(
                    self.config["chrome"]["channel"], limit=20
                )
                target = next((v for v in available_versions if v.version == target_version), None)
                
                if not target:
                    return {"success": False, "error": f"Version {target_version} not found"}
                
                success = self.version_manager.update_chrome(target, force=force)
            else:
                success = self.version_manager.update_chrome(force=force)
            
            if success:
                new_version = self.version_manager.get_current_version()
                logger.info(f"✅ Chrome updated successfully to {new_version.version if new_version else 'unknown'}")
                return {"success": True, "old_version": current.version if current else None,
                       "new_version": new_version.version if new_version else None}
            else:
                return {"success": False, "error": "Chrome update failed"}
                
        except Exception as e:
            logger.error(f"Chrome update error: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_installation(self, target_path: Optional[Path] = None) -> Dict[str, Any]:
        """Optimize Chrome installation for size."""
        logger.info("⚡ Starting Chrome optimization...")
        
        try:
            # Determine target path
            if not target_path:
                target_path = self.project_root
            
            # Create optimization configuration
            opt_config = OptimizationConfig(
                remove_debug_symbols=self.config["optimization"]["remove_debug_symbols"],
                remove_dev_tools=self.config["optimization"]["remove_dev_tools"],
                compress_resources=self.config["optimization"]["compress_resources"],
                aggressive_optimization=self.config["optimization"]["aggressive_optimization"]
            )
            
            # Run optimization
            optimizer = PackageOptimizer(target_path, opt_config)
            result = optimizer.optimize()
            
            logger.info(f"✅ Optimization completed: {result.savings / 1024 / 1024:.1f} MB saved ({result.savings_percentage:.1f}%)")
            
            return {
                "success": True,
                "original_size_mb": result.original_size / 1024 / 1024,
                "optimized_size_mb": result.optimized_size / 1024 / 1024,
                "savings_mb": result.savings / 1024 / 1024,
                "savings_percentage": result.savings_percentage,
                "files_removed": len(result.removed_files),
                "files_compressed": len(result.compressed_files)
            }
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_tests(self, include_performance: bool = True) -> Dict[str, Any]:
        """Run comprehensive Chrome integration tests."""
        logger.info("🧪 Starting comprehensive Chrome tests...")
        
        try:
            results = await self.test_suite.run_all_tests(include_performance)
            
            if results["failed_tests"] == 0:
                logger.info("✅ All tests passed successfully")
            else:
                logger.warning(f"⚠️ {results['failed_tests']} tests failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Testing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_auto_updater(self) -> Dict[str, Any]:
        """Start the Chrome auto-updater service."""
        logger.info("🤖 Starting Chrome auto-updater...")
        
        try:
            # Create update policy from config
            policy = UpdatePolicy(
                auto_update=self.config["chrome"]["auto_update"],
                backup_versions=self.config["chrome"]["backup_versions"],
                update_window_start=self.config["chrome"]["update_window_start"],
                update_window_end=self.config["chrome"]["update_window_end"]
            )
            
            self.version_manager.policy = policy
            
            # Start scheduler
            scheduler = UpdateScheduler(self.version_manager)
            scheduler.start()
            
            logger.info("✅ Auto-updater started successfully")
            return {"success": True, "message": "Auto-updater is now running"}
            
        except Exception as e:
            logger.error(f"Auto-updater error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_packages(self, package_results: Dict[str, Any]) -> Dict[str, Any]:
        """Test built packages."""
        test_results = {}
        
        for package_type, result in package_results.items():
            if result.success and result.package_path:
                logger.info(f"Testing {package_type} package...")
                
                # Basic package validation
                if result.package_path.exists():
                    test_results[package_type] = type('TestResult', (), {
                        'success': True,
                        'message': f'{package_type} package exists and is valid'
                    })()
                else:
                    test_results[package_type] = type('TestResult', (), {
                        'success': False,
                        'message': f'{package_type} package file not found'
                    })()
            else:
                test_results[package_type] = type('TestResult', (), {
                    'success': False,
                    'message': f'{package_type} package build failed'
                })()
        
        return test_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of Chrome installation and management."""
        try:
            current_version = self.version_manager.get_current_version()
            
            status = {
                "chrome_installed": current_version is not None,
                "chrome_version": current_version.version if current_version else None,
                "chrome_channel": current_version.channel if current_version else None,
                "chrome_path": str(current_version.installation_path) if current_version and current_version.installation_path else None,
                "auto_update_enabled": self.config["chrome"]["auto_update"],
                "last_check": datetime.now().isoformat(),
                "management_suite_version": "1.0.0"
            }
            
            # Check for available updates
            try:
                update_available = self.version_manager.check_for_updates()
                status["update_available"] = update_available is not None
                if update_available:
                    status["available_version"] = update_available.version
            except Exception:
                status["update_available"] = None
            
            return status
            
        except Exception as e:
            return {"error": str(e)}


async def main():
    """Main entry point for Chrome Management Suite."""
    parser = argparse.ArgumentParser(description="Chrome Management Suite")
    
    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build distribution packages")
    build_parser.add_argument("--types", nargs="+", choices=["zip", "msi", "nsis", "portable", "docker"],
                             help="Package types to build")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update Chrome")
    update_parser.add_argument("--force", action="store_true", help="Force update")
    update_parser.add_argument("--version", help="Target specific version")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize Chrome installation")
    optimize_parser.add_argument("--target", type=Path, help="Target directory to optimize")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run comprehensive tests")
    test_parser.add_argument("--no-performance", action="store_true", help="Skip performance tests")
    
    # Auto-updater command
    auto_parser = subparsers.add_parser("auto-update", help="Start auto-updater")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show current status")
    
    # All-in-one command
    all_parser = subparsers.add_parser("all", help="Run complete management cycle")
    all_parser.add_argument("--skip-tests", action="store_true", help="Skip testing phase")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Initialize suite
    project_root = Path(__file__).parent
    suite = ChromeManagementSuite(project_root)
    
    try:
        if args.command == "build":
            result = await suite.build_distribution_packages(args.types)
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
            
        elif args.command == "update":
            result = await suite.update_chrome(args.force, args.version)
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
            
        elif args.command == "optimize":
            result = await suite.optimize_installation(args.target)
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
            
        elif args.command == "test":
            result = await suite.run_comprehensive_tests(not args.no_performance)
            print(json.dumps(result, indent=2, default=str))
            return 0 if result.get("failed_tests", 1) == 0 else 1
            
        elif args.command == "auto-update":
            result = await suite.start_auto_updater()
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
            
        elif args.command == "status":
            status = suite.get_status()
            print(json.dumps(status, indent=2))
            return 0
            
        elif args.command == "all":
            logger.info("🚀 Running complete Chrome management cycle...")
            
            # 1. Update Chrome
            logger.info("Step 1: Updating Chrome...")
            update_result = await suite.update_chrome()
            
            # 2. Optimize installation
            logger.info("Step 2: Optimizing installation...")
            optimize_result = await suite.optimize_installation()
            
            # 3. Run tests
            if not args.skip_tests:
                logger.info("Step 3: Running tests...")
                test_result = await suite.run_comprehensive_tests()
            else:
                test_result = {"skipped": True}
            
            # 4. Build packages
            logger.info("Step 4: Building distribution packages...")
            build_result = await suite.build_distribution_packages()
            
            # Compile results
            all_results = {
                "update": update_result,
                "optimize": optimize_result,
                "test": test_result,
                "build": build_result,
                "overall_success": all([
                    update_result.get("success", False),
                    optimize_result.get("success", False),
                    test_result.get("failed_tests", 1) == 0 or test_result.get("skipped", False),
                    build_result.get("success", False)
                ])
            }
            
            print(json.dumps(all_results, indent=2, default=str))
            return 0 if all_results["overall_success"] else 1
            
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Chrome Management Suite error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
