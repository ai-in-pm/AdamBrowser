"""
Screenshot Manager for Adam Browser

Handles screenshot capture, storage, and management with automatic
naming, compression, and metadata tracking.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import Page
from loguru import logger

from ..config import config


class ScreenshotManager:
    """
    Manages screenshot capture and storage.
    
    Provides automatic screenshot capture with configurable intervals,
    intelligent naming, and metadata tracking.
    """
    
    def __init__(self, page: Page):
        """
        Initialize screenshot manager.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.screenshot_dir = Path(config.automation.screenshot_path)
        self.screenshot_count = 0
        self.last_screenshot_time = 0
        
        # Ensure screenshot directory exists
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshot metadata
        self.screenshots: List[Dict[str, Any]] = []
        
        logger.info(f"Screenshot manager initialized: {self.screenshot_dir}")
    
    async def take_screenshot(self, filename: Optional[str] = None, 
                             full_page: bool = True) -> Optional[str]:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional custom filename
            full_page: Whether to capture full page or just viewport
            
        Returns:
            str: Path to saved screenshot, or None if failed
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.screenshot_count += 1
                filename = f"screenshot_{timestamp}_{self.screenshot_count:04d}.png"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            screenshot_path = self.screenshot_dir / filename
            
            # Take screenshot
            await self.page.screenshot(
                path=str(screenshot_path),
                full_page=full_page,
                type='png'
            )
            
            # Update metadata
            await self._add_screenshot_metadata(screenshot_path, full_page)
            
            self.last_screenshot_time = time.time()
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def take_element_screenshot(self, selector: str, 
                                     filename: Optional[str] = None) -> Optional[str]:
        """
        Take a screenshot of a specific element.
        
        Args:
            selector: Element selector
            filename: Optional custom filename
            
        Returns:
            str: Path to saved screenshot, or None if failed
        """
        try:
            # Find element
            element = await self.page.wait_for_selector(selector, timeout=5000)
            if not element:
                logger.warning(f"Element not found for screenshot: {selector}")
                return None
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_selector = self._sanitize_filename(selector)
                filename = f"element_{safe_selector}_{timestamp}.png"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            screenshot_path = self.screenshot_dir / filename
            
            # Take element screenshot
            await element.screenshot(path=str(screenshot_path), type='png')
            
            # Update metadata
            await self._add_screenshot_metadata(screenshot_path, False, selector)
            
            logger.info(f"Element screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Element screenshot failed for {selector}: {e}")
            return None
    
    async def take_comparison_screenshot(self, baseline_path: str, 
                                        filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Take a screenshot and compare with baseline.
        
        Args:
            baseline_path: Path to baseline screenshot
            filename: Optional custom filename
            
        Returns:
            Dict containing comparison results, or None if failed
        """
        try:
            # Take current screenshot
            current_path = await self.take_screenshot(filename)
            if not current_path:
                return None
            
            # Compare with baseline (simplified comparison)
            baseline_size = os.path.getsize(baseline_path) if os.path.exists(baseline_path) else 0
            current_size = os.path.getsize(current_path)
            
            size_diff = abs(current_size - baseline_size)
            size_diff_percent = (size_diff / baseline_size * 100) if baseline_size > 0 else 100
            
            comparison_result = {
                'baseline_path': baseline_path,
                'current_path': current_path,
                'baseline_size': baseline_size,
                'current_size': current_size,
                'size_difference': size_diff,
                'size_difference_percent': size_diff_percent,
                'timestamp': datetime.now().isoformat(),
            }
            
            logger.info(f"Screenshot comparison completed: {size_diff_percent:.1f}% size difference")
            return comparison_result
            
        except Exception as e:
            logger.error(f"Screenshot comparison failed: {e}")
            return None
    
    async def _add_screenshot_metadata(self, screenshot_path: Path, 
                                      full_page: bool, element_selector: Optional[str] = None):
        """Add metadata for a screenshot."""
        try:
            # Get page information
            url = self.page.url
            title = await self.page.title()
            viewport = self.page.viewport_size
            
            metadata = {
                'path': str(screenshot_path),
                'filename': screenshot_path.name,
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'title': title,
                'full_page': full_page,
                'element_selector': element_selector,
                'viewport': viewport,
                'file_size': screenshot_path.stat().st_size,
            }
            
            self.screenshots.append(metadata)
            
            # Keep only recent screenshots in memory
            if len(self.screenshots) > 100:
                self.screenshots = self.screenshots[-100:]
                
        except Exception as e:
            logger.warning(f"Failed to add screenshot metadata: {e}")
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        
        # Limit length
        if len(text) > 50:
            text = text[:50]
        
        return text
    
    async def auto_screenshot_if_needed(self) -> Optional[str]:
        """
        Take automatic screenshot if interval has passed.
        
        Returns:
            str: Path to screenshot if taken, None otherwise
        """
        if config.automation.screenshot_interval <= 0:
            return None
        
        current_time = time.time()
        if current_time - self.last_screenshot_time >= config.automation.screenshot_interval:
            return await self.take_screenshot()
        
        return None
    
    def get_recent_screenshots(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent screenshot metadata.
        
        Args:
            count: Number of recent screenshots to return
            
        Returns:
            List of screenshot metadata
        """
        return self.screenshots[-count:] if self.screenshots else []
    
    def get_screenshots_for_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Get screenshots for a specific URL.
        
        Args:
            url: URL to filter by
            
        Returns:
            List of screenshot metadata for the URL
        """
        return [s for s in self.screenshots if s.get('url') == url]
    
    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        Clean up screenshots older than specified days.
        
        Args:
            days: Number of days to keep screenshots
            
        Returns:
            int: Number of screenshots deleted
        """
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for screenshot_file in self.screenshot_dir.glob("*.png"):
                if screenshot_file.stat().st_mtime < cutoff_time:
                    try:
                        screenshot_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete screenshot {screenshot_file}: {e}")
            
            # Clean up metadata
            self.screenshots = [
                s for s in self.screenshots 
                if Path(s['path']).exists()
            ]
            
            logger.info(f"Cleaned up {deleted_count} old screenshots")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Screenshot cleanup failed: {e}")
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get screenshot storage information."""
        try:
            total_size = 0
            file_count = 0
            
            for screenshot_file in self.screenshot_dir.glob("*.png"):
                total_size += screenshot_file.stat().st_size
                file_count += 1
            
            return {
                'directory': str(self.screenshot_dir),
                'file_count': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'recent_screenshots': len(self.screenshots),
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {}
    
    async def create_screenshot_gallery(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Create an HTML gallery of recent screenshots.
        
        Args:
            output_path: Optional output path for HTML file
            
        Returns:
            str: Path to created HTML file, or None if failed
        """
        try:
            if not output_path:
                output_path = self.screenshot_dir / "gallery.html"
            
            recent_screenshots = self.get_recent_screenshots(20)
            
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Adam Browser Screenshot Gallery</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .screenshot { margin: 20px 0; border: 1px solid #ccc; padding: 10px; }
        .screenshot img { max-width: 300px; max-height: 200px; }
        .metadata { margin-top: 10px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <h1>Adam Browser Screenshot Gallery</h1>
"""
            
            for screenshot in reversed(recent_screenshots):  # Most recent first
                rel_path = Path(screenshot['path']).name
                html_content += f"""
    <div class="screenshot">
        <img src="{rel_path}" alt="Screenshot">
        <div class="metadata">
            <strong>URL:</strong> {screenshot.get('url', 'Unknown')}<br>
            <strong>Title:</strong> {screenshot.get('title', 'Unknown')}<br>
            <strong>Time:</strong> {screenshot.get('timestamp', 'Unknown')}<br>
            <strong>Size:</strong> {screenshot.get('file_size', 0)} bytes
        </div>
    </div>
"""
            
            html_content += """
</body>
</html>
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Screenshot gallery created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to create screenshot gallery: {e}")
            return None
