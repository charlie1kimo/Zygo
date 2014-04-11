"""
inputPanel:
	Contain PanelInput class for handling the input panel tab
"""

import numpy
import os
import time
import traceback
import wx
from wx_extensions.windows import ScrolledPanelBase
from wx_extensions.exceptions import handlesErrors
from met5hexapod import Hexalign

###########################################################################
## Class PanelInput
###########################################################################

class PanelInput (ScrolledPanelBase):
	
	def __init__(self, parent):
		self.fieldCoordDefaultValue = "[(0,0),(1,1),(1,-1),(-1,-1),(-1,1)]"
		ScrolledPanelBase.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(700,150), style = wx.CLIP_CHILDREN|wx.FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL)
		
		boxSizerPanel = wx.BoxSizer(wx.VERTICAL)

		self.staticTextInputTitle = wx.StaticText( self, wx.ID_ANY, u"Wavefront Data Input", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextInputTitle.Wrap( -1 )
		self.staticTextInputTitle.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		boxSizerPanel.Add( self.staticTextInputTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		boxSizerScenario = wx.BoxSizer(wx.HORIZONTAL)
		
		self.radioButtonScenario = wx.RadioButton(self, wx.ID_ANY, "Scenario", wx.DefaultPosition, wx.DefaultSize, 0)
		boxSizerScenario.Add(self.radioButtonScenario, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.staticLineScenario = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)
		boxSizerScenario.Add(self.staticLineScenario, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5)
		
		self.staticTextScenarioFile = wx.StaticText(self, wx.ID_ANY, "File", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)
		self.staticTextScenarioFile.Wrap(-1)
		boxSizerScenario.Add(self.staticTextScenarioFile, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.textCtrlScenarioFile = wx.TextCtrl(self, wx.ID_ANY, 'systestdbl_simulated_01-Aug-2012_cset2_all.csv', wx.DefaultPosition, wx.Size( 300,-1 ), 0)
		boxSizerScenario.Add(self.textCtrlScenarioFile, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.buttonScnearioOpen = wx.Button(self, wx.ID_ANY, "Open...", wx.DefaultPosition, wx.DefaultSize, 0)
		boxSizerScenario.Add(self.buttonScnearioOpen, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.staticLineScenario2 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)
		boxSizerScenario.Add(self.staticLineScenario2, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5)
		
		self.staticTextColumn = wx.StaticText(self, wx.ID_ANY, "Column", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)
		self.staticTextColumn.Wrap(-1)
		boxSizerScenario.Add(self.staticTextColumn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.textCtrlScenarioColumn = wx.TextCtrl( self, wx.ID_ANY, "scenario4", wx.DefaultPosition, wx.Size( 100,-1 ), 0)
		boxSizerScenario.Add(self.textCtrlScenarioColumn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		boxSizerPanel.Add(boxSizerScenario, 0, wx.EXPAND, 5)
		
		boxSizerGntSet = wx.BoxSizer(wx.HORIZONTAL)
		
		self.radioButtonGntSet = wx.RadioButton(self, wx.ID_ANY, u"GntSet", wx.DefaultPosition, wx.DefaultSize, 0)
		boxSizerGntSet.Add(self.radioButtonGntSet, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.staticLineGntSet = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)
		boxSizerGntSet.Add(self.staticLineGntSet, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5)
		
		self.staticTextGntSetRoot = wx.StaticText(self, wx.ID_ANY, u"Root", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)
		self.staticTextGntSetRoot.Wrap(-1)
		boxSizerGntSet.Add(self.staticTextGntSetRoot, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.textCtrlGntSetRoot = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,-1 ), 0)
		self.textCtrlGntSetRoot.SetValue('xdogs_')			# default
		boxSizerGntSet.Add(self.textCtrlGntSetRoot, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.staticLineGntSet2 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)
		boxSizerGntSet.Add(self.staticLineGntSet2, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5)
		
		self.staticTextGntSetExt = wx.StaticText(self, wx.ID_ANY, u"Ext", wx.DefaultPosition, wx.DefaultSize, 0)
		self.staticTextGntSetExt.Wrap(-1)
		boxSizerGntSet.Add(self.staticTextGntSetExt, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.textCtrlGntSetExt = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100,-1 ), 0)
		self.textCtrlGntSetExt.SetValue('gnt')				# default
		boxSizerGntSet.Add(self.textCtrlGntSetExt, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		boxSizerPanel.Add(boxSizerGntSet, 0, wx.EXPAND, 5)
		
		boxSizerZernikes = wx.BoxSizer(wx.HORIZONTAL)
		
		self.radioButtonZernikes = wx.RadioButton(self, wx.ID_ANY, u"Zernikes", wx.DefaultPosition, wx.DefaultSize, 0)
		boxSizerZernikes.Add(self.radioButtonZernikes, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		##### TEMPORARY DISABLE ZERNIKES BUTTON; waiting align2.py implementation ######
		self.radioButtonZernikes.Enable(False)
		################################################################################
		
		self.staticLineZernikes = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL)
		boxSizerZernikes.Add(self.staticLineZernikes, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5)
		
		self.staticTextZernikesFile = wx.StaticText(self, wx.ID_ANY, u"File", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)
		self.staticTextZernikesFile.Wrap(-1)
		boxSizerZernikes.Add(self.staticTextZernikesFile, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.textCtrlZernikesFile = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0)
		boxSizerZernikes.Add(self.textCtrlZernikesFile, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.buttonZernikesOpen = wx.Button(self, wx.ID_ANY, u"Open...", wx.DefaultPosition, wx.DefaultSize, 0)
		boxSizerZernikes.Add(self.buttonZernikesOpen, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		boxSizerPanel.Add(boxSizerZernikes, 0, wx.EXPAND, 5)

		boxSizerStartAll = wx.BoxSizer( wx.HORIZONTAL )
		
		self.radioButtonStartAllZeros = wx.RadioButton( self, wx.ID_ANY, u"Start All Zeros", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.radioButtonStartAllZeros.SetValue(True)
		boxSizerStartAll.Add( self.radioButtonStartAllZeros, 0, wx.ALL, 5 )
		
		boxSizerPanel.Add( boxSizerStartAll, 0, wx.EXPAND, 5 )

		bSizerFieldCoord = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextFieldCoordTitle = wx.StaticText( self, wx.ID_ANY, u"Field Coordinates:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextFieldCoordTitle.Wrap( -1 )
		bSizerFieldCoord.Add( self.staticTextFieldCoordTitle, 0, wx.ALL, 5 )
		
		self.textCtrlFieldCoord = wx.TextCtrl( self, wx.ID_ANY, self.fieldCoordDefaultValue, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		bSizerFieldCoord.Add( self.textCtrlFieldCoord, 0, wx.ALL, 5 )
		
		boxSizerPanel.Add( bSizerFieldCoord, 0, wx.EXPAND, 5 )
		
		# seperated line
		self.staticlineSep1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		boxSizerPanel.Add( self.staticlineSep1, 0, wx.EXPAND |wx.ALL, 5 )
		
		# Displaying and controling parameters
		fgSizerParams = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizerParams.SetFlexibleDirection( wx.BOTH )
		fgSizerParams.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextMeasuredTrackLength = wx.StaticText( self, wx.ID_ANY, u"Measured Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasuredTrackLength.Wrap( -1 )
		fgSizerParams.Add( self.staticTextMeasuredTrackLength, 1, wx.ALL, 5 )
		
		self.textCtrlMeasuredTrackLength = wx.TextCtrl( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerParams.Add( self.textCtrlMeasuredTrackLength, 1, wx.ALL, 5 )
		
		self.staticTextTargetTrackLength = wx.StaticText( self, wx.ID_ANY, u"Target Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTargetTrackLength.Wrap( -1 )
		fgSizerParams.Add( self.staticTextTargetTrackLength, 1, wx.ALL, 5 )
		
		self.textCtrlTargetTrackLength = wx.TextCtrl( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerParams.Add( self.textCtrlTargetTrackLength, 1, wx.ALL, 5 )

		self.staticTextHexapodID = wx.StaticText( self, wx.ID_ANY, u"Hexapod ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHexapodID.Wrap( -1 )
		fgSizerParams.Add( self.staticTextHexapodID, 1, wx.ALL , 5 )

		self.textCtrlHexapodID = wx.TextCtrl( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerParams.Add( self.textCtrlHexapodID, 1, wx.ALL, 5 )
		
		boxSizerPanel.Add( fgSizerParams, 0, wx.EXPAND, 5 )

		self.buttonReset = wx.Button( self, wx.ID_ANY, u"Reset Hexapod Initial Start Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonReset.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		boxSizerPanel.Add( self.buttonReset, 0, wx.ALL, 5 )

		#self.buttonGoHome = wx.Button( self, wx.ID_ANY, u"Go To Hexapod Start Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		#self.buttonGoHome.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		#boxSizerPanel.Add( self.buttonGoHome, 0, wx.ALL, 5 )
		
		self.SetSizer(boxSizerPanel)
		self.Layout()
		self.SetupScrolling()
		boxSizerPanel.Fit(self)
		
		# Connect Events
		self.buttonScnearioOpen.Bind(wx.EVT_BUTTON, self.onScenarioFileOpen)
		self.buttonZernikesOpen.Bind(wx.EVT_BUTTON, self.onZernikesFileOpen)
		self.buttonReset.Bind( wx.EVT_BUTTON, self.onResetHexapodStartPosition )
		#self.buttonGoHome.Bind( wx.EVT_BUTTON, self.onGoHexpaodStartPosition)

		# disable if the actuator failed to initiate
		if self.getTopLevelWindow().actuator == None:
			self.buttonReset.Enable(False)
			#self.buttonGoHome.Enable(False)
	
	def __del__(self):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	@handlesErrors
	def onScenarioFileOpen(self, event):
		wildcard = "Comma Separated Value File (*.csv)|*.csv|" \
					"Excel File (*.xls)|*.xls|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.textCtrlScenarioFile.SetValue(os.path.basename(dialog.GetPath()))
		dialog.Destroy()
		event.Skip()
	
	@handlesErrors
	def onZernikesFileOpen(self, event):
		wildcard = "All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.textCtrlZernikesFile.SetValue(os.path.basename(dialog.GetPath()))
		dialog.Destroy()
		event.Skip()

	def onResetHexapodStartPosition(self, event):
		popUpOK = self.popInfoBox('Resetting Initial Position', 'Resetting Hexapod Initial Starting Position!\nAre you sure to contintue?')
		if popUpOK != wx.ID_OK:
			return
		else:
			try:
				actuator = self.getTopLevelWindow().actuator
				hexapodObj = self.getTopLevelWindow().hexapodObj
				if hexapodObj == None:
					hexapodObj = Hexalign(hexopod_id=self.textCtrlHexapodID.GetValue())
					self.getTopLevelWindow.hexapodObj = hexapodObj
				cap_readings = actuator.getPositions()
				hexapodObj.save_capGauge_readings(cap_readings, mode='new')
			except Exception, e:
				self.popErrorBox('ERROR in Resetting hexapod starting position',
					"ERROR: FAIL to reset hexapod starting position. \n\n"+traceback.format_exc())
				traceback.print_exc()

	def onGoHexpaodStartPosition(self, event):
		"""
		@Purpose:
			DEPRECATED.
		"""
		try:
			actuator = self.getTopLevelWindow().actuator
			hexapodObj = self.getTopLevelWindow().hexapodObj
			if hexapodObj == None:
				hexapodObj = Hexalign(hexopod_id=self.textCtrlHexapodID.GetValue())
				self.getTopLevelWindow.hexapodObj = hexapodObj
			(dateObj, starting_pos, commentsStr) = hexapodObj.read_capGauge_file()
			starting_pos = numpy.array(starting_pos)
			# REMEMBER to NOT update the plots...
			actuator.setMoveWidget(None)
			self.buttonGoHome.Enable(False)
			self.getTopLevelWindow().statusBarMain.PulseStart()
			threadID = self.__startThread__(actuator.capgaugeChange, starting_pos)
			threadMap = self.__getThreadMap__()

			# start the progress (pulse) dialog
			pulseDialog = wx.ProgressDialog("Loading...", 
											"Moving Motors, Please Wait...",
											maximum=100,
											parent=self,
											style=wx.PD_CAN_ABORT | wx.PD_APP_MODAL)
			keepgoing = True
			while keepgoing and threadMap[threadID].isAlive():
				(keepgoing, skip) = pulseDialog.Pulse()
				time.sleep(0.01)
			if not keepgoing:		# we ABORTED:
				actuator.stop()
				self.getTopLevelWindow().statusBarMain.SetStatus("ABORTED", stopPulse=True)
			else:
				self.getTopLevelWindow().statusBarMain.PulseStop()
			pulseDialog.Destroy()
			self.buttonGoHome.Enable(True)
		except Exception, e:
			self.popErrorBox('ERROR in Going hexapod\'s starting position',
					"ERROR: FAIL to go to hexapod starting position. \n\n"+traceback.format_exc())
			traceback.print_exc()


