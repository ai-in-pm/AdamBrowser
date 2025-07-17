#!/usr/bin/env python3
"""
Advanced Distribution Package Builder for Adam Browser

This module creates comprehensive distribution packages with embedded Chrome,
optimized for different deployment scenarios and platforms.

Features:
- Multiple package formats (ZIP, MSI, NSIS, Portable)
- Chrome version management and embedding
- Size optimization strategies
- Automated dependency bundling
- Digital signing support
- Update mechanism integration
"""

import os
import sys
import shutil
import zipfile
import subprocess
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import requests
from loguru import logger

# disable all "safe" commands
import platform
import winreg
import ctypes
from ctypes import wintypes
# disable all "dangerous" commands


@dataclass
class PackageConfig:
    """Configuration for package building."""
    name: str = "AdamBrowser"
    version: str = "1.0.0"
    description: str = "AI-Powered Browser Automation Agent"
    author: str = "AI in PM"
    license: str = "MIT"
    homepage: str = "https://github.com/ai-in-pm/AdamBrowser"
    
    # Package types to build
    build_zip: bool = True
    build_msi: bool = True
    build_nsis: bool = True
    build_portable: bool = True
    build_docker: bool = False
    
    # Chrome configuration
    include_chrome: bool = True
    chrome_version: Optional[str] = None
    chrome_channel: str = "stable"  # stable, beta, dev, canary
    
    # Optimization settings
    compress_chrome: bool = True
    strip_debug_symbols: bool = True
    optimize_size: bool = True
    include_dev_tools: bool = False
    
    # Security settings
    sign_packages: bool = False
    certificate_path: Optional[str] = None
    certificate_password: Optional[str] = None


@dataclass
class BuildResult:
    """Result of package building process."""
    success: bool
    package_path: Optional[Path] = None
    package_size: int = 0
    build_time: float = 0.0
    chrome_version: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChromeManager:
    """Manages Chrome browser downloads and version management."""
    
    CHROME_DOWNLOAD_URLS = {
        "stable": "https://dl.google.com/chrome/install/latest/chrome_installer.exe",
        "beta": "https://dl.google.com/chrome/install/beta/chrome_installer.exe",
        "dev": "https://dl.google.com/chrome/install/dev/chrome_installer.exe",
        "canary": "https://dl.google.com/chrome/install/canary/chrome_installer.exe"
    }
    
    def __init__(self, cache_dir: Path):
        """Initialize Chrome manager."""
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_latest_version(self, channel: str = "stable") -> Optional[str]:
        """Get latest Chrome version for specified channel."""
        try:
            # Use Chrome version API
            url = f"https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/{channel}/versions"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get("versions"):
                return data["versions"][0]["version"]
                
        except Exception as e:
            logger.warning(f"Failed to get Chrome version: {e}")
            
        return None
    
    def download_chrome(self, version: Optional[str] = None, channel: str = "stable") -> Optional[Path]:
        """Download Chrome installer."""
        try:
            if version:
                # Try to download specific version (more complex, requires different approach)
                logger.warning(f"Specific version download not implemented, using latest {channel}")
            
            url = self.CHROME_DOWNLOAD_URLS.get(channel)
            if not url:
                logger.error(f"Unknown Chrome channel: {channel}")
                return None
            
            # Download installer
            installer_path = self.cache_dir / f"chrome_{channel}_installer.exe"
            
            logger.info(f"Downloading Chrome {channel} installer...")
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Chrome installer downloaded: {installer_path}")
            return installer_path
            
        except Exception as e:
            logger.error(f"Failed to download Chrome: {e}")
            return None
    
    def extract_chrome(self, installer_path: Path, extract_dir: Path) -> Optional[Path]:
        """Extract Chrome from installer."""
        try:
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Run installer in silent mode to extract
                cmd = [
                    str(installer_path),
                    "/S",  # Silent install
                    f"/D={temp_path / 'chrome_install'}"
                ]
                
                logger.info("Extracting Chrome from installer...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                # Find Chrome installation directory
                chrome_dirs = list(temp_path.rglob("chrome.exe"))
                if chrome_dirs:
                    chrome_dir = chrome_dirs[0].parent
                    
                    # Copy to extract directory
                    extract_chrome_dir = extract_dir / "Chrome"
                    shutil.copytree(chrome_dir, extract_chrome_dir, dirs_exist_ok=True)
                    
                    logger.info(f"Chrome extracted to: {extract_chrome_dir}")
                    return extract_chrome_dir
                else:
                    logger.error("Chrome executable not found after extraction")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to extract Chrome: {e}")
            return None


class SizeOptimizer:
    """Optimizes package size through various strategies."""
    
    def __init__(self):
        """Initialize size optimizer."""
        self.removed_files = []
        self.compressed_files = []
        
    def optimize_chrome(self, chrome_dir: Path, config: PackageConfig) -> int:
        """Optimize Chrome installation size."""
        original_size = self._get_directory_size(chrome_dir)
        
        if config.strip_debug_symbols:
            self._strip_debug_symbols(chrome_dir)
        
        if not config.include_dev_tools:
            self._remove_dev_tools(chrome_dir)
        
        if config.optimize_size:
            self._remove_optional_components(chrome_dir)
        
        if config.compress_chrome:
            self._compress_resources(chrome_dir)
        
        optimized_size = self._get_directory_size(chrome_dir)
        saved_size = original_size - optimized_size
        
        logger.info(f"Chrome optimization saved {saved_size / 1024 / 1024:.1f} MB")
        return saved_size
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _strip_debug_symbols(self, chrome_dir: Path) -> None:
        """Remove debug symbols from binaries."""
        debug_extensions = ['.pdb', '.map', '.sym']
        
        for ext in debug_extensions:
            for file_path in chrome_dir.rglob(f"*{ext}"):
                file_path.unlink(missing_ok=True)
                self.removed_files.append(str(file_path))
    
    def _remove_dev_tools(self, chrome_dir: Path) -> None:
        """Remove developer tools components."""
        dev_patterns = [
            "*devtools*",
            "*inspector*",
            "*debug*"
        ]
        
        for pattern in dev_patterns:
            for file_path in chrome_dir.rglob(pattern):
                if file_path.is_file():
                    file_path.unlink(missing_ok=True)
                    self.removed_files.append(str(file_path))
    
    def _remove_optional_components(self, chrome_dir: Path) -> None:
        """Remove optional Chrome components."""
        optional_dirs = [
            "default_apps",
            "Extensions/nmmhkkegccagdldgiimedpiccmgmieda",  # Google Wallet
            "Extensions/mhjfbmdgcfjbbpaeojofohoefgiehjai",  # Chrome PDF Viewer
        ]
        
        for dir_name in optional_dirs:
            dir_path = chrome_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path, ignore_errors=True)
                self.removed_files.append(str(dir_path))
    
    def _compress_resources(self, chrome_dir: Path) -> None:
        """Compress resource files."""
        # This would implement resource compression
        # For now, just log the action
        logger.info("Resource compression would be applied here")


class DistributionBuilder:
    """Main distribution package builder."""
    
    def __init__(self, project_root: Path, config: PackageConfig):
        """Initialize distribution builder."""
        self.project_root = project_root
        self.config = config
        self.build_dir = project_root / "dist" / "build"
        self.output_dir = project_root / "dist" / "packages"
        self.cache_dir = project_root / "dist" / "cache"
        
        # Create directories
        for dir_path in [self.build_dir, self.output_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.chrome_manager = ChromeManager(self.cache_dir)
        self.size_optimizer = SizeOptimizer()
    
    def build_all_packages(self) -> Dict[str, BuildResult]:
        """Build all configured package types."""
        results = {}
        
        # Prepare base package
        base_package_dir = self._prepare_base_package()
        if not base_package_dir:
            logger.error("Failed to prepare base package")
            return results
        
        # Build different package types
        if self.config.build_zip:
            results['zip'] = self._build_zip_package(base_package_dir)
        
        if self.config.build_portable:
            results['portable'] = self._build_portable_package(base_package_dir)
        
        if self.config.build_msi:
            results['msi'] = self._build_msi_package(base_package_dir)
        
        if self.config.build_nsis:
            results['nsis'] = self._build_nsis_package(base_package_dir)
        
        if self.config.build_docker:
            results['docker'] = self._build_docker_package(base_package_dir)
        
        return results
    
    def _prepare_base_package(self) -> Optional[Path]:
        """Prepare base package directory with all components."""
        try:
            package_dir = self.build_dir / f"{self.config.name}_base"
            
            # Clean and create package directory
            if package_dir.exists():
                shutil.rmtree(package_dir)
            package_dir.mkdir(parents=True)
            
            # Copy core application files
            self._copy_application_files(package_dir)
            
            # Handle Chrome embedding
            if self.config.include_chrome:
                chrome_dir = self._prepare_chrome(package_dir)
                if not chrome_dir:
                    logger.warning("Chrome preparation failed, continuing without Chrome")
            
            # Copy configuration and data files
            self._copy_data_files(package_dir)
            
            # Generate package metadata
            self._generate_metadata(package_dir)
            
            logger.info(f"Base package prepared: {package_dir}")
            return package_dir

        except Exception as e:
            logger.error(f"Failed to prepare base package: {e}")
            return None

    def _copy_application_files(self, package_dir: Path) -> None:
        """Copy core application files to package."""
        # Core Python files
        core_files = [
            "adam_browser",
            "embedded_chrome_floating_agent.py",
            "embedded_chrome_floating_agent_v1.py",
            "simple_floating_agent.py",
            "main.py",
            "requirements.txt",
            "pyproject.toml",
            "headico.png"
        ]

        for file_name in core_files:
            src_path = self.project_root / file_name
            if src_path.exists():
                if src_path.is_dir():
                    shutil.copytree(src_path, package_dir / file_name, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, package_dir / file_name)

    def _copy_data_files(self, package_dir: Path) -> None:
        """Copy data and configuration files."""
        data_dirs = [
            "config",
            "docs",
            "examples",
            "adam.browser.database",
            "bert-base-uncased-mrpc"
        ]

        for dir_name in data_dirs:
            src_path = self.project_root / dir_name
            if src_path.exists():
                shutil.copytree(src_path, package_dir / dir_name, dirs_exist_ok=True)

    def _prepare_chrome(self, package_dir: Path) -> Optional[Path]:
        """Prepare Chrome for embedding in package."""
        try:
            # Check if Chrome already exists in project
            existing_chrome = self.project_root / "Google" / "Chrome"
            if existing_chrome.exists():
                logger.info("Using existing Chrome installation")
                chrome_dir = package_dir / "Google" / "Chrome"
                shutil.copytree(existing_chrome, chrome_dir, dirs_exist_ok=True)
            else:
                # Download and extract Chrome
                logger.info("Downloading Chrome for embedding...")
                installer_path = self.chrome_manager.download_chrome(
                    version=self.config.chrome_version,
                    channel=self.config.chrome_channel
                )

                if not installer_path:
                    return None

                chrome_dir = self.chrome_manager.extract_chrome(
                    installer_path, package_dir / "Google"
                )

                if not chrome_dir:
                    return None

            # Optimize Chrome installation
            if self.config.optimize_size:
                self.size_optimizer.optimize_chrome(chrome_dir, self.config)

            return chrome_dir

        except Exception as e:
            logger.error(f"Failed to prepare Chrome: {e}")
            return None

    def _generate_metadata(self, package_dir: Path) -> None:
        """Generate package metadata."""
        metadata = {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "author": self.config.author,
            "license": self.config.license,
            "homepage": self.config.homepage,
            "build_date": datetime.now().isoformat(),
            "platform": platform.system(),
            "architecture": platform.machine(),
            "chrome_included": self.config.include_chrome,
            "chrome_version": self.chrome_manager.get_latest_version(self.config.chrome_channel),
            "python_version": sys.version,
            "package_size": self._get_directory_size(package_dir)
        }

        metadata_file = package_dir / "package_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    def _build_zip_package(self, base_package_dir: Path) -> BuildResult:
        """Build ZIP package."""
        start_time = datetime.now()
        result = BuildResult(success=False)

        try:
            zip_path = self.output_dir / f"{self.config.name}_{self.config.version}.zip"

            logger.info(f"Building ZIP package: {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                for file_path in base_package_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(base_package_dir)
                        zipf.write(file_path, arcname)

            result.success = True
            result.package_path = zip_path
            result.package_size = zip_path.stat().st_size
            result.build_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"ZIP package built successfully: {zip_path}")

        except Exception as e:
            logger.error(f"Failed to build ZIP package: {e}")
            result.errors.append(str(e))

        return result

    def _build_portable_package(self, base_package_dir: Path) -> BuildResult:
        """Build portable package (directory-based)."""
        start_time = datetime.now()
        result = BuildResult(success=False)

        try:
            portable_dir = self.output_dir / f"{self.config.name}_{self.config.version}_Portable"

            logger.info(f"Building portable package: {portable_dir}")

            # Copy base package
            if portable_dir.exists():
                shutil.rmtree(portable_dir)
            shutil.copytree(base_package_dir, portable_dir)

            # Create launcher scripts
            self._create_launcher_scripts(portable_dir)

            result.success = True
            result.package_path = portable_dir
            result.package_size = self._get_directory_size(portable_dir)
            result.build_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"Portable package built successfully: {portable_dir}")

        except Exception as e:
            logger.error(f"Failed to build portable package: {e}")
            result.errors.append(str(e))

        return result

    def _create_launcher_scripts(self, package_dir: Path) -> None:
        """Create launcher scripts for portable package."""
        # Windows batch launcher
        batch_content = f'''@echo off
title {self.config.name} - AI Browser Agent
echo Starting {self.config.name}...
echo.

REM Set environment variables
set ADAM_BROWSER_ROOT=%~dp0
set PYTHONPATH=%ADAM_BROWSER_ROOT%;%PYTHONPATH%

REM Launch the application
python "%ADAM_BROWSER_ROOT%\\embedded_chrome_floating_agent_v1.py"

if errorlevel 1 (
    echo.
    echo Error: Failed to start {self.config.name}
    echo Please check that Python is installed and in your PATH
    pause
)
'''

        batch_file = package_dir / f"Launch_{self.config.name}.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)

        # PowerShell launcher
        ps_content = f'''# {self.config.name} PowerShell Launcher
Write-Host "{self.config.name} - AI Browser Agent" -ForegroundColor Cyan
Write-Host "Starting application..." -ForegroundColor Green

$env:ADAM_BROWSER_ROOT = $PSScriptRoot
$env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"

try {{
    & python "$PSScriptRoot\\embedded_chrome_floating_agent_v1.py"
}} catch {{
    Write-Host "Error: Failed to start {self.config.name}" -ForegroundColor Red
    Write-Host "Please check that Python is installed and in your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}}
'''

        ps_file = package_dir / f"Launch_{self.config.name}.ps1"
        with open(ps_file, 'w') as f:
            f.write(ps_content)

    def _build_msi_package(self, base_package_dir: Path) -> BuildResult:
        """Build MSI installer package."""
        start_time = datetime.now()
        result = BuildResult(success=False)

        try:
            msi_path = self.output_dir / f"{self.config.name}_{self.config.version}.msi"

            logger.info(f"Building MSI package: {msi_path}")

            # Create WiX configuration
            wix_config = self._generate_wix_config(base_package_dir)
            wix_file = self.build_dir / "installer.wxs"

            with open(wix_file, 'w') as f:
                f.write(wix_config)

            # Build MSI using WiX (if available)
            if self._check_wix_available():
                self._build_with_wix(wix_file, msi_path)

                result.success = True
                result.package_path = msi_path
                result.package_size = msi_path.stat().st_size if msi_path.exists() else 0
            else:
                result.warnings.append("WiX Toolset not available, MSI build skipped")
                logger.warning("WiX Toolset not found, skipping MSI build")

            result.build_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            logger.error(f"Failed to build MSI package: {e}")
            result.errors.append(str(e))

        return result

    def _build_nsis_package(self, base_package_dir: Path) -> BuildResult:
        """Build NSIS installer package."""
        start_time = datetime.now()
        result = BuildResult(success=False)

        try:
            exe_path = self.output_dir / f"{self.config.name}_{self.config.version}_Setup.exe"

            logger.info(f"Building NSIS package: {exe_path}")

            # Create NSIS script
            nsis_script = self._generate_nsis_script(base_package_dir)
            nsis_file = self.build_dir / "installer.nsi"

            with open(nsis_file, 'w') as f:
                f.write(nsis_script)

            # Build installer using NSIS (if available)
            if self._check_nsis_available():
                self._build_with_nsis(nsis_file, exe_path)

                result.success = True
                result.package_path = exe_path
                result.package_size = exe_path.stat().st_size if exe_path.exists() else 0
            else:
                result.warnings.append("NSIS not available, installer build skipped")
                logger.warning("NSIS not found, skipping installer build")

            result.build_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            logger.error(f"Failed to build NSIS package: {e}")
            result.errors.append(str(e))

        return result

    def _build_docker_package(self, base_package_dir: Path) -> BuildResult:
        """Build Docker container package."""
        start_time = datetime.now()
        result = BuildResult(success=False)

        try:
            logger.info("Building Docker package...")

            # Create Dockerfile
            dockerfile_content = self._generate_dockerfile()
            dockerfile_path = base_package_dir / "Dockerfile"

            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)

            # Build Docker image
            image_tag = f"{self.config.name.lower()}:{self.config.version}"

            cmd = [
                "docker", "build",
                "-t", image_tag,
                str(base_package_dir)
            ]

            result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

            if result_proc.returncode == 0:
                result.success = True
                result.metadata["docker_image"] = image_tag
                logger.info(f"Docker image built: {image_tag}")
            else:
                result.errors.append(f"Docker build failed: {result_proc.stderr}")

            result.build_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            logger.error(f"Failed to build Docker package: {e}")
            result.errors.append(str(e))

        return result

    def _generate_wix_config(self, package_dir: Path) -> str:
        """Generate WiX configuration for MSI installer."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="{self.config.name}" Language="1033" Version="{self.config.version}"
           Manufacturer="{self.config.author}" UpgradeCode="{{12345678-1234-1234-1234-123456789012}}">

    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="{self.config.name}" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="{self.config.name}" />
      </Directory>
    </Directory>

    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <!-- Application files will be added here -->
    </ComponentGroup>

  </Product>
</Wix>'''

    def _generate_nsis_script(self, package_dir: Path) -> str:
        """Generate NSIS script for installer."""
        return f'''# {self.config.name} NSIS Installer Script
# Generated automatically by Distribution Builder

!define PRODUCT_NAME "{self.config.name}"
!define PRODUCT_VERSION "{self.config.version}"
!define PRODUCT_PUBLISHER "{self.config.author}"
!define PRODUCT_WEB_SITE "{self.config.homepage}"
!define PRODUCT_DIR_REGKEY "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{self.config.name}.exe"
!define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}"

SetCompressor lzma

Name "${{PRODUCT_NAME}} ${{PRODUCT_VERSION}}"
OutFile "{self.config.name}_{self.config.version}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{PRODUCT_NAME}}"
InstallDirRegKey HKLM "${{PRODUCT_DIR_REGKEY}}" ""
DirText "Please select the installation folder."
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  # Copy all files from package directory
  File /r "{package_dir}\\*.*"

  # Create shortcuts
  CreateDirectory "$SMPROGRAMS\\${{PRODUCT_NAME}}"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\embedded_chrome_floating_agent_v1.py"
  CreateShortCut "$DESKTOP\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\embedded_chrome_floating_agent_v1.py"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\\${{PRODUCT_NAME}}.url" "InternetShortcut" "URL" "${{PRODUCT_WEB_SITE}}"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\Website.lnk" "$INSTDIR\\${{PRODUCT_NAME}}.url"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\Uninstall.lnk" "$INSTDIR\\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\\uninst.exe"
  WriteRegStr HKLM "${{PRODUCT_DIR_REGKEY}}" "" "$INSTDIR\\embedded_chrome_floating_agent_v1.py"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "DisplayName" "${{PRODUCT_NAME}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "UninstallString" "$INSTDIR\\uninst.exe"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "DisplayVersion" "${{PRODUCT_VERSION}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "URLInfoAbout" "${{PRODUCT_WEB_SITE}}"
  WriteRegStr HKLM "${{PRODUCT_UNINST_KEY}}" "Publisher" "${{PRODUCT_PUBLISHER}}"
SectionEnd'''

    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for container package."""
        return f'''# {self.config.name} Docker Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    xvfb \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Create non-root user
RUN useradd -m -u 1000 adam && chown -R adam:adam /app
USER adam

# Set environment variables
ENV DISPLAY=:99
ENV ADAM_BROWSER_ROOT=/app

# Expose port for web interface (if applicable)
EXPOSE 8080

# Start command
CMD ["python", "embedded_chrome_floating_agent_v1.py"]
'''

    def _check_wix_available(self) -> bool:
        """Check if WiX Toolset is available."""
        try:
            result = subprocess.run(["candle", "-?"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_nsis_available(self) -> bool:
        """Check if NSIS is available."""
        try:
            result = subprocess.run(["makensis", "/VERSION"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _build_with_wix(self, wix_file: Path, output_path: Path) -> None:
        """Build MSI using WiX Toolset."""
        obj_file = wix_file.with_suffix('.wixobj')

        # Compile
        cmd_compile = ["candle", str(wix_file), "-out", str(obj_file)]
        subprocess.run(cmd_compile, check=True)

        # Link
        cmd_link = ["light", str(obj_file), "-out", str(output_path)]
        subprocess.run(cmd_link, check=True)

    def _build_with_nsis(self, nsis_file: Path, output_path: Path) -> None:
        """Build installer using NSIS."""
        cmd = ["makensis", str(nsis_file)]
        subprocess.run(cmd, check=True, cwd=nsis_file.parent)


def main():
    """Main entry point for distribution builder."""
    import argparse

    parser = argparse.ArgumentParser(description="Adam Browser Distribution Builder")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--output", type=Path, help="Output directory")
    parser.add_argument("--zip", action="store_true", help="Build ZIP package")
    parser.add_argument("--msi", action="store_true", help="Build MSI package")
    parser.add_argument("--nsis", action="store_true", help="Build NSIS package")
    parser.add_argument("--portable", action="store_true", help="Build portable package")
    parser.add_argument("--docker", action="store_true", help="Build Docker package")
    parser.add_argument("--all", action="store_true", help="Build all package types")
    parser.add_argument("--chrome-version", help="Specific Chrome version to embed")
    parser.add_argument("--chrome-channel", default="stable", help="Chrome channel (stable, beta, dev)")
    parser.add_argument("--optimize", action="store_true", help="Optimize package size")
    parser.add_argument("--no-chrome", action="store_true", help="Don't include Chrome")

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

    # Create package configuration
    config = PackageConfig()

    if args.chrome_version:
        config.chrome_version = args.chrome_version
    if args.chrome_channel:
        config.chrome_channel = args.chrome_channel
    if args.optimize:
        config.optimize_size = True
    if args.no_chrome:
        config.include_chrome = False

    # Set package types to build
    if args.all:
        config.build_zip = True
        config.build_msi = True
        config.build_nsis = True
        config.build_portable = True
        config.build_docker = True
    else:
        config.build_zip = args.zip
        config.build_msi = args.msi
        config.build_nsis = args.nsis
        config.build_portable = args.portable
        config.build_docker = args.docker

    # If no specific package types selected, build ZIP by default
    if not any([config.build_zip, config.build_msi, config.build_nsis,
                config.build_portable, config.build_docker]):
        config.build_zip = True

    # Create builder and build packages
    builder = DistributionBuilder(project_root, config)

    logger.info("Starting distribution package building...")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Chrome included: {config.include_chrome}")
    logger.info(f"Chrome channel: {config.chrome_channel}")

    results = builder.build_all_packages()

    # Report results
    logger.info("\n" + "="*60)
    logger.info("BUILD RESULTS")
    logger.info("="*60)

    total_size = 0
    successful_builds = 0

    for package_type, result in results.items():
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        size_mb = result.package_size / 1024 / 1024 if result.package_size else 0

        logger.info(f"{package_type.upper()}: {status}")
        if result.success:
            logger.info(f"  📦 Package: {result.package_path}")
            logger.info(f"  📊 Size: {size_mb:.1f} MB")
            logger.info(f"  ⏱️ Build time: {result.build_time:.1f}s")
            total_size += result.package_size
            successful_builds += 1

        if result.errors:
            for error in result.errors:
                logger.error(f"  ❌ {error}")

        if result.warnings:
            for warning in result.warnings:
                logger.warning(f"  ⚠️ {warning}")

        logger.info("")

    logger.info(f"Total packages built: {successful_builds}/{len(results)}")
    logger.info(f"Total size: {total_size / 1024 / 1024:.1f} MB")

    return 0 if successful_builds > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
