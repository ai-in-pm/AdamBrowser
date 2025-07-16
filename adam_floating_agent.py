"""
Adam Browser - Floating Robot Agent
A draggable robot icon with chat interface for natural browser interaction
"""

import wx
import wx.adv
import asyncio
import threading
import math
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Adam Browser components
from adam_browser.agent import AdamAgent, AgentState
from adam_browser.config import config
from loguru import logger

class FloatingRobotIcon(wx.Frame):
    """Draggable robot icon that floats on desktop"""
    
    def __init__(self, parent):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED | wx.STAY_ON_TOP)
        
        self.parent = parent
        self.chat_window = None
        
        # Set size and initial position (bottom right)
        self.SetSize((80, 80))
        self.position_bottom_right()
        
        # Create robot icon
        self.create_robot_icon()
        
        # Dragging variables
        self.dragging = False
        self.drag_start_pos = None
        self.click_start_time = 0
        
        # Bind events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_click)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
        # Animation timer for floating effect
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_animation_timer)
        self.animation_offset = 0
        self.animation_timer.Start(100)  # 100ms intervals
        
        self.Show()
        
    def position_bottom_right(self):
        """Position icon at bottom right above taskbar"""
        display_size = wx.GetDisplaySize()
        taskbar_height = 60  # Approximate taskbar height
        
        x = display_size.width - 100  # 20px from right edge
        y = display_size.height - taskbar_height - 100  # Above taskbar
        
        self.SetPosition((x, y))
    
    def create_robot_icon(self):
        """Create robot icon from custom image file"""
        icon_path = r"D:\science_projects\adam_browser\headico.png"

        try:
            # Load the custom icon
            if wx.Image.CanRead(icon_path):
                image = wx.Image(icon_path, wx.BITMAP_TYPE_PNG)

                # Resize to widget size while maintaining aspect ratio
                original_width = image.GetWidth()
                original_height = image.GetHeight()

                # Calculate scaling to fit within 80x80 while maintaining aspect ratio
                scale = min(80.0 / original_width, 80.0 / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                # Resize the image
                image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

                # Convert to bitmap
                self.robot_bitmap = wx.Bitmap(image)

                # Create a transparent background bitmap
                final_bitmap = wx.Bitmap(80, 80)
                dc = wx.MemoryDC(final_bitmap)

                # Set transparent background
                dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0)))
                dc.Clear()

                # Center the icon in the 80x80 space
                x_offset = (80 - new_width) // 2
                y_offset = (80 - new_height) // 2

                # Draw the custom icon
                dc.DrawBitmap(self.robot_bitmap, x_offset, y_offset, True)

                dc.SelectObject(wx.NullBitmap)

                # Set the final bitmap
                self.robot_bitmap = final_bitmap

                # Create mask for transparency (black background becomes transparent)
                mask = wx.Mask(final_bitmap, wx.Colour(0, 0, 0))
                final_bitmap.SetMask(mask)

                # Set window shape
                self.SetShape(wx.Region(final_bitmap))

                print(f"✅ Successfully loaded custom icon: {icon_path}")
                print(f"   Original size: {original_width}x{original_height}")
                print(f"   Scaled size: {new_width}x{new_height}")

            else:
                print(f"❌ Cannot read image file: {icon_path}")
                self.create_fallback_icon()

        except Exception as e:
            print(f"❌ Error loading custom icon: {e}")
            print("   Using fallback robot icon...")
            self.create_fallback_icon()

    def create_fallback_icon(self):
        """Create fallback robot icon if custom icon fails to load"""
        # Create a bitmap for the robot
        bitmap = wx.Bitmap(80, 80)
        dc = wx.MemoryDC(bitmap)

        # Set a solid background
        dc.SetBackground(wx.Brush(wx.Colour(240, 248, 255)))  # Light blue background
        dc.Clear()

        # Draw robot
        self.draw_robot(dc)

        dc.SelectObject(wx.NullBitmap)

        # Set the shape and bitmap
        self.robot_bitmap = bitmap

        # Create a proper mask for transparency
        mask = wx.Mask(bitmap, wx.Colour(240, 248, 255))
        bitmap.SetMask(mask)

        # Set window shape based on the robot drawing
        self.SetShape(wx.Region(bitmap))
    
    def draw_robot(self, dc):
        """Draw the robot icon with enhanced visibility"""
        # Add a subtle background to make the widget more visible
        dc.SetBrush(wx.Brush(wx.Colour(240, 248, 255, 180)))  # Light blue with transparency
        dc.SetPen(wx.Pen(wx.Colour(70, 130, 180), 1))
        dc.DrawRoundedRectangle(2, 2, 76, 76, 6)

        # Robot body (rounded rectangle) - made larger and more prominent
        dc.SetBrush(wx.Brush(wx.Colour(70, 130, 180)))  # Steel blue
        dc.SetPen(wx.Pen(wx.Colour(25, 25, 112), 3))    # Thicker midnight blue border
        dc.DrawRoundedRectangle(12, 22, 56, 44, 10)

        # Robot head (circle) - made larger
        dc.SetBrush(wx.Brush(wx.Colour(100, 149, 237)))  # Cornflower blue
        dc.SetPen(wx.Pen(wx.Colour(25, 25, 112), 2))
        dc.DrawCircle(40, 18, 17)

        # Eyes - made larger and more prominent
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))  # White
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        dc.DrawCircle(34, 16, 4)  # Left eye
        dc.DrawCircle(46, 16, 4)  # Right eye

        # Eye pupils - made larger
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0)))  # Black
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        dc.DrawCircle(34, 16, 2)  # Left pupil
        dc.DrawCircle(46, 16, 2)  # Right pupil

        # Smile instead of straight mouth
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
        dc.DrawArc(36, 21, 44, 21, 40, 24)

        # Arms - made thicker and more visible
        dc.SetPen(wx.Pen(wx.Colour(70, 130, 180), 5))
        dc.DrawLine(12, 32, 2, 27)   # Left arm
        dc.DrawLine(68, 32, 78, 27)  # Right arm

        # Hands - added for more detail
        dc.SetBrush(wx.Brush(wx.Colour(100, 149, 237)))
        dc.SetPen(wx.Pen(wx.Colour(25, 25, 112), 1))
        dc.DrawCircle(2, 27, 3)   # Left hand
        dc.DrawCircle(78, 27, 3)  # Right hand

        # Legs - made thicker
        dc.SetPen(wx.Pen(wx.Colour(70, 130, 180), 5))
        dc.DrawLine(25, 66, 25, 76)  # Left leg
        dc.DrawLine(55, 66, 55, 76)  # Right leg

        # Feet - added for more detail
        dc.SetBrush(wx.Brush(wx.Colour(25, 25, 112)))
        dc.SetPen(wx.Pen(wx.Colour(25, 25, 112), 1))
        dc.DrawEllipse(20, 74, 10, 4)  # Left foot
        dc.DrawEllipse(50, 74, 10, 4)  # Right foot

        # Antenna - made more prominent
        dc.SetPen(wx.Pen(wx.Colour(255, 215, 0), 3))  # Thicker gold
        dc.DrawLine(40, 3, 40, 10)
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))   # Red tip
        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 1))
        dc.DrawCircle(40, 3, 3)

        # Chest panel - added for more robot-like appearance
        dc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
        dc.SetPen(wx.Pen(wx.Colour(100, 100, 100), 1))
        dc.DrawRoundedRectangle(30, 40, 20, 15, 3)

        # Chest buttons - colorful details
        dc.SetBrush(wx.Brush(wx.Colour(0, 255, 0)))  # Green
        dc.DrawCircle(35, 45, 2)
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))  # Red
        dc.DrawCircle(45, 45, 2)
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 255)))  # Blue
        dc.DrawCircle(40, 50, 2)
    
    def on_paint(self, event):
        """Handle paint event with floating animation"""
        dc = wx.PaintDC(self)

        # Clear with transparent background
        dc.Clear()

        # Apply floating animation offset
        y_offset = int(3 * math.sin(self.animation_offset))

        # Draw the custom icon bitmap with animation offset
        if hasattr(self, 'robot_bitmap') and self.robot_bitmap.IsOk():
            dc.DrawBitmap(self.robot_bitmap, 0, y_offset, True)
        else:
            # Fallback: draw robot directly if bitmap not available
            self.draw_robot(dc)
    
    def on_animation_timer(self, event):
        """Handle animation timer for floating effect"""
        self.animation_offset += 0.2
        if self.animation_offset > 6.28:  # 2*pi
            self.animation_offset = 0
        self.Refresh()
    
    def on_left_down(self, event):
        """Start dragging or prepare for click detection"""
        self.dragging = False
        self.drag_start_pos = event.GetPosition()
        self.click_start_time = wx.GetLocalTime()

        # Check for double-click
        if event.LeftDClick():
            self.open_chat_window()
            return

        # Start potential drag operation
        self.CaptureMouse()

    def on_left_up(self, event):
        """Handle click or stop dragging"""
        if self.HasCapture():
            self.ReleaseMouse()

        # Check if this was a click (not a drag)
        if not self.dragging:
            current_time = wx.GetLocalTime()
            click_duration = current_time - self.click_start_time

            # If it was a quick click (less than 500ms) and minimal movement
            if click_duration < 500:
                current_pos = event.GetPosition()
                distance = ((current_pos.x - self.drag_start_pos.x) ** 2 +
                           (current_pos.y - self.drag_start_pos.y) ** 2) ** 0.5

                # If movement was minimal (less than 5 pixels), treat as click
                if distance < 5:
                    self.open_chat_window()

        self.dragging = False
    
    def on_motion(self, event):
        """Handle dragging motion"""
        if event.Dragging() and self.HasCapture():
            # Check if we should start dragging
            if not self.dragging:
                current_pos = event.GetPosition()
                distance = ((current_pos.x - self.drag_start_pos.x) ** 2 +
                           (current_pos.y - self.drag_start_pos.y) ** 2) ** 0.5

                # Start dragging if moved more than 5 pixels
                if distance > 5:
                    self.dragging = True

            # Perform dragging if active
            if self.dragging:
                current_pos = self.GetPosition()
                mouse_pos = event.GetPosition()

                new_x = current_pos.x + (mouse_pos.x - self.drag_start_pos.x)
                new_y = current_pos.y + (mouse_pos.y - self.drag_start_pos.y)

                # Keep within screen bounds
                display_size = wx.GetDisplaySize()
                new_x = max(0, min(new_x, display_size.width - 80))
                new_y = max(0, min(new_y, display_size.height - 80))

                self.SetPosition((new_x, new_y))
    
    def on_right_click(self, event):
        """Show context menu"""
        menu = wx.Menu()
        
        chat_item = menu.Append(wx.ID_ANY, "💬 Open Chat")
        menu.AppendSeparator()
        hide_item = menu.Append(wx.ID_ANY, "👁️ Hide Robot")
        quit_item = menu.Append(wx.ID_EXIT, "❌ Quit Adam")
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, lambda evt: self.open_chat_window(), chat_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.Hide(), hide_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.parent.Close(), quit_item)
        
        self.PopupMenu(menu)
        menu.Destroy()
    
    def open_chat_window(self):
        """Open or focus the chat window"""
        logger.info("Opening chat window...")
        try:
            if self.chat_window is None or not self.chat_window:
                logger.debug("Creating new chat window")
                self.chat_window = ChatWindow(self)
                self.chat_window.Show()
                logger.info("Chat window created and shown")
            else:
                logger.debug("Focusing existing chat window")
                self.chat_window.Raise()
                self.chat_window.SetFocus()
                logger.info("Chat window focused")
        except Exception as e:
            logger.error(f"Error opening chat window: {e}")
            print(f"❌ Error opening chat: {e}")


class ChatWindow(wx.Frame):
    """Chat interface window for natural browser interaction"""

    def __init__(self, robot_icon):
        super().__init__(None, title="🤖 Adam Browser - AI Chat Assistant", size=(500, 700))

        self.robot_icon = robot_icon
        self.agent_running = False
        self.adam_agent: Optional[AdamAgent] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.agent_thread: Optional[threading.Thread] = None

        # Position near robot icon
        robot_pos = robot_icon.GetPosition()
        self.SetPosition((robot_pos.x - 400, robot_pos.y - 300))

        self.create_chat_interface()
        self.add_welcome_message()

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def create_chat_interface(self):
        """Create the chat interface"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(248, 249, 250))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header_panel = wx.Panel(panel)
        header_panel.SetBackgroundColour(wx.Colour(70, 130, 180))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Robot emoji and title
        robot_emoji = wx.StaticText(header_panel, label="🤖")
        robot_emoji.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        title = wx.StaticText(header_panel, label="Adam Browser AI Assistant")
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        # Status indicator
        self.status_indicator = wx.StaticText(header_panel, label="🔴")
        self.status_indicator.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        header_sizer.Add(robot_emoji, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        header_sizer.Add(title, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        header_sizer.Add(self.status_indicator, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        header_panel.SetSizer(header_sizer)
        
        # Chat display area
        self.chat_display = wx.TextCtrl(
            panel, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            size=(-1, 400)
        )
        self.chat_display.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.chat_display.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Input area
        input_panel = wx.Panel(panel)
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Agent control
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_btn = wx.Button(input_panel, label="🚀 Start Agent", size=(120, 30))
        self.stop_btn = wx.Button(input_panel, label="⏹️ Stop Agent", size=(120, 30))
        self.clear_btn = wx.Button(input_panel, label="🗑️ Clear Chat", size=(120, 30))
        
        control_sizer.Add(self.start_btn, 0, wx.ALL, 3)
        control_sizer.Add(self.stop_btn, 0, wx.ALL, 3)
        control_sizer.Add(self.clear_btn, 0, wx.ALL, 3)
        
        # Message input
        msg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.message_input = wx.TextCtrl(
            input_panel, 
            style=wx.TE_PROCESS_ENTER,
            size=(-1, 40)
        )
        self.message_input.SetHint("Type your browser command here... (e.g., 'Go to google.com and search for AI news')")
        self.message_input.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        self.send_btn = wx.Button(input_panel, label="Send 📤", size=(80, 40))
        self.send_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        msg_sizer.Add(self.message_input, 1, wx.EXPAND | wx.ALL, 5)
        msg_sizer.Add(self.send_btn, 0, wx.ALL, 5)
        
        # Quick commands
        quick_label = wx.StaticText(input_panel, label="Quick Commands:")
        quick_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        quick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        quick_commands = [
            ("🌐 Google", "go to google.com"),
            ("📰 News", "go to news.google.com"),
            ("📧 Gmail", "go to gmail.com"),
            ("📺 YouTube", "go to youtube.com"),
            ("📸 Screenshot", "take a screenshot")
        ]
        
        for label, command in quick_commands:
            btn = wx.Button(input_panel, label=label, size=(80, 25))
            btn.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            btn.Bind(wx.EVT_BUTTON, lambda evt, cmd=command: self.send_quick_command(cmd))
            quick_sizer.Add(btn, 0, wx.ALL, 2)
        
        input_sizer.Add(control_sizer, 0, wx.ALL | wx.CENTER, 5)
        input_sizer.Add(msg_sizer, 0, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(quick_label, 0, wx.ALL, 5)
        input_sizer.Add(quick_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        input_panel.SetSizer(input_sizer)
        
        # Add to main sizer
        main_sizer.Add(header_panel, 0, wx.EXPAND)
        main_sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # Bind events
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start_agent)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_agent)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_chat)
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send_message)
        self.message_input.Bind(wx.EVT_TEXT_ENTER, self.on_send_message)
    
    def add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_msg = """🤖 Hello! I'm Adam, your AI browser assistant.

I can help you with:
• Navigate to websites
• Search for information  
• Take screenshots
• Fill out forms
• Scroll and interact with pages
• Book travel and get directions

Just tell me what you want to do in natural language!

Examples:
"Go to google.com and search for Python tutorials"
"Take a screenshot of this page"
"Scroll down to see more content"
"Book a flight from NYC to LA"

Click 'Start Agent' to begin! 🚀"""
        
        self.add_chat_message("Adam", welcome_msg, is_bot=True)
    
    def add_chat_message(self, sender: str, message: str, is_bot: bool = False):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Set text style
        if is_bot:
            self.chat_display.SetDefaultStyle(wx.TextAttr(wx.Colour(70, 130, 180)))
            prefix = f"🤖 {sender} [{timestamp}]:\n"
        else:
            self.chat_display.SetDefaultStyle(wx.TextAttr(wx.Colour(25, 25, 112)))
            prefix = f"👤 {sender} [{timestamp}]:\n"
        
        # Add message
        self.chat_display.AppendText(prefix)
        
        # Message content in normal color
        self.chat_display.SetDefaultStyle(wx.TextAttr(wx.Colour(0, 0, 0)))
        self.chat_display.AppendText(f"{message}\n\n")
        
        # Scroll to bottom
        self.chat_display.SetInsertionPointEnd()
    
    def on_start_agent(self, event):
        """Start the browser agent"""
        if not self.agent_running:
            self.agent_running = True
            self.status_indicator.SetLabel("🟡")  # Yellow while starting
            self.add_chat_message("System", "🚀 Starting Adam Agent...", is_bot=True)

            # Update button states
            self.start_btn.Enable(False)
            self.stop_btn.Enable(False)  # Disable until fully started

            # Start agent in separate thread
            self.agent_thread = threading.Thread(target=self._start_agent_async, daemon=True)
            self.agent_thread.start()
    
    def on_stop_agent(self, event):
        """Stop the browser agent"""
        if self.agent_running:
            self.agent_running = False
            self.status_indicator.SetLabel("🔴")
            self.add_chat_message("System", "⏹️ Stopping agent...", is_bot=True)

            # Stop agent asynchronously
            if self.adam_agent and self.event_loop:
                asyncio.run_coroutine_threadsafe(self.adam_agent.stop(), self.event_loop)

            # Update button states
            self.start_btn.Enable(True)
            self.stop_btn.Enable(False)
    
    def on_clear_chat(self, event):
        """Clear the chat display"""
        self.chat_display.Clear()
        self.add_welcome_message()
    
    def on_send_message(self, event):
        """Send user message and process command"""
        message = self.message_input.GetValue().strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_chat_message("You", message)
        self.message_input.Clear()
        
        # Process command if agent is running
        if self.agent_running:
            self.process_browser_command(message)
        else:
            self.add_chat_message("Adam", "⚠️ Please start the agent first to process commands.", is_bot=True)
    
    def send_quick_command(self, command: str):
        """Send a quick command"""
        self.message_input.SetValue(command)
        self.on_send_message(None)
    
    def process_browser_command(self, command: str):
        """Process browser command with real execution"""
        self.add_chat_message("Adam", f"🔄 Processing: {command}", is_bot=True)

        # Execute command through real Adam agent
        if self.adam_agent and self.event_loop and self.agent_running:
            future = asyncio.run_coroutine_threadsafe(
                self._execute_real_command(command),
                self.event_loop
            )
            # Handle result in callback
            wx.CallLater(100, lambda: self._check_command_result(future))
        else:
            self.add_chat_message("Adam", "❌ Agent not running. Please start the agent first.", is_bot=True)
    

    
    def _start_agent_async(self):
        """Start the Adam agent in async context"""
        try:
            logger.info("Starting Adam agent in background thread...")

            # Create new event loop for this thread
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            logger.debug("Event loop created")

            # Initialize Adam agent
            logger.debug("Creating AdamAgent instance...")
            self.adam_agent = AdamAgent()

            # Run initialization
            logger.debug("Initializing Adam agent...")
            success = self.event_loop.run_until_complete(self.adam_agent.initialize())

            if success:
                logger.info("Adam agent initialized successfully")
                wx.CallAfter(self._on_agent_started_success)
                # Keep event loop running
                logger.debug("Starting event loop...")
                self.event_loop.run_forever()
            else:
                logger.error("Adam agent initialization failed")
                wx.CallAfter(self._on_agent_start_failed, "Failed to initialize agent")

        except Exception as e:
            logger.error(f"Agent start error: {e}")
            wx.CallAfter(self._on_agent_start_failed, str(e))

    def _on_agent_started_success(self):
        """Called when agent starts successfully"""
        self.status_indicator.SetLabel("🟢")
        self.add_chat_message("System", "✅ Adam Agent started successfully! Ready to process commands.", is_bot=True)
        self.stop_btn.Enable(True)

    def _on_agent_start_failed(self, error: str):
        """Called when agent fails to start"""
        self.agent_running = False
        self.status_indicator.SetLabel("🔴")
        self.add_chat_message("System", f"❌ Failed to start agent: {error}", is_bot=True)
        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)

    async def _execute_real_command(self, command: str) -> Dict[str, Any]:
        """Execute command through real Adam agent"""
        try:
            result = await self.adam_agent.process_command(command)
            return result
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'data': {}
            }

    def _check_command_result(self, future):
        """Check command execution result"""
        try:
            if future.done():
                result = future.result()
                self._handle_command_result(result)
            else:
                # Check again later
                wx.CallLater(100, lambda: self._check_command_result(future))
        except Exception as e:
            logger.error(f"Command result error: {e}")
            self.add_chat_message("Adam", f"❌ Command failed: {str(e)}", is_bot=True)

    def _handle_command_result(self, result: Dict[str, Any]):
        """Handle command execution result"""
        if result.get('success', False):
            message = result.get('message', 'Command completed successfully')
            self.add_chat_message("Adam", f"✅ {message}", is_bot=True)

            # Add additional info if available
            if result.get('url'):
                self.add_chat_message("Adam", f"🌐 Current page: {result['url']}", is_bot=True)

            if result.get('screenshot_path'):
                self.add_chat_message("Adam", f"📸 Screenshot saved: {result['screenshot_path']}", is_bot=True)
        else:
            message = result.get('message', 'Command failed')
            self.add_chat_message("Adam", f"❌ {message}", is_bot=True)

    def on_close(self, event):
        """Handle window close"""
        # Stop agent if running
        if self.agent_running and self.adam_agent and self.event_loop:
            asyncio.run_coroutine_threadsafe(self.adam_agent.stop(), self.event_loop)
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)

        self.Hide()  # Hide instead of destroy so it can be reopened


class AdamFloatingApp(wx.App):
    """Main application with floating robot and chat interface"""
    
    def OnInit(self):
        # Create floating robot icon
        self.robot_icon = FloatingRobotIcon(self)
        
        # Create system tray icon
        self.tray_icon = AdamTrayIcon(self)
        
        return True
    
    def show_robot(self):
        """Show the robot icon"""
        self.robot_icon.Show()
    
    def hide_robot(self):
        """Hide the robot icon"""
        self.robot_icon.Hide()


class AdamTrayIcon(wx.adv.TaskBarIcon):
    """System tray icon for Adam Browser"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        # Set tray icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16)))
        self.SetIcon(icon, "Adam Browser - AI Agent")
    
    def CreatePopupMenu(self):
        """Create tray icon context menu"""
        menu = wx.Menu()
        
        show_item = menu.Append(wx.ID_ANY, "👁️ Show Robot")
        hide_item = menu.Append(wx.ID_ANY, "🙈 Hide Robot")
        menu.AppendSeparator()
        chat_item = menu.Append(wx.ID_ANY, "💬 Open Chat")
        menu.AppendSeparator()
        quit_item = menu.Append(wx.ID_EXIT, "❌ Quit Adam")
        
        # Bind events
        self.Bind(wx.EVT_MENU, lambda evt: self.app.show_robot(), show_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.app.hide_robot(), hide_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.app.robot_icon.open_chat_window(), chat_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.app.ExitMainLoop(), quit_item)
        
        return menu


def main():
    """Main entry point"""
    print("🤖 Starting Enhanced Adam Browser Floating Agent...")
    print("=" * 60)
    print("Features:")
    print("✅ Physical browser command execution")
    print("✅ Real Adam Agent integration")
    print("✅ Robot icon click to open chat")
    print("✅ Actual browser automation")
    print("=" * 60)
    print("Look for the robot icon in the bottom-right corner of your screen!")
    print("Click the robot to open chat, or right-click for options.")
    print()

    try:
        app = AdamFloatingApp()
        app.MainLoop()
    except Exception as e:
        print(f"❌ Error starting floating agent: {e}")
        logger.error(f"Floating agent startup error: {e}")
        input("Press Enter to exit...")
        return 1

    return 0


if __name__ == '__main__':
    main()
