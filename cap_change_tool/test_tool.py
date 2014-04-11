# -*- coding: utf-8 -*- 

import os
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy
from wx_extensions.windows import FrameBase
import hexapod_actuator
from hexapod_actuator.actuator import HexaPodActuator
from hexapod_actuator.actuator_wxpanel import HexapodActuatorWxScrolledPanel


###########################################################################
## Class FrameMain
###########################################################################
class FrameMain ( FrameBase ):
	def __init__(self, parent, actuator):
		FrameBase.__init__ ( self, parent, id = wx.ID_ANY, title = u"Capgauge Movement Test Tool", pos = wx.DefaultPosition, size = wx.Size(1024, 700), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizerFrameMain = wx.BoxSizer( wx.VERTICAL )
		self.panelMain = PanelMain(self, actuator)
		bSizerFrameMain.Add( self.panelMain, 1, wx.EXPAND |wx.ALL, 0 )
		
		self.SetSizer( bSizerFrameMain )
		self.Layout()
		
		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

###########################################################################
## Class PanelMain
###########################################################################
class PanelMain ( HexapodActuatorWxScrolledPanel ):
	
	def __init__( self, parent, actuator ):
		HexapodActuatorWxScrolledPanel.__init__ ( self, parent, actuator, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizerPanelMain = wx.BoxSizer( wx.VERTICAL )
		
		##### matplotlib Figure #####
		self.figureCapChange = Figure()
		self.axesCapChange = self.figureCapChange.add_subplot(111)

		self.canvasCapChange = FigureCanvas(self, wx.ID_ANY, self.figureCapChange)
		bSizerPanelMain.Add( self.canvasCapChange, 1, wx.ALL|wx.EXPAND, 0 )

		### produce bar graph ###
		self.plotCapChange()
		#############################
		
		self.staticlineSepMain = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPanelMain.Add( self.staticlineSepMain, 0, wx.EXPAND |wx.ALL, 5 )
		
		gSizerLegControls = wx.GridSizer( 2, 4, 0, 0 )
		
		self.staticTextLegNumTitle = wx.StaticText( self, wx.ID_ANY, u"Leg #", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextLegNumTitle.Wrap( -1 )
		self.staticTextLegNumTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, True, wx.EmptyString ) )
		gSizerLegControls.Add( self.staticTextLegNumTitle, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.staticTextChangeAmountTitle = wx.StaticText( self, wx.ID_ANY, u"Change Amount", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeAmountTitle.Wrap( -1 )
		self.staticTextChangeAmountTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, True, wx.EmptyString ) )
		gSizerLegControls.Add( self.staticTextChangeAmountTitle, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.staticTextNumIterationsTitle = wx.StaticText( self, wx.ID_ANY, u"Number of Iterations", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextNumIterationsTitle.Wrap( -1 )
		self.staticTextNumIterationsTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, True, wx.EmptyString ) )
		gSizerLegControls.Add( self.staticTextNumIterationsTitle, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.staticTextToleranceTitle = wx.StaticText( self, wx.ID_ANY, u"Tolerance", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextToleranceTitle.Wrap( -1 )
		self.staticTextToleranceTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, True, wx.EmptyString ) )
		gSizerLegControls.Add( self.staticTextToleranceTitle, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.textCtrlLegNum = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		gSizerLegControls.Add( self.textCtrlLegNum, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlChangeAmount = wx.TextCtrl( self, wx.ID_ANY, u"0.0", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		gSizerLegControls.Add( self.textCtrlChangeAmount, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlNumIterations = wx.TextCtrl( self, wx.ID_ANY, u"3", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		gSizerLegControls.Add( self.textCtrlNumIterations, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlTolerance = wx.TextCtrl( self, wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		gSizerLegControls.Add( self.textCtrlTolerance, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerPanelMain.Add( gSizerLegControls, 0, wx.EXPAND, 5 )
		
		self.staticlineSepControls = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPanelMain.Add( self.staticlineSepControls, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerControls = wx.BoxSizer( wx.HORIZONTAL )
		
		self.buttonControlGo = wx.Button( self, wx.ID_ANY, u"GO", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonControlGo.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerControls.Add( self.buttonControlGo, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonContorlZero = wx.Button( self, wx.ID_ANY, u"Zero", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonContorlZero.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerControls.Add( self.buttonContorlZero, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerPanelMain.Add( bSizerControls, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizerPanelMain )
		self.Layout()
		self.SetupScrolling()
		bSizerPanelMain.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.buttonControlGo.Bind( wx.EVT_BUTTON, self.onControlGo )
		self.buttonContorlZero.Bind( wx.EVT_BUTTON, self.onControlZero )
	
	def __del__( self ):
		pass
	
	# default methods for plotting capgauge change in matplotlib
	# required exact signature to have actuator class to call
	def plotCapChange(self, isUpdatingFromLegChange=False):
		"""
		@Purpose:
			default inherited methods for plotting capgauge change in matplotlib
			required exact signature to have actuator class to call
		"""
		##### updates the self.cap_change_amounts, if necessary (due to already performed leg change) #####
		if self.actuator != None and isUpdatingFromLegChange:
			self.cap_change_amounts = self.cap_target_positions - self.actuator.getPositions()

		# reset the plot
		self.axesCapChange.clear()

		
		### test if we need to fix the autoscale for the plot ###
		bounds = 1.0 	# default
		notPlotted = True
		for i in self.cap_change_amounts:
			if i != 0.0:
				notPlotted = False
				break
		if notPlotted:
			self.axesCapChange.autoscale(True)
		else:
			bounds = numpy.max(numpy.abs(self.cap_change_amounts))
			self.axesCapChange.autoscale(False)
		

		# bar plots
		indCapChange = numpy.arange(len(self.cap_change_amounts)) + 0.35						# + margins
		rectsCapChange = self.axesCapChange.bar(indCapChange, self.cap_change_amounts, self.plot_width, color='g')
		self.axesCapChange.axhline(y=0, xmin=0, xmax=len(self.cap_change_amounts)-1, color='black')
		self.axesCapChange.set_ylabel('Projected Movements (micron)')
		self.axesCapChange.set_title('Cap Change Projected Movements')
		self.axesCapChange.set_xticks(indCapChange+self.plot_width/2.)
		self.cap_change_labels = self.leg_change_labels					# only in this program
		self.axesCapChange.set_xticklabels(tuple(self.cap_change_labels))
		### label value for each leg ###
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

	def plotLegChange(self):
		pass

	def initialPlot(self):
		self.cap_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.leg_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.plotCapChange()
		bounds = numpy.max(numpy.abs(self.cap_change_amounts))
		self.axesCapChange.set_ylim(-1*bounds-bounds/2, bounds+bounds/2)
		self.axesCapChange.autoscale(False)
		# refresh widget
		self.refreshWidget(self.canvasCapChange)

	# Virtual event handlers, overide them in your derived class
	def onControlGo( self, event ):
		### Zero everytime before we go ###
		self.onControlZero(event)

		tolerance = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
		# error checking:
		if not self.textCtrlLegNum.GetValue():
			self.popErrorBox('Please Enter Valid Leg #', 'ERROR: Please enter valid leg number.')
		elif not self.textCtrlChangeAmount.GetValue():
			self.popErrorBox('Please Enter Valid Change Amounts', 'ERROR: Please enter valid change amounts.')
		elif not self.textCtrlNumIterations.GetValue():
			self.popErrorBox('Please Enter Valid Iterations', 'ERROR: Please enter valid iterations.')
		elif not self.textCtrlTolerance.GetValue():
			self.popErrorBox('Please Enter Valid Tolerance', 'ERROR: Please enter valid tolerance number.')

		leg = int(self.textCtrlLegNum.GetValue())-1
		self.leg_change_amounts[leg] = float(self.textCtrlChangeAmount.GetValue())
		self.cap_change_amounts = self.leg_change_amounts
		iterations = int(self.textCtrlNumIterations.GetValue())
		tolerance[leg] = float(self.textCtrlTolerance.GetValue())

		##### remember to set the actuator move widget... #####
		super(PanelMain, self).onCapChange(event)
		#######################################################

		self.initialPlot()
		self.__startThread__(self.actuator.legChange, self.leg_change_amounts, tolerance, iterations)
	
	def onControlZero( self, event ):
		self.cap_change_amounts = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		self.cap_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.leg_change_labels = ['Leg1,i:0', 'Leg2,i:0', 'Leg3,i:0', 'Leg4,i:0', 'Leg5,i:0', 'Leg6,i:0']
		self.cap_start_pos = self.actuator.getPositions()
		self.plotCapChange()


################## MAIN ###################
if __name__ == "__main__":
	### actuator object ###
	motorControllers = ['8742-10140', '8742-10159']
	NI_config_file = os.path.dirname(hexapod_actuator.__file__) + '/NI_composite_capgauge.config'
	actuator = HexaPodActuator(NI_config_file, motorControllers)
	#######################

	app = wx.PySimpleApp()
	frame = FrameMain(None, actuator)
	frame.Show()
	app.MainLoop()
###########################################

