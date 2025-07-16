"""
Simple GUI test for Adam Browser
"""

import wx
import sys
from pathlib import Path

class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Adam Browser - Test GUI", size=(800, 600))
        
        # Create panel
        panel = wx.Panel(self)
        
        # Create sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add title
        title = wx.StaticText(panel, label="Adam Browser")
        title_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        
        # Add subtitle
        subtitle = wx.StaticText(panel, label="Autonomous AI Agent Browser Application")
        subtitle_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        subtitle.SetFont(subtitle_font)
        sizer.Add(subtitle, 0, wx.ALL | wx.CENTER, 10)
        
        # Add command input
        cmd_label = wx.StaticText(panel, label="Enter Command:")
        sizer.Add(cmd_label, 0, wx.ALL | wx.LEFT, 10)
        
        self.cmd_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.cmd_input.SetHint("e.g., 'Go to google.com'")
        sizer.Add(self.cmd_input, 0, wx.EXPAND | wx.ALL, 10)
        
        # Add buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_send = wx.Button(panel, label="Send Command")
        self.btn_screenshot = wx.Button(panel, label="Take Screenshot")
        self.btn_status = wx.Button(panel, label="Show Status")
        
        btn_sizer.Add(self.btn_send, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_screenshot, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_status, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        # Add log area
        log_label = wx.StaticText(panel, label="Activity Log:")
        sizer.Add(log_label, 0, wx.ALL | wx.LEFT, 10)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        
        # Set sizer
        panel.SetSizer(sizer)
        
        # Bind events
        self.btn_send.Bind(wx.EVT_BUTTON, self.on_send)
        self.btn_screenshot.Bind(wx.EVT_BUTTON, self.on_screenshot)
        self.btn_status.Bind(wx.EVT_BUTTON, self.on_status)
        self.cmd_input.Bind(wx.EVT_TEXT_ENTER, self.on_send)
        
        # Add initial log message
        self.add_log("Adam Browser GUI Test - Ready")
        
        # Center window
        self.Center()
    
    def add_log(self, message):
        """Add message to log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.AppendText(log_line)
    
    def on_send(self, event):
        """Handle send command."""
        command = self.cmd_input.GetValue().strip()
        if command:
            self.add_log(f"Command: {command}")
            self.add_log("Note: This is a test GUI - command processing not implemented")
            self.cmd_input.Clear()
        else:
            self.add_log("Please enter a command")
    
    def on_screenshot(self, event):
        """Handle screenshot button."""
        self.add_log("Screenshot requested (test mode)")
    
    def on_status(self, event):
        """Handle status button."""
        self.add_log("Status: GUI Test Mode - Agent not running")

class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
