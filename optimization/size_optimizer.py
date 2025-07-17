#!/usr/bin/env python3
"""
Advanced Size Optimization System

This module provides comprehensive size optimization for Chrome and the entire
Adam Browser distribution package, including:
- Chrome component analysis and removal
- Binary compression and stripping
- Resource optimization
- Dependency minimization
- Smart caching strategies
"""

import os
import sys
import shutil
import gzip
import lzma
import zipfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
import json
import hashlib
from loguru import logger

# disable all "safe" commands
import pefile
import struct
# disable all "dangerous" commands


@dataclass
class OptimizationResult:
    """Result of optimization process."""
    original_size: int
    optimized_size: int
    savings: int
    savings_percentage: float
    removed_files: List[str] = field(default_factory=list)
    compressed_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class OptimizationConfig:
    """Configuration for size optimization."""
    # Chrome optimization
    remove_debug_symbols: bool = True
    remove_dev_tools: bool = True
    remove_crash_reporter: bool = True
    remove_update_components: bool = True
    remove_unused_locales: bool = True
    keep_locales: List[str] = field(default_factory=lambda: ["en-US"])
    
    # Binary optimization
    strip_binaries: bool = True
    compress_resources: bool = True
    optimize_images: bool = True
    
    # Component removal
    remove_samples: bool = True
    remove_tests: bool = True
    remove_documentation: bool = False
    remove_source_maps: bool = True
    
    # Advanced optimization
    use_upx_compression: bool = False
    aggressive_optimization: bool = False
    preserve_functionality: bool = True


class ChromeOptimizer:
    """Optimizes Chrome installation for size."""
    
    # Files and directories that can be safely removed
    REMOVABLE_COMPONENTS = {
        'debug_symbols': ['*.pdb', '*.map', '*.sym'],
        'dev_tools': [
            'resources/inspector/*',
            'resources/devtools_app.html',
            'resources/devtools_app.js'
        ],
        'crash_reporter': [
            'chrome_wer.dll',
            'crash_reporter.exe',
            'crash_service.exe'
        ],
        'update_components': [
            'elevation_service.exe',
            'os_update_handler.exe',
            'GoogleUpdate.exe'
        ],
        'optional_features': [
            'default_apps/*',
            'Extensions/nmmhkkegccagdldgiimedpiccmgmieda',  # Google Wallet
            'Extensions/mhjfbmdgcfjbbpaeojofohoefgiehjai',  # Chrome PDF Viewer (optional)
        ],
        'media_codecs': [
            'WidevineCdm/*',  # Only if DRM not needed
        ]
    }
    
    # Locale directories (keep only specified locales)
    LOCALE_PATTERN = 'Locales/*.pak'
    
    def __init__(self, chrome_dir: Path, config: OptimizationConfig):
        """Initialize Chrome optimizer."""
        self.chrome_dir = chrome_dir
        self.config = config
        self.removed_files = []
        self.compressed_files = []
        self.errors = []
        self.warnings = []
    
    def optimize(self) -> OptimizationResult:
        """Perform comprehensive Chrome optimization."""
        logger.info(f"Starting Chrome optimization: {self.chrome_dir}")
        
        original_size = self._get_directory_size(self.chrome_dir)
        
        # Remove unnecessary components
        if self.config.remove_debug_symbols:
            self._remove_debug_symbols()
        
        if self.config.remove_dev_tools:
            self._remove_dev_tools()
        
        if self.config.remove_crash_reporter:
            self._remove_crash_reporter()
        
        if self.config.remove_update_components:
            self._remove_update_components()
        
        if self.config.remove_unused_locales:
            self._optimize_locales()
        
        # Optimize binaries
        if self.config.strip_binaries:
            self._strip_binaries()
        
        if self.config.compress_resources:
            self._compress_resources()
        
        if self.config.optimize_images:
            self._optimize_images()
        
        # Advanced optimizations
        if self.config.use_upx_compression:
            self._upx_compress_binaries()
        
        optimized_size = self._get_directory_size(self.chrome_dir)
        savings = original_size - optimized_size
        savings_percentage = (savings / original_size) * 100 if original_size > 0 else 0
        
        result = OptimizationResult(
            original_size=original_size,
            optimized_size=optimized_size,
            savings=savings,
            savings_percentage=savings_percentage,
            removed_files=self.removed_files,
            compressed_files=self.compressed_files,
            errors=self.errors,
            warnings=self.warnings
        )
        
        logger.info(f"Chrome optimization completed: {savings / 1024 / 1024:.1f} MB saved ({savings_percentage:.1f}%)")
        
        return result
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def _remove_debug_symbols(self) -> None:
        """Remove debug symbols and related files."""
        logger.info("Removing debug symbols...")
        
        patterns = self.REMOVABLE_COMPONENTS['debug_symbols']
        for pattern in patterns:
            for file_path in self.chrome_dir.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        self.removed_files.append(str(file_path))
                except Exception as e:
                    self.errors.append(f"Failed to remove {file_path}: {e}")
    
    def _remove_dev_tools(self) -> None:
        """Remove developer tools components."""
        logger.info("Removing developer tools...")
        
        patterns = self.REMOVABLE_COMPONENTS['dev_tools']
        for pattern in patterns:
            for file_path in self.chrome_dir.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        self.removed_files.append(str(file_path))
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        self.removed_files.append(str(file_path))
                except Exception as e:
                    self.errors.append(f"Failed to remove {file_path}: {e}")
    
    def _remove_crash_reporter(self) -> None:
        """Remove crash reporting components."""
        logger.info("Removing crash reporter...")
        
        patterns = self.REMOVABLE_COMPONENTS['crash_reporter']
        for pattern in patterns:
            for file_path in self.chrome_dir.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        self.removed_files.append(str(file_path))
                except Exception as e:
                    self.errors.append(f"Failed to remove {file_path}: {e}")
    
    def _remove_update_components(self) -> None:
        """Remove update-related components."""
        logger.info("Removing update components...")
        
        patterns = self.REMOVABLE_COMPONENTS['update_components']
        for pattern in patterns:
            for file_path in self.chrome_dir.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        self.removed_files.append(str(file_path))
                except Exception as e:
                    self.errors.append(f"Failed to remove {file_path}: {e}")
    
    def _optimize_locales(self) -> None:
        """Remove unused locale files."""
        logger.info(f"Optimizing locales (keeping: {self.config.keep_locales})...")
        
        locales_dir = self.chrome_dir / "Application" / "Locales"
        if not locales_dir.exists():
            return
        
        keep_files = set()
        for locale in self.config.keep_locales:
            keep_files.add(f"{locale}.pak")
        
        for locale_file in locales_dir.glob("*.pak"):
            if locale_file.name not in keep_files:
                try:
                    locale_file.unlink()
                    self.removed_files.append(str(locale_file))
                except Exception as e:
                    self.errors.append(f"Failed to remove locale {locale_file}: {e}")
    
    def _strip_binaries(self) -> None:
        """Strip debug information from binaries."""
        logger.info("Stripping binaries...")
        
        binary_extensions = ['.exe', '.dll']
        
        for file_path in self.chrome_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in binary_extensions:
                try:
                    # Use strip command if available (requires MinGW or similar)
                    if shutil.which('strip'):
                        result = subprocess.run(['strip', str(file_path)], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            self.compressed_files.append(str(file_path))
                        else:
                            self.warnings.append(f"Failed to strip {file_path}")
                except Exception as e:
                    self.warnings.append(f"Strip failed for {file_path}: {e}")
    
    def _compress_resources(self) -> None:
        """Compress resource files."""
        logger.info("Compressing resources...")
        
        compressible_extensions = ['.pak', '.dat', '.json', '.js', '.css']
        
        for file_path in self.chrome_dir.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix.lower() in compressible_extensions and
                file_path.stat().st_size > 1024):  # Only compress files > 1KB
                
                try:
                    # Try LZMA compression
                    original_size = file_path.stat().st_size
                    compressed_path = file_path.with_suffix(file_path.suffix + '.tmp')
                    
                    with open(file_path, 'rb') as f_in:
                        with lzma.open(compressed_path, 'wb', preset=6) as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    compressed_size = compressed_path.stat().st_size
                    
                    # Only keep compression if it saves significant space
                    if compressed_size < original_size * 0.8:  # 20% savings minimum
                        compressed_path.replace(file_path)
                        self.compressed_files.append(str(file_path))
                    else:
                        compressed_path.unlink()
                        
                except Exception as e:
                    self.warnings.append(f"Compression failed for {file_path}: {e}")
                    if compressed_path.exists():
                        compressed_path.unlink()
    
    def _optimize_images(self) -> None:
        """Optimize image files."""
        logger.info("Optimizing images...")
        
        image_extensions = ['.png', '.jpg', '.jpeg', '.ico', '.bmp']
        
        for file_path in self.chrome_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                try:
                    # Use optipng for PNG optimization if available
                    if file_path.suffix.lower() == '.png' and shutil.which('optipng'):
                        result = subprocess.run(['optipng', '-o7', str(file_path)], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            self.compressed_files.append(str(file_path))
                    
                    # Use jpegoptim for JPEG optimization if available
                    elif (file_path.suffix.lower() in ['.jpg', '.jpeg'] and 
                          shutil.which('jpegoptim')):
                        result = subprocess.run(['jpegoptim', '--strip-all', str(file_path)], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            self.compressed_files.append(str(file_path))
                            
                except Exception as e:
                    self.warnings.append(f"Image optimization failed for {file_path}: {e}")
    
    def _upx_compress_binaries(self) -> None:
        """Compress binaries with UPX."""
        logger.info("Compressing binaries with UPX...")
        
        if not shutil.which('upx'):
            self.warnings.append("UPX not found, skipping binary compression")
            return
        
        binary_extensions = ['.exe', '.dll']
        
        for file_path in self.chrome_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in binary_extensions:
                try:
                    # Skip critical system files
                    if file_path.name.lower() in ['chrome.exe', 'chrome.dll']:
                        continue
                    
                    result = subprocess.run(['upx', '--best', '--lzma', str(file_path)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.compressed_files.append(str(file_path))
                    else:
                        self.warnings.append(f"UPX compression failed for {file_path}")
                        
                except Exception as e:
                    self.warnings.append(f"UPX compression error for {file_path}: {e}")


class PackageOptimizer:
    """Optimizes the entire Adam Browser package."""
    
    def __init__(self, package_dir: Path, config: OptimizationConfig):
        """Initialize package optimizer."""
        self.package_dir = package_dir
        self.config = config
        self.chrome_optimizer = None
        
        # Find Chrome directory in package
        chrome_dir = package_dir / "Google" / "Chrome"
        if chrome_dir.exists():
            self.chrome_optimizer = ChromeOptimizer(chrome_dir, config)
    
    def optimize(self) -> OptimizationResult:
        """Optimize the entire package."""
        logger.info(f"Starting package optimization: {self.package_dir}")
        
        original_size = self._get_directory_size(self.package_dir)
        
        total_removed = []
        total_compressed = []
        total_errors = []
        total_warnings = []
        
        # Optimize Chrome if present
        if self.chrome_optimizer:
            chrome_result = self.chrome_optimizer.optimize()
            total_removed.extend(chrome_result.removed_files)
            total_compressed.extend(chrome_result.compressed_files)
            total_errors.extend(chrome_result.errors)
            total_warnings.extend(chrome_result.warnings)
        
        # Remove unnecessary package components
        if self.config.remove_samples:
            self._remove_samples(total_removed, total_errors)
        
        if self.config.remove_tests:
            self._remove_tests(total_removed, total_errors)
        
        if self.config.remove_documentation and not self.config.preserve_functionality:
            self._remove_documentation(total_removed, total_errors)
        
        if self.config.remove_source_maps:
            self._remove_source_maps(total_removed, total_errors)
        
        # Optimize Python bytecode
        self._optimize_python_files(total_compressed, total_errors)
        
        optimized_size = self._get_directory_size(self.package_dir)
        savings = original_size - optimized_size
        savings_percentage = (savings / original_size) * 100 if original_size > 0 else 0
        
        result = OptimizationResult(
            original_size=original_size,
            optimized_size=optimized_size,
            savings=savings,
            savings_percentage=savings_percentage,
            removed_files=total_removed,
            compressed_files=total_compressed,
            errors=total_errors,
            warnings=total_warnings
        )
        
        logger.info(f"Package optimization completed: {savings / 1024 / 1024:.1f} MB saved ({savings_percentage:.1f}%)")
        
        return result
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def _remove_samples(self, removed_files: List[str], errors: List[str]) -> None:
        """Remove sample files and directories."""
        sample_patterns = ['**/samples/**', '**/examples/**', '**/demo/**']
        
        for pattern in sample_patterns:
            for path in self.package_dir.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                        removed_files.append(str(path))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        removed_files.append(str(path))
                except Exception as e:
                    errors.append(f"Failed to remove sample {path}: {e}")
    
    def _remove_tests(self, removed_files: List[str], errors: List[str]) -> None:
        """Remove test files and directories."""
        test_patterns = ['**/test/**', '**/tests/**', '**/*test*.py', '**/unittest/**']
        
        for pattern in test_patterns:
            for path in self.package_dir.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                        removed_files.append(str(path))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        removed_files.append(str(path))
                except Exception as e:
                    errors.append(f"Failed to remove test {path}: {e}")
    
    def _remove_documentation(self, removed_files: List[str], errors: List[str]) -> None:
        """Remove documentation files."""
        doc_patterns = ['**/docs/**', '**/*.md', '**/*.rst', '**/*.txt']
        
        # Keep essential files
        keep_files = {'README.md', 'LICENSE', 'requirements.txt'}
        
        for pattern in doc_patterns:
            for path in self.package_dir.glob(pattern):
                if path.name not in keep_files:
                    try:
                        if path.is_file():
                            path.unlink()
                            removed_files.append(str(path))
                        elif path.is_dir():
                            shutil.rmtree(path)
                            removed_files.append(str(path))
                    except Exception as e:
                        errors.append(f"Failed to remove doc {path}: {e}")
    
    def _remove_source_maps(self, removed_files: List[str], errors: List[str]) -> None:
        """Remove source map files."""
        for path in self.package_dir.rglob("*.map"):
            try:
                path.unlink()
                removed_files.append(str(path))
            except Exception as e:
                errors.append(f"Failed to remove source map {path}: {e}")
    
    def _optimize_python_files(self, compressed_files: List[str], errors: List[str]) -> None:
        """Optimize Python files by compiling to bytecode."""
        import py_compile
        
        for py_file in self.package_dir.rglob("*.py"):
            try:
                # Compile to .pyc
                pyc_file = py_file.with_suffix('.pyc')
                py_compile.compile(py_file, pyc_file, doraise=True)
                
                # Remove original .py file if compilation successful
                py_file.unlink()
                compressed_files.append(str(py_file))
                
            except Exception as e:
                errors.append(f"Failed to compile {py_file}: {e}")


def main():
    """Main entry point for size optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adam Browser Size Optimizer")
    parser.add_argument("target", type=Path, help="Target directory to optimize")
    parser.add_argument("--chrome-only", action="store_true", help="Optimize Chrome only")
    parser.add_argument("--aggressive", action="store_true", help="Aggressive optimization")
    parser.add_argument("--keep-docs", action="store_true", help="Keep documentation")
    parser.add_argument("--use-upx", action="store_true", help="Use UPX compression")
    parser.add_argument("--keep-locales", nargs="+", default=["en-US"], help="Locales to keep")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Create optimization config
    config = OptimizationConfig(
        aggressive_optimization=args.aggressive,
        remove_documentation=not args.keep_docs,
        use_upx_compression=args.use_upx,
        keep_locales=args.keep_locales
    )
    
    try:
        if args.chrome_only:
            # Optimize Chrome only
            chrome_dir = args.target / "Google" / "Chrome"
            if not chrome_dir.exists():
                chrome_dir = args.target  # Assume target is Chrome directory
            
            optimizer = ChromeOptimizer(chrome_dir, config)
        else:
            # Optimize entire package
            optimizer = PackageOptimizer(args.target, config)
        
        result = optimizer.optimize()
        
        # Report results
        print(f"\n{'='*60}")
        print("OPTIMIZATION RESULTS")
        print(f"{'='*60}")
        print(f"Original size: {result.original_size / 1024 / 1024:.1f} MB")
        print(f"Optimized size: {result.optimized_size / 1024 / 1024:.1f} MB")
        print(f"Space saved: {result.savings / 1024 / 1024:.1f} MB ({result.savings_percentage:.1f}%)")
        print(f"Files removed: {len(result.removed_files)}")
        print(f"Files compressed: {len(result.compressed_files)}")
        
        if result.errors:
            print(f"\nErrors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"  ❌ {error}")
        
        if result.warnings:
            print(f"\nWarnings: {len(result.warnings)}")
            for warning in result.warnings[:5]:  # Show first 5 warnings
                print(f"  ⚠️ {warning}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
