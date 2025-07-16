"""
Adam Browser GUI Launcher

Simplified launcher for the Adam Browser GUI that handles import issues
and provides a working interface.
"""

import wx
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class AdamBrowserFrame(wx.Frame):
    """Main Adam Browser GUI Frame"""
    
    def __init__(self):
        super().__init__(None, title="Adam Browser v1.0.0", size=(1200, 800))
        
        # Set icon if available
        try:
            icon_path = current_dir / "headico.png"
            if icon_path.exists():
                icon = wx.Icon(str(icon_path), wx.BITMAP_TYPE_PNG)
                self.SetIcon(icon)
        except:
            pass
        
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        self.create_main_panel()
        
        # Center window
        self.Center()
        
        # Agent status
        self.agent_running = False
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New Session\tCtrl+N")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q")
        menubar.Append(file_menu, "&File")
        
        # Agent menu
        agent_menu = wx.Menu()
        self.menu_start = agent_menu.Append(wx.ID_ANY, "&Start Agent\tF5")
        self.menu_stop = agent_menu.Append(wx.ID_ANY, "S&top Agent\tF6")
        menubar.Append(agent_menu, "&Agent")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_start_agent, self.menu_start)
        self.Bind(wx.EVT_MENU, self.on_stop_agent, self.menu_stop)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = self.CreateToolBar()
        
        toolbar.AddTool(wx.ID_ANY, "Start", 
                       wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR),
                       "Start Agent")
        toolbar.AddTool(wx.ID_ANY, "Stop",
                       wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR),
                       "Stop Agent")
        toolbar.AddSeparator()
        toolbar.AddTool(wx.ID_ANY, "Screenshot",
                       wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR),
                       "Take Screenshot")
        
        toolbar.Realize()
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-1, 150, 100])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("Agent: Stopped", 1)
        self.status_bar.SetStatusText("v1.0.0", 2)
    
    def create_main_panel(self):
        """Create main panel"""
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Command input section
        command_box = wx.StaticBox(main_panel, label="Command Input")
        command_sizer = wx.StaticBoxSizer(command_box, wx.VERTICAL)
        
        # Command input
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.command_input = wx.TextCtrl(main_panel, style=wx.TE_PROCESS_ENTER, size=(-1, 30))
        self.command_input.SetHint("Enter natural language command (e.g., 'Go to google.com')")
        
        self.send_button = wx.Button(main_panel, label="Send", size=(80, 30))
        self.send_button.SetDefault()
        
        input_sizer.Add(self.command_input, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_button, 0, wx.EXPAND)
        
        command_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Quick commands
        quick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        quick_commands = [
            ("Go to Google", "go to google.com"),
            ("Take Screenshot", "take screenshot"),
            ("Scroll Down", "scroll down"),
            ("Get Directions", "get directions to downtown"),
        ]
        
        for label, command in quick_commands:
            btn = wx.Button(main_panel, label=label, size=(120, 25))
            btn.Bind(wx.EVT_BUTTON, lambda evt, cmd=command: self.send_quick_command(cmd))
            quick_sizer.Add(btn, 0, wx.RIGHT, 5)
        
        command_sizer.Add(quick_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Splitter for log and config
        splitter = wx.SplitterWindow(main_panel, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        
        # Log viewer
        log_panel = wx.Panel(splitter)
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        
        log_label = wx.StaticText(log_panel, label="Activity Log")
        log_sizer.Add(log_label, 0, wx.ALL, 5)
        
        self.log_text = wx.TextCtrl(log_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        log_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        
        log_panel.SetSizer(log_sizer)
        
        # Config panel
        config_panel = wx.Panel(splitter)
        config_sizer = wx.BoxSizer(wx.VERTICAL)
        
        config_label = wx.StaticText(config_panel, label="Configuration")
        config_sizer.Add(config_label, 0, wx.ALL, 5)
        
        # Simple config display
        config_text = wx.TextCtrl(config_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        config_text.SetValue("""Adam Browser Configuration:

Browser: Chrome (System)
Headless: False
Timeout: 30 seconds
AI Model: BERT (Local)
Debug Mode: False

Status: Ready for commands
""")
        config_sizer.Add(config_text, 1, wx.EXPAND | wx.ALL, 5)
        
        config_panel.SetSizer(config_sizer)
        
        # Split panels
        splitter.SplitHorizontally(log_panel, config_panel, -200)
        splitter.SetMinimumPaneSize(150)
        
        # Add to main sizer
        main_sizer.Add(command_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 5)
        
        main_panel.SetSizer(main_sizer)
        
        # Bind events
        self.command_input.Bind(wx.EVT_TEXT_ENTER, self.on_send_command)
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send_command)
        
        # Add initial log message
        self.add_log("Adam Browser GUI started successfully!")
        self.add_log("Enter commands above or click quick command buttons.")
        self.add_log("Note: This is a demo version - full agent integration pending.")
    
    def add_log(self, message):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.AppendText(log_line)
    
    def on_send_command(self, event):
        """Handle send command"""
        command = self.command_input.GetValue().strip()
        if command:
            self.add_log(f"Command: {command}")
            if self.agent_running:
                self.add_log("Processing command...")
                # Simulate command processing
                wx.CallLater(1000, lambda: self.add_log("Command completed (demo mode)"))
            else:
                self.add_log("Agent not running - start agent first")
            self.command_input.Clear()
        else:
            self.add_log("Please enter a command")
    
    def send_quick_command(self, command):
        """Send quick command"""
        self.command_input.SetValue(command)
        self.on_send_command(None)
    
    def on_start_agent(self, event):
        """Start agent"""
        if not self.agent_running:
            self.agent_running = True
            self.status_bar.SetStatusText("Agent: Running", 1)
            self.add_log("Agent started successfully!")
            self.add_log("Ready to process commands.")
    
    def on_stop_agent(self, event):
        """Stop agent"""
        if self.agent_running:
            self.agent_running = False
            self.status_bar.SetStatusText("Agent: Stopped", 1)
            self.add_log("Agent stopped.")
    
    def on_exit(self, event):
        """Exit application"""
        self.Close()
    
    def on_about(self, event):
        """Show about dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Adam Browser")
        info.SetVersion("1.0.0")
        info.SetDescription("Autonomous AI Agent Browser Application")
        info.SetCopyright("© 2024 Adam Browser Team")
        
        wx.adv.AboutBox(info)

class AdamBrowserApp(wx.App):
    """Adam Browser Application"""
    
    def OnInit(self):
        frame = AdamBrowserFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = AdamBrowserApp()
    app.MainLoop()
