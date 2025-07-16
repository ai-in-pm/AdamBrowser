"""
System Tray Icon for Adam Browser

Provides system tray integration with context menu and notifications.
"""

import wx
import wx.adv
from pathlib import Path
from loguru import logger

from ..config import config


class TrayIcon(wx.adv.TaskBarIcon):
    """
    System tray icon for Adam Browser.
    
    Provides quick access to application functions and status
    when the main window is minimized or hidden.
    """
    
    def __init__(self, main_window):
        """
        Initialize the tray icon.
        
        Args:
            main_window: Reference to main application window
        """
        super().__init__()
        
        self.main_window = main_window
        self.agent_status = "Stopped"
        
        # Set icon
        self._set_icon()
        
        # Bind events
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self._on_left_double_click)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self._on_right_click)
        
        logger.info("Tray icon initialized")
    
    def _set_icon(self):
        """Set the tray icon."""
        try:
            # Try to load custom icon
            icon_path = Path("headico.png")
            if icon_path.exists():
                icon = wx.Icon(str(icon_path), wx.BITMAP_TYPE_PNG)
            else:
                # Use default icon
                icon = wx.Icon()
                icon.CopyFromBitmap(wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16)))
            
            # Set icon with tooltip
            tooltip = f"{config.app_name} - {self.agent_status}"
            self.SetIcon(icon, tooltip)
            
        except Exception as e:
            logger.warning(f"Failed to set tray icon: {e}")
            # Use default system icon
            icon = wx.Icon()
            self.SetIcon(icon, config.app_name)
    
    def CreatePopupMenu(self):
        """Create the context menu for the tray icon."""
        menu = wx.Menu()
        
        # Show/Hide main window
        if self.main_window.IsShown():
            menu.Append(wx.ID_ANY, "Hide Window", "Hide the main window")
            menu.Bind(wx.EVT_MENU, self._on_hide_window, id=menu.GetMenuItems()[-1].GetId())
        else:
            menu.Append(wx.ID_ANY, "Show Window", "Show the main window")
            menu.Bind(wx.EVT_MENU, self._on_show_window, id=menu.GetMenuItems()[-1].GetId())
        
        menu.AppendSeparator()
        
        # Agent controls
        agent_menu = wx.Menu()
        
        start_item = agent_menu.Append(wx.ID_ANY, "Start Agent", "Start the Adam agent")
        stop_item = agent_menu.Append(wx.ID_ANY, "Stop Agent", "Stop the Adam agent")
        restart_item = agent_menu.Append(wx.ID_ANY, "Restart Agent", "Restart the Adam agent")
        
        # Enable/disable based on agent state
        if hasattr(self.main_window, 'agent_state'):
            from ..agent import AgentState
            is_running = self.main_window.agent_state not in [AgentState.STOPPED, AgentState.ERROR]
            start_item.Enable(not is_running)
            stop_item.Enable(is_running)
            restart_item.Enable(True)
        
        menu.AppendSubMenu(agent_menu, "Agent")
        
        # Bind agent menu events
        menu.Bind(wx.EVT_MENU, self._on_start_agent, start_item)
        menu.Bind(wx.EVT_MENU, self._on_stop_agent, stop_item)
        menu.Bind(wx.EVT_MENU, self._on_restart_agent, restart_item)
        
        # Quick actions
        actions_menu = wx.Menu()
        
        screenshot_item = actions_menu.Append(wx.ID_ANY, "Take Screenshot", "Take a screenshot")
        status_item = actions_menu.Append(wx.ID_ANY, "Show Status", "Show agent status")
        
        menu.AppendSubMenu(actions_menu, "Quick Actions")
        
        # Bind action menu events
        menu.Bind(wx.EVT_MENU, self._on_screenshot, screenshot_item)
        menu.Bind(wx.EVT_MENU, self._on_show_status, status_item)
        
        menu.AppendSeparator()
        
        # Settings and help
        settings_item = menu.Append(wx.ID_ANY, "Settings", "Open settings")
        help_item = menu.Append(wx.ID_ANY, "Help", "Show help")
        about_item = menu.Append(wx.ID_ABOUT, "About", "About Adam Browser")
        
        menu.Bind(wx.EVT_MENU, self._on_settings, settings_item)
        menu.Bind(wx.EVT_MENU, self._on_help, help_item)
        menu.Bind(wx.EVT_MENU, self._on_about, about_item)
        
        menu.AppendSeparator()
        
        # Exit
        exit_item = menu.Append(wx.ID_EXIT, "Exit", "Exit Adam Browser")
        menu.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        
        return menu
    
    def _on_left_double_click(self, event):
        """Handle left double-click on tray icon."""
        if self.main_window.IsShown():
            self.main_window.Hide()
        else:
            self.main_window.Show()
            self.main_window.Raise()
    
    def _on_right_click(self, event):
        """Handle right-click on tray icon."""
        # The popup menu is automatically shown by the base class
        pass
    
    def _on_show_window(self, event):
        """Show the main window."""
        self.main_window.Show()
        self.main_window.Raise()
    
    def _on_hide_window(self, event):
        """Hide the main window."""
        self.main_window.Hide()
    
    def _on_start_agent(self, event):
        """Start the agent."""
        if hasattr(self.main_window, '_start_agent'):
            self.main_window._start_agent()
    
    def _on_stop_agent(self, event):
        """Stop the agent."""
        if hasattr(self.main_window, '_stop_agent'):
            self.main_window._stop_agent()
    
    def _on_restart_agent(self, event):
        """Restart the agent."""
        if hasattr(self.main_window, '_restart_agent'):
            self.main_window._restart_agent()
    
    def _on_screenshot(self, event):
        """Take a screenshot."""
        try:
            if hasattr(self.main_window, 'agent') and self.main_window.agent:
                # This would need to be implemented as an async call
                self.show_notification("Screenshot", "Screenshot capture initiated")
            else:
                self.show_notification("Screenshot", "Agent not running")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            self.show_notification("Screenshot", "Screenshot failed")
    
    def _on_show_status(self, event):
        """Show agent status."""
        try:
            if hasattr(self.main_window, 'agent') and self.main_window.agent:
                status = self.main_window.agent.get_status()
                message = f"State: {status['state']}\nCommands: {status['metrics']['commands_processed']}\nSuccess Rate: {status['metrics']['success_rate']:.1f}%"
            else:
                message = "Agent is not running"
            
            wx.MessageBox(message, "Agent Status", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            wx.MessageBox("Failed to get agent status", "Error", wx.OK | wx.ICON_ERROR)
    
    def _on_settings(self, event):
        """Open settings."""
        self.main_window.Show()
        self.main_window.Raise()
        # Focus on config panel if available
        if hasattr(self.main_window, 'config_panel'):
            # This would need implementation in the main window
            pass
    
    def _on_help(self, event):
        """Show help."""
        help_text = f"""
{config.app_name} v{config.version}

Quick Commands:
• Double-click tray icon to show/hide window
• Right-click for context menu
• Use natural language commands in the main window

Examples:
• "Go to google.com"
• "Search for Python tutorials"
• "Take screenshot"
• "Get directions to downtown"

For more help, visit the main application window.
        """
        
        wx.MessageBox(help_text.strip(), "Help", wx.OK | wx.ICON_INFORMATION)
    
    def _on_about(self, event):
        """Show about dialog."""
        info = wx.adv.AboutDialogInfo()
        info.SetName(config.app_name)
        info.SetVersion(config.version)
        info.SetDescription("Autonomous AI Agent Browser Application")
        info.SetCopyright("© 2024 Adam Browser Team")
        info.SetWebSite("https://github.com/ai-in-pm/AdamBrowser")
        
        wx.adv.AboutBox(info)
    
    def _on_exit(self, event):
        """Exit the application."""
        self.main_window.Close()
    
    def update_status(self, status: str):
        """
        Update the agent status displayed in tooltip.
        
        Args:
            status: New status string
        """
        self.agent_status = status
        tooltip = f"{config.app_name} - {status}"
        
        try:
            # Update tooltip
            icon = self.GetIcon()
            self.SetIcon(icon, tooltip)
        except Exception as e:
            logger.warning(f"Failed to update tray tooltip: {e}")
    
    def show_notification(self, title: str, message: str, timeout: int = 5000):
        """
        Show a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            timeout: Timeout in milliseconds
        """
        try:
            # Use balloon tooltip for notification
            self.ShowBalloon(title, message, timeout, wx.ICON_INFORMATION)
        except Exception as e:
            logger.warning(f"Failed to show notification: {e}")
            # Fallback to message box
            wx.CallAfter(wx.MessageBox, message, title, wx.OK | wx.ICON_INFORMATION)
    
    def show_error_notification(self, title: str, message: str):
        """
        Show an error notification.
        
        Args:
            title: Error title
            message: Error message
        """
        try:
            self.ShowBalloon(title, message, 10000, wx.ICON_ERROR)
        except Exception as e:
            logger.warning(f"Failed to show error notification: {e}")
            wx.CallAfter(wx.MessageBox, message, title, wx.OK | wx.ICON_ERROR)


# Example usage for testing
if __name__ == "__main__":
    class MockMainWindow:
        def __init__(self):
            self.agent_state = "Stopped"
        
        def IsShown(self):
            return True
        
        def Show(self):
            print("Show window")
        
        def Hide(self):
            print("Hide window")
        
        def Raise(self):
            print("Raise window")
        
        def Close(self):
            print("Close window")
            wx.GetApp().ExitMainLoop()
    
    app = wx.App()
    
    # Create mock main window
    main_window = MockMainWindow()
    
    # Create tray icon
    tray_icon = TrayIcon(main_window)
    
    # Show notification
    tray_icon.show_notification("Test", "Tray icon is working!")
    
    app.MainLoop()
