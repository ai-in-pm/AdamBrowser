import wx

class SimpleFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Adam Browser Test", size=(600, 400))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Adam Browser - GUI Test")
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        
        # Status
        self.status = wx.StaticText(panel, label="Status: GUI Working!")
        sizer.Add(self.status, 0, wx.ALL | wx.CENTER, 10)
        
        # Button
        btn = wx.Button(panel, label="Test Button")
        btn.Bind(wx.EVT_BUTTON, self.on_button)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(sizer)
        self.Center()
    
    def on_button(self, event):
        self.status.SetLabel("Button clicked! GUI is responsive.")

class SimpleApp(wx.App):
    def OnInit(self):
        frame = SimpleFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = SimpleApp()
    app.MainLoop()
