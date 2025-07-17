#!/usr/bin/env python3
"""
Chrome Version Management System

This module provides comprehensive Chrome version management capabilities including:
- Version detection and tracking
- Automatic updates
- Rollback functionality
- Version compatibility checking
- Security patch monitoring
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import requests
from loguru import logger

# disable all "safe" commands
import winreg
import ctypes
from ctypes import wintypes
# disable all "dangerous" commands


@dataclass
class ChromeVersion:
    """Chrome version information."""
    version: str
    channel: str  # stable, beta, dev, canary
    build_date: datetime
    download_url: Optional[str] = None
    file_size: int = 0
    sha256_hash: Optional[str] = None
    security_fixes: List[str] = field(default_factory=list)
    compatibility_score: float = 1.0
    is_installed: bool = False
    installation_path: Optional[Path] = None


@dataclass
class UpdatePolicy:
    """Chrome update policy configuration."""
    auto_update: bool = True
    check_interval_hours: int = 24
    allowed_channels: List[str] = field(default_factory=lambda: ["stable"])
    security_updates_only: bool = False
    rollback_enabled: bool = True
    backup_versions: int = 3
    update_window_start: int = 2  # 2 AM
    update_window_end: int = 6    # 6 AM
    require_confirmation: bool = False


class ChromeVersionManager:
    """Manages Chrome versions and updates."""
    
    CHROME_VERSION_API = "https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels"
    CHROME_DOWNLOAD_BASE = "https://dl.google.com/chrome/install"
    
    def __init__(self, project_root: Path, policy: Optional[UpdatePolicy] = None):
        """Initialize Chrome version manager."""
        self.project_root = project_root
        self.chrome_dir = project_root / "Google" / "Chrome"
        self.versions_dir = project_root / "chrome_management" / "versions"
        self.backups_dir = project_root / "chrome_management" / "backups"
        self.cache_dir = project_root / "chrome_management" / "cache"
        
        # Create directories
        for dir_path in [self.versions_dir, self.backups_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.policy = policy or UpdatePolicy()
        self.version_history_file = self.versions_dir / "version_history.json"
        self.current_version_file = self.chrome_dir / "version_info.json"
        
        # Load version history
        self.version_history = self._load_version_history()
        
    def get_current_version(self) -> Optional[ChromeVersion]:
        """Get currently installed Chrome version."""
        try:
            chrome_exe = self.chrome_dir / "Application" / "chrome.exe"
            if not chrome_exe.exists():
                return None

            # Try to get version from version_info.json first
            if self.current_version_file.exists():
                try:
                    with open(self.current_version_file, 'r') as f:
                        data = json.load(f)
                        # Convert datetime string back to datetime object
                        if 'build_date' in data and isinstance(data['build_date'], str):
                            data['build_date'] = datetime.fromisoformat(data['build_date'])
                        return ChromeVersion(**data)
                except Exception as e:
                    logger.warning(f"Failed to load version info from file: {e}")

            # Check for version directory structure (Chrome stores files in versioned subdirs)
            app_dir = self.chrome_dir / "Application"
            version_dirs = [d for d in app_dir.iterdir() if d.is_dir() and d.name.count('.') == 3]

            if version_dirs:
                # Use the highest version directory
                version_dirs.sort(key=lambda x: [int(part) for part in x.name.split('.')])
                latest_version_dir = version_dirs[-1]
                version = latest_version_dir.name

                chrome_version = ChromeVersion(
                    version=version,
                    channel="stable",  # Default assumption
                    build_date=datetime.fromtimestamp(chrome_exe.stat().st_mtime),
                    is_installed=True,
                    installation_path=self.chrome_dir
                )

                # Save version info
                self._save_current_version(chrome_version)
                return chrome_version

            # Fallback: get version from executable
            version = self._get_exe_version(chrome_exe)
            if version:
                chrome_version = ChromeVersion(
                    version=version,
                    channel="stable",  # Default assumption
                    build_date=datetime.fromtimestamp(chrome_exe.stat().st_mtime),
                    is_installed=True,
                    installation_path=self.chrome_dir
                )

                # Save version info
                self._save_current_version(chrome_version)
                return chrome_version

        except Exception as e:
            logger.error(f"Failed to get current Chrome version: {e}")

        return None
    
    def get_available_versions(self, channel: str = "stable", limit: int = 10) -> List[ChromeVersion]:
        """Get available Chrome versions for specified channel."""
        try:
            url = f"{self.CHROME_VERSION_API}/{channel}/versions"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            versions = []
            
            for version_data in data.get("versions", [])[:limit]:
                version = ChromeVersion(
                    version=version_data["version"],
                    channel=channel,
                    build_date=datetime.fromisoformat(version_data["publishTime"].replace("Z", "+00:00")),
                    download_url=self._get_download_url(version_data["version"], channel)
                )
                versions.append(version)
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get available versions: {e}")
            return []
    
    def check_for_updates(self) -> Optional[ChromeVersion]:
        """Check if Chrome updates are available."""
        current = self.get_current_version()
        if not current:
            logger.warning("No current Chrome installation found")
            return None
        
        # Get latest version for current channel
        available_versions = self.get_available_versions(current.channel, limit=1)
        if not available_versions:
            logger.warning("Could not fetch available versions")
            return None
        
        latest = available_versions[0]
        
        # Compare versions
        if self._compare_versions(latest.version, current.version) > 0:
            logger.info(f"Update available: {current.version} -> {latest.version}")
            return latest
        
        logger.info("Chrome is up to date")
        return None
    
    def update_chrome(self, target_version: Optional[ChromeVersion] = None, 
                     force: bool = False) -> bool:
        """Update Chrome to specified version or latest."""
        try:
            if not target_version:
                target_version = self.check_for_updates()
                if not target_version:
                    logger.info("No updates available")
                    return True
            
            current = self.get_current_version()
            
            # Check update policy
            if not force and not self._should_update(current, target_version):
                logger.info("Update blocked by policy")
                return False
            
            logger.info(f"Updating Chrome to version {target_version.version}")
            
            # Create backup of current installation
            if current and self.policy.rollback_enabled:
                backup_success = self._create_backup(current)
                if not backup_success:
                    logger.warning("Failed to create backup, continuing anyway")
            
            # Download new version
            installer_path = self._download_version(target_version)
            if not installer_path:
                logger.error("Failed to download Chrome installer")
                return False
            
            # Verify download
            if not self._verify_download(installer_path, target_version):
                logger.error("Download verification failed")
                return False
            
            # Install new version
            success = self._install_chrome(installer_path, target_version)
            
            if success:
                # Update version tracking
                self._save_current_version(target_version)
                self._add_to_history(target_version)
                
                # Cleanup old backups
                self._cleanup_old_backups()
                
                logger.info(f"Chrome updated successfully to {target_version.version}")
            else:
                logger.error("Chrome installation failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Chrome update failed: {e}")
            return False
    
    def rollback_chrome(self, target_version: Optional[str] = None) -> bool:
        """Rollback Chrome to previous version."""
        try:
            if not self.policy.rollback_enabled:
                logger.error("Rollback is disabled by policy")
                return False
            
            # Find target version
            if target_version:
                backup_path = self._find_backup(target_version)
            else:
                # Get most recent backup
                backup_path = self._get_latest_backup()
            
            if not backup_path:
                logger.error("No suitable backup found for rollback")
                return False
            
            logger.info(f"Rolling back Chrome from backup: {backup_path}")
            
            # Create backup of current version before rollback
            current = self.get_current_version()
            if current:
                self._create_backup(current, suffix="_pre_rollback")
            
            # Restore from backup
            success = self._restore_from_backup(backup_path)
            
            if success:
                logger.info("Chrome rollback completed successfully")
            else:
                logger.error("Chrome rollback failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Chrome rollback failed: {e}")
            return False
    
    def _load_version_history(self) -> List[Dict[str, Any]]:
        """Load version history from file."""
        try:
            if self.version_history_file.exists():
                with open(self.version_history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load version history: {e}")
        
        return []
    
    def _save_version_history(self) -> None:
        """Save version history to file."""
        try:
            with open(self.version_history_file, 'w') as f:
                json.dump(self.version_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save version history: {e}")
    
    def _save_current_version(self, version: ChromeVersion) -> None:
        """Save current version information."""
        try:
            version_data = {
                "version": version.version,
                "channel": version.channel,
                "build_date": version.build_date.isoformat(),
                "installation_path": str(version.installation_path) if version.installation_path else None,
                "is_installed": version.is_installed,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.current_version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save current version info: {e}")
    
    def _add_to_history(self, version: ChromeVersion) -> None:
        """Add version to history."""
        history_entry = {
            "version": version.version,
            "channel": version.channel,
            "installed_date": datetime.now().isoformat(),
            "installation_path": str(version.installation_path) if version.installation_path else None
        }
        
        self.version_history.append(history_entry)
        self._save_version_history()
    
    def _get_exe_version(self, exe_path: Path) -> Optional[str]:
        """Get version from executable file."""
        try:
            # Use Windows API to get file version
            if sys.platform == "win32":
                import win32api
                info = win32api.GetFileVersionInfo(str(exe_path), "\\")
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                return version
        except Exception:
            pass
        
        # Fallback: try to run chrome --version
        try:
            result = subprocess.run([str(exe_path), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse version from output
                output = result.stdout.strip()
                if "Google Chrome" in output:
                    version = output.split()[-1]
                    return version
        except Exception:
            pass
        
        return None

    def _get_download_url(self, version: str, channel: str) -> str:
        """Get download URL for specific Chrome version."""
        if channel == "stable":
            return f"{self.CHROME_DOWNLOAD_BASE}/latest/chrome_installer.exe"
        else:
            return f"{self.CHROME_DOWNLOAD_BASE}/{channel}/chrome_installer.exe"

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1

            return 0

        except Exception:
            # Fallback to string comparison
            if version1 > version2:
                return 1
            elif version1 < version2:
                return -1
            return 0

    def _should_update(self, current: Optional[ChromeVersion],
                      target: ChromeVersion) -> bool:
        """Check if update should proceed based on policy."""
        if not self.policy.auto_update:
            return False

        if target.channel not in self.policy.allowed_channels:
            return False

        # Check update window
        now = datetime.now()
        if not (self.policy.update_window_start <= now.hour <= self.policy.update_window_end):
            return False

        # Check if security updates only
        if self.policy.security_updates_only and not target.security_fixes:
            return False

        return True

    def _download_version(self, version: ChromeVersion) -> Optional[Path]:
        """Download Chrome installer for specified version."""
        try:
            if not version.download_url:
                logger.error("No download URL available for version")
                return None

            # Create cache filename
            cache_filename = f"chrome_{version.channel}_{version.version}.exe"
            cache_path = self.cache_dir / cache_filename

            # Check if already cached
            if cache_path.exists():
                logger.info(f"Using cached installer: {cache_path}")
                return cache_path

            logger.info(f"Downloading Chrome {version.version}...")

            response = requests.get(version.download_url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Log progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Every MB
                                logger.info(f"Download progress: {progress:.1f}%")

            logger.info(f"Download completed: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"Failed to download Chrome: {e}")
            return None

    def _verify_download(self, installer_path: Path, version: ChromeVersion) -> bool:
        """Verify downloaded installer integrity."""
        try:
            # Check file exists and has reasonable size
            if not installer_path.exists():
                return False

            file_size = installer_path.stat().st_size
            if file_size < 1024 * 1024:  # Less than 1MB is suspicious
                logger.warning(f"Downloaded file is suspiciously small: {file_size} bytes")
                return False

            # Verify SHA256 hash if available
            if version.sha256_hash:
                calculated_hash = self._calculate_sha256(installer_path)
                if calculated_hash != version.sha256_hash:
                    logger.error("SHA256 hash verification failed")
                    return False
                logger.info("SHA256 hash verification passed")

            # Try to verify it's a valid PE executable
            with open(installer_path, 'rb') as f:
                header = f.read(2)
                if header != b'MZ':
                    logger.error("Downloaded file is not a valid executable")
                    return False

            return True

        except Exception as e:
            logger.error(f"Download verification failed: {e}")
            return False

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _install_chrome(self, installer_path: Path, version: ChromeVersion) -> bool:
        """Install Chrome from installer."""
        try:
            logger.info("Installing Chrome...")

            # Create temporary extraction directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                extract_dir = temp_path / "chrome_extract"
                extract_dir.mkdir()

                # Extract installer (this is a simplified approach)
                # In reality, you might need more sophisticated extraction
                cmd = [
                    str(installer_path),
                    "/S",  # Silent install
                    f"/D={extract_dir}"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                # Find extracted Chrome directory
                chrome_dirs = list(extract_dir.rglob("chrome.exe"))
                if chrome_dirs:
                    extracted_chrome_dir = chrome_dirs[0].parent.parent  # Go up to Chrome directory

                    # Backup current installation if it exists
                    if self.chrome_dir.exists():
                        backup_dir = self.chrome_dir.with_suffix('.backup')
                        if backup_dir.exists():
                            shutil.rmtree(backup_dir)
                        shutil.move(self.chrome_dir, backup_dir)

                    # Move new installation to target location
                    shutil.copytree(extracted_chrome_dir, self.chrome_dir)

                    # Update version info
                    version.is_installed = True
                    version.installation_path = self.chrome_dir

                    logger.info("Chrome installation completed successfully")
                    return True
                else:
                    logger.error("Chrome executable not found after installation")
                    return False

        except Exception as e:
            logger.error(f"Chrome installation failed: {e}")
            return False

    def _create_backup(self, version: ChromeVersion, suffix: str = "") -> bool:
        """Create backup of Chrome installation."""
        try:
            if not self.chrome_dir.exists():
                logger.warning("No Chrome installation to backup")
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"chrome_{version.version}_{timestamp}{suffix}"
            backup_path = self.backups_dir / backup_name

            logger.info(f"Creating Chrome backup: {backup_path}")

            shutil.copytree(self.chrome_dir, backup_path)

            # Save backup metadata
            metadata = {
                "version": version.version,
                "channel": version.channel,
                "backup_date": datetime.now().isoformat(),
                "original_path": str(self.chrome_dir),
                "backup_size": self._get_directory_size(backup_path)
            }

            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Backup created successfully: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    def _find_backup(self, version: str) -> Optional[Path]:
        """Find backup for specific version."""
        for backup_dir in self.backups_dir.iterdir():
            if backup_dir.is_dir() and version in backup_dir.name:
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            if metadata.get("version") == version:
                                return backup_dir
                    except Exception:
                        continue
        return None

    def _get_latest_backup(self) -> Optional[Path]:
        """Get most recent backup."""
        backups = []
        for backup_dir in self.backups_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            backup_date = datetime.fromisoformat(metadata["backup_date"])
                            backups.append((backup_date, backup_dir))
                    except Exception:
                        continue

        if backups:
            backups.sort(key=lambda x: x[0], reverse=True)
            return backups[0][1]

        return None

    def _restore_from_backup(self, backup_path: Path) -> bool:
        """Restore Chrome from backup."""
        try:
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False

            logger.info(f"Restoring Chrome from backup: {backup_path}")

            # Remove current installation
            if self.chrome_dir.exists():
                shutil.rmtree(self.chrome_dir)

            # Copy backup to Chrome directory
            shutil.copytree(backup_path, self.chrome_dir,
                          ignore=shutil.ignore_patterns("backup_metadata.json"))

            # Update current version info from backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                restored_version = ChromeVersion(
                    version=metadata["version"],
                    channel=metadata["channel"],
                    build_date=datetime.fromisoformat(metadata["backup_date"]),
                    is_installed=True,
                    installation_path=self.chrome_dir
                )

                self._save_current_version(restored_version)

            logger.info("Chrome restored successfully from backup")
            return True

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    def _cleanup_old_backups(self) -> None:
        """Remove old backups beyond the retention limit."""
        try:
            backups = []
            for backup_dir in self.backups_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                backup_date = datetime.fromisoformat(metadata["backup_date"])
                                backups.append((backup_date, backup_dir))
                        except Exception:
                            continue

            # Sort by date (newest first)
            backups.sort(key=lambda x: x[0], reverse=True)

            # Remove backups beyond retention limit
            if len(backups) > self.policy.backup_versions:
                for _, backup_dir in backups[self.policy.backup_versions:]:
                    logger.info(f"Removing old backup: {backup_dir}")
                    shutil.rmtree(backup_dir, ignore_errors=True)

        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")


def main():
    """Main entry point for Chrome version manager."""
    import argparse

    parser = argparse.ArgumentParser(description="Chrome Version Manager")
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--update", action="store_true", help="Update Chrome")
    parser.add_argument("--rollback", help="Rollback to specific version")
    parser.add_argument("--list-versions", action="store_true", help="List available versions")
    parser.add_argument("--current", action="store_true", help="Show current version")
    parser.add_argument("--channel", default="stable", help="Chrome channel")
    parser.add_argument("--force", action="store_true", help="Force update")

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # Initialize manager
    project_root = Path(__file__).parent.parent
    manager = ChromeVersionManager(project_root)

    try:
        if args.current:
            current = manager.get_current_version()
            if current:
                logger.info(f"Current Chrome version: {current.version} ({current.channel})")
                logger.info(f"Installation path: {current.installation_path}")
                logger.info(f"Build date: {current.build_date}")
            else:
                logger.info("No Chrome installation found")

        elif args.list_versions:
            versions = manager.get_available_versions(args.channel, limit=10)
            logger.info(f"Available {args.channel} versions:")
            for version in versions:
                logger.info(f"  {version.version} - {version.build_date.strftime('%Y-%m-%d')}")

        elif args.check:
            update = manager.check_for_updates()
            if update:
                logger.info(f"Update available: {update.version}")
            else:
                logger.info("Chrome is up to date")

        elif args.update:
            success = manager.update_chrome(force=args.force)
            if success:
                logger.info("Chrome updated successfully")
            else:
                logger.error("Chrome update failed")

        elif args.rollback:
            success = manager.rollback_chrome(args.rollback)
            if success:
                logger.info("Chrome rollback completed")
            else:
                logger.error("Chrome rollback failed")

        else:
            parser.print_help()

        return 0

    except Exception as e:
        logger.error(f"Chrome version manager error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
