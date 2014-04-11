#!/usr/bin/env python
import wx
import wx.grid as gridlib
import wx_extensions.grid as gridExt

class TestGridFrame(wx.Frame):
	""" We simply derive a new class of Frame. """
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(1000,500), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
		#self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		
		self.colLabels = ['ID', 'Description', 'Severity', 'Priority', 'Platform',
                          'Opened?', 'Fixed?', 'Tested?', 'TestFloat']

		self.dataTypes = [gridlib.GRID_VALUE_NUMBER,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_CHOICE + ':only in a million years!,wish list,minor,normal,major,critical',
                          gridlib.GRID_VALUE_NUMBER + ':1,5',
                          gridlib.GRID_VALUE_CHOICE + ':all,MSW,GTK,other',
                          gridlib.GRID_VALUE_BOOL,
                          gridlib.GRID_VALUE_BOOL,
                          gridlib.GRID_VALUE_BOOL,
                          gridlib.GRID_VALUE_FLOAT + ':6,2',
                          ]
						  
		self.data = [
			[1010, "The foo doesn't bar", "major", 1, 'MSW', 1, 1, 1, 1.12],
			[1011, "I've got a wicket in my wocket", "wish list", 2, 'other', 0, 0, 0, 1.50],
			[1012, "Rectangle() returns a triangle", "critical", 5, 'all', 0, 0, 0, 1.56]
			]
		
		bSizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL )
		bSizerMain.Add( self.panel, 1, wx.EXPAND, 5 )
		
		bSizerPanel = wx.BoxSizer( wx.VERTICAL )
		
		self.grid = gridExt.CustomDataGrid(self.panel, self.colLabels, self.dataTypes, self.data)
		bSizerPanel.Add( self.grid, 1, wx.EXPAND, 5 )
		
		self.panel.SetSizer(bSizerPanel)
		self.SetSizer(bSizerMain)
		self.Layout()

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = TestGridFrame(None, 'Test Grid')
	frame.Show(True)	
	app.MainLoop()