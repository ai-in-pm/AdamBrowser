"""
Force GUI to appear on desktop
"""

import wx
import sys

class ForceVisibleFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Adam Browser - Force Visible", size=(800, 600))
        
        # Force window to appear
        self.SetPosition((100, 100))  # Set specific position
        self.Raise()  # Bring to front
        self.RequestUserAttention()  # Request attention
        
        # Create simple content
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Large title
        title = wx.StaticText(panel, label="🤖 ADAM BROWSER GUI 🌐")
        font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(wx.Colour(0, 100, 200))
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 30)
        
        # Status
        status = wx.StaticText(panel, label="✅ GUI is now visible on your desktop!")
        status_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        status.SetFont(status_font)
        status.SetForegroundColour(wx.Colour(0, 150, 0))
        sizer.Add(status, 0, wx.ALL | wx.CENTER, 20)
        
        # Instructions
        instructions = wx.StaticText(panel, label="""
This is the Adam Browser GUI test window.

If you can see this window, then wxPython GUI is working correctly!

Features:
• Natural language command processing
• Browser automation with Playwright
• AI-powered intent classification
• Real-time logging and monitoring
• Secure credential management

Click the button below to test interactivity:
        """)
        instructions.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(instructions, 0, wx.ALL | wx.CENTER, 20)
        
        # Test button
        self.test_btn = wx.Button(panel, label="🚀 Click Me to Test!", size=(200, 50))
        self.test_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.test_btn.Bind(wx.EVT_BUTTON, self.on_test_click)
        sizer.Add(self.test_btn, 0, wx.ALL | wx.CENTER, 20)
        
        # Result text
        self.result_text = wx.StaticText(panel, label="")
        self.result_text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        sizer.Add(self.result_text, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(sizer)
        
        # Set background color
        panel.SetBackgroundColour(wx.Colour(240, 248, 255))  # Alice blue
        
        # Center on screen
        self.CenterOnScreen()
        
        # Force focus
        self.SetFocus()
        
        print("GUI window created and should be visible!")
        
    def on_test_click(self, event):
        self.result_text.SetLabel("🎉 Great! The GUI is working perfectly!")
        self.result_text.SetForegroundColour(wx.Colour(0, 150, 0))
        self.test_btn.SetLabel("✅ GUI Test Passed!")

class ForceVisibleApp(wx.App):
    def OnInit(self):
        # Create and show frame
        frame = ForceVisibleFrame()
        frame.Show(True)
        
        # Force to front
        frame.Raise()
        frame.RequestUserAttention()
        
        # Set as top window
        self.SetTopWindow(frame)
        
        print("App initialized, frame should be visible!")
        return True

if __name__ == '__main__':
    print("Starting GUI application...")
    print("If you don't see a window, check your taskbar or try Alt+Tab")
    
    app = ForceVisibleApp()
    app.MainLoop()
    
    print("GUI application closed.")
