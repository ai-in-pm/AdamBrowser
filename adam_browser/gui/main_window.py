"""
Main Window for Adam Browser GUI

Provides the primary interface for controlling the Adam Browser agent
with real-time status updates, command input, and log viewing.
"""

import wx
import asyncio
import threading
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger

from ..config import config
from ..agent import AdamAgent, AgentState
from .log_viewer import LogViewer
from .config_panel import ConfigPanel
from .tray_icon import TrayIcon


class AdamMainWindow(wx.Frame):
    """
    Main application window for Adam Browser.
    
    Provides agent control, command input, real-time logging,
    and configuration management in a user-friendly interface.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__(
            None,
            title=f"{config.app_name} v{config.version}",
            size=(config.gui.window_width, config.gui.window_height)
        )
        
        # Set application icon
        self._set_icon()
        
        # Initialize agent
        self.agent: Optional[AdamAgent] = None
        self.agent_thread: Optional[threading.Thread] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # GUI components
        self.log_viewer: Optional[LogViewer] = None
        self.config_panel: Optional[ConfigPanel] = None
        self.tray_icon: Optional[TrayIcon] = None
        
        # Status tracking
        self.agent_state = AgentState.STOPPED
        self.last_command = ""
        
        # Create GUI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_main_panel()
        self._create_tray_icon()
        
        # Bind events
        self._bind_events()
        
        # Center window
        self.Center()
        
        logger.info("Main window initialized")
    
    def _set_icon(self) -> None:
        """Set the application icon."""
        try:
            icon_path = Path("headico.png")
            if icon_path.exists():
                icon = wx.Icon(str(icon_path), wx.BITMAP_TYPE_PNG)
                self.SetIcon(icon)
            else:
                logger.warning("Application icon not found: headico.png")
        except Exception as e:
            logger.error(f"Failed to set application icon: {e}")
    
    def _create_menu_bar(self) -> None:
        """Create the menu bar."""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New Session\tCtrl+N", "Start a new session")
        file_menu.Append(wx.ID_OPEN, "&Open Log\tCtrl+O", "Open log file")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit application")
        menubar.Append(file_menu, "&File")
        
        # Agent menu
        agent_menu = wx.Menu()
        self.menu_start = agent_menu.Append(wx.ID_ANY, "&Start Agent\tF5", "Start the Adam agent")
        self.menu_stop = agent_menu.Append(wx.ID_ANY, "S&top Agent\tF6", "Stop the Adam agent")
        self.menu_restart = agent_menu.Append(wx.ID_ANY, "&Restart Agent\tF7", "Restart the Adam agent")
        agent_menu.AppendSeparator()
        agent_menu.Append(wx.ID_ANY, "&Clear History", "Clear command history")
        menubar.Append(agent_menu, "&Agent")
        
        # Tools menu
        tools_menu = wx.Menu()
        tools_menu.Append(wx.ID_ANY, "&Configuration\tCtrl+,", "Open configuration")
        tools_menu.Append(wx.ID_ANY, "&Screenshot\tF12", "Take screenshot")
        tools_menu.AppendSeparator()
        tools_menu.Append(wx.ID_ANY, "&Metrics", "View performance metrics")
        menubar.Append(tools_menu, "&Tools")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About", "About Adam Browser")
        help_menu.Append(wx.ID_HELP, "&Help\tF1", "Show help")
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
    
    def _create_toolbar(self) -> None:
        """Create the toolbar."""
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_TEXT)
        
        # Agent control buttons
        self.btn_start = toolbar.AddTool(
            wx.ID_ANY, "Start", 
            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR),
            "Start Agent"
        )
        
        self.btn_stop = toolbar.AddTool(
            wx.ID_ANY, "Stop",
            wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR),
            "Stop Agent"
        )
        
        toolbar.AddSeparator()
        
        # Screenshot button
        toolbar.AddTool(
            wx.ID_ANY, "Screenshot",
            wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR),
            "Take Screenshot"
        )
        
        # Configuration button
        toolbar.AddTool(
            wx.ID_ANY, "Config",
            wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR),
            "Configuration"
        )
        
        toolbar.Realize()
    
    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-1, 150, 100])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("Agent: Stopped", 1)
        self.status_bar.SetStatusText("", 2)
    
    def _create_main_panel(self) -> None:
        """Create the main panel with splitter windows."""
        # Main panel
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Command input section
        command_box = wx.StaticBox(main_panel, label="Command Input")
        command_sizer = wx.StaticBoxSizer(command_box, wx.VERTICAL)
        
        # Command input field
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.command_input = wx.TextCtrl(
            main_panel, 
            style=wx.TE_PROCESS_ENTER,
            size=(-1, 30)
        )
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
            btn.Bind(wx.EVT_BUTTON, lambda evt, cmd=command: self._send_quick_command(cmd))
            quick_sizer.Add(btn, 0, wx.RIGHT, 5)
        
        command_sizer.Add(quick_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Splitter for log viewer and config
        splitter = wx.SplitterWindow(main_panel, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        
        # Log viewer
        self.log_viewer = LogViewer(splitter)
        
        # Config panel
        self.config_panel = ConfigPanel(splitter)
        
        # Split horizontally
        splitter.SplitHorizontally(self.log_viewer, self.config_panel, -200)
        splitter.SetMinimumPaneSize(150)
        
        # Add to main sizer
        main_sizer.Add(command_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 5)
        
        main_panel.SetSizer(main_sizer)
    
    def _create_tray_icon(self) -> None:
        """Create system tray icon."""
        if config.gui.minimize_to_tray:
            try:
                self.tray_icon = TrayIcon(self)
            except Exception as e:
                logger.error(f"Failed to create tray icon: {e}")
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        # Window events
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_ICONIZE, self._on_minimize)
        
        # Menu events
        self.Bind(wx.EVT_MENU, self._on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self._on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self._on_start_agent, self.menu_start)
        self.Bind(wx.EVT_MENU, self._on_stop_agent, self.menu_stop)
        self.Bind(wx.EVT_MENU, self._on_restart_agent, self.menu_restart)
        
        # Toolbar events
        self.Bind(wx.EVT_TOOL, self._on_start_agent, self.btn_start)
        self.Bind(wx.EVT_TOOL, self._on_stop_agent, self.btn_stop)
        
        # Command input events
        self.command_input.Bind(wx.EVT_TEXT_ENTER, self._on_send_command)
        self.send_button.Bind(wx.EVT_BUTTON, self._on_send_command)
        
        # Keyboard shortcuts
        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT),
            (wx.ACCEL_NORMAL, wx.WXK_F5, self.menu_start.GetId()),
            (wx.ACCEL_NORMAL, wx.WXK_F6, self.menu_stop.GetId()),
            (wx.ACCEL_NORMAL, wx.WXK_F7, self.menu_restart.GetId()),
        ])
        self.SetAcceleratorTable(accel_table)
    
    def _on_send_command(self, event) -> None:
        """Handle send command event."""
        command = self.command_input.GetValue().strip()
        if command and self.agent and self.agent_state != AgentState.STOPPED:
            self.last_command = command
            self.command_input.Clear()
            self._execute_command_async(command)
        elif not command:
            wx.MessageBox("Please enter a command", "No Command", wx.OK | wx.ICON_WARNING)
        else:
            wx.MessageBox("Agent is not running", "Agent Stopped", wx.OK | wx.ICON_WARNING)
    
    def _send_quick_command(self, command: str) -> None:
        """Send a quick command."""
        if self.agent and self.agent_state != AgentState.STOPPED:
            self.command_input.SetValue(command)
            self._execute_command_async(command)
        else:
            wx.MessageBox("Agent is not running", "Agent Stopped", wx.OK | wx.ICON_WARNING)
    
    def _execute_command_async(self, command: str) -> None:
        """Execute command asynchronously."""
        if self.event_loop and self.agent:
            # Schedule command execution in the agent's event loop
            future = asyncio.run_coroutine_threadsafe(
                self.agent.process_command(command), 
                self.event_loop
            )
            
            # Update UI
            self.status_bar.SetStatusText(f"Executing: {command[:50]}...", 0)
            self.log_viewer.add_log(f"Command: {command}", "INFO")
    
    def _on_start_agent(self, event) -> None:
        """Handle start agent event."""
        if self.agent_state == AgentState.STOPPED:
            self._start_agent()
    
    def _on_stop_agent(self, event) -> None:
        """Handle stop agent event."""
        if self.agent_state != AgentState.STOPPED:
            self._stop_agent()
    
    def _on_restart_agent(self, event) -> None:
        """Handle restart agent event."""
        self._stop_agent()
        wx.CallLater(1000, self._start_agent)  # Restart after 1 second
    
    def _start_agent(self) -> None:
        """Start the Adam agent."""
        try:
            self.log_viewer.add_log("Starting Adam Agent...", "INFO")
            
            # Create agent
            self.agent = AdamAgent()
            
            # Set up callbacks
            self.agent.set_callbacks(
                on_state_change=self._on_agent_state_change,
                on_command_complete=self._on_command_complete,
                on_error=self._on_agent_error
            )
            
            # Start agent in separate thread
            self.agent_thread = threading.Thread(target=self._run_agent, daemon=True)
            self.agent_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start agent: {e}")
            self.log_viewer.add_log(f"Failed to start agent: {e}", "ERROR")
    
    def _stop_agent(self) -> None:
        """Stop the Adam agent."""
        try:
            self.log_viewer.add_log("Stopping Adam Agent...", "INFO")
            
            if self.agent and self.event_loop:
                # Schedule agent stop in its event loop
                asyncio.run_coroutine_threadsafe(
                    self.agent.stop(), 
                    self.event_loop
                )
            
            self.agent_state = AgentState.STOPPED
            self._update_ui_state()
            
        except Exception as e:
            logger.error(f"Failed to stop agent: {e}")
            self.log_viewer.add_log(f"Failed to stop agent: {e}", "ERROR")
    
    def _run_agent(self) -> None:
        """Run the agent in its own event loop."""
        try:
            # Create new event loop for this thread
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            # Start the agent
            self.event_loop.run_until_complete(self.agent.start())
            
            # Keep the event loop running
            self.event_loop.run_forever()
            
        except Exception as e:
            logger.error(f"Agent thread error: {e}")
            wx.CallAfter(self.log_viewer.add_log, f"Agent error: {e}", "ERROR")
        finally:
            if self.event_loop:
                self.event_loop.close()
                self.event_loop = None
    
    def _on_agent_state_change(self, state: AgentState) -> None:
        """Handle agent state change."""
        self.agent_state = state
        wx.CallAfter(self._update_ui_state)
        wx.CallAfter(self.log_viewer.add_log, f"Agent state: {state.value}", "DEBUG")
    
    def _on_command_complete(self, result: Dict[str, Any]) -> None:
        """Handle command completion."""
        success = result.get('success', False)
        execution_time = result.get('execution_time', 0)
        
        status_msg = f"Command completed ({'success' if success else 'failed'}) in {execution_time:.2f}s"
        log_level = "INFO" if success else "ERROR"
        
        wx.CallAfter(self.status_bar.SetStatusText, "Ready", 0)
        wx.CallAfter(self.log_viewer.add_log, status_msg, log_level)
    
    def _on_agent_error(self, error: Exception) -> None:
        """Handle agent error."""
        error_msg = f"Agent error: {str(error)}"
        wx.CallAfter(self.log_viewer.add_log, error_msg, "ERROR")
        wx.CallAfter(self.status_bar.SetStatusText, "Error", 0)
    
    def _update_ui_state(self) -> None:
        """Update UI based on agent state."""
        is_running = self.agent_state not in [AgentState.STOPPED, AgentState.ERROR]
        
        # Update status bar
        self.status_bar.SetStatusText(f"Agent: {self.agent_state.value.title()}", 1)
        
        # Update buttons
        self.send_button.Enable(is_running)
        self.command_input.Enable(is_running)
        
        # Update menu items
        self.menu_start.Enable(not is_running)
        self.menu_stop.Enable(is_running)
        self.menu_restart.Enable(True)
    
    def _on_minimize(self, event) -> None:
        """Handle window minimize."""
        if config.gui.minimize_to_tray and self.tray_icon:
            self.Hide()
        else:
            event.Skip()
    
    def _on_close(self, event) -> None:
        """Handle window close."""
        # Stop agent if running
        if self.agent_state != AgentState.STOPPED:
            self._stop_agent()
        
        # Cleanup tray icon
        if self.tray_icon:
            self.tray_icon.Destroy()
        
        # Close window
        self.Destroy()
    
    def _on_exit(self, event) -> None:
        """Handle exit menu."""
        self.Close()
    
    def _on_about(self, event) -> None:
        """Handle about menu."""
        info = wx.adv.AboutDialogInfo()
        info.SetName(config.app_name)
        info.SetVersion(config.version)
        info.SetDescription("Autonomous AI Agent Browser Application")
        info.SetCopyright("© 2024 Adam Browser Team")
        info.SetWebSite("https://github.com/ai-in-pm/AdamBrowser")
        
        wx.adv.AboutBox(info)
