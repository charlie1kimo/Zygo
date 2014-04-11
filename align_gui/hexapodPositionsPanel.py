"""
hexapodPositionsPanel.py
	this file contains the panel class which displays and moves the hexapod positions.
"""

import numpy
import wx
import wx.grid as gridlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from wx_extensions.grid import CustomDataGrid
from wx_extensions.exceptions import handlesErrors
from align_py.hexapod_actuator.actuator_wx import HexapodActuatorWxScrolledPanel
import align_py.hexapod_actuator.actuator_wx as actuator_wx
from align_py.hexapod_actuator.capgauge import CapgaugeException

###########################################################################
## Class PanelHexapodPositions
###########################################################################

class PanelHexapodPositions ( HexapodActuatorWxScrolledPanel ):
	
	def __init__( self, parent, alignObj, hexapodObj, actuator ):
		self.alignObj = alignObj
		self.hexapodObj = hexapodObj
		self.currCapPos = numpy.zeros(6)
		self.homePositions = numpy.zeros(6)
		self.cap_change_amounts = numpy.zeros(6)
		HexapodActuatorWxScrolledPanel.__init__( self, parent, actuator, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
		
		##### Timers #####
		self.continuous_update_timer = wx.Timer(self, wx.NewId())
		##################

		bSizerPanel = wx.BoxSizer( wx.HORIZONTAL )
		
		############## Left Control Panel ###############
		bSizerLeftPanel = wx.BoxSizer( wx.VERTICAL )
		
		### Display Title ###
		self.staticTextHexapodPositionsTitle = wx.StaticText( self, wx.ID_ANY, u"Hexapod Positions (ID: "+self.alignObj.hexapodID+")", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHexapodPositionsTitle.Wrap( -1 )
		self.staticTextHexapodPositionsTitle.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerLeftPanel.Add( self.staticTextHexapodPositionsTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		### positions and movement grid ###
		labels = ["Leg#", "Current Position (um)\nFrom Offset #1", "Offset Changes (um)\nMove", "Target Position (um)\nFrom Offset #1"]
		datatypes = [gridlib.GRID_VALUE_NUMBER, gridlib.GRID_VALUE_FLOAT+':6,3', gridlib.GRID_VALUE_FLOAT+':6,3', gridlib.GRID_VALUE_FLOAT+':6,3']
		self.gridPositions = CustomDataGrid(self, labels, datatypes)

		self.gridPositions.SetColLabelSize(30)
		self.gridPositions.AutoSize()

		####################
		# Cell Attributes
		####################
		self.gridPositions.SetColReadOnly(0)
		self.gridPositions.SetColReadOnly(1)
		self.gridPositions.SetColReadOnly(3)

		bSizerLeftPanel.Add( self.gridPositions, 1, wx.ALIGN_CENTER|wx.ALL, 5 )

		notesString = \
"""
Notes:
A Positive Offset Change Move Causes:
    The leg length to increase
    The Cap Gauge gap to increase
    The Cap Gauge Voltage to decrease (Negative)
    The Motor to un-Screw from the flexure
    The M1 Mirror to translate -Z (down direction) 
"""
		self.staticTextNotes = wx.StaticText( self, wx.ID_ANY, notesString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextNotes.Wrap( -1 )
		self.staticTextNotes.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerLeftPanel.Add( self.staticTextNotes, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		##### A spacer for the layout #####
		bSizerLeftPanel.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		fgSizerControl = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizerControl.SetFlexibleDirection( wx.HORIZONTAL )
		#fgSizerControl.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.buttonUpdatePositions = wx.Button( self, wx.ID_ANY, u"Update / Refresh", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonUpdatePositions.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )

		fgSizerControl.Add( self.buttonUpdatePositions, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )

		self.toggleBtnContinuousUpdates = wx.ToggleButton( self, wx.ID_ANY, u"Continuous Updates", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnContinuousUpdates.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerControl.Add( self.toggleBtnContinuousUpdates, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.buttonSaveOffsets = wx.Button( self, wx.ID_ANY, u"Save Offsets", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonSaveOffsets.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerControl.Add( self.buttonSaveOffsets, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.buttonSelectOffsets = wx.Button( self, wx.ID_ANY, u"Select Offsets (0)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonSelectOffsets.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerControl.Add( self.buttonSelectOffsets, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.buttonBackToStart = wx.Button( self, wx.ID_ANY, u"Back To Home Offsets", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonBackToStart.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerControl.Add( self.buttonBackToStart, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.buttonZeroChanges = wx.Button( self, wx.ID_ANY, u"Zero Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonZeroChanges.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerControl.Add( self.buttonZeroChanges, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		fgSizerControl.AddGrowableCol(0, 1)
		fgSizerControl.AddGrowableCol(1, 1)
		
		bSizerLeftPanel.Add( fgSizerControl, 0, wx.EXPAND, 5 )
		
		bSizerPanel.Add( bSizerLeftPanel, 1, wx.EXPAND, 5 )
		
		################## Right Display Panel #################
		bSizerRightPanel = wx.BoxSizer( wx.VERTICAL )
		
		##### setup canvas display for Cap Change ######
		self.figureCapChange = Figure()
		self.axesCapChange = self.figureCapChange.add_subplot(111)
		self.axesCapChange.grid(color='gray', linestyle='dashed')

		self.canvasCapChange = FigureCanvas(self, wx.ID_ANY, self.figureCapChange)
		bSizerRightPanel.Add( self.canvasCapChange, 1, wx.ALL|wx.EXPAND, 0 )
		################################################

		radioBoxCapChangeAlgoChoices = [ u"Normal", u"Quick" ]
		self.radioBoxCapChangeAlgo = wx.RadioBox( self, wx.ID_ANY, u"Capgauge Change Algorithm", wx.DefaultPosition, wx.DefaultSize, radioBoxCapChangeAlgoChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxCapChangeAlgo.SetSelection( 0 )
		bSizerRightPanel.Add( self.radioBoxCapChangeAlgo, 0, wx.ALL, 5 )

		bSizerRightControl = wx.BoxSizer( wx.HORIZONTAL )
		
		self.buttonCapgaugeChangePositions = wx.Button( self, wx.ID_ANY, u"Capgauge Change Positions", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonCapgaugeChangePositions.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerRightControl.Add( self.buttonCapgaugeChangePositions, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.buttonStop = wx.Button( self, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonStop.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		bSizerRightControl.Add( self.buttonStop, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		bSizerRightPanel.Add( bSizerRightControl, 0, wx.EXPAND, 5)

		bSizerPanel.Add( bSizerRightPanel, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizerPanel )
		self.Layout()

		# Connect Events
		self.gridPositions.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.onOffsetChanges)
		self.buttonUpdatePositions.Bind( wx.EVT_BUTTON, self.onUpdatePositions )
		self.toggleBtnContinuousUpdates.Bind( wx.EVT_TOGGLEBUTTON, self.onContinousUpdatesToggle )
		self.buttonSaveOffsets.Bind( wx.EVT_BUTTON, self.onSaveOffsets )
		self.buttonSelectOffsets.Bind( wx.EVT_BUTTON, self.onSelectOffsets )
		self.buttonBackToStart.Bind( wx.EVT_BUTTON, self.onBackToStart )
		self.buttonZeroChanges.Bind( wx.EVT_BUTTON, self.onZeroChanges )
		self.buttonCapgaugeChangePositions.Bind( wx.EVT_BUTTON, self.onCapChange )
		self.buttonStop.Bind( wx.EVT_BUTTON, self.onStop )
		self.Bind(wx.EVT_TIMER, self.onUpdatePositions, self.continuous_update_timer)
		self.Bind(actuator_wx.EVT_ACTUATOR_DONE, self.onActuatorDoneEvent)

		# setup the home positions
		if self.hexapodObj == None:
			self.popAlertBox("WARNING: hexapodObj is None.", "WARNING: hexapodObj is None. 'Hexapod Positions' display absolute capgauge readings.")
			print "WARNING: hexapodObj is None.", "WARNING: hexapodObj is None. 'Hexapod Positions' display absolute capgauge readings."
			self.buttonSelectOffsets.Enable(False)
			self.buttonBackToStart.Enable(False)
			self.buttonSaveOffsets.Enable(False)
		else:
			try:
				(dateObj, homePos, comments) = self.hexapodObj.read_capGauge_file()
				self.homePositions = numpy.array(homePos)
			except IOError, e:
				self.popErrorBox("ERROR: Hexapod Home Positions ARE NOT SET.", 
								"ERROR: Hexapod home positions are not yet set. Please use the 'Rest Hexapod Initial Start Position' button in 'Input' tab to set home positions.")
				print "ERROR: Hexapod home positions are not yet set. Please use the 'Rest Hexapod Initial Start Position' button in 'Input' tab to set home positions, and then restart."
				self.buttonSelectOffsets.Enable(False)
				self.buttonBackToStart.Enable(False)
				self.buttonSaveOffsets.Enable(False)

		# check if we have actuator
		if self.actuator == None:
			self.buttonCapgaugeChangePositions.Enable(False)
			self.buttonStop.Enable(False)
		else:
			self.currCapPos = self.actuator.getPositions()

		# update the grid to the default value
		self.updateGridPositions()
	
	def __del__( self ):
		pass

	@handlesErrors
	def updateGridPositions(self, fromUpdatePositions=False):
		"""
		@Purpose:
			update the values in gridPositions
		"""
		if self.actuator == None:
			diffCapPos = numpy.zeros(6)
		else:
			diffCapPos = self.currCapPos - self.homePositions

		for legNum in xrange(6):
			self.gridPositions.SetCellValue(legNum, 0, legNum+1)
			self.gridPositions.SetCellValue(legNum, 1, diffCapPos[legNum])
			self.gridPositions.SetCellValue(legNum, 2, self.cap_change_amounts[legNum])
			self.gridPositions.SetCellValue(legNum, 3, diffCapPos[legNum]+self.cap_change_amounts[legNum])
		if hasattr(self, 'buttonSelectOffsets'):
			self.buttonSelectOffsets.SetLabel("Select Offsets (0)")
		if not fromUpdatePositions:
			self.setAutoPlotCapYLim()
		self.plotCapChange(editedChangeAmounts=True)
		self.refreshWidget(self.gridPositions)

	@handlesErrors
	def plotCapChange(self, editedChangeAmounts=False):
		"""
		@Purpose:
			Overriding inherited method from HexapodActuatorWxScrolledPanel
			Perform the actual capChange plotting
		"""
		self.axesCapChange.clear()
		self.axesCapChange.grid(color='gray', linestyle='dashed')
		self.axesCapChange.set_ylim(self.cap_plot_ylims)

		##### updates the self.cap_change_amounts, always.(due to already performed leg change) #####
		if self.actuator != None and not editedChangeAmounts:
			self.cap_change_amounts = self.cap_target_positions - self.actuator.getPositions()

		# bar plots
		indCapChange = numpy.arange(len(self.cap_change_amounts)) + 0.35						# + margins
		rectsCapChange = self.axesCapChange.bar(indCapChange, self.cap_change_amounts, self.plot_width, color='g')
		self.axesCapChange.axhline(y=0, xmin=0, xmax=len(self.cap_change_amounts)-1, color='black')
		self.axesCapChange.set_ylabel('Target Movements (micron)')
		self.axesCapChange.set_title('Delta Cap Gauge Change Target Readings')
		self.axesCapChange.set_xticks(indCapChange+self.plot_width/2.)
		self.axesCapChange.set_xticklabels(tuple(self.cap_change_labels))
		### label value for each leg ###
		bounds = numpy.max(numpy.abs(self.cap_change_amounts))
		bounds_neg = -1*self.cap_plot_ylims[0]
		bounds_pos = -1*self.cap_plot_ylims[1]
		for rect in rectsCapChange:
			height = rect.get_height()
			if rect.get_y() < 0:
				label_height_scale = bounds_neg/5.0
				inverted = -1.0
			else:
				label_height_scale = bounds_pos/5.0
				inverted = 1.0
			self.axesCapChange.text(rect.get_x()+rect.get_width()/2., label_height_scale, '%0.3f' % (inverted*height), ha='center', va='bottom')
		# refresh widget
		self.refreshWidget(self.canvasCapChange)

	# Virtual event handlers, overide them in your derived class
	@handlesErrors
	def onUpdatePositions( self, event ):
		if self.actuator != None:
			try:
				self.currCapPos = self.actuator.getPositions()
			except CapgaugeException, e:
				self.toggleBtnContinuousUpdates.SetValue(False)
				self.getTopLevelWindow().statusBarMain.SetStatus("ERROR")
				self.continuous_update_timer.Stop()
				self.toggleBtnContinuousUpdates.SetBackgroundColour(wx.Colour(255, 255, 255))
				font = self.toggleBtnContinuousUpdates.GetFont()
				font.SetStyle(wx.FONTSTYLE_NORMAL)
				self.toggleBtnContinuousUpdates.SetFont(font)
				raise e
		self.cap_change_amounts = self.cap_target_positions - self.currCapPos
		self.updateGridPositions(fromUpdatePositions=True)

	@handlesErrors
	def onContinousUpdatesToggle( self, event ):
		if self.toggleBtnContinuousUpdates.GetValue():
			self.getTopLevelWindow().statusBarMain.PulseStart()
			self.continuous_update_timer.Start(2000)
			self.toggleBtnContinuousUpdates.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnContinuousUpdates.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			self.toggleBtnContinuousUpdates.SetFont(font)

		else:
			self.getTopLevelWindow().statusBarMain.PulseStop()
			self.continuous_update_timer.Stop()
			self.toggleBtnContinuousUpdates.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnContinuousUpdates.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			self.toggleBtnContinuousUpdates.SetFont(font)

	@handlesErrors
	def onOffsetChanges( self, event ):
		event_row = event.GetRow()
		event_col = event.GetCol()
		if event_col == 2:
			self.cap_change_amounts[event_row] = self.gridPositions.GetCellValue(event_row, event_col)
			self.cap_target_positions[event_row] = self.currCapPos[event_row] + self.cap_change_amounts[event_row]
		self.updateGridPositions()

	@handlesErrors
	def onSaveOffsets( self, event ):
		commentDlg = wx.TextEntryDialog(self, "Optional: Please enter a comment on this offset position.", "Enter a comment for this offset.", "")
		if commentDlg.ShowModal() == wx.ID_OK:
			comment = commentDlg.GetValue()
			curr_abs_cap_readings = self.actuator.getPositions()
			self.hexapodObj.save_capGauge_readings(curr_abs_cap_readings, comment=comment)
	
	@handlesErrors
	def onSelectOffsets( self, event ):
		cap_pos_map = self.hexapodObj.read_capGague_file_positions()
		choices_list = []
		for key in sorted(cap_pos_map.keys()):
			(cap_pos, dateObj, comments) = cap_pos_map[key]
			choice = str(key)+ ": ["
			for posInd in xrange(6):
				choice += "%0.3f" % cap_pos[posInd]
				if posInd < 5:
					choice += ","
				else:
					choice += "]"
			choice += "; " + dateObj.strftime("%Y-%m-%d %H:%M:%S") + "; " + comments
			choices_list.append(choice)

		choiceDlg = wx.SingleChoiceDialog(self, "Please Select an Offset to Setup Calculated Changes.", "Select an Offset", choices_list, wx.CHOICEDLG_STYLE)
		choiceDlg.SetSize(wx.Size(700, 300))
		if choiceDlg.ShowModal() == wx.ID_OK:
			selected_key = int(choiceDlg.GetStringSelection().split(':')[0])
			(cap_pos, dateObj, comments) = cap_pos_map[selected_key]
			if self.actuator != None:
				self.currCapPos = self.actuator.getPositions()
			self.cap_target_positions = numpy.array(cap_pos)
			self.cap_change_amounts = self.cap_target_positions - self.currCapPos
			self.updateGridPositions()	
			self.buttonSelectOffsets.SetLabel("Select Offsets (%d)" % selected_key)
			self.refreshWidget(self.buttonSelectOffsets)
	
	@handlesErrors
	def onBackToStart( self, event ):
		(dateObj, cap_pos, comments) = self.hexapodObj.read_capGauge_file()
		if self.actuator != None:
			self.currCapPos = self.actuator.getPositions()
		self.cap_target_positions = numpy.array(cap_pos)
		self.cap_change_amounts = self.cap_target_positions - self.currCapPos
		self.updateGridPositions()	
		self.buttonSelectOffsets.SetLabel("Select Offsets (1)")
		self.refreshWidget(self.buttonSelectOffsets)
	
	@handlesErrors
	def onZeroChanges( self, event ):
		self.cap_change_amounts = numpy.zeros(6)
		if self.actuator != None:
			self.currCapPos = self.actuator.getPositions()
			self.cap_target_positions = self.currCapPos
		self.updateGridPositions()
	
	@handlesErrors
	def onCapChange( self, event ):
		for leg in xrange(6):			# set cap_target_positions first.
			self.cap_target_positions[leg] = self.gridPositions.GetCellValue(leg, 3) + self.homePositions[leg]

		super(PanelHexapodPositions, self).onCapChange(event)

		self.getTopLevelWindow().statusBarMain.PulseStart()
		self.buttonUpdatePositions.Enable(False)
		self.toggleBtnContinuousUpdates.Enable(False)
		self.buttonSelectOffsets.Enable(False)
		self.buttonZeroChanges.Enable(False)
		self.buttonSaveOffsets.Enable(False)
		self.buttonBackToStart.Enable(False)
		self.buttonCapgaugeChangePositions.Enable(False)

		if self.radioBoxCapChangeAlgo.GetStringSelection() == "Quick":
			self.__startThread__(self.actuator.capgaugeChangeQuick, self.cap_target_positions, debug=self.__debug__)
		else:	
			self.__startThread__(self.actuator.capgaugeChange, self.cap_target_positions, debug=self.__debug__)

	@handlesErrors
	def onStop( self, event ):
		self.actuator.stop()
		topWindow = self.getTopLevelWindow()
		topWindow.statusBarMain.SetStatus('STOPPED', True)
		if self.hexapodObj != None:
			self.buttonUpdatePositions.Enable(True)
			self.toggleBtnContinuousUpdates.Enable(True)
			self.buttonSelectOffsets.Enable(True)
			self.buttonSaveOffsets.Enable(True)
			self.buttonBackToStart.Enable(True)
		self.buttonZeroChanges.Enable(True)
		self.buttonCapgaugeChangePositions.Enable(True)

	@handlesErrors
	def onActuatorDoneEvent( self, event ):
		self.getTopLevelWindow().statusBarMain.PulseStop()
		if self.hexapodObj != None:
			self.buttonUpdatePositions.Enable(True)
			self.toggleBtnContinuousUpdates.Enable(True)
			self.buttonSelectOffsets.Enable(True)
			self.buttonSaveOffsets.Enable(True)
			self.buttonBackToStart.Enable(True)
		self.buttonZeroChanges.Enable(True)
		self.buttonCapgaugeChangePositions.Enable(True)
		self.currCapPos = self.actuator.getPositions()
		self.updateGridPositions()
