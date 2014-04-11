"""
adjustHexapodPanel.py
	Contains PanelAdjustHexapod class for displaying adjust hexapod information
"""

import os
import numpy
import re
import time
import traceback
import wx
import wx.grid as gridlib
from wx_extensions.windows import ScrolledPanelBase
from wx_extensions.grid import CustomDataGrid
from wx_extensions.dialogs import DialogProgress
from wx_extensions.exceptions import handlesErrors
from moveHexapodPanel import PanelMoveHexapod

###########################################################################
## Class PanelAdjustHexapod
###########################################################################

class PanelAdjustHexapod ( ScrolledPanelBase ):
	
	def __init__( self, parent, alignObj, hexapodObj, actuator ):
		self.alignObj = alignObj
		self.hexapodObj = hexapodObj
		self.actuator = actuator
		self.hasLegCapgaugeGrid = False
		ScrolledPanelBase.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
		
		bSizerPanel = wx.BoxSizer( wx.VERTICAL )
		
		#####################
		# adjustment label
		#####################
		self.staticTextHexapodAdjustment = wx.StaticText( self, wx.ID_ANY, u"Hexapod Adjustment (ID: "+self.alignObj.hexapodID+")", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHexapodAdjustment.Wrap( -1 )
		self.staticTextHexapodAdjustment.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerPanel.Add( self.staticTextHexapodAdjustment, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		bSizerAdjustGrid = wx.BoxSizer( wx.HORIZONTAL )

		bSizerAdjustGrid.AddSpacer( (20, 20), 1, wx.EXPAND|wx.ALL, 5 )
		
		####################
		# adjustment grid
		####################
		labels = ["Compensator", "Solve Amounts", "Include", "Move", "Units"]
		dataTypes = [gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT+':6,9', gridlib.GRID_VALUE_BOOL, gridlib.GRID_VALUE_FLOAT+':6,9', gridlib.GRID_VALUE_STRING]
		self.adjustHexapodGrid = CustomDataGrid(self, labels, dataTypes)
		self.updateAdjustGrid()												# fill the data
		self.adjustHexapodGrid.SetColLabelSize(30)
		self.adjustHexapodGrid.AutoSize()

		####################
		# Cell Attributes
		####################
		self.adjustHexapodGrid.SetColReadOnly(0)
		self.adjustHexapodGrid.SetColReadOnly(1)
		self.adjustHexapodGrid.SetColReadOnly(3)
		self.adjustHexapodGrid.SetColReadOnly(4)

		bSizerAdjustGrid.Add( self.adjustHexapodGrid, 1, wx.ALL|wx.ALIGN_CENTER, 5 )
		
		bSizerAdjustGridControl = wx.BoxSizer( wx.VERTICAL )
		
		self.buttonIncludeAll = wx.Button( self, wx.ID_ANY, u"Include All", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerAdjustGridControl.Add( self.buttonIncludeAll, 0, wx.ALL, 5 )
		#self.buttonIncludeAll.Hide()
		
		self.textCtrlFactor = wx.TextCtrl( self, wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerAdjustGridControl.Add( self.textCtrlFactor, 0, wx.ALL, 5 )
		#self.textCtrlFactor.Hide()
		
		self.buttonFactor = wx.Button( self, wx.ID_ANY, u"Set Factor", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerAdjustGridControl.Add( self.buttonFactor, 0, wx.ALL, 5 )
		#self.buttonFactor.Hide()

		bSizerAdjustGridControl.Layout()
		bSizerAdjustGrid.Add( bSizerAdjustGridControl, 0, wx.ALIGN_CENTER, 5 )	

		self.staticTextAdjustmentNotes = wx.StaticText( self, wx.ID_ANY, u"Note:\nCorrection move is\nopposite of solve amount", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextAdjustmentNotes.Wrap( -1 )
		self.staticTextAdjustmentNotes.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		bSizerAdjustGrid.Add( self.staticTextAdjustmentNotes, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		bSizerAdjustGrid.AddSpacer( ( 20, 20), 1, wx.EXPAND|wx.ALL, 5 )

		bSizerAdjustGrid.Layout()
		
		bSizerPanel.Add( bSizerAdjustGrid, 0, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5 )
		self.refreshWidget(self.adjustHexapodGrid)

		self.SetSizer( bSizerPanel )
		self.Layout()
		self.SetupScrolling()
		bSizerPanel.Fit(self)
		self.getTopLevelWindow().Layout()

		# Connect Events
		self.adjustHexapodGrid.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.onAdjustHexapodGridCellChange )
		self.buttonIncludeAll.Bind( wx.EVT_BUTTON, self.onInclude )
		self.buttonFactor.Bind( wx.EVT_BUTTON, self.onSetFactor )
	
	def __del__( self ):
		pass

	@handlesErrors
	def updateLegCapgaugeGrid(self):
		"""
		@Purpose:
			Initialize the leg / capgauge grid
			***** MUST BE CALLED AFTER updateAdjustGrid() *****
		"""
		self.refreshWidget(self.legCapgaugeGrid)
		# get the perturbation adjust amount from adjustHexapodGrid
		pert_adjust = []
		for row in range(self.adjustHexapodGrid.GetNumberRows()):
			adjust = self.adjustHexapodGrid.GetCellValue(row, 3)
			pert_adjust.append(adjust)

		# calculate the hexapod leg movement with perturbation adjustments
		self.hexapodObj.set_pert_adjusts(pert_adjust)
		threadID = self.__startThread__(self.hexapodObj.solve)
		threadMap = self.__getThreadMap__()
		# start the progress (pulse) dialog
		pulseDialog = wx.ProgressDialog("Loading...", 
										"Performing Calculation, Please Wait...",
										maximum=100,
										parent=self,
										style=wx.PD_APP_MODAL)
		while threadMap[threadID].isAlive():
			pulseDialog.Pulse()
			time.sleep(0.01)
		pulseDialog.Destroy()

		if self.actuator == None:
			##### ERROR Handling #####
			self.popErrorBox("ERROR: actuator object NOT FOUND.", 
				"ERROR: actuator object == None. Check if you have the proper connection to the Capgauge and Picomotors.")
		else:
			try:
				curr_cap_positions = self.actuator.getPositions()
				(date_time_obj, starting_cap_positions, comments) = self.hexapodObj.read_capGauge_file()
			except Exception, e:
				##### HANDLES read capgauge starting position errors #####
				self.popErrorBox("ERROR: read capgauge starting position FAILED.",
					"ERROR: read capgauge starting position FAILED.\n\n"+traceback.format_exc())
				print "ERROR: read capgauge starting position FAILED."
				traceback.print_exc()
				##########################################################

		for legNum in range(6):
			self.legCapgaugeGrid.SetCellValue(legNum, 0, legNum+1)
			self.legCapgaugeGrid.SetCellValue(legNum, 1, self.hexapodObj.leg_changes[legNum])
			self.legCapgaugeGrid.SetCellValue(legNum, 2, self.hexapodObj.cap_changes[legNum])
			if self.actuator != None:
				total_changes = curr_cap_positions[legNum]/1000.0 + self.hexapodObj.cap_changes[legNum] - starting_cap_positions[legNum]/1000.0
				self.legCapgaugeGrid.SetCellValue(legNum, 3, total_changes)
			else:
				self.legCapgaugeGrid.SetCellValue(legNum, 3, self.hexapodObj.cap_changes[legNum])

			if abs(self.legCapgaugeGrid.GetCellValue(legNum, 3)) > 0.1:
				self.legCapgaugeGrid.SetCellBackgroundColour(legNum, 3, (255,0,0))
			else:
				self.legCapgaugeGrid.ResetDefaultCellBackgroundColour(legNum, 3)

		self.refreshWidget(self.legCapgaugeGrid)

	@handlesErrors
	def updateAdjustGrid(self):
		"""
		@Purpose:
			Initialize the adjustment hexapod grid
		"""
		compensator_name_map = {'xrot': 'xrot_m1',
								'yrot': 'yrot_m1',
								'xtrans': 'xtrans_m1',
								'ytrans': 'ytrans_m1',
								'ztrans': 'ztrans_m1'}
		compensators = ['xrot', 'yrot', 'zrot', 'xtrans', 'ytrans', 'ztrans']
		for ind in range(len(compensators)):
			self.adjustHexapodGrid.SetCellValue(ind, 0, compensators[ind])		# compensators
			try:
				comp_index = list(self.alignObj.usedperts).index(compensator_name_map[compensators[ind]])
				solve_adjust = self.alignObj.p_radians[comp_index]
				units = self.alignObj.units_radians[comp_index]
			except KeyError, e:
				solve_adjust = numpy.NaN
				units = 'rad'
			self.adjustHexapodGrid.SetCellValue(ind, 1, solve_adjust)			# solve adjustment
			self.adjustHexapodGrid.SetCellValue(ind, 2, False)					# Include
			if compensators[ind] == 'zrot':
				self.adjustHexapodGrid.SetCellValue(ind, 3, numpy.NaN)			# zrot special case to default to NaN
			else:
				self.adjustHexapodGrid.SetCellValue(ind, 3, 0.0)				# move (default = 0.0)
			self.adjustHexapodGrid.SetCellValue(ind, 4, units)					# units
		self.refreshWidget(self.adjustHexapodGrid)

	@handlesErrors
	def onSolve(self):
		"""
		@Purpose:
			perform the solve functionality when we click on solve button on focus of this tab
		"""
		if not self.hasLegCapgaugeGrid:			# initialize the legCapgaugeGrid
			# add the legCapgaugeGrid
			bSizerPanel = self.GetSizer()

			######################
			# Leg / Capgauge label
			######################
			self.staticTextLegCapgaugeMove = wx.StaticText( self, wx.ID_ANY, u"Leg / Capgauge Move", wx.DefaultPosition, wx.DefaultSize, 0 )
			self.staticTextLegCapgaugeMove.Wrap( -1 )
			self.staticTextLegCapgaugeMove.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
			
			bSizerPanel.Add( self.staticTextLegCapgaugeMove, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
			
			#####################
			# Leg / Capgauge grid
			#####################
			labels = ["Leg#", "Calculated Leg Length Changes (mm)", "Calculated Capgauge Gap Changes (mm)", "After Move Total Capgauge Changes\nFrom Initial Starting Position (mm)"]
			datatypes = [gridlib.GRID_VALUE_NUMBER, gridlib.GRID_VALUE_FLOAT+':6,6', gridlib.GRID_VALUE_FLOAT+':6,6', gridlib.GRID_VALUE_FLOAT+':6,6']
			self.legCapgaugeGrid = CustomDataGrid(self, labels, datatypes)
			self.updateLegCapgaugeGrid()
			self.legCapgaugeGrid.SetColLabelSize(70)
			self.legCapgaugeGrid.AutoSize()

			#####################
			# Cell Attributes
			#####################
			self.legCapgaugeGrid.SetColReadOnly(0)
			self.legCapgaugeGrid.SetColReadOnly(1)
			self.legCapgaugeGrid.SetColReadOnly(2)
			self.legCapgaugeGrid.SetColReadOnly(3)

			bSizerPanel.Add( self.legCapgaugeGrid, 0, wx.ALL|wx.ALIGN_CENTER, 5 )

			#####################
			# Move Button
			#####################
			self.buttonMove = wx.Button( self, wx.ID_ANY, u"MOVE TAB", wx.DefaultPosition, wx.DefaultSize, 0 )
			self.buttonMove.SetToolTipString("Perform the actual movement on the hexapod.")
			self.buttonMove.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
			bSizerPanel.Add( self.buttonMove, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

			#####################
			# Connect Events
			#####################
			self.buttonMove.Bind( wx.EVT_BUTTON, self.onMove )

			self.Layout()
			self.SetupScrolling()
			bSizerPanel.Fit(self)
			self.refreshWidget(self.legCapgaugeGrid)

			self.hasLegCapgaugeGrid = True

		# else just update the grid
		else:
			self.updateLegCapgaugeGrid()
			self.buttonMove.Enable(True)
			self.buttonMove.SetToolTipString("Perform the actual movement on the hexapod.")


	# Virtual event handlers, overide them in your derived class
	def onAdjustHexapodGridCellChange( self, event ):
		event_row = event.GetRow()
		event_col = event.GetCol()
		if event_col == 2:														# include changed
			if self.adjustHexapodGrid.GetCellValue(event_row, event_col):		# including, copy the solve adjustment ot move
				copy_value = -1 * self.adjustHexapodGrid.GetCellValue(event_row, 1)	# reverse the sign of move.
				self.adjustHexapodGrid.SetCellValue(event_row, 3, copy_value)
				self.adjustHexapodGrid.SetReadOnly(event_row, 3, False)			# including, should be editable.
			else:
				if self.adjustHexapodGrid.GetCellValue(event_row, 0) == 'zrot':
					self.adjustHexapodGrid.SetCellValue(event_row, 3, numpy.NaN)	# excluding, set the move to numpy.NaN
				else:
					self.adjustHexapodGrid.SetCellValue(event_row, 3, 0.0)			# excluding, set to default 0.0
				self.buttonIncludeAll.SetLabel("Include All")						# include button should be include all cus we exclude one here.
				self.adjustHexapodGrid.SetReadOnly(event_row, 3, True)				# excluding, should NOT be editable.
		self.refreshWidget(self.adjustHexapodGrid)
		# disable move button because we need to re-do the calculation
		if hasattr(self, 'buttonMove'):
			self.buttonMove.SetToolTipString("Disabled. Changes are not solved yet.")
			self.buttonMove.Enable(False)

	def onInclude( self, event ):
		allIncluded = True
		for row in range(self.adjustHexapodGrid.GetNumberRows()):
			if not self.adjustHexapodGrid.GetCellValue(row, 2):
				allIncluded = False
				break
		if allIncluded:															# excluding everything
			self.buttonIncludeAll.SetLabel("Include All")
			for row in range(self.adjustHexapodGrid.GetNumberRows()):
				self.adjustHexapodGrid.SetCellValue(row, 2, False)
				if self.adjustHexapodGrid.GetCellValue(row, 0) == 'zrot':
					self.adjustHexapodGrid.SetCellValue(row, 3, numpy.NaN)
				else:
					self.adjustHexapodGrid.SetCellValue(row, 3, 0.0)
				self.adjustHexapodGrid.SetReadOnly(row, 3, True)
		else:																	# including everything
			self.buttonIncludeAll.SetLabel("Exclude All")
			for row in range(self.adjustHexapodGrid.GetNumberRows()):
				self.adjustHexapodGrid.SetCellValue(row, 2, True)
				copy_value = -1 * self.adjustHexapodGrid.GetCellValue(row, 1)	# reverse the move sign
				self.adjustHexapodGrid.SetCellValue(row, 3, copy_value)
				self.adjustHexapodGrid.SetReadOnly(row, 3, False)
		self.refreshWidget(self.adjustHexapodGrid)
	
	def onSetFactor( self, event ):
		factor = float(self.textCtrlFactor.GetValue())
		for row in range(self.adjustHexapodGrid.GetNumberRows()):
			move_value = self.adjustHexapodGrid.GetCellValue(row, 3)
			self.adjustHexapodGrid.SetCellValue(row, 3, move_value*factor)
		self.refreshWidget(self.adjustHexapodGrid)

	@handlesErrors
	def onMove( self, event ):
		# sanity check for large move (>0.1 mm)
		isLargeMove = False
		for legNum in xrange(6):			
			if abs(self.legCapgaugeGrid.GetCellValue(legNum, 3)) > 0.1:
				isLargeMove = True
				break
		if isLargeMove:
			choice = self.popInfoBox("Attention: Large Move Detected.",
									"Attention: The moves are fairly large. Are you okay with this?")
			if choice != wx.ID_OK:
				return

		leg_move_amounts = []
		for leg in range(len(self.hexapodObj.leg_changes)):
			# move_amounts in micron, obj units in mm.
			leg_move_amounts.append(self.hexapodObj.leg_changes[leg]*1000)

		cap_move_col = 2
		cap_move_amounts = []
		for row in range(self.legCapgaugeGrid.GetNumberRows()):
			# the move_amounts is in micron, and cell display is in mm
			cap_move_amounts.append(self.legCapgaugeGrid.GetCellValue(row, cap_move_col)*1000)

		topWindow = self.getTopLevelWindow()
		topWindow.deleteTab("Move Hexapod")				# delete before proceed
		page = PanelMoveHexapod(topWindow, [leg_move_amounts, cap_move_amounts], self.actuator)
		topWindow.addTab(page, "Move Hexapod")

