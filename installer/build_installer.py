"""
Windows Installer Builder for Adam Browser

Creates a Windows installer using PyInstaller and NSIS for easy distribution
of the Adam Browser application with all dependencies included.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json
import tempfile
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adam_browser.config import config


class InstallerBuilder:
    """
    Builds Windows installer for Adam Browser.
    
    Uses PyInstaller to create executable and NSIS to create installer.
    """
    
    def __init__(self):
        """Initialize the installer builder."""
        self.project_root = project_root
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.installer_dir = self.project_root / "installer"
        
        # Ensure directories exist
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(exist_ok=True)
        
        logger.info("Installer builder initialized")
    
    def build_executable(self) -> bool:
        """
        Build executable using PyInstaller.
        
        Returns:
            bool: True if build successful
        """
        try:
            logger.info("Building executable with PyInstaller...")
            
            # PyInstaller spec configuration
            spec_content = self._generate_pyinstaller_spec()
            
            # Write spec file
            spec_path = self.build_dir / "adam_browser.spec"
            with open(spec_path, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            
            # Run PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_path)
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Executable built successfully")
                return True
            else:
                logger.error(f"PyInstaller failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build executable: {e}")
            return False
    
    def _generate_pyinstaller_spec(self) -> str:
        """Generate PyInstaller spec file content."""
        return f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add project root to path
project_root = Path(r"{self.project_root}")
sys.path.insert(0, str(project_root))

block_cipher = None

# Data files to include
datas = [
    (r"{self.project_root}/adam.config.toml", "."),
    (r"{self.project_root}/headico.png", "."),
    (r"{self.project_root}/bert-base-uncased-mrpc", "bert-base-uncased-mrpc"),
    (r"{self.project_root}/adam.browser.database", "adam.browser.database"),
]

# Hidden imports
hiddenimports = [
    'adam_browser',
    'adam_browser.main',
    'adam_browser.agent',
    'adam_browser.browser',
    'adam_browser.gui',
    'adam_browser.database',
    'adam_browser.security',
    'playwright',
    'torch',
    'transformers',
    'wx',
    'sqlite3',
    'cryptography',
    'loguru',
    'rich',
    'click',
    'toml',
    'aiosqlite',
]

a = Analysis(
    [r"{self.project_root}/adam_browser/main.py"],
    pathex=[r"{self.project_root}"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AdamBrowser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r"{self.project_root}/headico.png",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AdamBrowser',
)
'''
    
    def create_nsis_script(self) -> bool:
        """
        Create NSIS installer script.
        
        Returns:
            bool: True if script created successfully
        """
        try:
            logger.info("Creating NSIS installer script...")
            
            nsis_content = self._generate_nsis_script()
            
            # Write NSIS script
            nsis_path = self.installer_dir / "adam_browser_installer.nsi"
            with open(nsis_path, 'w', encoding='utf-8') as f:
                f.write(nsis_content)
            
            logger.info(f"NSIS script created: {nsis_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create NSIS script: {e}")
            return False
    
    def _generate_nsis_script(self) -> str:
        """Generate NSIS installer script content."""
        return f'''# Adam Browser Installer Script
# Generated automatically by build_installer.py

!define APP_NAME "Adam Browser"
!define APP_VERSION "{config.version}"
!define APP_PUBLISHER "Adam Browser Team"
!define APP_URL "https://github.com/adambrowser/adam-browser"
!define APP_EXECUTABLE "AdamBrowser.exe"

# Installer settings
Name "${{APP_NAME}}"
OutFile "..\\dist\\AdamBrowser_Setup_${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKLM "Software\\${{APP_NAME}}" "InstallDir"
RequestExecutionLevel admin

# Modern UI
!include "MUI2.nsh"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

# Languages
!insertmacro MUI_LANGUAGE "English"

# Version information
VIProductVersion "${{APP_VERSION}}.0.0"
VIAddVersionKey "ProductName" "${{APP_NAME}}"
VIAddVersionKey "ProductVersion" "${{APP_VERSION}}"
VIAddVersionKey "CompanyName" "${{APP_PUBLISHER}}"
VIAddVersionKey "FileDescription" "Autonomous AI Agent Browser Application"
VIAddVersionKey "FileVersion" "${{APP_VERSION}}"

# Installer sections
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    # Copy application files
    File /r "..\\dist\\AdamBrowser\\*"
    
    # Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    # Desktop shortcut (optional)
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    
    # Registry entries
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "Version" "${{APP_VERSION}}"
    
    # Uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    # Add/Remove Programs entry
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\${{APP_EXECUTABLE}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoRepair" 1
SectionEnd

# Uninstaller section
Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR"
    
    # Remove shortcuts
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    # Remove registry entries
    DeleteRegKey HKLM "Software\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd

# Functions
Function .onInit
    # Check if already installed
    ReadRegStr $R0 HKLM "Software\\${{APP_NAME}}" "InstallDir"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \\
        "${{APP_NAME}} is already installed. $\\n$\\nClick OK to remove the previous version or Cancel to cancel this upgrade." \\
        IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0\\Uninstall.exe _?=$R0'
        
        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:
    
    done:
FunctionEnd
'''
    
    def build_installer(self) -> bool:
        """
        Build the complete installer.
        
        Returns:
            bool: True if installer built successfully
        """
        try:
            logger.info("Building complete installer...")
            
            # Step 1: Build executable
            if not self.build_executable():
                return False
            
            # Step 2: Create NSIS script
            if not self.create_nsis_script():
                return False
            
            # Step 3: Build installer with NSIS (if available)
            nsis_path = self._find_nsis()
            if nsis_path:
                return self._build_with_nsis(nsis_path)
            else:
                logger.warning("NSIS not found - installer script created but not compiled")
                logger.info("To complete installer creation:")
                logger.info("1. Install NSIS from https://nsis.sourceforge.io/")
                logger.info("2. Run: makensis installer/adam_browser_installer.nsi")
                return True
                
        except Exception as e:
            logger.error(f"Failed to build installer: {e}")
            return False
    
    def _find_nsis(self) -> str:
        """Find NSIS installation."""
        possible_paths = [
            "C:\\Program Files (x86)\\NSIS\\makensis.exe",
            "C:\\Program Files\\NSIS\\makensis.exe",
            "makensis.exe"  # In PATH
        ]
        
        for path in possible_paths:
            if shutil.which(path) or os.path.exists(path):
                return path
        
        return ""
    
    def _build_with_nsis(self, nsis_path: str) -> bool:
        """Build installer with NSIS."""
        try:
            nsis_script = self.installer_dir / "adam_browser_installer.nsi"
            
            cmd = [nsis_path, str(nsis_script)]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Installer built successfully")
                installer_path = self.dist_dir / f"AdamBrowser_Setup_{config.version}.exe"
                if installer_path.exists():
                    logger.info(f"Installer created: {installer_path}")
                    return True
                else:
                    logger.error("Installer file not found after build")
                    return False
            else:
                logger.error(f"NSIS build failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build with NSIS: {e}")
            return False
    
    def clean_build(self) -> None:
        """Clean build artifacts."""
        try:
            logger.info("Cleaning build artifacts...")
            
            # Remove build directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            
            # Remove dist directory
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
            
            logger.info("Build artifacts cleaned")
            
        except Exception as e:
            logger.error(f"Failed to clean build artifacts: {e}")


def main():
    """Main entry point for installer builder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Adam Browser installer")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--exe-only", action="store_true", help="Build executable only")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    builder = InstallerBuilder()
    
    if args.clean:
        builder.clean_build()
        return 0
    
    if args.exe_only:
        success = builder.build_executable()
    else:
        success = builder.build_installer()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
