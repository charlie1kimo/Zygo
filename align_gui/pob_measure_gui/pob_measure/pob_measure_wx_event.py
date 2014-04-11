"""
pob_measure_wx_event.py
	This module contains custom wxEvents for communication between low level module and GUI module.
"""
import wx
import wx.lib.newevent

############################ CONSTANTS ################################
PobMeasureProgressEvent, EVT_POB_MEAS_PROG = wx.lib.newevent.NewEvent()
PobMeasureErrorEvent, EVT_POB_MEAS_ERROR = wx.lib.newevent.NewEvent()
PobMeasureUpdateTestLetterEvent, EVT_POB_UPDATE_TEST_LETTER = wx.lib.newevent.NewEvent()
#######################################################################