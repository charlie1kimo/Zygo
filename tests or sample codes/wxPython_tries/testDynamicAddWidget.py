###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.grid
from wx.lib.scrolledpanel import ScrolledPanel

###########################################################################
## Class MyFrame3
###########################################################################

class MyFrame3 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer27 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter2 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SUNKEN_BORDER )
		self.m_splitter2.SetMinimumPaneSize( 30 )
		
		self.m_panel8 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer29 = wx.BoxSizer( wx.VERTICAL )
		
		#self.m_scrolledWindow2 = wx.ScrolledWindow( self.m_panel8, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		#self.m_scrolledWindow2.SetScrollRate( 5, 5 )
		#bSizer30 = wx.BoxSizer( wx.VERTICAL )
		
		#self.m_panel10 = wx.Panel( self.m_scrolledWindow2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel10 = ScrolledPanel(self.m_panel8, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer32 = wx.BoxSizer( wx.VERTICAL )
		self.bSizer32 = bSizer32
		
		self.m_panel10.SetSizer( bSizer32 )
		self.m_panel10.Layout()
		bSizer32.Fit( self.m_panel10 )
		#bSizer30.Add( self.m_panel10, 1, wx.EXPAND |wx.ALL, 5 )
		
		#self.m_scrolledWindow2.SetSizer( bSizer30 )
		#self.m_scrolledWindow2.Layout()
		#bSizer30.Fit( self.m_scrolledWindow2 )
		#bSizer29.Add( self.m_scrolledWindow2, 1, wx.EXPAND |wx.ALL, 5 )
		bSizer29.Add( self.m_panel10, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.m_panel8.SetSizer( bSizer29 )
		self.m_panel8.Layout()
		bSizer29.Fit( self.m_panel8 )
		self.m_panel9 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer31 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_button11 = wx.Button( self.m_panel9, wx.ID_ANY, u"Add!", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer31.Add( self.m_button11, 0, wx.ALL, 5 )
		
		self.m_panel9.SetSizer( bSizer31 )
		self.m_panel9.Layout()
		bSizer31.Fit( self.m_panel9 )
		self.m_splitter2.SplitHorizontally( self.m_panel8, self.m_panel9, -1 )
		bSizer27.Add( self.m_splitter2, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer27 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button11.Bind( wx.EVT_BUTTON, self.onAddButton )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onAddButton( self, event ):
		# add the grid widget
		self.m_grid5 = wx.grid.Grid( self.m_panel10, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.m_grid5.CreateGrid( 10, 10 )
		self.m_grid5.EnableEditing( True )
		self.m_grid5.EnableGridLines( True )
		self.m_grid5.EnableDragGridSize( False )
		self.m_grid5.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid5.EnableDragColMove( False )
		self.m_grid5.EnableDragColSize( True )
		self.m_grid5.SetColLabelSize( 30 )
		self.m_grid5.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid5.EnableDragRowSize( True )
		self.m_grid5.SetRowLabelSize( 80 )
		self.m_grid5.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid5.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.bSizer32.Add( self.m_grid5, 0, wx.ALL, 5 )

		self.bSizer32.Layout()
		self.m_panel10.SetupScrolling()
		widget = self.m_panel10
		widget.Layout()
		while widget.GetParent():
			widget = widget.GetParent()
			widget.Layout()
			if widget.IsTopLevel():
				break
		
		event.Skip()
	
	def m_splitter2OnIdle( self, event ):
		self.m_splitter2.SetSashPosition( 0 )
		self.m_splitter2.Unbind( wx.EVT_IDLE )
	

if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = MyFrame3(None)
	frame.Show(True)
	app.MainLoop()
