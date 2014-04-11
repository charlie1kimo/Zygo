# -*- coding: utf-8 -*- 

import numpy
import os
import traceback
import wx
from wx_extensions.windows import FrameBase
from wx_extensions.windows import ScrolledPanelBase
from cap_gauge.capgauge import CompositeCapgauge
from cap_gauge.capgauge import CapgaugeException

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( FrameBase ):
	
	def __init__( self, parent ):
		"""
		Constructor
		"""
		########### class instance variables ###########
		### constants ###
		self.X_LEG_ANGLE = 55				# X LEG ANGLE in degrees
		#################
		self.defaultCfgDir = os.getcwd()
		self.capgauge = None
		self.gapX0 = 0.0
		self.y0 = 0.0
		self.z0 = 0.0
		self.displayMode = "Gap"
		self.lastGapX = 0.0
		self.lastGapY = 0.0
		self.lastGapZ = 0.0
		self.lastSetGapZeroFile = 'C:/temp/lastGapZero_for_cap_coords_display.txt'
		self.threadID = 999
		################################################

		FrameBase.__init__ ( self, parent, id = wx.ID_ANY, title = u"Capgauge Monitoring Tool", pos = wx.DefaultPosition, size = wx.Size( 1200,700 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizerMainFrame = wx.BoxSizer( wx.VERTICAL )
		
		self.panelMain = ScrolledPanelBase( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPanel = wx.BoxSizer( wx.VERTICAL )
		
		bSizerDisplayAndOptions = wx.BoxSizer( wx.HORIZONTAL )
		
		fgSizerDisplay = wx.FlexGridSizer( 3, 3, 0, 0 )
		fgSizerDisplay.SetFlexibleDirection( wx.BOTH )
		fgSizerDisplay.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextXTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextXTitle.Wrap( -1 )
		self.staticTextXTitle.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextXTitle, 1, wx.ALL, 5 )
		
		self.staticTextXValues = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextXValues.Wrap( -1 )
		self.staticTextXValues.SetFont( wx.Font( 80, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextXValues, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextXUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"um", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextXUnits.Wrap( -1 )
		self.staticTextXUnits.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextXUnits, 0, wx.ALL, 5 )
		
		self.staticTextYTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextYTitle.Wrap( -1 )
		self.staticTextYTitle.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextYTitle, 0, wx.ALL, 5 )
		
		self.staticTextYValues = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextYValues.Wrap( -1 )
		self.staticTextYValues.SetFont( wx.Font( 80, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextYValues, 0, wx.ALL, 5 )
		
		self.staticTextYUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"um", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextYUnits.Wrap( -1 )
		self.staticTextYUnits.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextYUnits, 0, wx.ALL, 5 )
		
		self.staticTextZTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Z:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextZTitle.Wrap( -1 )
		self.staticTextZTitle.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextZTitle, 0, wx.ALL, 5 )
		
		self.staticTextZValues = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextZValues.Wrap( -1 )
		self.staticTextZValues.SetFont( wx.Font( 80, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextZValues, 0, wx.ALL, 5 )
		
		self.staticTextZUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"um", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextZUnits.Wrap( -1 )
		self.staticTextZUnits.SetFont( wx.Font( 50, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplay.Add( self.staticTextZUnits, 0, wx.ALL, 5 )
		
		
		bSizerDisplayAndOptions.Add( fgSizerDisplay, 1, wx.EXPAND, 5 )
		
		self.staticlineDisplayAndOptions = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizerDisplayAndOptions.Add( self.staticlineDisplayAndOptions, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerOptions = wx.BoxSizer( wx.VERTICAL )
		
		radioBoxTestModesChoices = [ u"M1", u"M2" ]
		self.radioBoxTestModes = wx.RadioBox( self.panelMain, wx.ID_ANY, u"Test Modes:", wx.DefaultPosition, wx.DefaultSize, radioBoxTestModesChoices, 2, wx.RA_SPECIFY_ROWS )
		self.radioBoxTestModes.SetSelection( 0 )
		bSizerOptions.Add( self.radioBoxTestModes, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		radioBoxDisplayValuesChoices = [ u"Gap", u"Cartesian Values" ]
		self.radioBoxDisplayValues = wx.RadioBox( self.panelMain, wx.ID_ANY, u"Display Values In:", wx.DefaultPosition, wx.DefaultSize, radioBoxDisplayValuesChoices, 2, wx.RA_SPECIFY_ROWS )
		self.radioBoxDisplayValues.SetSelection( 0 )
		bSizerOptions.Add( self.radioBoxDisplayValues, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextUpdateIntervalTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Update Intervals (secs):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextUpdateIntervalTitle.Wrap( -1 )
		bSizerOptions.Add( self.staticTextUpdateIntervalTitle, 0, wx.ALL, 5 )
		
		self.textCtrlUpdateIntervalValues = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerOptions.Add( self.textCtrlUpdateIntervalValues, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonReset = wx.Button( self.panelMain, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonReset.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerOptions.Add( self.buttonReset, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerDisplayAndOptions.Add( bSizerOptions, 0, wx.EXPAND, 5 )
		
		
		bSizerPanel.Add( bSizerDisplayAndOptions, 0, wx.EXPAND, 5 )
		
		self.staticlineDisplayAndControls = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPanel.Add( self.staticlineDisplayAndControls, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerControls = wx.BoxSizer( wx.VERTICAL )
		
		bSizerTitleControls = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextTitleControl = wx.StaticText( self.panelMain, wx.ID_ANY, u"Capgauges Config:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTitleControl.Wrap( -1 )
		self.staticTextTitleControl.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerTitleControls.Add( self.staticTextTitleControl, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		config_path = "N:/Shared/Users/cchen/cap_gauge_coordinate_display/cap_gauge/NI_composite_capgauge.config"
		self.textCtrlCapConfigControls = wx.TextCtrl( self.panelMain, wx.ID_ANY, config_path, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerTitleControls.Add( self.textCtrlCapConfigControls, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.buttonBrowseControls = wx.Button( self.panelMain, wx.ID_ANY, u"Browse...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerTitleControls.Add( self.buttonBrowseControls, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		bSizerControls.Add( bSizerTitleControls, 0, wx.EXPAND, 5 )
		
		bSizerXYZChannels = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextXChannelTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"X Channel:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextXChannelTitle.Wrap( -1 )
		bSizerXYZChannels.Add( self.staticTextXChannelTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlXChannel = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerXYZChannels.Add( self.textCtrlXChannel, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextYChannelTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Y Channel:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextYChannelTitle.Wrap( -1 )
		bSizerXYZChannels.Add( self.staticTextYChannelTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlYChannel = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerXYZChannels.Add( self.textCtrlYChannel, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextZChannelTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Z Channel:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextZChannelTitle.Wrap( -1 )
		bSizerXYZChannels.Add( self.staticTextZChannelTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlZChannel = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerXYZChannels.Add( self.textCtrlZChannel, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		bSizerControls.Add( bSizerXYZChannels, 0, wx.EXPAND, 5 )
		
		self.buttonTitleControlSet = wx.Button( self.panelMain, wx.ID_ANY, u"Set Capgauges", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonTitleControlSet.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerControls.Add( self.buttonTitleControlSet, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerPanel.Add( bSizerControls, 0, wx.EXPAND, 5 )		
		
		self.panelMain.SetSizer( bSizerPanel )
		self.panelMain.Layout()
		self.panelMain.SetupScrolling()
		bSizerPanel.Fit( self.panelMain )
		bSizerMainFrame.Add( self.panelMain, 1, wx.EXPAND |wx.ALL, 0 )
		
		
		self.SetSizer( bSizerMainFrame )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.radioBoxTestModes.Bind( wx.EVT_RADIOBOX, self.onChangeTestModes )
		self.radioBoxDisplayValues.Bind( wx.EVT_RADIOBOX, self.onChangeDisplayValues )
		self.textCtrlUpdateIntervalValues.Bind( wx.EVT_TEXT, self.onChangeUpdateIntervals )
		self.buttonReset.Bind( wx.EVT_BUTTON, self.onReset )
		self.buttonBrowseControls.Bind( wx.EVT_BUTTON, self.onCapgaugeConfigBrowse )
		self.buttonTitleControlSet.Bind( wx.EVT_BUTTON, self.onSetCapgauges )

		########### timer ###########
		self.timerUpdates = wx.Timer(self, wx.NewId())
		#############################

		# Timer Events
		self.Bind(wx.EVT_TIMER, self.onUpdateTimer, self.timerUpdates)
	
	def __del__( self ):
		FrameBase.__del__(self)
	
	def loadLastGapZero(self):
		if os.path.isfile(self.lastSetGapZeroFile):
			f = open(self.lastSetGapZeroFile, 'r')
			gapZeros = f.readline().split(',')
			(self.gapX0, self.y0, self.z0) = (float(gapZeros[0]), float(gapZeros[1]), float(gapZeros[2]))
			f.close()

	# Virtual event handlers, overide them in your derived class
	def onChangeTestModes( self, event ):
		event.Skip()
	
	def onChangeDisplayValues( self, event ):
		self.displayMode = self.radioBoxDisplayValues.GetStringSelection()
	
	def onChangeUpdateIntervals( self, event ):
		if self.timerUpdates.IsRunning():
			self.timerUpdates.Stop()
		if self.capgauge:
			try:
				updateInterval = float(self.textCtrlUpdateIntervalValues.GetValue())
				if updateInterval == 0:
					return
				self.timerUpdates.Start(updateInterval*1000)
			except ValueError, e:
				self.popErrorBox('Please enter a valid update intervals', 'ERROR: please enter a valid update intervals.')
	
	def onReset( self, event ):
		(self.gapX0, self.y0, self.z0) = (self.lastGapX, self.lastGapY, self.lastGapZ)
		# save the gapZeroFile:
		f = open(self.lastSetGapZeroFile, 'w')
		f.write(str(self.gapX0)+','+str(self.y0)+','+str(self.z0)+'\n')
		f.close()
		if self.displayMode != "Gap":
			self.staticTextXValues.SetLabel('0.00000')
			self.staticTextYValues.SetLabel('0.00000')
			self.staticTextZValues.SetLabel('0.00000')
	
	def onSetCapgauges( self, event ):
		config = self.textCtrlCapConfigControls.GetValue()
		xChan = self.textCtrlXChannel.GetValue()
		yChan = self.textCtrlYChannel.GetValue()
		zChan = self.textCtrlZChannel.GetValue()
		if not bool(config):
			self.popErrorBox('Please enter capgauge config path', 'ERROR: Please enter capgauge config path.')
			return
		elif not bool(xChan):
			self.popErrorBox('Please enter X channel', 'ERROR: please enter X channel')
			return
		elif not bool(yChan):
			self.popErrorBox('Please enter Y channel', 'ERROR: please enter Y channel')
			return
		elif not bool(zChan):
			self.popErrorBox('Please enter Z channel', 'ERROR: please enter Z channel')
			return

		try:
			self.capgauge = CompositeCapgauge([int(xChan), int(yChan), int(zChan)], config)
		except Exception, e:
			self.popErrorBox('ERROR: FAIL to initialize capgauge object', traceback.format_exc())
			traceback.print_exc()
			raise e

		if os.path.isfile(self.lastSetGapZeroFile):
			self.loadLastGapZero()
		else:
			try:
				(self.gapX0, self.y0, self.z0) = self.capgauge.readPositions(100, 0)
			except CapgaugeException, e:
				title = 'ERROR: FAIL to communicate to the capgauge controller.'
				message = \
"""
ERROR: FAIL to communicate to the capgauge controller; make sure the controller chassis is reserved by following steps:

1. Open "Measurement & Automation Explorer" program from Desktop
2. From the left pannel, navigate through "My System" -> "Devices and Interfaces" -> "Network Devices"
3. Under "Network Devices", find the controller named "cDAQ9181-17F25A2"
4. Left click on "cDAQ9181-17F25A2"
5. Left click on "Reserve Chassis" on the right panel, if prompt asking if override, click yes.
6. Restart the program and see if this solves the problem.

If it still doesn't solve the problem. Contact me (Charlie Chen) @ <cchen@zygo.com>
"""
			self.popErrorBox(title, message)
			traceback.print_exc()
		updateInterval = float(self.textCtrlUpdateIntervalValues.GetValue())
		self.timerUpdates.Start(updateInterval*1000)
	
	def onCapgaugeConfigBrowse( self, event ):
		wildcard = "Config File (*.config)|*.config|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", self.defaultCfgDir, "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetPath()
			self.textCtrlCapConfigControls.SetValue(file)
			self.defaultCfgDir =  dialog.GetDirectory()
		dialog.Destroy()

	def onUpdateTimer( self, event ):
		#self.__startThreadWithID__(self.threadID, self.updateValues)
		self.updateValues()

	def updateValues(self):
		(self.lastGapX, self.lastGapY, self.lastGapZ) = self.capgauge.readPositions(100, 0)
		try:
			if self.displayMode == "Cartesian Values":			# cartesian values display mode
				"""
				##########EQUATIONS ###########
				dx = [(gap_x - gap_x0) - dz * sin(55 deg)] / cos(55 deg)
				dy = gap_y - y0
				dz = gap_z - z0
				###############################
				"""
				dz = self.lastGapZ - self.z0
				dy = self.lastGapY - self.y0
				dx = ((self.lastGapX - self.gapX0) - dz * numpy.sin(numpy.pi/180.*self.X_LEG_ANGLE)) / numpy.cos(numpy.pi/180.*self.X_LEG_ANGLE)
				self.staticTextXValues.SetLabel('%0.2f' % dx)
				self.refreshWidget(self.staticTextXValues)
				self.staticTextYValues.SetLabel('%0.2f' % dy)
				self.refreshWidget(self.staticTextYValues)
				self.staticTextZValues.SetLabel('%0.2f' % dz)
				self.refreshWidget(self.staticTextZValues)
			else:												# gap display mode
				self.staticTextXValues.SetLabel('%0.2f' % self.lastGapX)
				self.refreshWidget(self.staticTextXValues)
				self.staticTextYValues.SetLabel('%0.2f' % self.lastGapY)
				self.refreshWidget(self.staticTextYValues)
				self.staticTextZValues.SetLabel('%0.2f' % self.lastGapZ)
				self.refreshWidget(self.staticTextZValues)
		except wx.PyDeadObjectError, e:	# fix thread hasn't finished but window is closed problem
			pass


################ MAIN #################
if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = MainFrame(None)
	frame.Show()
	app.MainLoop()
#######################################