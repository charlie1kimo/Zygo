"""
pob_measure_gui.py
	This is the GUI module for the pob measurement automation
"""

from datetime import datetime
import logging
import os
import sys
import wx
import traceback
from align_py import pob_measure_gui
from align_py.pob_measure_gui.pob_measure.pob_measure import PobMeasure
from align_py.pob_measure_gui.pob_measure.pob_measure import PobMeasureException
from align_py.pob_measure_gui.pob_measure import pob_measure_wx_event
from wx_extensions.windows import FrameBase
from wx_extensions.windows import ScrolledPanelBase

###########################################################################
## Class FrameMain
###########################################################################

class FrameMain ( FrameBase ):
	
	def __init__( self, parent, metroProIP ):
		self.__isLoggingToFile__ = False
		self.timeStrFormat = "%Y-%m-%d %H:%M:%S"
		self.pobMeasureObj = PobMeasure(metroProIP, wxWidget=self)

		FrameBase.__init__ ( self, parent, id = wx.ID_ANY, title = "POB Measurement Automation", pos = wx.DefaultPosition, size = wx.Size( 1024,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizerFrameMain = wx.BoxSizer( wx.VERTICAL )
		
		self.panelMain = ScrolledPanelBase( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextDisplayTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"POB Measurement Automation", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayTitle.Wrap( -1 )
		self.staticTextDisplayTitle.SetFont( wx.Font( 20, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerMain.Add( self.staticTextDisplayTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		sbSizerDisplay = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"Progress:" ), wx.VERTICAL )
		
		self.textCtrlDisplayProgress = wx.TextCtrl( self.panelMain, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		self.textCtrlDisplayProgress.SetFont( wx.Font( 16, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlDisplayProgress.SetMaxLength( 0 ) 
		self.textCtrlDisplayProgress.SetForegroundColour( "WHITE" )
		self.textCtrlDisplayProgress.SetBackgroundColour( "BLACK" )
		
		sbSizerDisplay.Add( self.textCtrlDisplayProgress, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerMain.Add( sbSizerDisplay, 1, wx.EXPAND, 5 )
		
		sbSizerParameters = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"Parameters" ), wx.VERTICAL )
		
		fgSizerParameters = wx.FlexGridSizer( 4, 6, 0, 0 )
		fgSizerParameters.SetFlexibleDirection( wx.BOTH )
		fgSizerParameters.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextParameterPobId = wx.StaticText( self.panelMain, wx.ID_ANY, u"POB ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterPobId.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterPobId, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterPobId = wx.TextCtrl( self.panelMain, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterPobId.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterPobId, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterFieldCoords = wx.StaticText( self.panelMain, wx.ID_ANY, u"Field Coords:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterFieldCoords.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterFieldCoords, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterFieldCoords = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterFieldCoords.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterFieldCoords, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterTsCenterFieldCoords = wx.StaticText( self.panelMain, wx.ID_ANY, u"TS Center Field Coords:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterTsCenterFieldCoords.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterTsCenterFieldCoords, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterTsCenterFieldCoords = wx.TextCtrl( self.panelMain, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterTsCenterFieldCoords.SetMaxLength( 0 )
		self.textCtrlParameterTsCenterFieldCoords.SetToolTipString( u"enter 3 floats separated by commas" ) 
		fgSizerParameters.Add( self.textCtrlParameterTsCenterFieldCoords, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterPobRotation = wx.StaticText( self.panelMain, wx.ID_ANY, u"POB Rotation:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterPobRotation.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterPobRotation, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterPobRotation = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterPobRotation.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterPobRotation, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterNumAvgMapPerField = wx.StaticText( self.panelMain, wx.ID_ANY, u"# Avg Maps Per Field:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterNumAvgMapPerField.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterNumAvgMapPerField, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterNumAvgMapPerField = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"128", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterNumAvgMapPerField.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterNumAvgMapPerField, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterNumFieldRepeats = wx.StaticText( self.panelMain, wx.ID_ANY, u"# of Field Repeats:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterNumFieldRepeats.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterNumFieldRepeats, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterNumFieldRepeats = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"4", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterNumFieldRepeats.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterNumFieldRepeats, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterNumFullMeasRepeats = wx.StaticText( self.panelMain, wx.ID_ANY, u"# of Full Measurement Repeats:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterNumFullMeasRepeats.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterNumFullMeasRepeats, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterNumFullMeasRepeats = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterNumFullMeasRepeats.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterNumFullMeasRepeats, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterRetroRotation = wx.StaticText( self.panelMain, wx.ID_ANY, u"Retro Rotation:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterRetroRotation.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterRetroRotation, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterRetroRotation = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterRetroRotation.SetMaxLength( 0 )
		fgSizerParameters.Add( self.textCtrlParameterRetroRotation, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextParameterTestLetter = wx.StaticText( self.panelMain, wx.ID_ANY, u"Test Letter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterTestLetter.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterTestLetter, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterTestLetter = wx.TextCtrl( self.panelMain, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlParameterTestLetter.SetMaxLength( 0 ) 
		fgSizerParameters.Add( self.textCtrlParameterTestLetter, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.staticTextParameterMeasurementStartDelay = wx.StaticText( self.panelMain, wx.ID_ANY, u"Measurement Start Delay (min):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextParameterMeasurementStartDelay.Wrap( -1 )
		fgSizerParameters.Add( self.staticTextParameterMeasurementStartDelay, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlParameterMeasurementStartDelay = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerParameters.Add( self.textCtrlParameterMeasurementStartDelay, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		sbSizerParameters.Add( fgSizerParameters, 1, wx.EXPAND, 5 )
		
		bSizerMain.Add( sbSizerParameters, 0, wx.EXPAND, 5 )


		sbSizerAutoNull = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"AutoNull" ), wx.HORIZONTAL )
		
		radioBoxAutoNullRSOptionsChoices = [ u"Tilt Only", u"Tilt + Power" ]
		self.radioBoxAutoNullRSOptions = wx.RadioBox( self.panelMain, wx.ID_ANY, u"RS Options:", wx.DefaultPosition, wx.DefaultSize, radioBoxAutoNullRSOptionsChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxAutoNullRSOptions.SetSelection( 0 )
		sbSizerAutoNull.Add( self.radioBoxAutoNullRSOptions, 0, wx.ALL, 5 )
		
		self.staticTextAutoNullRSIterTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"RS Iter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextAutoNullRSIterTitle.Wrap( -1 )
		sbSizerAutoNull.Add( self.staticTextAutoNullRSIterTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlAutoNullRSIter = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizerAutoNull.Add( self.textCtrlAutoNullRSIter, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		radioBoxAutoNullTSOptionsChoices = [ u"Tilt Only", u"Tilt + Power" ]
		self.radioBoxAutoNullTSOptions = wx.RadioBox( self.panelMain, wx.ID_ANY, u"TS Options", wx.DefaultPosition, wx.DefaultSize, radioBoxAutoNullTSOptionsChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxAutoNullTSOptions.SetSelection( 0 )
		sbSizerAutoNull.Add( self.radioBoxAutoNullTSOptions, 0, wx.ALL, 5 )
		
		self.staticTextAutoNullTSIterTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"TS Iter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextAutoNullTSIterTitle.Wrap( -1 )
		sbSizerAutoNull.Add( self.staticTextAutoNullTSIterTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlAutoNullTSIter = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizerAutoNull.Add( self.textCtrlAutoNullTSIter, 0, wx.ALIGN_CENTER|wx.ALL, 5 )	
		
		bSizerMain.Add( sbSizerAutoNull, 0, wx.EXPAND, 5 )

		
		sbSizerControls = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"Controls" ), wx.HORIZONTAL )
		
		self.buttonControlMeasure = wx.Button( self.panelMain, wx.ID_ANY, u"MEASURE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonControlMeasure.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		sbSizerControls.Add( self.buttonControlMeasure, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonControlStop = wx.Button( self.panelMain, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonControlStop.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		sbSizerControls.Add( self.buttonControlStop, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerMain.Add( sbSizerControls, 0, wx.EXPAND, 5 )
		
		
		self.panelMain.SetSizer( bSizerMain )
		self.panelMain.Layout()
		self.panelMain.SetupScrolling()
		bSizerMain.Fit( self.panelMain )
		bSizerFrameMain.Add( self.panelMain, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizerFrameMain )
		self.Layout()

		# MenuBar, Menu, and MenuItems
		self.menubarMain = wx.MenuBar( 0 )
		self.menuLog = wx.Menu()
		self.menuItemLogToFile = wx.MenuItem( self.menuLog, wx.ID_ANY, u"Log To File", wx.EmptyString, wx.ITEM_CHECK )
		self.menuLog.AppendItem( self.menuItemLogToFile )
		self.menuItemClearConsoleLog = wx.MenuItem( self.menuLog, wx.ID_ANY, u"Clear Console Log", wx.EmptyString, wx.ITEM_CHECK )
		self.menuLog.AppendItem( self.menuItemClearConsoleLog )
		
		self.menubarMain.Append( self.menuLog, u"Log" ) 
		
		self.menuAbout = wx.Menu()
		self.menuItemAbout = wx.MenuItem( self.menuAbout, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuAbout.AppendItem( self.menuItemAbout )
		
		self.menubarMain.Append( self.menuAbout, u"About" ) 
		
		self.SetMenuBar( self.menubarMain )

		# Icon
		self.baseDir = os.path.dirname(os.path.abspath(__file__)) + "/"
		self.SetIcon(wx.Icon(self.baseDir+"icons/icon.ico", wx.BITMAP_TYPE_ICO))
		
		# Connect Events
		self.buttonControlMeasure.Bind( wx.EVT_BUTTON, self.onControlMeasure )
		self.buttonControlStop.Bind( wx.EVT_BUTTON, self.onControlStop )
		self.Bind( wx.EVT_MENU, self.onMenuLogToFile, id = self.menuItemLogToFile.GetId() )
		self.Bind( wx.EVT_MENU, self.onMenuClearConsoleLog, id = self.menuItemClearConsoleLog.GetId() )
		self.Bind( wx.EVT_MENU, self.onMenuAbout, id = self.menuItemAbout.GetId() )
		self.Bind(pob_measure_wx_event.EVT_POB_MEAS_PROG, self.onPobMeasureProgressEvent)
		self.Bind(pob_measure_wx_event.EVT_POB_MEAS_ERROR, self.onPobMeasureErrorEvent)
		self.Bind(pob_measure_wx_event.EVT_POB_UPDATE_TEST_LETTER, self.onPobUpdateTestLetterEvent)
	
	def __del__( self ):
		pass

	def __startLogToFile__(self):
		"""
		@Puprose:
			private function to start logging to file.
		"""
		self.logFileName = "%spob_measure_%s.log" % \
		(os.path.dirname(os.path.abspath(__file__))+"/logs/", datetime.now().strftime("%Y%m%d%H%M%S"))
		logging.basicConfig(filename=self.logFileName, format="[%(asctime)s] %(levelname)s: %(message)s")
	
	def logEvents(self, level, message):
		"""
		@Purpose:
			logging any events happens during the measurement automation. It writes the log to GUI console and a log file.
		@Inputs:
			(str) level = 'info', 'warning', 'error', 'critical', 'exception'
			(str) message = logging message
		"""
		timeNowStr = datetime.now().strftime(self.timeStrFormat)
		self.textCtrlDisplayProgress.AppendText("[%s] %s: %s\n" % (timeNowStr, level.upper(), message))
		eval("logging.%s(\"%s\")" % (level, message))

	def setupAutoNullParameters(self):
		RSParams = {}
		if self.radioBoxAutoNullRSOptions.GetStringSelection() == "Tilt Only":
			RSParams['type'] = "RetroSph Trans"
		else:
			RSParams['type'] = "RetroSph Trans w Power"
		TSParams = {}
		if self.radioBoxAutoNullTSOptions.GetStringSelection() == "Tilt Only":
			TSParams['type'] = "TransSph Trans"
		else:
			TSParams['type'] = "TransSph Trans w Power"
		try:
			RSParams['iter'] = int(self.textCtrlAutoNullRSIter.GetValue())
			TSParams['iter'] = int(self.textCtrlAutoNullTSIter.GetValue())
			self.pobMeasureObj.setAutoNullParameter(RSParams, TSParams)
		except ValueError, exception:
			errMsg = "ERROR: Invalid Values for 'RS Iteration' or 'TS Iteration'."
			self.logEvents("error", errMsg)
			self.popErrorBox("ERROR: setAutoNullParameters", errMsg)
			print errMsg
			raise exception

	def setupParameters(self):
		"""
		@Purpose:
			setup the parameters between the GUI and low level measurement object.
		"""
		self.pobMeasureObj.setPobID(self.textCtrlParameterPobId.GetValue())
		tempStr = self.textCtrlParameterFieldCoords.GetValue()
		try:
			self.pobMeasureObj.setFieldCoordinates(eval(tempStr))
		except PobMeasureException, exception:
			self.logEvents("error", "ERROR: setFieldCorrdinates"+exception.__str__())
			self.popErrorBox("ERROR: setFieldCorrdinates", exception.__str__())
			traceback.print_exc()
			raise exception
		tempStr = self.textCtrlParameterTsCenterFieldCoords.GetValue()
		if len(tempStr) > 0:
			try:
				self.pobMeasureObj.setTSCenterFieldCoordinates(map(float, tempStr.split(",")))
			except ValueError, exception:
				errMsg = "ERROR: Invalid Value or Format in TS Center Field Coordinates Inputs."
				self.logEvents("error", errMsg)
				self.popErrorBox("ERROR: setTSCenterFieldCoordinates", errMsg)
				print errMsg
				raise exception
		else:
			self.pobMeasureObj.setTSCenterFieldCoordinates(None)
		try:
			self.pobMeasureObj.setPobRotation(int(self.textCtrlParameterPobRotation.GetValue()))
			self.pobMeasureObj.setNumAvgMapPerField(int(self.textCtrlParameterNumAvgMapPerField.GetValue()))
			self.pobMeasureObj.setNumFieldRepeats(int(self.textCtrlParameterNumFieldRepeats.GetValue()))
			self.pobMeasureObj.setNumFullMeasurementRepeats(int(self.textCtrlParameterNumFullMeasRepeats.GetValue()))
			self.pobMeasureObj.setRetroRotation(int(self.textCtrlParameterRetroRotation.GetValue()))
			self.pobMeasureObj.setTestLetter(self.textCtrlParameterTestLetter.GetValue())
			self.pobMeasureObj.setMeasurementStartDelay(float(self.textCtrlParameterMeasurementStartDelay.GetValue()))
		except ValueError, exception:
			errMsg = "ERROR: Invalid Value in Parameters"
			self.logEvents("error", errMsg)
			self.popErrorBox("ERROR: Parameter setting error", errMsg)
			print errMsg
			raise exception

	# Virtual event handlers, overide them in your derived class
	def onControlMeasure( self, event ):
		self.setupParameters()
		self.setupAutoNullParameters()
		self.__startThread__(self.pobMeasureObj.measure)
		self.buttonControlMeasure.Enable(False)
	
	def onControlStop( self, event ):
		self.pobMeasureObj.stop()
		self.logEvents("warning", "STOP REQUESTED by users!")
		self.buttonControlMeasure.Enable(True)

	def onMenuLogToFile( self, event ):
		if self.menuItemLogToFile.IsChecked():
			self.__isLoggingToFile__ = True
			self.__startLogToFile__()
		else:
			self.__isLoggingToFile__ = False
			logging.shutdown()

	def onMenuClearConsoleLog( self, event ):
		self.textCtrlDisplayProgress.SetValue("")

	def onMenuAbout( self, event ):
		descriptions = \
"""
This POB Measure Automation program provides the user interface to perform batch / group automation optics data collection.
"""
		license = \
"""
(C) 2014 Zygo Corporation, all right reserved
"""
		info = wx.AboutDialogInfo()
		info.SetIcon(wx.Icon(self.baseDir+"icons/icon.ico", wx.BITMAP_TYPE_ICO))
		info.SetName("POB Measurement Automation")
		info.SetDescription(descriptions)
		info.SetLicense(license)
		info.SetVersion(pob_measure_gui.__version__)
		info.SetCopyright(" (C) 2014 Zygo Corporation")
		info.SetWebSite("http://www.zygo.com")
		info.AddDeveloper("Charlie Chen <cchen@zygo.com>")
		info.AddDocWriter("Charlie Chen <cchen@zygo.com>")
		wx.AboutBox(info)

	def onPobMeasureProgressEvent( self, event ):
		self.logEvents("info", event.message)
		if event.message == "Measurements are ALL DONE.":
			self.buttonControlMeasure.Enable(True)

	def onPobMeasureErrorEvent( self, event ):
		self.popErrorBox("ERROR: Error in performing measure in PobMeasure", event.message)
		self.logEvents("error", event.message)
		self.buttonControlMeasure.Enable(True)

	def onPobUpdateTestLetterEvent( self, event ):
		self.textCtrlParameterTestLetter.SetValue(event.testLetter)
	

########################## MAIN #############################
if __name__ == "__main__":
	##### Make log dir #####
	thisPath = os.path.dirname(os.path.abspath(__file__))
	try:
		os.mkdir(thisPath+"/logs")
	except Exception, e:
		pass
	########################
	if len(sys.argv) < 2:
		# default POB metroPro computer IP
		ip = "172.18.106.130"
	else:
		ip = sys.argv[1]
	app = wx.PySimpleApp()
	frame = FrameMain(None, ip)
	frame.Show(True)
	app.MainLoop()
#############################################################
