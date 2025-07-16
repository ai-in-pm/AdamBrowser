"""
Log Viewer for Adam Browser GUI

Provides real-time log display with filtering, search, and export capabilities.
"""

import wx
import threading
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger


class LogViewer(wx.Panel):
    """
    Real-time log viewer with filtering and search capabilities.
    
    Displays application logs with color coding, timestamps,
    and filtering options for different log levels.
    """
    
    def __init__(self, parent):
        """Initialize the log viewer."""
        super().__init__(parent)
        
        # Log storage
        self.log_entries: List[Dict[str, Any]] = []
        self.max_entries = 1000
        self.auto_scroll = True
        
        # Filter settings
        self.show_debug = False
        self.show_info = True
        self.show_warning = True
        self.show_error = True
        self.filter_text = ""
        
        # Create GUI
        self._create_controls()
        self._create_layout()
        self._bind_events()
        
        # Colors for different log levels
        self.colors = {
            'DEBUG': wx.Colour(128, 128, 128),    # Gray
            'INFO': wx.Colour(0, 0, 0),           # Black
            'WARNING': wx.Colour(255, 140, 0),    # Orange
            'ERROR': wx.Colour(255, 0, 0),        # Red
            'CRITICAL': wx.Colour(139, 0, 0),     # Dark Red
        }
        
        logger.info("Log viewer initialized")
    
    def _create_controls(self):
        """Create log viewer controls."""
        # Toolbar
        self.toolbar = wx.Panel(self)
        
        # Filter controls
        self.chk_debug = wx.CheckBox(self.toolbar, label="Debug")
        self.chk_info = wx.CheckBox(self.toolbar, label="Info")
        self.chk_warning = wx.CheckBox(self.toolbar, label="Warning")
        self.chk_error = wx.CheckBox(self.toolbar, label="Error")
        
        # Set initial states
        self.chk_debug.SetValue(self.show_debug)
        self.chk_info.SetValue(self.show_info)
        self.chk_warning.SetValue(self.show_warning)
        self.chk_error.SetValue(self.show_error)
        
        # Search box
        self.search_ctrl = wx.SearchCtrl(self.toolbar, size=(200, -1))
        self.search_ctrl.SetDescriptiveText("Filter logs...")
        
        # Control buttons
        self.btn_clear = wx.Button(self.toolbar, label="Clear", size=(60, -1))
        self.btn_export = wx.Button(self.toolbar, label="Export", size=(60, -1))
        self.btn_auto_scroll = wx.ToggleButton(self.toolbar, label="Auto Scroll", size=(80, -1))
        self.btn_auto_scroll.SetValue(self.auto_scroll)
        
        # Log display
        self.log_ctrl = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        
        # Set monospace font for better readability
        font = wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_ctrl.SetFont(font)
    
    def _create_layout(self):
        """Create the layout."""
        # Toolbar layout
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Filter checkboxes
        filter_box = wx.StaticBox(self.toolbar, label="Show Levels")
        filter_sizer = wx.StaticBoxSizer(filter_box, wx.HORIZONTAL)
        filter_sizer.Add(self.chk_debug, 0, wx.ALL, 2)
        filter_sizer.Add(self.chk_info, 0, wx.ALL, 2)
        filter_sizer.Add(self.chk_warning, 0, wx.ALL, 2)
        filter_sizer.Add(self.chk_error, 0, wx.ALL, 2)
        
        toolbar_sizer.Add(filter_sizer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.Add(wx.StaticLine(self.toolbar, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        toolbar_sizer.Add(wx.StaticText(self.toolbar, label="Search:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.Add(self.search_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.AddStretchSpacer()
        toolbar_sizer.Add(self.btn_auto_scroll, 0, wx.ALL, 2)
        toolbar_sizer.Add(self.btn_clear, 0, wx.ALL, 2)
        toolbar_sizer.Add(self.btn_export, 0, wx.ALL, 2)
        
        self.toolbar.SetSizer(toolbar_sizer)
        
        # Main layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)
        main_sizer.Add(self.log_ctrl, 1, wx.EXPAND | wx.ALL, 2)
        
        self.SetSizer(main_sizer)
    
    def _bind_events(self):
        """Bind event handlers."""
        # Filter checkboxes
        self.chk_debug.Bind(wx.EVT_CHECKBOX, self._on_filter_change)
        self.chk_info.Bind(wx.EVT_CHECKBOX, self._on_filter_change)
        self.chk_warning.Bind(wx.EVT_CHECKBOX, self._on_filter_change)
        self.chk_error.Bind(wx.EVT_CHECKBOX, self._on_filter_change)
        
        # Search control
        self.search_ctrl.Bind(wx.EVT_TEXT, self._on_search_change)
        
        # Buttons
        self.btn_clear.Bind(wx.EVT_BUTTON, self._on_clear)
        self.btn_export.Bind(wx.EVT_BUTTON, self._on_export)
        self.btn_auto_scroll.Bind(wx.EVT_TOGGLEBUTTON, self._on_auto_scroll_toggle)
    
    def add_log(self, message: str, level: str = "INFO", timestamp: Optional[datetime] = None):
        """
        Add a log entry.
        
        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            timestamp: Optional timestamp (current time if None)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message
        }
        
        # Add to storage
        self.log_entries.append(log_entry)
        
        # Limit entries
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries:]
        
        # Update display
        wx.CallAfter(self._update_display)
    
    def _update_display(self):
        """Update the log display with current filters."""
        # Clear current display
        self.log_ctrl.Clear()
        
        # Filter entries
        filtered_entries = self._filter_entries()
        
        # Add filtered entries
        for entry in filtered_entries:
            self._append_log_entry(entry)
        
        # Auto scroll to bottom
        if self.auto_scroll:
            self.log_ctrl.SetInsertionPointEnd()
    
    def _filter_entries(self) -> List[Dict[str, Any]]:
        """Filter log entries based on current settings."""
        filtered = []
        
        for entry in self.log_entries:
            # Level filter
            level = entry['level']
            if level == 'DEBUG' and not self.show_debug:
                continue
            if level == 'INFO' and not self.show_info:
                continue
            if level == 'WARNING' and not self.show_warning:
                continue
            if level in ['ERROR', 'CRITICAL'] and not self.show_error:
                continue
            
            # Text filter
            if self.filter_text:
                if self.filter_text.lower() not in entry['message'].lower():
                    continue
            
            filtered.append(entry)
        
        return filtered
    
    def _append_log_entry(self, entry: Dict[str, Any]):
        """Append a single log entry to the display."""
        timestamp_str = entry['timestamp'].strftime("%H:%M:%S")
        level = entry['level']
        message = entry['message']
        
        # Format log line
        log_line = f"[{timestamp_str}] {level:8} | {message}\n"
        
        # Get color for level
        color = self.colors.get(level, wx.Colour(0, 0, 0))
        
        # Set text color and append
        self.log_ctrl.SetDefaultStyle(wx.TextAttr(color))
        self.log_ctrl.AppendText(log_line)
    
    def _on_filter_change(self, event):
        """Handle filter checkbox changes."""
        self.show_debug = self.chk_debug.GetValue()
        self.show_info = self.chk_info.GetValue()
        self.show_warning = self.chk_warning.GetValue()
        self.show_error = self.chk_error.GetValue()
        
        self._update_display()
    
    def _on_search_change(self, event):
        """Handle search text changes."""
        self.filter_text = self.search_ctrl.GetValue()
        self._update_display()
    
    def _on_clear(self, event):
        """Handle clear button."""
        self.log_entries.clear()
        self.log_ctrl.Clear()
    
    def _on_export(self, event):
        """Handle export button."""
        try:
            # File dialog
            with wx.FileDialog(
                self,
                "Export logs",
                wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            ) as dialog:
                
                if dialog.ShowModal() == wx.ID_OK:
                    filepath = dialog.GetPath()
                    
                    # Export filtered entries
                    filtered_entries = self._filter_entries()
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Adam Browser Log Export\n")
                        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total entries: {len(filtered_entries)}\n")
                        f.write("-" * 50 + "\n\n")
                        
                        for entry in filtered_entries:
                            timestamp_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"[{timestamp_str}] {entry['level']:8} | {entry['message']}\n")
                    
                    wx.MessageBox(f"Logs exported to {filepath}", "Export Complete", wx.OK | wx.ICON_INFORMATION)
                    
        except Exception as e:
            wx.MessageBox(f"Export failed: {str(e)}", "Export Error", wx.OK | wx.ICON_ERROR)
    
    def _on_auto_scroll_toggle(self, event):
        """Handle auto scroll toggle."""
        self.auto_scroll = self.btn_auto_scroll.GetValue()
    
    def get_log_count(self) -> int:
        """Get total number of log entries."""
        return len(self.log_entries)
    
    def get_filtered_count(self) -> int:
        """Get number of filtered log entries."""
        return len(self._filter_entries())
    
    def set_max_entries(self, max_entries: int):
        """Set maximum number of log entries to keep."""
        self.max_entries = max_entries
        
        # Trim if necessary
        if len(self.log_entries) > max_entries:
            self.log_entries = self.log_entries[-max_entries:]
            self._update_display()


# Example usage for testing
if __name__ == "__main__":
    app = wx.App()
    
    frame = wx.Frame(None, title="Log Viewer Test", size=(800, 600))
    log_viewer = LogViewer(frame)
    
    # Add some test logs
    log_viewer.add_log("Application started", "INFO")
    log_viewer.add_log("Debug information", "DEBUG")
    log_viewer.add_log("Warning message", "WARNING")
    log_viewer.add_log("Error occurred", "ERROR")
    log_viewer.add_log("Critical failure", "CRITICAL")
    
    frame.Show()
    app.MainLoop()
