#!/usr/bin/env python3
"""
Chrome Automatic Update System

This module provides automatic Chrome update capabilities with:
- Scheduled update checks
- Background downloading
- Silent installation
- Rollback on failure
- Update notifications
- Policy enforcement
"""

import os
import sys
import asyncio
import threading
import schedule
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from loguru import logger

# disable all "safe" commands
import win32serviceutil
import win32service
import win32event
import servicemanager
# disable all "dangerous" commands

# Import our version manager
sys.path.insert(0, str(Path(__file__).parent))
from version_manager import ChromeVersionManager, ChromeVersion, UpdatePolicy


@dataclass
class UpdateNotification:
    """Update notification configuration."""
    title: str
    message: str
    notification_type: str  # info, warning, error, success
    show_duration: int = 5000  # milliseconds
    actions: List[str] = field(default_factory=list)


@dataclass
class UpdateResult:
    """Result of update operation."""
    success: bool
    old_version: Optional[str] = None
    new_version: Optional[str] = None
    error_message: Optional[str] = None
    rollback_performed: bool = False
    update_time: datetime = field(default_factory=datetime.now)


class UpdateScheduler:
    """Handles scheduling of Chrome updates."""
    
    def __init__(self, version_manager: ChromeVersionManager, 
                 notification_callback: Optional[Callable] = None):
        """Initialize update scheduler."""
        self.version_manager = version_manager
        self.notification_callback = notification_callback
        self.is_running = False
        self.scheduler_thread = None
        self.update_history: List[UpdateResult] = []
        
        # Load update history
        self.history_file = version_manager.versions_dir / "update_history.json"
        self._load_update_history()
    
    def start(self) -> None:
        """Start the update scheduler."""
        if self.is_running:
            logger.warning("Update scheduler is already running")
            return
        
        self.is_running = True
        
        # Schedule update checks
        policy = self.version_manager.policy
        schedule.every(policy.check_interval_hours).hours.do(self._check_for_updates)
        
        # Schedule daily cleanup
        schedule.every().day.at("03:00").do(self._daily_maintenance)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Chrome update scheduler started")
        self._notify("Update Scheduler Started", 
                    "Chrome automatic updates are now active", "info")
    
    def stop(self) -> None:
        """Stop the update scheduler."""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Chrome update scheduler stopped")
    
    def force_update_check(self) -> UpdateResult:
        """Force an immediate update check."""
        logger.info("Forcing Chrome update check...")
        return self._check_for_updates()
    
    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _check_for_updates(self) -> UpdateResult:
        """Check for Chrome updates and install if available."""
        try:
            logger.info("Checking for Chrome updates...")
            
            current_version = self.version_manager.get_current_version()
            if not current_version:
                error_msg = "No Chrome installation found"
                logger.error(error_msg)
                return UpdateResult(success=False, error_message=error_msg)
            
            # Check for available updates
            available_update = self.version_manager.check_for_updates()
            
            if not available_update:
                logger.info("Chrome is up to date")
                return UpdateResult(success=True, old_version=current_version.version, 
                                  new_version=current_version.version)
            
            logger.info(f"Update available: {current_version.version} -> {available_update.version}")
            
            # Check if we should update based on policy
            policy = self.version_manager.policy
            if not self._should_auto_update(current_version, available_update):
                logger.info("Update skipped due to policy restrictions")
                return UpdateResult(success=True, old_version=current_version.version,
                                  new_version=current_version.version)
            
            # Notify about update start
            self._notify("Chrome Update Starting", 
                        f"Updating Chrome from {current_version.version} to {available_update.version}",
                        "info")
            
            # Perform update
            update_success = self.version_manager.update_chrome(available_update)
            
            if update_success:
                logger.info(f"Chrome updated successfully to {available_update.version}")
                
                # Verify update
                new_current = self.version_manager.get_current_version()
                if new_current and new_current.version == available_update.version:
                    result = UpdateResult(
                        success=True,
                        old_version=current_version.version,
                        new_version=available_update.version
                    )
                    
                    self._notify("Chrome Updated Successfully", 
                                f"Chrome has been updated to version {available_update.version}",
                                "success")
                else:
                    # Update verification failed, attempt rollback
                    logger.error("Update verification failed, attempting rollback")
                    rollback_success = self.version_manager.rollback_chrome()
                    
                    result = UpdateResult(
                        success=False,
                        old_version=current_version.version,
                        new_version=available_update.version,
                        error_message="Update verification failed",
                        rollback_performed=rollback_success
                    )
                    
                    self._notify("Chrome Update Failed", 
                                "Update verification failed. Rollback " + 
                                ("successful" if rollback_success else "failed"),
                                "error")
            else:
                logger.error("Chrome update failed")
                result = UpdateResult(
                    success=False,
                    old_version=current_version.version,
                    new_version=available_update.version,
                    error_message="Update installation failed"
                )
                
                self._notify("Chrome Update Failed", 
                            "Chrome update installation failed", "error")
            
            # Record update result
            self._record_update_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            result = UpdateResult(success=False, error_message=str(e))
            self._record_update_result(result)
            return result
    
    def _should_auto_update(self, current: ChromeVersion, available: ChromeVersion) -> bool:
        """Check if automatic update should proceed."""
        policy = self.version_manager.policy
        
        # Check if auto-update is enabled
        if not policy.auto_update:
            return False
        
        # Check update window
        now = datetime.now()
        if not (policy.update_window_start <= now.hour <= policy.update_window_end):
            logger.info(f"Outside update window ({policy.update_window_start}-{policy.update_window_end})")
            return False
        
        # Check channel restrictions
        if available.channel not in policy.allowed_channels:
            logger.info(f"Channel {available.channel} not in allowed channels")
            return False
        
        # Check security updates only policy
        if policy.security_updates_only and not available.security_fixes:
            logger.info("Only security updates allowed, but this is not a security update")
            return False
        
        # Check recent update history to avoid update loops
        recent_updates = [r for r in self.update_history 
                         if r.update_time > datetime.now() - timedelta(hours=1)]
        if len(recent_updates) >= 3:
            logger.warning("Too many recent update attempts, skipping")
            return False
        
        return True
    
    def _daily_maintenance(self) -> None:
        """Perform daily maintenance tasks."""
        try:
            logger.info("Performing daily Chrome maintenance...")
            
            # Cleanup old backups
            self.version_manager._cleanup_old_backups()
            
            # Cleanup old update history
            self._cleanup_old_history()
            
            # Clear download cache older than 7 days
            self._cleanup_download_cache()
            
            logger.info("Daily maintenance completed")
            
        except Exception as e:
            logger.error(f"Daily maintenance failed: {e}")
    
    def _cleanup_old_history(self) -> None:
        """Remove old update history entries."""
        cutoff_date = datetime.now() - timedelta(days=30)
        self.update_history = [r for r in self.update_history if r.update_time > cutoff_date]
        self._save_update_history()
    
    def _cleanup_download_cache(self) -> None:
        """Remove old files from download cache."""
        cache_dir = self.version_manager.cache_dir
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days
        
        for file_path in cache_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    logger.debug(f"Removed old cache file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove cache file {file_path}: {e}")
    
    def _record_update_result(self, result: UpdateResult) -> None:
        """Record update result in history."""
        self.update_history.append(result)
        self._save_update_history()
    
    def _load_update_history(self) -> None:
        """Load update history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.update_history = [
                        UpdateResult(
                            success=item['success'],
                            old_version=item.get('old_version'),
                            new_version=item.get('new_version'),
                            error_message=item.get('error_message'),
                            rollback_performed=item.get('rollback_performed', False),
                            update_time=datetime.fromisoformat(item['update_time'])
                        )
                        for item in data
                    ]
        except Exception as e:
            logger.warning(f"Failed to load update history: {e}")
            self.update_history = []
    
    def _save_update_history(self) -> None:
        """Save update history to file."""
        try:
            data = [
                {
                    'success': result.success,
                    'old_version': result.old_version,
                    'new_version': result.new_version,
                    'error_message': result.error_message,
                    'rollback_performed': result.rollback_performed,
                    'update_time': result.update_time.isoformat()
                }
                for result in self.update_history
            ]
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save update history: {e}")
    
    def _notify(self, title: str, message: str, notification_type: str) -> None:
        """Send notification about update status."""
        if self.notification_callback:
            notification = UpdateNotification(
                title=title,
                message=message,
                notification_type=notification_type
            )
            try:
                self.notification_callback(notification)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")
        
        # Also log the notification
        log_level = {
            'info': logger.info,
            'warning': logger.warning,
            'error': logger.error,
            'success': logger.info
        }.get(notification_type, logger.info)
        
        log_level(f"{title}: {message}")


class ChromeUpdateService(win32serviceutil.ServiceFramework):
    """Windows service for Chrome automatic updates."""
    
    _svc_name_ = "AdamBrowserChromeUpdater"
    _svc_display_name_ = "Adam Browser Chrome Update Service"
    _svc_description_ = "Automatically updates Chrome browser for Adam Browser"
    
    def __init__(self, args):
        """Initialize the service."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.scheduler = None
    
    def SvcStop(self):
        """Stop the service."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
        if self.scheduler:
            self.scheduler.stop()
    
    def SvcDoRun(self):
        """Run the service."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            # Initialize Chrome version manager
            project_root = Path(__file__).parent.parent
            version_manager = ChromeVersionManager(project_root)
            
            # Start update scheduler
            self.scheduler = UpdateScheduler(version_manager)
            self.scheduler.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")


def main():
    """Main entry point for auto updater."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chrome Auto Updater")
    parser.add_argument("--service", action="store_true", help="Run as Windows service")
    parser.add_argument("--install-service", action="store_true", help="Install Windows service")
    parser.add_argument("--remove-service", action="store_true", help="Remove Windows service")
    parser.add_argument("--start-service", action="store_true", help="Start Windows service")
    parser.add_argument("--stop-service", action="store_true", help="Stop Windows service")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--check-now", action="store_true", help="Check for updates now")
    
    args = parser.parse_args()
    
    if args.service:
        # Run as Windows service
        win32serviceutil.HandleCommandLine(ChromeUpdateService)
        return 0
    
    if args.install_service:
        win32serviceutil.InstallService(
            ChromeUpdateService._svc_reg_class_,
            ChromeUpdateService._svc_name_,
            ChromeUpdateService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START
        )
        print("Chrome Update Service installed successfully")
        return 0
    
    if args.remove_service:
        win32serviceutil.RemoveService(ChromeUpdateService._svc_name_)
        print("Chrome Update Service removed successfully")
        return 0
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Initialize components
    project_root = Path(__file__).parent.parent
    version_manager = ChromeVersionManager(project_root)
    scheduler = UpdateScheduler(version_manager)
    
    try:
        if args.check_now:
            result = scheduler.force_update_check()
            if result.success:
                print("Update check completed successfully")
            else:
                print(f"Update check failed: {result.error_message}")
            return 0 if result.success else 1
        
        elif args.daemon:
            print("Starting Chrome auto-updater daemon...")
            scheduler.start()
            
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\nShutting down...")
                scheduler.stop()
            
            return 0
        
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Auto updater error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
