"""
statusbar.py
	statusbar.py contains class that extends wxPython StatusBar class.
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/7/2013	cchen	first created documentation
'''

import wx
import traceback

###########################################################################
## Class StatusBarGauge
##	@Purpose:
##		Create a StatusBar with Gauge (progress) on the right.
###########################################################################
class StatusBarGauge(wx.StatusBar):
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1)

		self.pulsing = False
		self.percent = 0
		
		# This status bar has three fields
		self.SetFieldsCount(2)
		# Sets the three fields to be relative widths to each other.
		self.SetStatusWidths([-4, -1])
		self.sizeChanged = False
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

		# Field 0 ... just text
		self.SetStatusText("Ready", 0)

		# This will fall into field 1 (the second field)
		self.gauge = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize)

		# set the initial position of the checkbox
		self.Reposition()

		# We're going to use a timer to drive a 'clock' in the last field.
		self.timer = wx.PyTimer(self.Notify)

	# set the status
	def SetStatus(self, text, stopPulse=True):
		self.SetStatusText(text, 0)
		if stopPulse and self.pulsing:
			self.pulsing = False
			self.timer.Stop()
			self.gauge.SetValue(0)
		
	# start the pulse timer
	def PulseStart(self):
		self.SetStatus("Running...", False)
		self.timer.Start(500)
		self.pulsing = True
		self.Notify()
	
	# stop the pulse timer
	def PulseStop(self):
		self.SetStatus("Ready", True)
		
	# set the gauge value
	def SetGaugeValue(self, value):
		self.gauge.SetValue(value)
	
	# Handles events from the timer we started in __init__().
	# We're using it to drive a 'clock' in field 2 (the third field).
	def Notify(self):
		try:
			if self.pulsing:
				self.gauge.Pulse()
		except wx.PyAssertionError, e:
			traceback.print_exc()
		except Exception, e:
			traceback.print_exc()
			raise e

	# return if the gauge is pulsing or not
	def IsPulsing(self):
		return self.pulsing

	# on sizing events
	def OnSize(self, evt):
		self.Reposition()  # for normal size events
		# Set a flag so the idle time handler will also do the repositioning.
		# It is done this way to get around a buglet where GetFieldRect is not
		# accurate during the EVT_SIZE resulting from a frame maximize.
		self.sizeChanged = True

	# on idle events
	def OnIdle(self, evt):
		if self.sizeChanged:
			self.Reposition()

	# reposition the gauge
	def Reposition(self):
		rect = self.GetFieldRect(1)
		self.gauge.SetPosition((rect.x+2, rect.y+2))
		self.gauge.SetSize((rect.width-4, rect.height-4))
		self.sizeChanged = False