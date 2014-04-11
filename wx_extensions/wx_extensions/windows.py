# -*- coding: utf-8 -*- 
"""
window.py
	window.py contains the class for wxPython windows extension
	(such as Frame, Panel, ScrolledPane). It extends some utility methods
	that can help developing wxPython application more rapidly.
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/7/2013	cchen	first created documentation
'''

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import threading
import wx
from wx.lib.scrolledpanel import ScrolledPanel

###########################################################################
## Class WindowBase
## @Purpose:
##		This is an abstract class that setup the default utility methods
##		for wx.Window objects.
###########################################################################
class WindowBase(object):
	def __init__(self):
		self.__threadID__ = 0
		self.__threadMap__ = {}

	def __del__(self):
		while len(self.__threadMap__) > 0:
			self.__cleanThreadMap__()

	# __cleanThreadMap__
	# @Purpose:
	#	Private function to clean up the thread Map
	def __cleanThreadMap__(self):
		for key in self.__threadMap__.keys():
			thread = self.__threadMap__[key]
			if not thread.isAlive():
				del self.__threadMap__[key]

	# __getThreadMap__
	# @Purpose:
	#	return the threadMap that's associate with this window widget
	# @Outputs:
	#	(dict) this window's thread map
	def __getThreadMap__(self):
		return self.__threadMap__

	# __startThreadWithID__
	# @Purpose:
	#	start a thread with specific ID
	# @Inputs:
	#	(int) ID = specific id
	#	(obj) funct = function name
	#	(list) *args = functions's arguments
	#	(dict) **kwargs = function's keyword arguments
	def __startThreadWithLocks__(self, ID, funct, *args, **kwargs):
		if self.__threadMap__.has_key(ID):
			thread = self.__threadMap__[ID]
			while thread.isAlive():
				pass
			del thread
		thread = threading.Thread(target=funct, args=args, kwargs=kwargs)
		self.__threadMap__[ID] = thread
		thread.start()

	# __startThread__
	# @Purpose:
	#	Private method to start a background thread to not hang the user interface
	# @Inputs:
	#	(obj) funct = function name
	#	(list) *args = function's arguments
	#	(dict) **kwargs = functions's keyword arguments
	# @Outputs:
	#	(int) this started Thread's ID
	def __startThread__(self, funct, *args, **kwargs):
		# before starting thread, clean up. (limited 10 threads)
		if self.__threadID__ % 10 == 0:
			self.__cleanThreadMap__()

		thread = threading.Thread(target=funct, args=args, kwargs=kwargs)
		ID = self.__threadID__
		self.__threadMap__[ID] = thread
		if self.__threadID__ == 2147483647:				# largest int32
			self.__threadID__ = 0
		else:
			self.__threadID__ += 1
		thread.start()
		return ID
	
	# getTopLevelWindow(self):
	# @Purpose:
	#	get the top level window in the wxApp
	# @Inputs:
	#	N/A
	# @Outputs:
	#	(wxWidget) topLeveledWindow
	def getTopLevelWindow(self):
		widget = self
		while not widget.IsTopLevel():
			widget = widget.GetParent()
		return widget

	# refreshWidget:
	# @Purpose:
	#	refresh the given widget along with all its parents
	# @Inputs:
	#	widget = the target widget to be refreshed
	def refreshWidget(self, widget):
		while widget:
			widget.Layout()
			widget.Refresh()
			widget.Update()
			if isinstance(widget, ScrolledPanel):
				widget.SetupScrolling()
			if isinstance(widget, FigureCanvas):
				widget.draw()
			if widget.IsTopLevel():
				break
			widget = widget.GetParent()
		
	# popErrorBox:
	# @Purpose:
	#   pop up Error Box with set title and message
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	def popErrorBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_ERROR)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
	
	# popAlertBox:
	# @Purpose:
	#   pop up Warning Box with set title and message
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	def popAlertBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_WARNING)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

	# popInfoBox:
	# @Purpose:
	#   pop up Information Box with set title and message
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	def popInfoBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked

	# popInfoBoxAndReturnBool
	# @Purpose:
	#	updated API for poping information box with returning boolean value (OK = True, Cancel = False)
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	# @Outputs:
	#	True if pressed OK
	#	False otherwise
	def popInfoBoxAndReturnBool(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked == wx.ID_OK
	
	# popInfoOKBox:
	# @Purpose:
	#   pop up Information Box with set title and message (only OK button)
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	def popInfoOKBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_INFORMATION)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
	
	# popRetryBox:
	# @Purpose:
	#	pop up a Retry Box with title and message
	# @Inputs:
	#	title = message dialog box title
	#	msg = message dialog box message
	def popRetryBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.YES | wx.NO | wx.ICON_ERROR)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked

	# popRetryBoxAndReturnBool:
	# @Purpose:
	# updated API for popRetryBox, return Yes = True, No = False
	# @Inputs:	
	#	title = message dialog box title
	#	msg = message dialog box message
	# @Outputs:
	#	True if pressed Yes, False otherwise
	def popRetryBoxAndReturnBool(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.YES | wx.NO | wx.ICON_ERROR)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked == wx.ID_YES

###########################################################################
## Class FrameBase
##	@Purpose:
##		This is the base abstract class that extends the utility methods 
##		for error handling and updating wigets
###########################################################################
class FrameBase(wx.Frame, WindowBase):
	# __init__:
	# @Purpose:
	#	default dummy constructor that just calls wx.Frame
	def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, 
				size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL):
		WindowBase.__init__(self)
		wx.Frame.__init__(self, parent, id, title, pos, size, style)

	# __del__:
	# @Purpose:
	# 	default destructor
	def __del__(self):
		WindowBase.__del__(self)

	
class PanelBase(wx.Panel, WindowBase):
	# __init__:
	# @Purpose:
	#	default dummy constructor that just calls wx.Panel
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
				size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		WindowBase.__init__(self)
		wx.Panel.__init__(self, parent, id, pos, size, style)

	# __del__:
	# @Purpose:
	# 	default destructor
	def __del__(self):
		WindowBase.__del__(self)


class ScrolledPanelBase(ScrolledPanel, WindowBase):
	# __init__:
	# @Purpose:
	#	default dummy constructor that just calls wx.lib.scrolledpanel
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
				size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		WindowBase.__init__(self)
		ScrolledPanel.__init__(self, parent, id, pos, size, style)
		self.Bind( wx.EVT_LEFT_DOWN, self.onMouseLeftDown )

	# __del__:
	# @Purpose:
	# 	default destructor
	def __del__(self):
		WindowBase.__del__(self)

	# This method handles the focus on panel, so mouse scrolling would works.
	def onMouseLeftDown( self, event ):
		self.SetFocusIgnoringChildren()
		event.Skip()

