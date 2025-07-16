#!/usr/bin/env python3
"""
Adam Browser Launcher
Run this file directly to start the Adam Browser GUI
"""

import wx
import sys
import os

class AdamBrowserGUI(wx.Frame):
    def __init__(self):
        super().__init__(None, title="🤖 Adam Browser - AI Agent Browser", size=(1000, 700))
        
        # Force window to be visible
        self.SetPosition((50, 50))
        
        # Create main panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(245, 245, 245))
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header_panel = wx.Panel(panel)
        header_panel.SetBackgroundColour(wx.Colour(70, 130, 180))
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(header_panel, label="ADAM BROWSER")
        title.SetFont(wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        subtitle = wx.StaticText(header_panel, label="Autonomous AI Agent Browser Application")
        subtitle.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        subtitle.SetForegroundColour(wx.Colour(220, 220, 220))
        
        header_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        header_sizer.Add(subtitle, 0, wx.ALL | wx.CENTER, 5)
        header_panel.SetSizer(header_sizer)
        
        # Command section
        cmd_box = wx.StaticBox(panel, label="Natural Language Commands")
        cmd_sizer = wx.StaticBoxSizer(cmd_box, wx.VERTICAL)
        
        # Command input
        self.cmd_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(-1, 40))
        self.cmd_input.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.cmd_input.SetHint("Type your command here (e.g., 'Go to google.com', 'Search for AI news', 'Take screenshot')")
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.send_btn = wx.Button(panel, label="🚀 Execute Command", size=(150, 40))
        self.send_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Quick action buttons
        quick_btns = [
            ("🌐 Go to Google", "go to google.com"),
            ("📸 Screenshot", "take screenshot"),
            ("📜 Scroll Down", "scroll down"),
            ("🗺️ Get Directions", "get directions to downtown")
        ]
        
        for label, cmd in quick_btns:
            btn = wx.Button(panel, label=label, size=(120, 30))
            btn.Bind(wx.EVT_BUTTON, lambda evt, command=cmd: self.execute_quick_command(command))
            btn_sizer.Add(btn, 0, wx.ALL, 3)
        
        cmd_sizer.Add(self.cmd_input, 0, wx.EXPAND | wx.ALL, 5)
        cmd_sizer.Add(self.send_btn, 0, wx.ALL | wx.CENTER, 5)
        cmd_sizer.Add(wx.StaticText(panel, label="Quick Actions:"), 0, wx.ALL, 5)
        cmd_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        # Status and log section
        status_box = wx.StaticBox(panel, label="Agent Status & Activity Log")
        status_sizer = wx.StaticBoxSizer(status_box, wx.VERTICAL)
        
        # Agent status
        status_panel = wx.Panel(panel)
        status_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_label = wx.StaticText(status_panel, label="Agent Status:")
        self.status_value = wx.StaticText(status_panel, label="🔴 Stopped")
        self.status_value.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        self.start_btn = wx.Button(status_panel, label="▶️ Start Agent", size=(100, 30))
        self.stop_btn = wx.Button(status_panel, label="⏹️ Stop Agent", size=(100, 30))
        
        status_panel_sizer.Add(self.status_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        status_panel_sizer.Add(self.status_value, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        status_panel_sizer.AddStretchSpacer()
        status_panel_sizer.Add(self.start_btn, 0, wx.ALL, 3)
        status_panel_sizer.Add(self.stop_btn, 0, wx.ALL, 3)
        status_panel.SetSizer(status_panel_sizer)
        
        # Activity log
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        status_sizer.Add(status_panel, 0, wx.EXPAND | wx.ALL, 5)
        status_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Add all to main sizer
        main_sizer.Add(header_panel, 0, wx.EXPAND)
        main_sizer.Add(cmd_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(status_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
        
        # Bind events
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_execute_command)
        self.cmd_input.Bind(wx.EVT_TEXT_ENTER, self.on_execute_command)
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start_agent)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_agent)
        
        # Initialize
        self.agent_running = False
        self.add_log("🚀 Adam Browser GUI initialized successfully!")
        self.add_log("💡 Enter natural language commands above to control the browser")
        self.add_log("⚠️  Note: This is a demo version - start the agent to enable full functionality")
        
        # Center and show
        self.CenterOnScreen()
        self.Show(True)
        self.Raise()
        
    def add_log(self, message):
        """Add message to activity log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.AppendText(f"[{timestamp}] {message}\n")
        
    def on_execute_command(self, event):
        """Execute user command"""
        command = self.cmd_input.GetValue().strip()
        if not command:
            self.add_log("❌ Please enter a command")
            return
            
        self.add_log(f"📝 Command: {command}")
        
        if self.agent_running:
            self.add_log("🔄 Processing command...")
            # Simulate processing
            wx.CallLater(1500, lambda: self.add_log("✅ Command completed successfully (demo mode)"))
        else:
            self.add_log("⚠️  Agent is not running - please start the agent first")
            
        self.cmd_input.Clear()
        
    def execute_quick_command(self, command):
        """Execute a quick command"""
        self.cmd_input.SetValue(command)
        self.on_execute_command(None)
        
    def on_start_agent(self, event):
        """Start the agent"""
        if not self.agent_running:
            self.agent_running = True
            self.status_value.SetLabel("🟢 Running")
            self.status_value.SetForegroundColour(wx.Colour(0, 150, 0))
            self.add_log("🟢 Agent started successfully!")
            self.add_log("🎯 Ready to process natural language commands")
            
    def on_stop_agent(self, event):
        """Stop the agent"""
        if self.agent_running:
            self.agent_running = False
            self.status_value.SetLabel("🔴 Stopped")
            self.status_value.SetForegroundColour(wx.Colour(150, 0, 0))
            self.add_log("🔴 Agent stopped")

class AdamBrowserApp(wx.App):
    def OnInit(self):
        # Create and show the main frame
        frame = AdamBrowserGUI()
        self.SetTopWindow(frame)
        return True

def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 ADAM BROWSER - AI Agent Browser Application")
    print("=" * 60)
    print("Starting GUI...")
    print("If the window doesn't appear, check your taskbar or try Alt+Tab")
    print("=" * 60)
    
    # Create and run the application
    app = AdamBrowserApp()
    app.MainLoop()
    
    print("Adam Browser GUI closed.")

if __name__ == '__main__':
    main()
