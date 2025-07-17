#!/usr/bin/env python3
"""
Simple wxPython test to verify GUI functionality
"""

try:
    import wx
    print("✅ wxPython imported successfully")
    
    class TestApp(wx.App):
        def OnInit(self):
            frame = wx.Frame(None, title="✅ wxPython Test - SUCCESS!", size=(400, 200))
            panel = wx.Panel(frame)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            text1 = wx.StaticText(panel, label="🎉 GUI is working!")
            text1.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            
            text2 = wx.StaticText(panel, label="Adam Browser GUI should work now")
            
            sizer.Add(text1, 0, wx.ALL | wx.CENTER, 20)
            sizer.Add(text2, 0, wx.ALL | wx.CENTER, 10)
            
            panel.SetSizer(sizer)
            frame.Center()
            frame.Show()
            
            return True
    
    print("Creating GUI application...")
    app = TestApp()
    print("Starting GUI main loop...")
    app.MainLoop()
    print("GUI closed successfully")
    
except ImportError as e:
    print("❌ ERROR: wxPython not installed")
    print("Please run: pip install wxpython")
    print(f"Error details: {e}")
    input("Press Enter to continue...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    input("Press Enter to continue...")
