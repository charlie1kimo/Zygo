"""
matplotlibInWxPython
"""

import wx
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

class MplCanvasFrame(wx.Frame):
	
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, title='Matplotlib in Wx', size=(600, 400))
		self.figure = Figure()
		self.axes = self.figure.add_subplot(111)
		x = np.arange(0, 6, .01)
		y = np.sin(x**2)*np.exp(-x)
		self.axes.plot(x, y)
		
		self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
		
		self.toolbar = NavigationToolbar2Wx(self.canvas)
		self.toolbar.Realize()
		self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
		self.toolbar.Show()
		
		self.SetSizer(self.sizer)
		self.Fit()
		
if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = MplCanvasFrame()
	frame.Show(True)
	app.MainLoop()