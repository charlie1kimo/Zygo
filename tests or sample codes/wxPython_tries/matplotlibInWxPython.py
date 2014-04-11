"""
matplotlibInWxPython
"""

import wx
import matplotlib
matplotlib.use('WxAgg')
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

import matplotlib.pyplot as plt

class MplCanvasFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Matplotlib in Wx', size=(600, 400))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.EXPAND|wx.ALL)
        self.sizerPanel = wx.BoxSizer(wx.VERTICAL)
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.x = np.arange(0, 6, .01)
        x = self.x
        self.y = np.sin(x**2)*np.exp(-x)
        y = self.y
        
        self.canvas = FigureCanvas(self.panel, wx.ID_ANY, self.figure)
        self.sizerPanel.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        
        #cursor = SnaptoCursor(self.canvas, self.axes, 0, 0)
        #self.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)
        self.canvas.mpl_connect('motion_notify_event', self.onMouseMove)
        self.axes.plot(x, y)
        
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        self.sizerPanel.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.toolbar.Show()
        
        self.panel.SetSizer(self.sizerPanel)
        self.sizer.Add(self.panel, 0, wx.EXPAND | wx.ALL)
        
        self.SetSizer(self.sizer)
        self.Fit()
        
    def onMouseMove(self, event):
        self.axes.clear()					# clear for redraw
        
        lx = self.axes.axhline(color='k')  # the horiz line
        ly = self.axes.axvline(color='k')  # the vert line
        txt = self.axes.text(0.7, 0.9, '', transform=self.axes.transAxes)
        
        if not event.inaxes: return

        x, y = event.xdata, event.ydata
        # update the line positions
        lx.set_ydata(y)
        ly.set_xdata(x)

        txt.set_text('x=%1.2f, y=%1.2f' % (x,y))
		
        self.axes.plot(self.x, self.y)
        self.canvas.draw()
        self.panel.Refresh()

    def saveFigure(self, name):
        format = 'eps'
        self.figure.savefig(name+'.'+format, format=format)

        
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MplCanvasFrame()
    frame.Show(True)
    frame.saveFigure('test')
    app.MainLoop()
