"""
moveHexapodPanel.py
	This file contains the panel class for actually moving the hexapod.
"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy
import wx
from wx_extensions.exceptions import handlesErrors
from align_py.hexapod_actuator.actuator_wx import HexapodActuatorWxScrolledPanel
import align_py.hexapod_actuator.actuator_wx as actuator_wx

###########################################################################
## Class PanelMoveHexapod
###########################################################################
class PanelMoveHexapod ( HexapodActuatorWxScrolledPanel ):
	
	def __init__( self, parent, move_amounts, actuator ):
		HexapodActuatorWxScrolledPanel.__init__ ( self, parent, actuator, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
		##### change the default class variables #####
		self.leg_change_amounts = numpy.array(move_amounts[0])
		self.cap_change_amounts = numpy.array(move_amounts[1])
		######## setup starting capgauge position and target capgauge positions ############
		if self.actuator != None:
			self.cap_start_positions = self.actuator.getPositions()
			self.cap_target_positions = self.cap_start_positions + self.cap_change_amounts
	
		###############################################
		##### plot fixed scale variables ######
		self.setAutoPlotLegYLim()
		self.setAutoPlotCapYLim()
		#######################################

		bSizerPanel = wx.BoxSizer( wx.VERTICAL )
		
		bSizerFigureDisplay = wx.BoxSizer( wx.HORIZONTAL )
		
		##### setup canvas display for Leg Change #####
		self.figureLegChange = Figure()
		self.axesLegChange = self.figureLegChange.add_subplot(111)
		self.axesLegChange.grid(color='gray', linestyle='dashed')

		self.canvasLegChange = FigureCanvas(self, wx.ID_ANY, self.figureLegChange)
		bSizerFigureDisplay.Add( self.canvasLegChange, 1, wx.ALL|wx.EXPAND, 0 )

		# produce bar plots
		self.plotLegChange()
		self.axesLegChange.autoscale(False)
		###############################################
		
		##### setup canvas display for Cap Change ######
		self.figureCapChange = Figure()
		self.axesCapChange = self.figureCapChange.add_subplot(111)
		self.axesCapChange.grid(color='gray', linestyle='dashed')

		self.canvasCapChange = FigureCanvas(self, wx.ID_ANY, self.figureCapChange)
		bSizerFigureDisplay.Add( self.canvasCapChange, 1, wx.ALL|wx.EXPAND, 0 )

		# produce bar plots
		self.plotCapChange()
		self.axesCapChange.autoscale(False)
		################################################
		
		bSizerPanel.Add( bSizerFigureDisplay, 1, wx.EXPAND, 5 )
		
		bSizerMoveControl = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizerMoveControl.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonLegChange = wx.Button( self, wx.ID_ANY, u"Leg Change Move", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonLegChange.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		if self.actuator == None:
			self.buttonLegChange.Enable(False)
			self.buttonLegChange.SetToolTipString("Disabled due to actuator NOT FOUND.")
		bSizerMoveControl.Add( self.buttonLegChange, 0, wx.ALL, 5 )
		
		bSizerMoveControl.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonCapChange = wx.Button( self, wx.ID_ANY, u"Cap Gauge Change Move", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonCapChange.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		if self.actuator == None:
			self.buttonCapChange.Enable(False)
			self.buttonCapChange.SetToolTipString("Disabled due to actuator NOT FOUND.")
		bSizerMoveControl.Add( self.buttonCapChange, 0, wx.ALL, 5 )
		
		radioBoxCapChangeAlgoChoices = [ u"Normal", u"Quick" ]
		self.radioBoxCapChangeAlgo = wx.RadioBox( self, wx.ID_ANY, u"Capgauge Change Algorithm", wx.DefaultPosition, wx.DefaultSize, radioBoxCapChangeAlgoChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxCapChangeAlgo.SetSelection( 0 )
		bSizerMoveControl.Add( self.radioBoxCapChangeAlgo, 0, wx.ALL, 5 )
		
		bSizerPanel.Add( bSizerMoveControl, 0, wx.EXPAND, 5 )
		
		bSizerStop = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizerStop.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonStop = wx.Button( self, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonStop.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		if self.actuator == None:
			self.buttonStop.Enable(False)
			self.buttonStop.SetToolTipString("Disabled due to actuator NOT FOUND.")
		
		bSizerStop.Add( self.buttonStop, 0, wx.ALL, 5 )
		
		bSizerStop.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		bSizerPanel.Add( bSizerStop, 0, wx.EXPAND, 5 )
		
		self.SetSizer( bSizerPanel )
		self.Layout()
		
		# Connect Events
		self.buttonLegChange.Bind( wx.EVT_BUTTON, self.onLegChange )
		self.buttonCapChange.Bind( wx.EVT_BUTTON, self.onCapChange )
		self.buttonStop.Bind( wx.EVT_BUTTON, self.onStop )
		self.Bind(actuator_wx.EVT_ACTUATOR_DONE, self.onActuatorDoneEvent)

	def __del__( self ):
		pass

	@handlesErrors
	def plotLegChange(self):
		self.axesLegChange.clear()
		self.axesLegChange.grid(color='gray', linestyle='dashed')
		self.axesLegChange.set_ylim(self.leg_plot_ylims)

		# bar plots
		indLegChange = numpy.arange(len(self.leg_change_amounts)) + 0.35					# + margins
		rectsLegChange = self.axesLegChange.bar(indLegChange, self.leg_change_amounts, self.plot_width, color='b')
		self.axesLegChange.axhline(y=0, xmin=0, xmax=len(self.leg_change_amounts)-1, color='black')
		self.axesLegChange.set_ylabel('Target Movements (micron)')
		self.axesLegChange.set_title('Individual Leg Change Movements\n(First Move Only)')
		self.axesLegChange.set_xticks(indLegChange+self.plot_width/2.)
		self.axesLegChange.set_xticklabels(tuple(self.leg_change_labels))
		### label value for each leg ###
		bounds = numpy.max(numpy.abs(self.leg_change_amounts))
		for rect in rectsLegChange:
			height = rect.get_height()
			if rect.get_y() < 0:
				label_height_scale = bounds/5.0
				inverted = -1.0
			else:
				label_height_scale = -1*bounds/5.0
				inverted = 1.0
			self.axesLegChange.text(rect.get_x()+rect.get_width()/2., label_height_scale, '%0.3f' % (inverted*height), ha='center', va='bottom')
		# refresh widget
		self.refreshWidget(self.canvasLegChange)

	@handlesErrors
	def plotCapChange(self):
		self.axesCapChange.clear()
		self.axesCapChange.grid(color='gray', linestyle='dashed')
		self.axesCapChange.set_ylim(self.cap_plot_ylims)

		##### updates the self.cap_change_amounts, always.(due to already performed leg change) #####
		if self.actuator != None:
			self.cap_change_amounts = self.cap_target_positions - self.actuator.getPositions()

		# bar plots
		indCapChange = numpy.arange(len(self.cap_change_amounts)) + 0.35						# + margins
		rectsCapChange = self.axesCapChange.bar(indCapChange, self.cap_change_amounts, self.plot_width, color='g')
		self.axesCapChange.axhline(y=0, xmin=0, xmax=len(self.cap_change_amounts)-1, color='black')
		self.axesCapChange.set_ylabel('Target Movements (micron)')
		self.axesCapChange.set_title('Delta Cap Gauge Change Target Readings\n(First or Second Move)')
		self.axesCapChange.set_xticks(indCapChange+self.plot_width/2.)
		self.axesCapChange.set_xticklabels(tuple(self.cap_change_labels))
		### label value for each leg ###
		bounds = numpy.max(numpy.abs(self.cap_change_amounts))
		for rect in rectsCapChange:
			height = rect.get_height()
			if rect.get_y() < 0:
				label_height_scale = bounds/5.0
				inverted = -1.0
			else:
				label_height_scale = -1*bounds/5.0
				inverted = 1.0
			self.axesCapChange.text(rect.get_x()+rect.get_width()/2., label_height_scale, '%0.3f' % (inverted*height), ha='center', va='bottom')
		# refresh widget
		self.refreshWidget(self.canvasCapChange)
	
	# Virtual event handlers, overide them in your derived class
	@handlesErrors
	def onLegChange( self, event ):
		# remember to call inherited method
		super(PanelMoveHexapod, self).onLegChange(event)

		self.buttonLegChange.Enable(False)
		self.buttonCapChange.Enable(False)
		self.getTopLevelWindow().statusBarMain.PulseStart()
		self.__startThread__(self.actuator.legChange, self.leg_change_amounts, debug=self.__debug__)
	
	@handlesErrors
	def onCapChange( self, event ):
		# remember to call inherited method
		super(PanelMoveHexapod, self).onCapChange(event)

		self.buttonCapChange.Enable(False)
		self.getTopLevelWindow().statusBarMain.PulseStart()
		self.buttonLegChange.Enable(False)				# performing cap change. Leg change shouldn't be allowed afterward
		if self.radioBoxCapChangeAlgo.GetStringSelection() == "Quick":
			self.__startThread__(self.actuator.capgaugeChangeQuick, self.cap_target_positions, debug=self.__debug__)
		else:
			self.__startThread__(self.actuator.capgaugeChange, self.cap_target_positions, debug=self.__debug__)
	
	@handlesErrors
	def onStop( self, event ):
		self.actuator.stop()
		topWindow = self.getTopLevelWindow()
		topWindow.statusBarMain.SetStatus('STOPPED', True)
		self.buttonLegChange.Enable(True)
		self.buttonCapChange.Enable(True)

	@handlesErrors
	def onActuatorDoneEvent( self, event ):
		self.getTopLevelWindow().statusBarMain.PulseStop()
		if event.fromFunction == 'legChange':
			self.buttonLegChange.Enable(True)
		self.buttonCapChange.Enable(True)

