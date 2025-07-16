"""
Splash Screen for Adam Browser

Displays application logo and loading progress during startup.
"""

import wx
import wx.adv
from pathlib import Path
from loguru import logger

from ..config import config


class SplashScreen(wx.adv.SplashScreen):
    """
    Splash screen displayed during application startup.
    
    Shows the Adam Browser logo and loading progress with
    a professional appearance and smooth animations.
    """
    
    def __init__(self):
        """Initialize the splash screen."""
        # Create splash bitmap
        bitmap = self._create_splash_bitmap()
        
        # Initialize splash screen
        super().__init__(
            bitmap,
            wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
            3000,  # 3 seconds timeout
            None,
            style=wx.BORDER_SIMPLE | wx.FRAME_NO_TASKBAR
        )
        
        # Bind events
        self.Bind(wx.EVT_CLOSE, self._on_close)
        
        logger.info("Splash screen initialized")
    
    def _create_splash_bitmap(self) -> wx.Bitmap:
        """Create the splash screen bitmap."""
        try:
            # Try to load the application icon
            icon_path = Path("headico.png")
            if icon_path.exists():
                # Load and scale the icon
                image = wx.Image(str(icon_path), wx.BITMAP_TYPE_PNG)
                
                # Scale to appropriate size
                image = image.Scale(128, 128, wx.IMAGE_QUALITY_HIGH)
                
                # Create a larger bitmap for the splash
                splash_width = 400
                splash_height = 300
                
                # Create bitmap with background
                bitmap = wx.Bitmap(splash_width, splash_height)
                dc = wx.MemoryDC(bitmap)
                
                # Fill background with gradient
                dc.GradientFillLinear(
                    wx.Rect(0, 0, splash_width, splash_height),
                    wx.Colour(240, 248, 255),  # Alice blue
                    wx.Colour(176, 196, 222),  # Light steel blue
                    wx.SOUTH
                )
                
                # Draw icon
                icon_bitmap = wx.Bitmap(image)
                icon_x = (splash_width - 128) // 2
                icon_y = 50
                dc.DrawBitmap(icon_bitmap, icon_x, icon_y, True)
                
                # Draw text
                dc.SetTextForeground(wx.Colour(25, 25, 112))  # Midnight blue
                
                # Title
                title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                dc.SetFont(title_font)
                title_text = config.app_name
                title_size = dc.GetTextExtent(title_text)
                title_x = (splash_width - title_size.width) // 2
                title_y = icon_y + 128 + 20
                dc.DrawText(title_text, title_x, title_y)
                
                # Version
                version_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                dc.SetFont(version_font)
                version_text = f"Version {config.version}"
                version_size = dc.GetTextExtent(version_text)
                version_x = (splash_width - version_size.width) // 2
                version_y = title_y + title_size.height + 10
                dc.DrawText(version_text, version_x, version_y)
                
                # Subtitle
                subtitle_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
                dc.SetFont(subtitle_font)
                subtitle_text = "Autonomous AI Agent Browser"
                subtitle_size = dc.GetTextExtent(subtitle_text)
                subtitle_x = (splash_width - subtitle_size.width) // 2
                subtitle_y = version_y + version_size.height + 5
                dc.DrawText(subtitle_text, subtitle_x, subtitle_y)
                
                # Loading text
                loading_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                dc.SetFont(loading_font)
                loading_text = "Loading..."
                loading_size = dc.GetTextExtent(loading_text)
                loading_x = (splash_width - loading_size.width) // 2
                loading_y = splash_height - 30
                dc.DrawText(loading_text, loading_x, loading_y)
                
                # Draw border
                dc.SetPen(wx.Pen(wx.Colour(100, 149, 237), 2))  # Cornflower blue
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawRectangle(0, 0, splash_width, splash_height)
                
                dc.SelectObject(wx.NullBitmap)
                
                return bitmap
                
            else:
                # Fallback: create simple text splash
                return self._create_text_splash()
                
        except Exception as e:
            logger.warning(f"Failed to create splash bitmap: {e}")
            return self._create_text_splash()
    
    def _create_text_splash(self) -> wx.Bitmap:
        """Create a simple text-based splash screen."""
        splash_width = 400
        splash_height = 200
        
        bitmap = wx.Bitmap(splash_width, splash_height)
        dc = wx.MemoryDC(bitmap)
        
        # Fill background
        dc.SetBackground(wx.Brush(wx.Colour(240, 248, 255)))
        dc.Clear()
        
        # Draw text
        dc.SetTextForeground(wx.Colour(25, 25, 112))
        
        # Title
        title_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(title_font)
        title_text = config.app_name
        title_size = dc.GetTextExtent(title_text)
        title_x = (splash_width - title_size.width) // 2
        title_y = 60
        dc.DrawText(title_text, title_x, title_y)
        
        # Version
        version_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(version_font)
        version_text = f"Version {config.version}"
        version_size = dc.GetTextExtent(version_text)
        version_x = (splash_width - version_size.width) // 2
        version_y = title_y + title_size.height + 10
        dc.DrawText(version_text, version_x, version_y)
        
        # Subtitle
        subtitle_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(subtitle_font)
        subtitle_text = "Autonomous AI Agent Browser"
        subtitle_size = dc.GetTextExtent(subtitle_text)
        subtitle_x = (splash_width - subtitle_size.width) // 2
        subtitle_y = version_y + version_size.height + 20
        dc.DrawText(subtitle_text, subtitle_x, subtitle_y)
        
        # Draw border
        dc.SetPen(wx.Pen(wx.Colour(100, 149, 237), 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, splash_width, splash_height)
        
        dc.SelectObject(wx.NullBitmap)
        
        return bitmap
    
    def _on_close(self, event):
        """Handle close event."""
        self.Destroy()
        event.Skip()


# Simple splash screen without advanced features (fallback)
class SimpleSplashScreen(wx.Frame):
    """
    Simple splash screen fallback for systems without wx.adv.SplashScreen.
    """
    
    def __init__(self):
        """Initialize simple splash screen."""
        super().__init__(
            None,
            title="",
            style=wx.FRAME_NO_TASKBAR | wx.BORDER_SIMPLE,
            size=(400, 200)
        )
        
        # Center on screen
        self.Center()
        
        # Create panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(240, 248, 255))
        
        # Create sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add some spacing
        sizer.AddSpacer(40)
        
        # Title
        title = wx.StaticText(panel, label=config.app_name)
        title_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(25, 25, 112))
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Version
        version = wx.StaticText(panel, label=f"Version {config.version}")
        version_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        version.SetFont(version_font)
        version.SetForegroundColour(wx.Colour(25, 25, 112))
        sizer.Add(version, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Subtitle
        subtitle = wx.StaticText(panel, label="Autonomous AI Agent Browser")
        subtitle_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(wx.Colour(25, 25, 112))
        sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Loading
        loading = wx.StaticText(panel, label="Loading...")
        loading_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        loading.SetFont(loading_font)
        loading.SetForegroundColour(wx.Colour(25, 25, 112))
        sizer.Add(loading, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        # Auto-close timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self.timer.Start(3000, oneShot=True)  # 3 seconds
        
        logger.info("Simple splash screen initialized")
    
    def _on_timer(self, event):
        """Handle timer event to close splash."""
        self.Close()


# Factory function to create appropriate splash screen
def create_splash_screen():
    """
    Create appropriate splash screen based on available features.
    
    Returns:
        Splash screen instance
    """
    try:
        # Try to create advanced splash screen
        return SplashScreen()
    except Exception as e:
        logger.warning(f"Advanced splash screen not available: {e}")
        try:
            # Fallback to simple splash screen
            return SimpleSplashScreen()
        except Exception as e2:
            logger.error(f"Failed to create splash screen: {e2}")
            return None


# Example usage for testing
if __name__ == "__main__":
    app = wx.App()
    
    splash = create_splash_screen()
    if splash:
        splash.Show()
        
        # Create main window after splash
        def create_main_window():
            frame = wx.Frame(None, title="Main Window", size=(800, 600))
            frame.Show()
        
        wx.CallLater(3500, create_main_window)
        
        app.MainLoop()
    else:
        print("Failed to create splash screen")
