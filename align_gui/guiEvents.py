"""
guiEvents.py
	This file contains the custom wxPython Events for handling special cases
"""
import wx

#############################################################################
## Constants
#############################################################################
EVT_TYPE_MOVE_THREAD_TERMINATED = wx.NewEventType()
EVT_MOVE_THREAD_TERMINATED = wx.PyEventBinder(EVT_TYPE_MOVE_THREAD_TERMINATED, 1)

#############################################################################
## class ThreadTerminatedEvent
#############################################################################
class MoveThreadTerminatedEvent(wx.PyCommandEvent):
	def __init__(self, etype, eid):
		wx.PyCommandEvent.__init__(self, etype, eid)

