"""
Force Visible Adam Browser Widget
A widget that MUST appear on desktop with maximum visibility
"""

import wx
import math
from datetime import datetime
import sys

class ForceVisibleWidget(wx.Frame):
    def __init__(self):
        # Force window to be visible with all possible flags
        super().__init__(
            None, 
            title="🤖 Adam Browser Widget - VISIBLE TEST",
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP,
            size=(200, 200)
        )
        
        # Force bright colors and large size for visibility
        self.SetBackgroundColour(wx.Colour(255, 255, 0))  # Bright yellow
        
        # Position in multiple locations to ensure visibility
        display_size = wx.GetDisplaySize()
        
        # Try center of screen first
        center_x = (display_size.width - 200) // 2
        center_y = (display_size.height - 200) // 2
        self.SetPosition((center_x, center_y))
        
        self.create_visible_content()
        
        # Force window properties
        self.Raise()
        self.SetFocus()
        self.RequestUserAttention()
        self.Show(True)
        
        # Animation timer for attention
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_animation_timer)
        self.animation_offset = 0
        self.animation_timer.Start(500)  # Flash every 500ms
        
        # Bind events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        print("🤖 FORCE VISIBLE WIDGET LAUNCHED!")
        print(f"Position: {center_x}, {center_y}")
        print(f"Size: 200x200")
        print("Look for BRIGHT YELLOW window in center of screen!")
        print("If you can see this, the widget system works!")
        
    def create_visible_content(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 0))  # Bright yellow
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Large visible title
        title = wx.StaticText(panel, label="🤖 ADAM WIDGET TEST 🤖")
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.Colour(255, 0, 0))  # Red text
        
        # Status message
        status = wx.StaticText(panel, label="WIDGET IS WORKING!\nClick to continue...")
        status.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status.SetForegroundColour(wx.Colour(0, 0, 255))  # Blue text
        
        # Large button
        self.test_btn = wx.Button(panel, label="✅ LAUNCH ROBOT WIDGET", size=(180, 50))
        self.test_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.test_btn.SetBackgroundColour(wx.Colour(0, 255, 0))  # Green button
        self.test_btn.Bind(wx.EVT_BUTTON, self.launch_robot_widget)
        
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(status, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(self.test_btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(sizer)
    
    def on_animation_timer(self, event):
        # Flash the window for attention
        self.animation_offset += 1
        if self.animation_offset % 2 == 0:
            self.SetBackgroundColour(wx.Colour(255, 255, 0))  # Yellow
        else:
            self.SetBackgroundColour(wx.Colour(255, 200, 0))  # Orange
        self.Refresh()
    
    def on_click(self, event):
        wx.MessageBox("Great! The widget system is working!\nNow I'll launch the robot widget.", "Success!", wx.OK | wx.ICON_INFORMATION)
        self.launch_robot_widget(None)
    
    def on_right_click(self, event):
        menu = wx.Menu()
        launch_item = menu.Append(wx.ID_ANY, "🚀 Launch Robot Widget")
        quit_item = menu.Append(wx.ID_EXIT, "❌ Quit")
        
        self.Bind(wx.EVT_MENU, self.launch_robot_widget, launch_item)
        self.Bind(wx.EVT_MENU, self.on_close, quit_item)
        
        self.PopupMenu(menu)
        menu.Destroy()
    
    def launch_robot_widget(self, event):
        print("Launching robot widget...")
        self.animation_timer.Stop()
        
        # Hide this test window
        self.Hide()
        
        # Launch the actual robot widget
        self.robot_widget = ActualRobotWidget()
        
    def on_close(self, event):
        self.animation_timer.Stop()
        self.Destroy()
        wx.GetApp().ExitMainLoop()

class ActualRobotWidget(wx.Frame):
    def __init__(self):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED | wx.STAY_ON_TOP)
        
        self.SetSize((100, 100))
        
        # Position at bottom right
        display_size = wx.GetDisplaySize()
        x = display_size.width - 120
        y = display_size.height - 180
        self.SetPosition((x, y))
        
        self.create_robot()
        
        # Dragging
        self.dragging = False
        self.drag_start_pos = None
        
        # Events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_click)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
        # Animation
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_animation_timer)
        self.animation_offset = 0
        self.animation_timer.Start(150)
        
        self.Show(True)
        self.Raise()
        
        print(f"🤖 Robot widget launched at position: {x}, {y}")
        print("Look for blue robot in bottom-right corner!")
        
    def create_robot(self):
        bitmap = wx.Bitmap(100, 100)
        dc = wx.MemoryDC(bitmap)
        
        dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        dc.Clear()
        
        # Robot body
        dc.SetBrush(wx.Brush(wx.Colour(70, 130, 180)))
        dc.SetPen(wx.Pen(wx.Colour(25, 25, 112), 3))
        dc.DrawRoundedRectangle(20, 35, 60, 50, 10)
        
        # Robot head
        dc.SetBrush(wx.Brush(wx.Colour(100, 149, 237)))
        dc.DrawCircle(50, 25, 18)
        
        # Eyes
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
        dc.DrawCircle(43, 22, 4)
        dc.DrawCircle(57, 22, 4)
        
        # Pupils
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0)))
        dc.DrawCircle(43, 22, 2)
        dc.DrawCircle(57, 22, 2)
        
        # Smile
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
        dc.DrawArc(45, 28, 55, 28, 50, 32)
        
        # Arms
        dc.SetPen(wx.Pen(wx.Colour(70, 130, 180), 6))
        dc.DrawLine(20, 45, 8, 38)
        dc.DrawLine(80, 45, 92, 38)
        
        # Legs
        dc.DrawLine(35, 85, 35, 95)
        dc.DrawLine(65, 85, 65, 95)
        
        # Antenna
        dc.SetPen(wx.Pen(wx.Colour(255, 215, 0), 3))
        dc.DrawLine(50, 7, 50, 15)
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        dc.DrawCircle(50, 7, 3)
        
        dc.SelectObject(wx.NullBitmap)
        self.robot_bitmap = bitmap
        self.SetShape(wx.Region(bitmap))
    
    def on_paint(self, event):
        dc = wx.PaintDC(self)
        y_offset = int(4 * math.sin(self.animation_offset))
        dc.Clear()
        if hasattr(self, 'robot_bitmap'):
            dc.DrawBitmap(self.robot_bitmap, 0, y_offset)
    
    def on_animation_timer(self, event):
        self.animation_offset += 0.15
        if self.animation_offset > 6.28:
            self.animation_offset = 0
        self.Refresh()
    
    def on_left_down(self, event):
        if event.LeftDClick():
            wx.MessageBox("Robot widget is working!\nDouble-click detected!", "Success!", wx.OK | wx.ICON_INFORMATION)
        else:
            self.dragging = True
            self.drag_start_pos = event.GetPosition()
            self.CaptureMouse()
    
    def on_left_up(self, event):
        if self.dragging:
            self.dragging = False
            if self.HasCapture():
                self.ReleaseMouse()
    
    def on_motion(self, event):
        if self.dragging and event.Dragging():
            current_pos = self.GetPosition()
            mouse_pos = event.GetPosition()
            
            new_x = current_pos.x + (mouse_pos.x - self.drag_start_pos.x)
            new_y = current_pos.y + (mouse_pos.y - self.drag_start_pos.y)
            
            display_size = wx.GetDisplaySize()
            new_x = max(0, min(new_x, display_size.width - 100))
            new_y = max(0, min(new_y, display_size.height - 100))
            
            self.SetPosition((new_x, new_y))
    
    def on_right_click(self, event):
        menu = wx.Menu()
        pos_item = menu.Append(wx.ID_ANY, f"📍 Position: {self.GetPosition()}")
        hide_item = menu.Append(wx.ID_ANY, "👁️ Hide Robot")
        quit_item = menu.Append(wx.ID_EXIT, "❌ Quit")
        
        self.Bind(wx.EVT_MENU, lambda evt: None, pos_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.Hide(), hide_item)
        self.Bind(wx.EVT_MENU, lambda evt: self.Close(), quit_item)
        
        self.PopupMenu(menu)
        menu.Destroy()

class ForceVisibleApp(wx.App):
    def OnInit(self):
        print("🤖 Starting Force Visible Widget Test...")
        self.test_widget = ForceVisibleWidget()
        return True

def main():
    print("=" * 60)
    print("🤖 ADAM BROWSER - FORCE VISIBLE WIDGET TEST")
    print("=" * 60)
    print("This will show a BRIGHT YELLOW window in the center of your screen.")
    print("If you can see it, then the widget system works!")
    print("Click the green button to launch the actual robot widget.")
    print("=" * 60)
    
    app = ForceVisibleApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
