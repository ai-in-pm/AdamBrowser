import wx

app = wx.App()
frame = wx.Frame(None, title="Adam Browser Test", size=(400, 300))
panel = wx.Panel(frame)

text = wx.StaticText(panel, label="Adam Browser GUI Test", pos=(100, 100))
font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
text.SetFont(font)

frame.Show()
app.MainLoop()
