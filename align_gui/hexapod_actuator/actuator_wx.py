"""
actuator_wx.py
"""

import numpy
import wx
import wx.lib.newevent
from wx_extensions.windows import ScrolledPanelBase
from wx_extensions.exceptions import handlesErrors

############################ CONSTANTS ################################
ActuatorDoneEvent, EVT_ACTUATOR_DONE = wx.lib.newevent.NewEvent()
#######################################################################

class HexapodActuatorWxScrolledPanel(ScrolledPanelBase):
	"""
	@Purpose:
		Abstract class / Interface for setting up HexapodActuator wxScrolledPanel
	"""
	def __init__(self, parent, actuator, id=wx.ID_ANY, pos=wx.DefaultPosition, 
				size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		##### necessary class variables ######
		self.actuator = actuator
		self.plot_width = 0.35
		self.cap_start_positions = numpy.zeros(6)
		self.cap_target_positions = numpy.zeros(6)
		self.cap_change_amounts = numpy.zeros(6)
		self.cap_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.cap_plot_ylims = (-10,10)
		self.leg_change_amounts = numpy.zeros(6)
		self.leg_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.leg_plot_ylims = (-10,10)
		######################################
		### DEBUG ###
		self.__debug__ = False

		if self.actuator != None:
			self.cap_start_positions = self.actuator.getPositions()
			self.cap_target_positions = self.cap_start_positions

		ScrolledPanelBase.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )

		topLevelWindow = parent.getTopLevelWindow()
		if hasattr(topLevelWindow, "menuItemDebug"):
			if topLevelWindow.menuItemDebug.IsChecked():
				self.__debug__ = True
			else:
				self.__debug = False

	@handlesErrors
	def setAutoPlotLegYLim(self):
		leg_change_abs_max = numpy.max(numpy.abs(self.leg_change_amounts))
		if leg_change_abs_max == 0:
			self.leg_plot_ylims = (-10, 10)
		else:
			self.leg_plot_ylims = (-1*leg_change_abs_max-leg_change_abs_max/2.0, leg_change_abs_max+leg_change_abs_max/2.0)

	@handlesErrors
	def setAutoPlotCapYLim(self):
		cap_change_abs_max = numpy.max(numpy.abs(self.cap_change_amounts))
		if cap_change_abs_max == 0:
			self.cap_plot_ylims = (-10, 10)
		else:
			self.cap_plot_ylims = (-1*cap_change_abs_max-cap_change_abs_max/2.0, cap_change_abs_max+cap_change_abs_max/2.0)

	@handlesErrors
	def plotCapChange(self):
		"""
		@Purpose:
			API method for plotting CapChange
		"""
		print "WARNING: calling HexapodActuatorWxScrolledPanel.plotCapChange(). Override plotCapChange() on child class to get the desired behavior."

	@handlesErrors
	def plotLegChange(self):
		"""
		@Purpose:
			API method for plotting LegChange
		"""
		print "WARNING: calling HexapodActuatorWxScrolledPanel.plotLegChange(). Override plotLegChange() on child class to get the desired behavior."

	@handlesErrors
	def onCapChange(self, event):
		"""
		@Purpose:
			API method for handling capgauge changing event
		"""
		if self.actuator == None:
			print "ERROR: HexapodActuatorWxScrolledPanel.actuator is NULL. Check your actuator class initialization!"
		else:
			self.cap_start_positions = self.actuator.getPositions()
			self.cap_change_amounts = self.cap_target_positions - self.cap_start_positions
			self.actuator.setMoveWidget(self)
			self.cap_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
			self.setAutoPlotCapYLim()
			self.plotCapChange()

	@handlesErrors
	def onLegChange(self, event):
		if self.actuator == None:
			print "ERROR: HexapodActuatorWxScrolledPanel.actuator is NULL. Check your actuator class initialization!"
		else:
			self.actuator.setMoveWidget(self)
			self.leg_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
			self.plotLegChange()