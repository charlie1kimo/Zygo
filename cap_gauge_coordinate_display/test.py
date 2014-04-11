import wx

class Frame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,700 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.timer = wx.Timer(self, wx.NewId())

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = Frame(None)
	frame.Show()
	app.MainLoop()
