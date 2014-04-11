"""
radiusGUI.py
	This file includes the MAIN GUI class for the radius
	measurment programs.
Author: Charlie Chen
"""
from finddir import finddir

import datetime
import os
import numpy
import re
import subprocess
import time
import traceback
import wx
import wx.grid as gridlib
from wx.lib.scrolledpanel import ScrolledPanel
import win32api
import win32print

from wx_extensions.grid import CustomDataGrid
from wx_extensions.statusbar import StatusBarGauge
import radius3.psprint
from radius3.dmi import DMIPollingException
from radius3.weather_station import WeatherProbingException
from radius3.gui.gui_components import *
from radius3.utilities import OutputBuffer
import radius3.utilities as utilities

###########################################################################
## Decorators (for fun!!!)
###########################################################################
# handleErrorsInMainGUI
# @Purpose:
#	decorator function for handling all the errors in gui
def handleErrorsInMainGUI(funct, *args):
	def wrapper(self, *args):
		isTimer = re.search('Timer', funct.__name__)
		isToggle = re.search('Toggle', funct.__name__)
		isDMI = re.search('DMI', funct.__name__)
		try:
			if not isTimer and not isToggle:
				self.statusBarMain.PulseStart()
			funct(self, *args)
			if not isTimer and not isToggle:
				self.statusBarMain.PulseStop()
				if isDMI:
					self.setDMIStatus('A-OK')
			# refresh the GUI
			self.bSizerPositionContents.Layout()
			self.fgSizerConstants.Layout()
			self.panelScrolled.Refresh()
			self.panelScrolled.Layout()
			self.statusBarMain.SetStatus("Ready", True)
		except DMIPollingException, e:
			self.statusBarMain.SetStatus("WARNING", True)
			self.setDMIStatus('WARNING')
			self.printBuffer.writePrintOutFlush("WARNING: DMI polling error.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popAlertBox("WARNING", "WARNING: DMI polling error. Tried to poll DMI too fast?")
		except AttributeError, e:
			if funct.__name__ == 'onRemoveMeasurements':
				self.statusBarMain.PulseStop()
		except ValueError, e:							# for handling float(wrong string) in setting up Custom part temperature
			self.statusBarMain.SetStatus("ERROR", True)
			self.printBuffer.writePrintOutFlush("ERROR: please enter valid part temperature value!")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: please enter valid part temperature value!")
		except Exception, e:
			self.statusBarMain.SetStatus("ERROR", True)
			if isDMI:
				self.setDMIStatus('ERROR')
			
			if isinstance(e, WeatherProbingException):
				if re.match('^db.getLatestValue', e.expr):
					msg = "ERROR: cannot find input part temperature probe name: %s; Is the probe name correct?" % \
							self.comboBoxPartTemperatureProbeName.GetValue()
					# rollback the part temperature probe name to air temperature probe name
					self.weatherStation.setPartTemperatureStation(self.weatherStation.temperatureStation)
					self.comboBoxPartTemperatureProbeName.SetValue(self.weatherStation.partTemperatureStation)
				else:
					msg = "ERROR: cannot update weather in weather station. Check internet connection or database? Using default environment values."
					self.setWeatherStationStatus()

			elif isDMI:
				msg = "ERROR: cannot sample DMI. check DMI connection?"
			else:
				msg = "ERROR: Exception thrown in %s()." % funct.__name__
			self.popErrorBox("ERROR", msg)
			self.printBuffer.writePrintOutFlush("ERROR: Exception thrown in %s()." % funct.__name__)
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			
	return wrapper


###########################################################################
## Class FrameMain
###########################################################################
class FrameMain ( FrameOutputBuffered ):
	
	# __init__
	# @Purpose:
	#	Constructor
	def __init__( self, parent, cmdParams, dmi, ws, ps, printBuffer=OutputBuffer(), debug=False ):
		self.baseDir = os.path.dirname(radius3.__file__)+"/"
		self.cmdParams = cmdParams
		self.dmi = dmi
		self.weatherStation = ws
		self.phaseStation = ps
		self.phaseStation.mainFrame = self			# setup phase station's main frame GUI
		self.printBuffer = printBuffer
		self.printBuffer.setFrame(self)
		self.debug = debug
		########## measurement variables ##########
		self.fcCalibrated = False					# if it's focus correct calibrated already
		self.meas_num = 0							# measurement # starts from 0
		self.max_meas = 10							# maximum measurements allowed for one part.
		self.isNewMeasurement = True				# flag for continuous measurement; True if it's new one; False if it's continuing
		self.GapMeas = False						# flag for gap (no cat eye) measurement
		self.sTS_Offset = 0.0						# no cat eye transmission sphere offset
		self.sGap_Offset = 0.0						# no cat eye gap offset
		self.gDMI_Wave = 0.0						# for focus calibration
		self.gDMI_rd = [None for i in range(2*self.max_meas)]		# 20 entries place holder
		self.gFocus_Zrn = [None for i in range(2*self.max_meas)]	# 20 entries place holder
		self.gFC_Rad = [None for i in range(self.max_meas)]			# 10 entries place holder
		self.gFC_CCDMI = [None for i in range(self.max_meas)]		# 10 entries place holder
		self.gFC_CEDMI = [None for i in range(self.max_meas)]		# 10 entries place holder
		self.gCC_Foc = [None for i in range(self.max_meas)]			# 10 entries place holder
		self.gCE_Foc = [None for i in range(self.max_meas)]			# 10 entries place holder
		self.sCTE_Cmp_Rad = 0.0										# CTE radius calculation
		self.outputfile = "Radius3_Measured_Data.txt"					# default output file name
		self.version = radius3.__version__
	
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Unified Radius Measurement Program", pos = wx.DefaultPosition, size = wx.Size( 1000,700 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		##### Timers #####
		self.key_polling_timer = wx.Timer(self, wx.NewId())
		self.time_timer = wx.Timer(self, wx.NewId())
		self.ws_timer = wx.Timer(self, wx.NewId())
		self.dmi_read_timer = wx.Timer(self, wx.NewId())
		##################
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.splitterMain = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SUNKEN_BORDER )
		self.splitterMain.SetMinimumPaneSize( 70 )
		
		self.panelTop = wx.Panel( self.splitterMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL )
		self.panelTop.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		
		bSizerPanelTop = wx.BoxSizer( wx.VERTICAL )
		
		self.panelScrolled = ScrolledPanel( self.panelTop, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL|wx.TAB_TRAVERSAL )
		bSizerPanelScrolled = wx.BoxSizer( wx.VERTICAL )
		
		bSizerTitle = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextTime = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Time", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTime.Wrap( -1 )
		self.staticTextTime.SetFont( wx.Font( 12, 70, 90, 90, False, "@Meiryo" ) )
		
		bSizerTitle.Add( self.staticTextTime, 0, wx.ALL, 5 )

		bSizerTitle.AddSpacer( ( 20, 0), 1, wx.EXPAND, 5 )
		
		self.staticTextTitle = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Unified Radius Measurement Program", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextTitle.Wrap( -1 )
		self.staticTextTitle.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerTitle.Add( self.staticTextTitle, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		bSizerTitle.AddSpacer( ( 20, 0), 1, wx.EXPAND, 5 )
		
		self.staticTextVersion = wx.StaticText( self.panelScrolled, wx.ID_ANY, self.version, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.staticTextVersion.Wrap( -1 )
		self.staticTextVersion.SetFont( wx.Font( 12, 75, 90, 91, False, wx.EmptyString ) )
		
		bSizerTitle.Add( self.staticTextVersion, 0, wx.ALL, 5 )
		
		bSizerPanelScrolled.Add( bSizerTitle, 0, wx.EXPAND, 5 )
		
		bSizerContents = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizerContentsLeft = wx.BoxSizer( wx.VERTICAL )	
		
		bSizerPositions = wx.BoxSizer( wx.VERTICAL )
		
		bSizerPositionsTitle = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextBoard = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Board", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextBoard.Wrap( -1 )
		self.staticTextBoard.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPositionsTitle.Add( self.staticTextBoard, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextPositionMM = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Position (mm)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextPositionMM.Wrap( -1 )
		self.staticTextPositionMM.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPositionsTitle.Add( self.staticTextPositionMM, 3, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextPositionStd = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"std (mm)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextPositionStd.Wrap( -1 )
		self.staticTextPositionStd.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPositionsTitle.Add( self.staticTextPositionStd, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextStatus = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Status", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextStatus.Wrap( -1 )
		self.staticTextStatus.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPositionsTitle.Add( self.staticTextStatus, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizerPositions.Add( bSizerPositionsTitle, 0, wx.EXPAND, 5 )
		
		bSizerPositionContents = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextBoardContent = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextBoardContent.Wrap( -1 )
		self.staticTextBoardContent.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		self.staticTextBoardContent.SetForegroundColour( 'WHITE' )
		
		bSizerPositionContents.Add( self.staticTextBoardContent, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextPositionMMContents = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.staticTextPositionMMContents.Wrap( -1 )
		self.staticTextPositionMMContents.SetFont( wx.Font( 34, 70, 90, 90, False, wx.EmptyString ) )
		self.staticTextPositionMMContents.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		
		bSizerPositionContents.Add( self.staticTextPositionMMContents, 3, wx.ALL, 5 )
		
		self.staticTextPositionStdContents = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextPositionStdContents.Wrap( -1 )
		self.staticTextPositionStdContents.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		self.staticTextPositionStdContents.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
		
		bSizerPositionContents.Add( self.staticTextPositionStdContents, 1, wx.ALL, 5 )
		
		self.staticTextStatusContent = wx.StaticText( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextStatusContent.Wrap( -1 )
		self.staticTextStatusContent.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPositionContents.Add( self.staticTextStatusContent, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizerPositions.Add( bSizerPositionContents, 1, wx.EXPAND, 5 )
		
		bSizerContentsLeft.Add( bSizerPositions, 0, wx.EXPAND, 5 )
		
		self.staticlineContentsLeftSep1 = wx.StaticLine( self.panelScrolled, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerContentsLeft.Add( self.staticlineContentsLeftSep1, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerMeasurements = wx.BoxSizer( wx.VERTICAL )
		self.bSizerMeasurements = bSizerMeasurements
		
		bSizerContentsLeft.Add( bSizerMeasurements, 1, wx.EXPAND, 5 )
		
		bSizerContents.Add( bSizerContentsLeft, 1, wx.EXPAND, 5 )
		
		self.staticlineSepContents1 = wx.StaticLine( self.panelScrolled, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizerContents.Add( self.staticlineSepContents1, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizerConstants = wx.FlexGridSizer( 7, 3, 0, 0 )
		fgSizerConstants.SetFlexibleDirection( wx.BOTH )
		fgSizerConstants.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.staticTextWeatherStationName = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Weather Station Status:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextWeatherStationName.Wrap( -1 )
		self.staticTextWeatherStationName.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextWeatherStationName, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextWeatherStationStatus = wx.StaticText( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextWeatherStationStatus.Wrap( -1 )
		self.staticTextWeatherStationStatus.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.setWeatherStationStatus()
		
		fgSizerConstants.Add( self.staticTextWeatherStationStatus, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.buttonWeatherStationRefresh = wx.Button( self.panelScrolled, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonWeatherStationRefresh.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.buttonWeatherStationRefresh, 0, wx.ALL, 5 )
	

		self.comboBoxPartTemperatureProbeNameChoices = [ u"Custom" ]
		self.comboBoxPartTemperatureProbeNameChoices.append(self.weatherStation.partTemperatureStation)
		self.comboBoxPartTemperatureProbeName = wx.ComboBox( self.panelScrolled, wx.ID_ANY, self.weatherStation.partTemperatureStation, wx.DefaultPosition, wx.DefaultSize, self.comboBoxPartTemperatureProbeNameChoices, 0 )
		self.comboBoxPartTemperatureProbeName.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.comboBoxPartTemperatureProbeName.SetToolTipString( u"setup part temperature name" )
		
		fgSizerConstants.Add( self.comboBoxPartTemperatureProbeName, 1, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )

		self.textCtrlPartTemperatureProbeValue = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlPartTemperatureProbeValue.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlPartTemperatureProbeValue.SetValue("%0.2f" % self.weatherStation.partTemperature)
		
		fgSizerConstants.Add( self.textCtrlPartTemperatureProbeValue, 1, wx.ALL, 5 )
		
		self.staticTextPartTemperatureProbeUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Degree C", wx.DefaultPosition, wx.DefaultSize, 0)
		self.staticTextPartTemperatureProbeUnit.Wrap( -1 )
		self.staticTextPartTemperatureProbeUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextPartTemperatureProbeUnit, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.toggleBtnTemperature = wx.ToggleButton( self.panelScrolled, wx.ID_ANY, u"Air Temperature:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnTemperature.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.toggleBtnTemperature.SetToolTipString( u"toggle to override temperature" )
		
		fgSizerConstants.Add( self.toggleBtnTemperature, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlTemperature = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlTemperature.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlTemperature.SetValue("%0.2f" % self.weatherStation.temperature)
		
		fgSizerConstants.Add( self.textCtrlTemperature, 1, wx.ALL, 5 )
		
		self.staticTextTemperatureUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Degree C", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTemperatureUnit.Wrap( -1 )
		self.staticTextTemperatureUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextTemperatureUnit, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.toggleBtnPressure = wx.ToggleButton( self.panelScrolled, wx.ID_ANY, u"Air Pressure:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnPressure.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.toggleBtnPressure.SetToolTipString( u"toggle to override pressure" )
		
		fgSizerConstants.Add( self.toggleBtnPressure, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlPressure = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlPressure.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlPressure.SetValue("%0.2f" % self.weatherStation.pressure)
		
		fgSizerConstants.Add( self.textCtrlPressure, 1, wx.ALL, 5 )
		
		self.staticTextPressureUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"mmHg", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextPressureUnit.Wrap( -1 )
		self.staticTextPressureUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextPressureUnit, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.toggleBtnHumidity = wx.ToggleButton( self.panelScrolled, wx.ID_ANY, u"Air Humidity:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnHumidity.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.toggleBtnHumidity.SetToolTipString( u"toggle to override humidity" )
		
		fgSizerConstants.Add( self.toggleBtnHumidity, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlHumidity = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlHumidity.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlHumidity.SetValue("%0.2f" % self.weatherStation.humidity)
		
		fgSizerConstants.Add( self.textCtrlHumidity, 1, wx.ALL, 5 )
		
		self.staticTextHumidityUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"%", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHumidityUnit.Wrap( -1 )
		self.staticTextHumidityUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextHumidityUnit, 0, wx.ALL, 5 )
		
		self.buttonIndexOfAir = wx.Button( self.panelScrolled, wx.ID_ANY, u"Index of Air:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonIndexOfAir.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.buttonIndexOfAir.SetToolTipString( u"click to update the environment variables" )
		
		fgSizerConstants.Add( self.buttonIndexOfAir, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlIndexOfAir = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, ("%0.9f" % self.weatherStation.index_of_air), wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlIndexOfAir.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.textCtrlIndexOfAir, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.staticTextIndexOfAirUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextIndexOfAirUnit.Wrap( -1 )
		self.staticTextIndexOfAirUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextIndexOfAirUnit, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.buttonFocusCorrection = wx.Button( self.panelScrolled, wx.ID_ANY, u"Focus Sensitivity:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonFocusCorrection.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		self.buttonFocusCorrection.SetToolTipString( u"Click to reset Focus Corrected Calibration" )
		
		fgSizerConstants.Add( self.buttonFocusCorrection, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlFocusCorrectionValue = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, u"0.0", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE|wx.TE_READONLY )
		self.textCtrlFocusCorrectionValue.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.textCtrlFocusCorrectionValue, 0, wx.ALL, 5 )
		
		self.staticTextFocusCorrectionUnit = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"mm/wave", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextFocusCorrectionUnit.Wrap( -1 )
		self.staticTextFocusCorrectionUnit.SetFont( wx.Font( 9, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerConstants.Add( self.staticTextFocusCorrectionUnit, 1, wx.ALL, 5 )
		
		bSizerContents.Add( fgSizerConstants, 0, wx.EXPAND, 5 )
		
		bSizerPanelScrolled.Add( bSizerContents, 1, wx.EXPAND, 5 )
		
		self.staticlineScrolledSep1 = wx.StaticLine( self.panelScrolled, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPanelScrolled.Add( self.staticlineScrolledSep1, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerInfo = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextStation = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Station:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.staticTextStation.Wrap( -1 )
		self.staticTextStation.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerInfo.Add( self.staticTextStation, 0, wx.ALL, 5 )
		
		self.staticTextStationName = wx.StaticText( self.panelScrolled, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextStationName.Wrap( -1 )
		self.staticTextStationName.SetFont( wx.Font( 12, 70, 93, 92, False, wx.EmptyString ) )
		if self.cmdParams.wave_shift:
			self.staticTextStationName.SetLabel("Wave Shift, "+self.cmdParams.dmi_info.dmi_type+", "+self.cmdParams.phase_info.phase_type)
		else:
			self.staticTextStationName.SetLabel(self.cmdParams.dmi_info.dmi_type+", "+self.cmdParams.phase_info.phase_type)
		
		bSizerInfo.Add( self.staticTextStationName, 0, wx.ALL, 5 )

		bSizerInfo.AddSpacer( ( 20, 0), 1, wx.EXPAND, 5 )
		
		self.staticTextPartPath = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Part Path:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextPartPath.Wrap( -1 )
		self.staticTextPartPath.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerInfo.Add( self.staticTextPartPath, 0, wx.ALL, 5 )
		
		self.textCtrlPartPath = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, self.cmdParams.part_info.omase_path, wx.DefaultPosition, wx.Size( 300,-1 ), wx.TE_READONLY )
		self.textCtrlPartPath.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerInfo.Add( self.textCtrlPartPath, 0, wx.ALL, 5 )
		
		bSizerInfo.AddSpacer( ( 20, 0), 1, wx.EXPAND, 5 )
		
		self.staticTextBench = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Test Bench:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextBench.Wrap( -1 )
		self.staticTextBench.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerInfo.Add( self.staticTextBench, 0, wx.ALL, 5 )
		
		self.staticTextBenchName = wx.StaticText( self.panelScrolled, wx.ID_ANY, self.cmdParams.test_bench, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextBenchName.Wrap( -1 )
		self.staticTextBenchName.SetFont( wx.Font( 12, 70, 93, 92, False, wx.EmptyString ) )
		
		bSizerInfo.Add( self.staticTextBenchName, 0, wx.ALL, 5 )
		
		bSizerPanelScrolled.Add( bSizerInfo, 0, wx.EXPAND, 5 )
		
		self.panelScrolled.SetSizer( bSizerPanelScrolled )
		self.panelScrolled.Layout()
		self.panelScrolled.SetupScrolling()

		bSizerPanelTop.Add( self.panelScrolled, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizerButtons0 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.buttonF1 = wx.Button( self.panelTop, wx.ID_ANY, u"Single DMI Read <F1> ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF1.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF1.SetToolTipString( u"click to get single DMI read" )
		
		bSizerButtons0.Add( self.buttonF1, 1, wx.ALL, 5 )
		
		self.toggleBtnF2 = wx.ToggleButton( self.panelTop, wx.ID_ANY, u"Continuous DMI Read <F2>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnF2.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.toggleBtnF2.SetToolTipString( u"toggle to get continuous DMI read" )
		
		bSizerButtons0.Add( self.toggleBtnF2, 1, wx.ALL, 5 )
		
		self.buttonF3 = wx.Button( self.panelTop, wx.ID_ANY, u"Zero DMI <F3>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF3.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF3.SetToolTipString( u"click to zero DMI" )
		
		bSizerButtons0.Add( self.buttonF3, 1, wx.ALL, 5 )
		
		self.buttonF4 = wx.Button( self.panelTop, wx.ID_ANY, u"Clear DMI Error <F4>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF4.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF4.SetToolTipString( u"click to clear all DMI errors" )
		
		bSizerButtons0.Add( self.buttonF4, 1, wx.ALL, 5 )
		
		bSizerPanelTop.Add( bSizerButtons0, 0, wx.EXPAND, 5 )
		
		bSizerButtons1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.buttonF5 = wx.Button( self.panelTop, wx.ID_ANY, u"Normal Measurement <F5>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF5.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF5.SetToolTipString( u"click to perform normal measurement" )
		
		bSizerButtons1.Add( self.buttonF5, 1, wx.ALL, 5 )
		
		self.buttonF6 = wx.Button( self.panelTop, wx.ID_ANY, u"Focus Corrected Measurement <F6>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF6.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF6.SetToolTipString( u"click to perform focus corrected measurement" )
		
		bSizerButtons1.Add( self.buttonF6, 1, wx.ALL, 5 )
		
		self.toggleBtnF7 = wx.ToggleButton( self.panelTop, wx.ID_ANY, u"Gap Measurement <F7>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.toggleBtnF7.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.toggleBtnF7.SetToolTipString( u"toggle to set Gap Measurement ON" )
		
		bSizerButtons1.Add( self.toggleBtnF7, 1, wx.ALL, 5 )
		
		self.buttonF8 = wx.Button( self.panelTop, wx.ID_ANY, u"Remove Measurements <F8>", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonF8.SetFont( wx.Font( 9, 70, 90, 92, False, wx.EmptyString ) )
		self.buttonF8.SetToolTipString( u"Click to remove selected measurements" )
		
		bSizerButtons1.Add( self.buttonF8, 1, wx.ALL, 5 )
		
		bSizerPanelTop.Add( bSizerButtons1, 0, wx.EXPAND, 5 )
		
		self.panelTop.SetSizer( bSizerPanelTop )
		self.panelTop.Layout()
		bSizerPanelTop.Fit( self.panelTop )
		self.panelBot = wx.Panel( self.splitterMain, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL )
		self.panelBot.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )
		
		bSizerPanelBot = wx.BoxSizer( wx.VERTICAL )
		
		self.panelLog = wx.Panel( self.panelBot, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelLog.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )
		
		bSizerPanelLog = wx.BoxSizer( wx.VERTICAL )
		
		self.textCtrlLog = wx.TextCtrl( self.panelLog, wx.ID_ANY, u"Info / Warning / Error Log:\n", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		self.textCtrlLog.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )
		
		bSizerPanelLog.Add( self.textCtrlLog, 1, wx.ALL|wx.EXPAND, 0 )
		
		self.panelLog.SetSizer( bSizerPanelLog )
		self.panelLog.Layout()
		bSizerPanelLog.Fit( self.panelLog )
		bSizerPanelBot.Add( self.panelLog, 1, wx.EXPAND |wx.ALL, 0 )
		
		self.panelBot.SetSizer( bSizerPanelBot )
		self.panelBot.Layout()
		bSizerPanelBot.Fit( self.panelBot )
		self.splitterMain.SplitHorizontally( self.panelTop, self.panelBot, -1 )
		bSizerMain.Add( self.splitterMain, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizerMain )
		self.Layout()
		#self.statusBarMain = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.statusBarMain = StatusBarGauge(self)
		self.SetStatusBar(self.statusBarMain)
		self.toolBarMain = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.toolBarMain.AddLabelTool( 111, u"New", wx.Bitmap( self.baseDir+"gui/icons/file.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"New", u"Perform a new measurement" ) 
		self.toolBarMain.AddLabelTool( 222, u"Open", wx.Bitmap( self.baseDir+"gui/icons/folder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Open", u"Open a config file" ) 
		self.toolBarMain.AddLabelTool( 333, u"Save", wx.Bitmap( self.baseDir+"gui/icons/save.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Save", u"Save a config file" ) 
		self.toolBarMain.AddLabelTool( 444, u"Print", wx.Bitmap( self.baseDir+"gui/icons/print.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Print", u"Print a measurement report" )
		self.toolBarMain.AddLabelTool( 555, u"SetParts", wx.Bitmap( self.baseDir+"gui/icons/settings.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Settings", u"Setup Parts Information" )
		self.toolBarMain.AddLabelTool( 666, u"Clear", wx.Bitmap( self.baseDir+"gui/icons/close-tab.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Clear", u"Clear log panel" ) 
		self.toolBarMain.AddLabelTool( 777, u"About", wx.Bitmap( self.baseDir+"gui/icons/info.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"About", u"About Author information" ) 
		self.toolBarMain.Realize()
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.buttonWeatherStationRefresh.Bind( wx.EVT_BUTTON, self.onUpdateWeather )
		self.comboBoxPartTemperatureProbeName.Bind( wx.EVT_TEXT_ENTER, self.onPartTemperatureProbeEnterChange )
		self.comboBoxPartTemperatureProbeName.Bind( wx.EVT_COMBOBOX, self.onPartTemperatureProbeEnterChange )
		self.textCtrlPartTemperatureProbeValue.Bind( wx.EVT_TEXT_ENTER, self.onOverridePartTemperature )
		self.toggleBtnTemperature.Bind( wx.EVT_TOGGLEBUTTON, self.onConstantTemperatureToggle )
		self.textCtrlTemperature.Bind( wx.EVT_TEXT, self.onConstantTemperatureValue )
		self.textCtrlTemperature.Bind( wx.EVT_TEXT_ENTER, self.onConstantTemperatureValue )
		self.toggleBtnPressure.Bind( wx.EVT_TOGGLEBUTTON, self.onConstantPressureToggle )
		self.textCtrlPressure.Bind( wx.EVT_TEXT, self.onConstantPressureValue )
		self.textCtrlPressure.Bind( wx.EVT_TEXT_ENTER, self.onConstantPressureValue )
		self.toggleBtnHumidity.Bind( wx.EVT_TOGGLEBUTTON, self.onConstantHumidityToggle )
		self.textCtrlHumidity.Bind( wx.EVT_TEXT, self.onConstantHumidityValue )
		self.textCtrlHumidity.Bind( wx.EVT_TEXT_ENTER, self.onConstantHumidityValue )
		self.buttonFocusCorrection.Bind( wx.EVT_BUTTON, self.onFocusCorrectionReset )
		self.buttonIndexOfAir.Bind( wx.EVT_BUTTON, self.onUpdateWeather )
		self.buttonF1.Bind( wx.EVT_BUTTON, self.onSingleDMIRead )
		self.toggleBtnF2.Bind( wx.EVT_TOGGLEBUTTON, self.onContinuousDMIRead )
		self.buttonF3.Bind( wx.EVT_BUTTON, self.onZeroDMI )
		self.buttonF4.Bind( wx.EVT_BUTTON, self.onClearDMIErr )
		self.buttonF5.Bind( wx.EVT_BUTTON, self.onNormalMeasurement )
		self.buttonF6.Bind( wx.EVT_BUTTON, self.onFCMeasurement )
		self.toggleBtnF7.Bind( wx.EVT_TOGGLEBUTTON, self.onGapMeasure )
		self.buttonF8.Bind( wx.EVT_BUTTON, self.onRemoveMeasurements )
		self.Bind( wx.EVT_TOOL, self.onToolNew, id = 111 )
		self.Bind( wx.EVT_TOOL, self.onToolOpen, id = 222 )
		self.Bind( wx.EVT_TOOL, self.onToolSave, id = 333 )
		self.Bind( wx.EVT_TOOL, self.onToolPrint, id = 444 )
		self.Bind( wx.EVT_TOOL, self.onToolSetting, id = 555 )
		self.Bind( wx.EVT_TOOL, self.onToolClearLog, id = 666 )
		self.Bind( wx.EVT_TOOL, self.onToolAbout, id = 777 )
		
		# Timer
		self.Bind(wx.EVT_TIMER, self.onKeyPressTimer, self.key_polling_timer)
		self.Bind(wx.EVT_TIMER, self.onTimeTimer, self.time_timer)
		self.Bind(wx.EVT_TIMER, self.onWSTimer, self.ws_timer)
		self.Bind(wx.EVT_TIMER, self.onDMIReadTimer, self.dmi_read_timer)
		self.key_polling_timer.Start(100)	# 100 ms polling interval
		self.time_timer.Start(1000)			# 1 s updating interval
		self.ws_timer.Start(300000)			# 5 minutes updating interval
		
		# setting out_buffer
		self.__set_out_buffer__(self.textCtrlLog)
		
		# setup icon
		self.SetIcon(wx.Icon(self.baseDir+"gui/icons/radius2.png", wx.BITMAP_TYPE_PNG, 32, 32))

		# test DMI connection
		dmiError = self.dmi.chk_stat_reg2()
		if dmiError:
			self.setDMIStatus('ERROR')
			self.popErrorBox("ERROR", "ERROR: DMI communication failed. Check DMI connection?")
		else:
			self.setDMIStatus('A-OK')
			# sample DMI and print
			############################ we seems to have beamlines = 1 always; ASSUMING beamlines = 1 FOR NOW
			try:
				(positionMM, positionStd) = self.dmi.sampleDMI(100, 'M', 1, True, self.weatherStation)
				self.staticTextPositionMMContents.SetLabel("%0.6f" % positionMM[0])
				self.staticTextPositionStdContents.SetLabel("%0.6f" % positionStd[0])
			except Exception, e:
				self.printBuffer.writePrintOutFlush("ERROR: sampling DMI error.")
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
				self.statusBarMain.SetStatus("ERROR", True)
				self.popErrorBox("ERROR", "ERROR: cannot sample DMI. check DMI connection?")
	
	# __del__
	# @Purpose:
	#	destructor
	def __del__( self ):
		self.dmi.close()
		self.weatherStation.close()
		self.phaseStation.close()
	
	# onTimeTimer:
	# @Purpose:
	#	handling the time display timer event
	def onTimeTimer(self, event):
		timeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.staticTextTime.SetLabel(timeStr)
		event.Skip()
		
	# onWSTimer
	# @Purpose:
	#	handling weather update timer event
	@handleErrorsInMainGUI
	def onWSTimer(self, event):
		if self.isNewMeasurement:					# only update when it's not in measurements!
			self.weatherStation.updateWeather()
			if not self.toggleBtnTemperature.GetValue():
				self.textCtrlTemperature.SetValue("%0.2f" % self.weatherStation.temperature)
			if not self.toggleBtnPressure.GetValue():
				self.textCtrlPressure.SetValue("%0.2f" % self.weatherStation.pressure)
			if not self.toggleBtnHumidity.GetValue():
				self.textCtrlHumidity.SetValue("%0.2f" % self.weatherStation.humidity)
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
			self.textCtrlPartTemperatureProbeValue.SetValue("%0.2f" % self.weatherStation.partTemperature)
			self.setWeatherStationStatus()
		event.Skip()
	
	# onDMIReadTimer
	# @Purpose:
	#	handle the continuous DMI read timer event
	@handleErrorsInMainGUI
	def onDMIReadTimer(self, event):
		# sample DMI and print
		############### we seems to have beamlines = 1 always; ASSUMING beamlines = 1 FOR NOW #################
		try:
			(positionMM, positionStd) = self.dmi.sampleDMI(100, 'M', 1, True, self.weatherStation)
			self.staticTextPositionMMContents.SetLabel("%0.6f" % positionMM[0])
			self.staticTextPositionStdContents.SetLabel("%0.6f" % positionStd[0])
		except DMIPollingException, e:
			self.toggleBtnF2.SetValue(False)
			self.toggleBtnF2.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnF2.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			self.toggleBtnF2.SetFont(font)
			self.toggleBtnF2.GetParent().Refresh()
			self.dmi_read_timer.Stop()
			raise e
		except Exception, e:
			self.toggleBtnF2.SetValue(False)
			self.toggleBtnF2.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnF2.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			self.toggleBtnF2.SetFont(font)
			self.toggleBtnF2.GetParent().Refresh()
			self.dmi_read_timer.Stop()
			raise e
		event.Skip()
	
	# onPartTemperatureProbeEnterChange
	# @Purpose:
	#	handle the changing of the part temperature probe name
	@handleErrorsInMainGUI
	def onPartTemperatureProbeEnterChange( self, event ):
		comboBoxValue = self.comboBoxPartTemperatureProbeName.GetValue()
		if comboBoxValue == 'Custom':
			self.textCtrlPartTemperatureProbeValue.SetEditable(True)
			self.weatherStation.setPartTemperatureOverride(True)
		else:
			self.textCtrlPartTemperatureProbeValue.SetEditable(False)
			self.weatherStation.setPartTemperatureOverride(False)
			self.weatherStation.setPartTemperatureStation(comboBoxValue)
			self.onWSTimer(event)

	# onOverridePartTemperature
	# @Purpose:
	#	handles the overriding part temperature.
	@handleErrorsInMainGUI
	def onOverridePartTemperature( self, event ):
		self.weatherStation.partTemperature = float(self.textCtrlPartTemperatureProbeValue.GetValue())
		self.onWSTimer(event)
	
	# onConstantTemperatureToggle
	# @Purpose:
	#	handle constant temperature toggle button event
	@handleErrorsInMainGUI
	def onConstantTemperatureToggle( self, event ):
		self.weatherStation.setTemperatureOverride(self.toggleBtnTemperature.GetValue())
		self.textCtrlTemperature.SetEditable(self.toggleBtnTemperature.GetValue())
		if not self.toggleBtnTemperature.GetValue():
			self.weatherStation.updateWeather()
			self.textCtrlTemperature.SetValue("%0.2f" % self.weatherStation.temperature)
			self.toggleBtnTemperature.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnTemperature.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			self.toggleBtnTemperature.SetFont(font)
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		else:
			self.toggleBtnTemperature.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnTemperature.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			self.toggleBtnTemperature.SetFont(font)
		event.Skip()
	
	# onConstantTemperatureValue
	# @Purpose:
	#	handle constant temperature value changing event
	def onConstantTemperatureValue( self, event ):
		if self.toggleBtnTemperature.GetValue():
			try:
				self.weatherStation.setTemperature(float(self.textCtrlTemperature.GetValue()))
			except ValueError, e:
				pass
			self.weatherStation.atmosphereCorrect()
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		event.Skip()
	
	# onConstantPressureToggle
	# @Purpose:
	#	handle constant pressure toggle button event
	@handleErrorsInMainGUI
	def onConstantPressureToggle( self, event ):
		self.weatherStation.setPressureOverride(self.toggleBtnPressure.GetValue())
		self.textCtrlPressure.SetEditable(self.toggleBtnPressure.GetValue())
		if not self.toggleBtnPressure.GetValue():
			self.weatherStation.updateWeather()
			self.textCtrlPressure.SetValue("%0.2f" % self.weatherStation.pressure)
			self.toggleBtnPressure.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnPressure.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			self.toggleBtnPressure.SetFont(font)
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		else:
			self.toggleBtnPressure.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnPressure.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			self.toggleBtnPressure.SetFont(font)
		event.Skip()
	
	# onConstantPressureValue
	# @Purpose:
	#	handle constant pressure value changing event
	def onConstantPressureValue( self, event ):
		if self.toggleBtnPressure.GetValue():
			try:
				self.weatherStation.setPressure(float(self.textCtrlPressure.GetValue()))
			except ValueError, e:
				pass
			self.weatherStation.atmosphereCorrect()
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		event.Skip()
	
	# onConstantHumidityToggle
	# @Purpose:
	#	handle constant humidity toggle button event
	@handleErrorsInMainGUI
	def onConstantHumidityToggle( self, event ):
		self.weatherStation.setHumidityOverride(self.toggleBtnHumidity.GetValue())
		self.textCtrlHumidity.SetEditable(self.toggleBtnHumidity.GetValue())
		if not self.toggleBtnHumidity.GetValue():
			self.weatherStation.updateWeather()
			self.textCtrlHumidity.SetValue("%0.2f" % self.weatherStation.humidity)
			self.toggleBtnHumidity.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnHumidity.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			self.toggleBtnHumidity.SetFont(font)
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		else:
			self.toggleBtnHumidity.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnHumidity.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			self.toggleBtnHumidity.SetFont(font)
		event.Skip()
	
	# onConstantHumidityValue
	# @Purpose:
	#	handle constant humidity value changing event
	def onConstantHumidityValue( self, event ):
		if self.toggleBtnHumidity.GetValue():
			try:
				self.weatherStation.setHumidity(float(self.textCtrlHumidity.GetValue()))
			except ValueError, e:
				pass
			self.weatherStation.atmosphereCorrect()
			self.textCtrlIndexOfAir.SetValue("%0.9f" % self.weatherStation.index_of_air)
		event.Skip()
	
	# onFocusCorrectionReset
	# @Purpose:
	#	action to reset focus correction value. (make it re-calibrates)
	def onFocusCorrectionReset( self, event ):
		self.fcCalibrated = False
		self.textCtrlFocusCorrectionValue.SetValue("0.0")
		event.Skip()
	
	# onUpdateWeather
	# @Purpose:
	#	action to force update the environment variables in weather station
	def onUpdateWeather( self, event ):
		self.weatherStation.partTemperatureStation = self.comboBoxPartTemperatureProbeName.GetValue()
		self.onWSTimer(event)
	
	# onSingleDMIRead
	# @Purpose:
	#	handle the single DMI read event (F1)
	@handleErrorsInMainGUI
	def onSingleDMIRead( self, event ):
		# sample DMI and print
		############################ we seems to have beamlines = 1 always; ASSUMING beamlines = 1 FOR NOW
		(positionMM, positionStd) = self.dmi.sampleDMI(100, 'M', 1, True, self.weatherStation)
		self.staticTextPositionMMContents.SetLabel("%0.6f" % positionMM[0])
		self.staticTextPositionStdContents.SetLabel("%0.6f" % positionStd[0])
		event.Skip()
	
	# onContinuousDMIRead
	# @Purpose:
	#	handle continuous DMI read event (F2)
	def onContinuousDMIRead( self, event ):
		if event.GetEventType() == wx.wxEVT_TIMER:	# F2 key pressed:
			self.toggleBtnF2.SetValue(not self.toggleBtnF2.GetValue())
		if self.toggleBtnF2.GetValue():
			self.dmi_read_timer.Start(1000)			# start the timer with 1s update interval;
			self.toggleBtnF2.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnF2.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			self.toggleBtnF2.SetFont(font)
			self.statusBarMain.PulseStart()
		else:
			self.dmi_read_timer.Stop()
			self.toggleBtnF2.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnF2.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			self.toggleBtnF2.SetFont(font)
			self.statusBarMain.PulseStop()
		event.Skip()
	
	# onZeroDMI
	# @Purpose:
	#	handle zero DMI event (F3)
	@handleErrorsInMainGUI
	def onZeroDMI( self, event ):
		self.dmi.zeroDMI()
		self.staticTextPositionMMContents.SetLabel("%0.6f" % 0.0)
		event.Skip()
	
	# onClearDMIErr
	# @Purpose:
	#	handle clearing DMI error event (F4)
	@handleErrorsInMainGUI
	def onClearDMIErr( self, event ):
		self.dmi.clearDMI()
		self.staticTextPositionMMContents.SetLabel("%0.6f" % 0.0)
		event.Skip()
	
	# onNormalMeasurement
	# @Purpose:
	#	handle normal measurement event (F5)
	@handleErrorsInMainGUI
	def onNormalMeasurement( self, event ):
		self.measureRadius(False, True)
		event.Skip()
	
	# onFCMeasurement
	# @Purpose:
	#	handle focus corrected measurement event (F6)
	@handleErrorsInMainGUI
	def onFCMeasurement( self, event ):
		self.measureRadius(True, False)
		event.Skip()
	
	# onGapMeasure
	# @Purpose:
	#	a toggle button to toggle on gap measurement or not.
	def onGapMeasure( self, event ):
		if event.GetEventType() == wx.wxEVT_TIMER:
			self.toggleBtnF7.SetValue(not self.toggleBtnF7.GetValue())
		self.GapMeas = self.toggleBtnF7.GetValue()
		if self.GapMeas:
			self.toggleBtnF7.SetBackgroundColour(wx.Colour(0, 0, 0))
			font = self.toggleBtnF7.GetFont()
			font.SetStyle(wx.FONTSTYLE_ITALIC)
			self.toggleBtnF7.SetFont(font)
			dlg = DialogNoCatEyePrompt(self)
			dlg.ShowModal()
		else:
			self.sTS_Offset = 0.0						# for non-cat eye measurement
			self.sGap_Offset = 0.0						# for non-cat eye measurement
			self.toggleBtnF7.SetBackgroundColour(wx.Colour(255, 255, 255))
			font = self.toggleBtnF7.GetFont()
			font.SetStyle(wx.FONTSTYLE_NORMAL)
			self.toggleBtnF7.SetFont(font)
		event.Skip()
	
	# onRemoveMeasurements
	# @Purpose:
	#	perform removing a specific measurement from statistic calculation
	@handleErrorsInMainGUI
	def onRemoveMeasurements( self, event ):
		for r in range(self.gridMeasurements.GetNumberRows()):
			attr = gridlib.GridCellAttr()
			if self.gridMeasurements.GetCellValue(r, 6):		# removed is ticked
				attr.SetBackgroundColour('BLACK')
				attr.SetTextColour('DARK GREY')
				# set this measurement to be invalid
				self.gFC_Rad[r] = None
				self.gFC_CCDMI[r] = None
				self.gFC_CEDMI[r] = None
				self.gCC_Foc[r] = None
				self.gCE_Foc[r] = None
			else:
				# turn this measurement on
				attr.SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ))
				attr.SetTextColour('BLACK')
				self.gFC_Rad[r] = self.gridMeasurements.GetCellValue(r, 1)
				self.gFC_CCDMI[r] = self.gridMeasurements.GetCellValue(r, 2)
				self.gFC_CEDMI[r] = self.gridMeasurements.GetCellValue(r, 3)
				self.gCC_Foc[r] = self.gridMeasurements.GetCellValue(r, 4)
				self.gCE_Foc[r] = self.gridMeasurements.GetCellValue(r, 5)
				
			self.gridMeasurements.SetRowAttr(r, attr)
			self.updateMeasurementStatsVariation()					# update the stats...
		# repaint the panel...
		self.refreshResultsGrids()
		event.Skip()
		
	# onToolNew
	# @Purpose:
	#	perform new measurement setup for toolbox - new
	def onToolNew( self, event ):
		self.cmdParams.part_info.initialized = False	# force operator to re-enter part information:
		self.meas_num = 0								# reset measurement #
		self.isNewMeasurement = True					# reset measurement series flag
		self.deleteMeasurements()						# delete the measurement title display
		self.onFocusCorrectionReset(event)				# reset focus correction values
		event.Skip()
	
	# onToolOpen
	# @Purpose:
	#	open a config file openning dialog, and try to load the config
	@handleErrorsInMainGUI
	def onToolOpen( self, event ):
		default_cfg_dir = os.getenv('omasepath')+"\\machinfo"
		wildcard = "Config File (*.cfg)|*.cfg|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", default_cfg_dir, "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetPath()
			utilities.parseConfig(file, self.cmdParams, self.printBuffer, self.debug)
			self.printBuffer.writePrintOutFlush("INFO: read config file: %s" % file)
		dialog.Destroy()
		event.Skip()
	
	# onToolSave
	# @Purpose:
	#	save a report file to the disk
	@handleErrorsInMainGUI
	def onToolSave( self, event ):
		default_dir = self.textCtrlPartPath.GetValue()
		wildcard = "Report File (*.alg)|*.alg|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", default_dir, self.outputfile, wildcard, wx.SAVE|wx.OVERWRITE_PROMPT)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetPath()
			self.setupReportFile(file)
			self.printBuffer.writePrintOutFlush("INFO: saved report file to: %s" % file)
		dialog.Destroy()
		event.Skip()
	
	# onToolPrint
	# @Purpose:
	#	print the measurement results
	@handleErrorsInMainGUI
	def onToolPrint( self, event ):
		self.statusBarMain.PulseStart()
		# setup the output file for print
		if not self.setupReportFile():
			return
		# print to default printer
		##### win32api printing from DOS CMD NOT WORKING... need to investigate ######
		# win32api.ShellExecute(0, "print", self.outputfile, '/d:"%s"' % win32print.GetDefaultPrinter(), ".", 0)
		##############################################################################

		##### Using ps (postscript) printing message from Dan... #####	(DEPRECATED)
		# radius3.psprint.PrintText(self.outputfile)
		##############################################################
		##### Using notepad to print... #####
		subprocess.call(['notepad', '/p', self.outputfile])
		#####
		# self.printBuffer.writePrintOutFlush("INFO: You can find a the report file at: %s" % os.getcwd()+"\\"+self.outputfile)
		#os.remove(self.outputfile)			# clean up the report file
		event.Skip()
	
	# onToolSetting
	# @Purpose:
	#	open the part information setup dialog
	def onToolSetting( self, event ):
		dlg = DialogPartPrompt(self, self.cmdParams)
		dlg.ShowModal()
		self.textCtrlPartPath.SetValue(self.cmdParams.part_info.omase_path)
		event.Skip()
	
	# onToolClearLog
	# @Purpose:
	#	clear the log messages in the log area.
	def onToolClearLog( self, event ):
		self.textCtrlLog.SetValue("")
		event.Skip()
	
	# onToolAbout
	# @Purpose:
	#	open a About windows display program description and author information
	def onToolAbout( self, event ):
		info = wx.AboutDialogInfo()
		info.SetIcon(wx.Icon(self.baseDir+"gui/icons/radius2.png", wx.BITMAP_TYPE_PNG, 32, 32))
		info.SetName("Unified Radius Measurement Program")
		info.SetDescription(utilities.PROG_DESCRIPTION)
		info.SetLicense(utilities.LICENSE)
		info.SetVersion(radius3.__version__)
		info.SetCopyright(" (C) 2013 Zygo Corporation")
		info.SetWebSite("http://www.zygo.com")
		info.AddDeveloper("Charlie Chen <cchen@zygo.com>")
		info.AddDeveloper("Gary Crumback <>")
		info.AddDeveloper("Lou Marchetti <lmarchetti@zygo.com>")
		info.AddDocWriter("Charlie Chen <cchen@zygo.com>")
		wx.AboutBox(info)
		event.Skip()

	# onKeyPress
	# @Purpose:
	#	binding Function keys to the corresponding operation buttons
	def onKeyPressTimer(self, event):
		if wx.GetKeyState(wx.WXK_F1):
			self.onSingleDMIRead(event)
		elif wx.GetKeyState(wx.WXK_F2):
			self.onContinuousDMIRead(event)
		elif wx.GetKeyState(wx.WXK_F3):
			self.onZeroDMI(event)
		elif wx.GetKeyState(wx.WXK_F4):
			self.onClearDMIErr(event)
		elif wx.GetKeyState(wx.WXK_F5):
			self.onNormalMeasurement(event)
		elif wx.GetKeyState(wx.WXK_F6):
			self.onFCMeasurement(event)
		elif wx.GetKeyState(wx.WXK_F7):
			self.onGapMeasure(event)
		elif wx.GetKeyState(wx.WXK_F8):
			self.onRemoveMeasurements(event)
		else:
			pass
		event.Skip()
	
	# setupReportFile:
	# @Purpose:
	#	This funciton setups the report file to store and print
	# @Output:
	#	True if success, False otherwise
	def setupReportFile(self, f=None):
		# setup file
		if f == None:
			f = self.outputfile

		# test if we have measurements already...
		try:
			measurement_type_str = self.staticTextMeasurementsRadiusTitle.GetLabel()
		except AttributeError, e:
			self.printBuffer.writePrintOutFlush("ERROR: No measurements are made! Please perform measurements first in order to print the report!")
			self.popErrorBox("No Measurements to print!",
						"ERROR: Cannot print! No measurements are made!\n Please perform measurements first in order to print the report!")
			return False
		
		# setup the output file for print
		fout = open(f, 'w')
		# report header section
		fout.write("Date & Time: "+datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"))
		fout.write("\t\t\t%s\n" %self.version)
		fout.write("Omase Path:\t\t%s\n" % self.cmdParams.part_info.omase_path)
		fout.write("Book Title:\t\t%s\n" % self.cmdParams.part_info.book_title)
		fout.write("Part Name:\t\t%s\n" % self.cmdParams.part_info.name)
		fout.write("Part ID:\t\t%s\n" % self.cmdParams.part_info.id)
		fout.write("Part Surface:\t\t%s\n" % self.cmdParams.part_info.surface)
		fout.write("Operator:\t\t%s\n" % self.cmdParams.part_info.user)
		fout.write("Test Bench:\t\t%s\n" % self.cmdParams.test_bench)
		fout.write("\n")
		fout.write("Air Temperature: %0.2f deg C;  Air Pressure: %0.2f mmHg;  Air Humidity: %0.2f %%\n" % \
					(self.weatherStation.temperature, self.weatherStation.pressure, self.weatherStation.humidity))
		if self.weatherStation.temperatureStation == self.weatherStation.partTemperatureStation:
			fout.write("Part Temperature: Air Temperature\n")
		else:
			fout.write("Part Temperature: %0.2f deg C\n" % self.weatherStation.partTemperature)
		if self.sCTE_Cmp_Rad != 0.0:
			fout.write("CTE: %0.2e/deg C. (%s);  Report Temperature: %0.2f deg C\n" % \
						(self.cmdParams.part_info.cte, self.cmdParams.part_info.glass_type, self.cmdParams.part_info.target_temp))
		
		try:
			ap_length = self.phaseStation.getLength()
			ap_width = self.phaseStation.getWidth()
		except Exception, e:
			ap_length = -1.0
			ap_width = -1.0
			self.printBuffer.writePrintOutFlush(traceback.format_exc())

		fout.write("Aperture Length: %0.3f mm;  Aperture Width: %0.3f mm\n" % \
					(ap_length, ap_width))
		fout.write("------------------------------------------------------------------------------------\n\n")
		fout.flush()
		# report measurements section
		fout.write(""+measurement_type_str+"\n")
		fout.write("-----------------------\n")
		fout.write("Meas.#\t    Radius\tCC Focus\tFC CC DMI\tCE Focus\tFC CE DMI\n")
		fout.write("\t     (mm)\t(wv 633)\t   (mm)\t\t(wv 633)\t   (mm)\n")
		for m in range(self.meas_num):
			if self.gFC_Rad[m] == None:
				continue
			fout.write("  %d\t   % 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\n" % \
					(m, self.gFC_Rad[m], self.gCC_Foc[m], self.gFC_CCDMI[m], self.gCE_Foc[m], self.gFC_CEDMI[m]))
		fout.write("------------------------------------------------------------------------------------\n")
		fout.write("Avg.\t   % 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\n" % \
					(self.gridMeasurementsStats.GetCellValue(0, 1),
					self.gridMeasurementsStats.GetCellValue(0, 2),
					self.gridMeasurementsStats.GetCellValue(0, 3),
					self.gridMeasurementsStats.GetCellValue(0, 4),
					self.gridMeasurementsStats.GetCellValue(0, 5)))
		fout.write("Stdev\t   % 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\t% 0.6f\n" % \
					(self.gridMeasurementsStats.GetCellValue(1, 1),
					self.gridMeasurementsStats.GetCellValue(1, 2),
					self.gridMeasurementsStats.GetCellValue(1, 3),
					self.gridMeasurementsStats.GetCellValue(1, 4),
					self.gridMeasurementsStats.GetCellValue(1, 5)))
		fout.write("Stdev(wv)  % 0.6f\t         \t% 0.6f\t         \t% 0.6f\n" % \
					(self.gridMeasurementsStats.GetCellValue(2, 1),
					self.gridMeasurementsStats.GetCellValue(2, 3),
					self.gridMeasurementsStats.GetCellValue(2, 5)))
		fout.write("\n")
		fout.write("Variation From Average:\n")
		fout.write("------------------------------------------------------------------------------------\n")
		fout.write("\t  Radius\t\t   FC CC DMI\t\t\tFC CE DMI\n")
		fout.write("Meas.#\t(mm)\t(wv 633)\t(mm)\t(wv 633)\t   (mm)\t\t(wv633)\n")
		for m in range(self.meas_num):
			if self.gFC_Rad[m] == None:
				continue
			fout.write("  %d   % 0.6f\t% 0.4f\t     % 0.6f\t% 0.4f\t\t% 0.6f\t% 0.4f\n" % \
					(self.gridMeasurementsVariations.GetCellValue(m, 0),
					self.gridMeasurementsVariations.GetCellValue(m, 1),
					self.gridMeasurementsVariations.GetCellValue(m, 2),
					self.gridMeasurementsVariations.GetCellValue(m, 3),
					self.gridMeasurementsVariations.GetCellValue(m, 4),
					self.gridMeasurementsVariations.GetCellValue(m, 5),
					self.gridMeasurementsVariations.GetCellValue(m, 6)))
		fout.write("\n")
		fout.write("____________________________________________________________________________________\n")
		fout.write("| Average Radius	=	%0.6f	(mm) \n" % self.gridMeasurementsStats.GetCellValue(0, 1))
		fout.write("------------------------------------------------------------------------------------\n")
		fout.write("\n")
		fout.flush()
		fout.write(" * Denotes Measurement(s) Excluded from Statistics.\n\n")
		fout.write("Corrected IC Scale Factor Was:\t%f (cts/mm)\n" % (self.weatherStation.sAtm_IC * 25.4))
		fout.write("Index of Air Was:\t\t%0.9f\n" % self.weatherStation.index_of_air)
		if measurement_type_str == "Focus Corrected Radius:":	# FC measurement
			fout.write("Focus Correction Factor Was:\t%f (mm/wave of Seidel Focus)\n" % self.gDMI_Wave)
		else:
			fout.write("NOT A FOCUS CORRECTED MEASUREMENT!\n")
		if self.GapMeas:
			fout.write("MEASUREMENT USED GAP GAUGE!\n")
			fout.write("Transmission Sphere Offset:\t%0.3f mm\n" % self.sTS_Offset)
			fout.write("Gap Offset:\t\t\t%0.3f mm\n" % self.sGap_Offset)
		fout.write("\n")
		fout.write("Output File:\t\t\t %s\n" % self.outputfile)
		if self.sCTE_Cmp_Rad != 0.0:
			fout.write("\n")
			fout.write("\n\n")
			fout.write("______________________________________________________________________________\n")
			fout.write(" Temperature Compensated Radius @ %0.2f (deg C) = % 0.6f (mm)\n" % \
						(self.cmdParams.part_info.target_temp, self.sCTE_Cmp_Rad))
			fout.write("______________________________________________________________________________\n")
		fout.flush()
		fout.close()
		return True
	
	# measureRadius	(previously measure_foccorr)
	# @Purpose:
	#	This function performs the radius measurements
	# @Inputs:
	#	isFCMeasure = True if it's focus corrected measurement; False otherwise
	#	skipFocusCorrected = True if skipping focus corrected measurement; False otherwise
	def measureRadius(self, isFCMeasure, skipFocusCorrected):
		# check if it's a brand new measurement series!
		if self.isNewMeasurement:
			self.meas_num = 0					# reset total measurement counts
			self.isNewMeasurement = False		# mark continuous
			# delete the current measurement results grid, if any exists
			self.deleteMeasurements()
			
			# gather part information
			self.cmdParams.id = ""				# reset ID force operator to check
			dlg = DialogPartPrompt(None, self.cmdParams)
			dlg.ShowModal()
			self.textCtrlPartPath.SetValue(self.cmdParams.part_info.omase_path)
			
			# setup output file name
			timenow = datetime.datetime.now()
			self.outputfile = "Z-%s-%sx%s.alg" % (self.cmdParams.part_info.id, \
								timenow.strftime("%y%m%d"), timenow.strftime("%H%M%S"))
			# update the weather before measurement
			self.weatherStation.updateWeather()
			# zero DMI
			self.dmi.zeroDMI()
			# first DMI reading
			try:
				pos = self.dmi.sampleDMI(100, 'M', 1, False, self.weatherStation)[0][0]	# ASSUME 1 beamline
			except Exception, e:
				self.printBuffer.writePrintOutFlush("ERROR: sampling DMI error.")
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
				self.popErrorBox("ERROR", "ERROR: sampling DMI error; check ERROR LOG or console.")
				self.isNewMeasurement = True		# reset new measurement value before return!
				return
		
			if isFCMeasure:
				if self.cmdParams.phase_info.phase_type == "OpticodePCS":
					# prompt operator for setting phase station to remote mode
					self.printBuffer.writePrintOutFlush("INFO: Please Turn OpticodePCS to REMOTE MODE")
					title = "Please Turn OpticodePCS to REMOTE MODE"
					msg = "Please Turn OpticodePCS to REMOTE MODE.\nOpticode must be in remote tirgger mode; Hit <F2> on Phase Computer if not!!!\nApply data masks in Opticode if applicable\n\n Hit <OK> to begin; <CANCEL> to leave."
					if self.popInfoBox(title, msg) == wx.ID_CANCEL:
						self.isNewMeasurement = True		# reset new measurement value before return!
						return
						
				while True:
					try:
						self.phaseStation.sync()
						break
					except Exception, e:
						self.printBuffer.writePrintOutFlush("ERROR: Phase station sync timeout!")
						self.printBuffer.writePrintOutFlush(traceback.format_exc())
						if self.cmdParams.phase_info.phase_type == "OpticodePCS":
							ans = self.popRetryBox("ERROR", "ERROR: Phase station sync timeout! \n Press F2 to FORCE sync Phase station before trying again.\nContinue to try?")
						elif self.cmdParams.phase_info.phase_type == "MetroPro":
							ans = self.popRetryBox("ERROR", "ERROR: Phase station sync timeout! \n Press F11 to active remote control for Phase station before trying again.\nContinue to try?")
						if ans == wx.ID_NO:
							self.isNewMeasurement = True		# reset new measurement value before return!
							return
		
			########### Part to CE for focus calibration ###########
			if not skipFocusCorrected and not self.fcCalibrated:
				if not self.focusCorrectCalibration(isFCMeasure):
					self.isNewMeasurement = True		# reset new measurement value before return!
					return
		
			########### Setup the display title if it's the first measurement! ###########
			self.showMeasurementTitle(isFCMeasure)
		
		########### Radius Measurement Routine ###########
		while self.meas_num < self.max_meas:
			meas_num = self.meas_num
			cc_arrpos = meas_num*2						# array position for cc dmi reading
			ce_arrpos = meas_num*2+1					# array position for ce dmi reading
			
			self.printBuffer.writePrintOutFlush("############################")
			self.printBuffer.writePrintOutFlush("Radius Measurement #%d" % meas_num)
			self.printBuffer.writePrintOutFlush("############################")
			self.printBuffer.writePrintOutFlush("INFO: Position part at center of curvature position.")
			title = "Radius Measurement #%d" % meas_num
			msg = "INFO: Radius Measurement #%d\nPosition part at center of curvature position.\nContinue Measurement?\nPress <YES> to continue; <NO> to quit." % meas_num
			clicked = self.popYesNoBox(title, msg)
			if clicked == wx.ID_NO:
				break			# finish operation
				
			try:
				if self.cmdParams.wave_shift and isFCMeasure:
					if meas_num == 0 and skipFocusCorrected:
						self.phaseStation.setWaveShift(False, self.cmdParams.part_info.ts_radius, \
														self.cmdParams.part_info.part_radius)
					else:
						self.phaseStation.loadConfig(self.phaseStation.centerofcurvature_cfg)
					
				# center of curvature dmi_phase
				if not self.dmiPhase(cc_arrpos, False, False, isFCMeasure):
					break				# error out
					
				if self.GapMeas:
					self.printBuffer.writePrintOutFlush("INFO: Position Part so Gap Gauge Reads 0.0")
					self.popInfoOKBox("INFO", "Position Part so Gap Gauge Reads 0.0\n Hit <OK> When Ready.")
				else:
					self.printBuffer.writePrintOutFlush("INFO: Position Part at Cat Eye Position.")
					self.popInfoOKBox("INFO", "Position Part at Cat Eye Position.\n Hit <OK> When Ready.")
				
				if self.cmdParams.wave_shift and not self.GapMeas:
					if isFCMeasure:
						if meas_num == 0:
							self.phaseStation.setWaveShift(True, self.cmdParams.part_info.ts_radius, \
														self.cmdParams.part_info.part_radius)
						else:
							self.phaseStation.loadConfig(self.phaseStation.cateye_cfg)
					
				# cat eye dmi_phase
				if not self.dmiPhase(ce_arrpos, False, self.GapMeas, isFCMeasure):
					break				# error out
						
				### find corrected radius ###
				self.gCC_Foc[meas_num] = self.gFocus_Zrn[cc_arrpos]
				self.gCE_Foc[meas_num] = self.gFocus_Zrn[ce_arrpos]
				self.gFC_CCDMI[meas_num] = self.gDMI_rd[cc_arrpos] - (self.gCC_Foc[meas_num] * self.gDMI_Wave)
				self.gFC_CEDMI[meas_num] = self.gDMI_rd[ce_arrpos] - (self.gCE_Foc[meas_num] * self.gDMI_Wave)
				self.gFC_Rad[meas_num] = self.gFC_CEDMI[meas_num] - self.gFC_CCDMI[meas_num]
				if self.debug:
					self.printBuffer.writePrintOutFlush("INFO: CC_FOC[%d]: %f:" % (meas_num, self.gCC_Foc[meas_num]))
					self.printBuffer.writePrintOutFlush("INFO: CE_FOC[%d]: %f:" % (meas_num, self.gCE_Foc[meas_num]))
					self.printBuffer.writePrintOutFlush("INFO: FC_CCDMI[%d]: %f:" % (meas_num, self.gFC_CCDMI[meas_num]))
					self.printBuffer.writePrintOutFlush("INFO: FC_CEDMI[%d]: %f:" % (meas_num, self.gFC_CEDMI[meas_num]))
					self.printBuffer.writePrintOutFlush("INFO: FC_Rad[%d]: %f:" % (meas_num, self.gFC_Rad[meas_num]))
				
			except Exception, e:
				self.printBuffer.writePrintOutFlush("ERROR: Phase Station error.")
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
				self.popErrorBox("ERROR", "ERROR: Phase station error! Please check error log or console.")
				
			self.meas_num += 1
			# setup the GUI display
			self.showMeasurement(meas_num)
		
		# clean up
		self.isNewMeasurement = True
	
	# focusCorrectCalibration:
	# @Purpose:
	#	perform a focus correct calibration
	# @Output:
	#	True if successful; False otherwise
	def focusCorrectCalibration(self, isFCMeasure):
		self.printBuffer.writePrintOutFlush("INFO: Focus Calibration. Position part at center of curvature position.")
		title = "Focus calibration"
		msg = "Performing focus calibration. \nPosition part at center of curvature position. \nHit <OK> to proceed; <CANCEL> to leave."
		if self.popInfoBox(title, msg) == wx.ID_CANCEL:
			return False
			
		if self.cmdParams.wave_shift:		# if a wave shifter
			try:
				self.phaseStation.setWaveShift(False, self.cmdParams.part_info.ts_radius, \
												self.cmdParams.part_info.part_radius)
			except Exception, e:
				self.printBuffer.writePrintOutFlush("ERROR: setWaveShift error - Phase Station fails to set wave shift.")
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
				self.popErrorBox("ERROR", "ERROR: Phase station failed to set wave shift!")
				return False
			
		if not self.dmiPhase(0, True, False, isFCMeasure):
			self.printBuffer.writePrintOutFlush("ERROR: dmiPhase error - DMI and Phase Station error.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: DMI and Phase Station Error; check ERROR LOG or console.")
			return False
			
		# alert the operator to put parts to creat 4-5 Rings
		self.printBuffer.writePrintOutFlush("INFO: Focus Calibration. Please position part to create 4 -5 rings.")
		self.popInfoOKBox("Attention", "Please position part to create 4 - 5 rings.\n Press <OK> to continue.")
		if not self.dmiPhase(1, False, False, isFCMeasure):
			self.printBuffer.writePrintOutFlush("ERROR: dmiPhase error - DMI and Phase Station error.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: DMI and Phase Station Error; check ERROR LOG or console.")
			return False
			
		### find (mm/wave) term for Null Len ###
		distance = self.gDMI_rd[1] - self.gDMI_rd[0]
		self.gDMI_Wave = distance / (self.gFocus_Zrn[1] - self.gFocus_Zrn[0])	# (mm/wave) correct term
		if isFCMeasure:
			self.textCtrlFocusCorrectionValue.SetValue("%0.4e" % self.gDMI_Wave)
			self.fcCalibrated = True
		else:
			self.textCtrlFocusCorrectionValue.SetValue("0.0")
		
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: gDMI_rd[1]: %0.5f\n" % self.gDMI_rd[1])
			self.printBuffer.writePrintOutFlush("INFO: gDMI_rd[0]: %0.5f\n" % self.gDMI_rd[0])
			self.printBuffer.writePrintOutFlush("INFO: distance: %0.5f\n" % distance)
			self.printBuffer.writePrintOutFlush("INFO: gDMI_Wave: %0.5f\n" % self.gDMI_Wave)
			
		# restore the "borrowed" class variable space:
		self.gDMI_rd[0] = None
		self.gDMI_rd[1] = None
		self.gFocus_Zrn[0] = None
		self.gFocus_Zrn[1] = None
		
		return True
	
	# dmiPhase
	# @Purpose:
	#	This function samples the DMI, reads the Phase station, and save the data.
	# @Inputs:
	#	dmiIndex = index of DMI array position and focus term array position
	#	zeroDMI = True if zero-ing DMI; False otherwise
	#	gapMeasurement = True if Gap Measurement; False if cat eye measurement
	#	isFCMeasure = True if it's focus corrected measurement; False otherwise
	# @Outputs:
	#	return True if successful; False otherwise
	def dmiPhase(self, dmiIndex, zeroDMI, gapMeasurement, isFCMeasure):
		measurementTimes = 10
		tempDMI = []
		tempFocus = []
	
		dmiError = self.dmi.chk_stat_reg2()
		if dmiError:
			self.setDMIStatus('ERROR')
			self.popErrorBox("ERROR", "ERROR: DMI communication failed. DMI has broken beam?")
			return False
		if zeroDMI:
			self.dmi.zeroDMI()
		time.sleep(0.001)
				
		for i in range(measurementTimes):
			try:
				tempDMI.append(self.dmi.sampleDMI(100, 'M', 1, False, self.weatherStation)[0][0])
			except Exception, e:
				self.printBuffer.writePrintOutFlush("ERROR: sampling DMI error in dmiPhase.")
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
				self.popErrorBox("ERROR", "ERROR: sampling DMI error; check ERROR LOG or console.")
				return False
				
			if isFCMeasure and (not gapMeasurement):
				if not self.getFocusTerm():
					return False					# error out
				tempFocus.append(self.phaseStation.getFocus())
				
				try:
					tempDMI.append(self.dmi.sampleDMI(100, 'M', 1, False, self.weatherStation)[0][0])
				except Exception, e:
					self.printBuffer.writePrintOutFlush("ERROR: sampling DMI error in dmiPhase.")
					self.printBuffer.writePrintOutFlush(traceback.format_exc())
					self.popErrorBox("ERROR", "ERROR: sampling DMI error; check ERROR LOG or console.")
					return False
				
				### check if DMI measurement agree, if not , throw out and repeat ###
				goBack = False
				errMsg = ""
				# if difference of 2 measurements is more than a threshold
				if abs(tempDMI[-1] - tempDMI[-2]) > 0.1:
					errMsg += "ERROR: Bad DMI Data: %0.3f, %0.3f\n" % (tempDMI[-1], tempDMI[-2])
					goBack = True
				if abs(tempFocus[-1]) < 0.0002 or abs(tempFocus[-1]) > 10.0:
					errMsg += "ERROR: Bad Phase Data: %0.3f\n" % tempFocus[-1]
					goBack = True
				
				if goBack:
					# pop all last measurements out.
					tempDMI.pop(-1)
					tempDMI.pop(-1)
					tempFocus.pop(-1)
					if self.popRetryBox("ERROR", errMsg+"Retry?") == wx.ID_NO:
						return False
				else:						# no error; no need to repeat measurements.
					break
			else:							# not a focus corrected measurement; no need to repeat.
				break
				
				
		### average DMI and Phase Data ###
		self.gDMI_rd[dmiIndex] = sum(tempDMI) / len(tempDMI)
		if gapMeasurement:		# if gap measurement, add offsets
			self.gDMI_rd[dmiIndex] -= self.sTS_Offset + self.sGap_Offset
			
		if isFCMeasure and (not gapMeasurement):
			self.gFocus_Zrn[dmiIndex] = sum(tempFocus) / len(tempFocus)
		else:
			self.gFocus_Zrn[dmiIndex] = 0.0
			
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: self.gDMI_rd[%d]: %f" % (dmiIndex, self.gDMI_rd[dmiIndex]))
			self.printBuffer.writePrintOutFlush("INFO: self.gFocus_Zrn[%d]: %f" % (dmiIndex, self.gFocus_Zrn[dmiIndex]))
		
		return True
		
	# getFocusTerm:
	# @Purpose:
	#	This function does a focus correction calibration
	# @Output:
	#	return True if successful; False otherwise
	def getFocusTerm(self):
		retryCount = 0
		retries = 3
		again = True
		while again:
			try:
				if not self.phaseStation.isSync:
					self.phaseStation.sync()
			except Exception, e:
				title = "CANNOT SYNC with Phase Station!"
				msg = "ERROR: Cannot sync with Phase Station. Try Again?"
				if self.popRetryBox(title, msg) == wx.ID_NO:
					return False
			try:
				self.phaseStation.go()
			except Exception, e:
				if retryCount < retries:
					retryCount += 1
					continue
				else:
					title = "ERROR"
					msg = "ERROR: Error in communicating with phase computer. Try Again?"
					if self.popRetryBox(title, msg) == wx.ID_NO:
						return False
					else:
						retryCount = 0
			try:
				focus = self.phaseStation.getFocus()
				tiltZernike = self.phaseStation.getTiltZernike()
				tipZernike = self.phaseStation.getTipZernike()
				"""
				title = "Are these values ok?"
				msg = "INFO: Measured these values: \nFocus Term: %0.7f (waves of Sidel Focus).\nTilt Term: %0.7f (waves). \nTip Term: %0.7f (waves). \n\n Press <OK> to accept; <CANCEL> to re-measure.\n" % (focus, tiltZernike, tipZernike)
				if self.popInfoBox(title, msg) == wx.ID_OK:
					again = False
				"""
				again = False
			except Exception, e:
				title = "ERROR in getFocusTerm()"
				msg = "ERROR: Error in retrieving report from phase station computer!"
				self.popErrorBox(title, msg)
				return False
				
		return True
			
	# showMeasurementTitle		(NEED TO FIX Layout() issue)
	# @Purpose:
	#	Setup and display measurement title; and setup grids
	# @Inputs:
	#	isFCMeasure = True if it's focus corrected measurements; False if it's normal measurement
	def showMeasurementTitle(self, isFCMeasure):
		if isFCMeasure:
			title = "Focus Corrected Radius:"
		else:
			title = "Radius of Curvature:"
		self.staticTextMeasurementsRadiusTitle = wx.StaticText( self.panelScrolled, wx.ID_ANY, title, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasurementsRadiusTitle.Wrap( -1 )
		self.staticTextMeasurementsRadiusTitle.SetFont( wx.Font( 9, 70, 90, 92, True, wx.EmptyString ) )
		
		self.bSizerMeasurements.Add( self.staticTextMeasurementsRadiusTitle, 0, wx.ALL, 5 )
		
		##### Grid for measurements
		labels = ["Measurement #", "Radius (mm)",
				"CC Focus (wv 633)", "FC CC DMI (mm)",
				"CE Focus (wv 633)", "FC CE DMI (mm)", 
				"Remove?"]
		dataTypes = [gridlib.GRID_VALUE_NUMBER, gridlib.GRID_VALUE_FLOAT + ':6,6', 
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6',
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6',
					gridlib.GRID_VALUE_BOOL]
		data = [[0, 0.0, 0.0, 0.0, 0.0, 0.0, False]]
		self.gridMeasurements = CustomDataGrid(self.panelScrolled, labels, dataTypes, data)
		
		self.gridMeasurements.EnableEditing( True )
		self.gridMeasurements.EnableGridLines( True )
		self.gridMeasurements.EnableDragGridSize( False )
		self.gridMeasurements.SetMargins( 0, 0 )
		
		# setup only editable column is "remove?"
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly(True)
		for col in range(self.gridMeasurements.GetNumberCols()):
			if col != self.gridMeasurements.GetNumberCols() - 1:
				self.gridMeasurements.SetColAttr(col, attr)
		
		# Columns
		self.gridMeasurements.AutoSizeColumns()
		self.gridMeasurements.EnableDragColMove( False )
		self.gridMeasurements.EnableDragColSize( True )
		self.gridMeasurements.SetColLabelSize( 30 )
		
		# Rows
		self.gridMeasurements.AutoSizeRows()
		self.gridMeasurements.EnableDragRowSize( True )
		self.gridMeasurements.SetRowLabelSize( 0 )
		
		# Label Appearance
		self.gridMeasurements.SetLabelBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
				
		# Cell Defaults
		self.gridMeasurements.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.gridMeasurements.SetDefaultCellAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
		self.bSizerMeasurements.Add( self.gridMeasurements, 0, wx.ALL, 0 )
		
		### Separate line 1
		self.staticlineMeasurements1 = wx.StaticLine( self.panelScrolled, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		self.bSizerMeasurements.Add( self.staticlineMeasurements1, 0, wx.EXPAND |wx.ALL, 5 )
		
		##### Grid for average stats
		labels = ["Measurement #", "Radius (mm)",
				"CC Focus (wv 633)", "FC CC DMI (mm)",
				"CE Focus (wv 633)", "FC CE DMI (mm)"]
		dataTypes = [gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT + ':6,6', 
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6',
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6']
		data = [["Avg.", 0.0, 0.0, 0.0, 0.0, 0.0],
				["Stdev", 0.0, 0.0, 0.0, 0.0, 0.0],
				["Stdev (wv)", 0.0, 0.0, 0.0, 0.0, 0.0]]
		self.gridMeasurementsStats = CustomDataGrid(self.panelScrolled, labels, dataTypes, data)
		
		self.gridMeasurementsStats.EnableEditing( False )
		self.gridMeasurementsStats.EnableGridLines( True )
		self.gridMeasurementsStats.EnableDragGridSize( False )
		self.gridMeasurementsStats.SetMargins( 0, 0 )
		
		# Columns
		self.gridMeasurementsStats.AutoSizeColumns()
		self.gridMeasurementsStats.EnableDragColMove( False )
		self.gridMeasurementsStats.EnableDragColSize( True )
		self.gridMeasurementsStats.SetColLabelSize( 0 )
		
		# Rows
		self.gridMeasurementsStats.AutoSizeRows()
		self.gridMeasurementsStats.EnableDragRowSize( True )
		self.gridMeasurementsStats.SetRowLabelSize( 0 )
		
		# Label Appearance
		self.gridMeasurementsStats.SetLabelBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		
		# Cell Defaults
		self.gridMeasurementsStats.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.gridMeasurementsStats.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.bSizerMeasurements.Add( self.gridMeasurementsStats, 0, wx.ALL, 0 )
		
		### Separate line 2
		self.staticlineMeasurements2 = wx.StaticLine( self.panelScrolled, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		self.bSizerMeasurements.Add( self.staticlineMeasurements2, 0, wx.EXPAND |wx.ALL, 5 )
		
		### Variation title
		self.staticTextMeasurementsVariationTitle = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Variation From Average:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasurementsVariationTitle.Wrap( -1 )
		self.staticTextMeasurementsVariationTitle.SetFont( wx.Font( 9, 70, 90, 92, True, wx.EmptyString ) )
		
		self.bSizerMeasurements.Add( self.staticTextMeasurementsVariationTitle, 0, wx.ALL, 5 )
		
		##### Grid for Variations
		labels = ["Measurement #", "Radius (mm)", "Radius (wv 633)",
				"FC CC DMI (mm)", "FC CC DMI (wv 633)",
				"FC CE DMI (mm)", "FC CE DMI (wv 633)"]
		dataTypes = [gridlib.GRID_VALUE_NUMBER, gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6',
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6',
					gridlib.GRID_VALUE_FLOAT + ':6,6', gridlib.GRID_VALUE_FLOAT + ':6,6']
		data = [[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
		self.gridMeasurementsVariations = CustomDataGrid(self.panelScrolled, labels, dataTypes, data)
		
		self.gridMeasurementsVariations.EnableEditing( False )
		self.gridMeasurementsVariations.EnableGridLines( True )
		self.gridMeasurementsVariations.EnableDragGridSize( False )
		self.gridMeasurementsVariations.SetMargins( 0, 0 )
		
		# Columns
		self.gridMeasurementsVariations.AutoSizeColumns()
		self.gridMeasurementsVariations.EnableDragColMove( False )
		self.gridMeasurementsVariations.EnableDragColSize( True )
		self.gridMeasurementsVariations.SetColLabelSize( 30 )
		
		# Rows
		self.gridMeasurementsVariations.AutoSizeRows()
		self.gridMeasurementsVariations.EnableDragRowSize( True )
		self.gridMeasurementsVariations.SetRowLabelSize( 0 )
		
		# Label Appearance
		self.gridMeasurementsVariations.SetLabelBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		
		# Cell Defaults
		self.gridMeasurementsVariations.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.gridMeasurementsVariations.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.bSizerMeasurements.Add( self.gridMeasurementsVariations, 0, wx.ALL, 5 )
		
		# displaying average in (mm) and (inch)
		bSizerMeasurementsAverage = wx.BoxSizer( wx.HORIZONTAL )
		self.bSizerMeasurementsAverage = bSizerMeasurementsAverage
		
		self.staticTextMeasurementsAverageTitle = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"Average Radius:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasurementsAverageTitle.Wrap( -1 )
		self.staticTextMeasurementsAverageTitle.SetFont( wx.Font( 12, 70, 90, 92, True, wx.EmptyString ) )
		
		bSizerMeasurementsAverage.Add( self.staticTextMeasurementsAverageTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlMeasurementsAverageValueMM = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		self.textCtrlMeasurementsAverageValueMM.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerMeasurementsAverage.Add( self.textCtrlMeasurementsAverageValueMM, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextMeasurementsAverageUnitMM = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"(mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasurementsAverageUnitMM.Wrap( -1 )
		self.staticTextMeasurementsAverageUnitMM.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerMeasurementsAverage.Add( self.staticTextMeasurementsAverageUnitMM, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlMeasurementsAverageValueInch = wx.TextCtrl( self.panelScrolled, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
		self.textCtrlMeasurementsAverageValueInch.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerMeasurementsAverage.Add( self.textCtrlMeasurementsAverageValueInch, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextMeasurementsAverageUnitInch = wx.StaticText( self.panelScrolled, wx.ID_ANY, u"(inch)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMeasurementsAverageUnitInch.Wrap( -1 )
		self.staticTextMeasurementsAverageUnitInch.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerMeasurementsAverage.Add( self.staticTextMeasurementsAverageUnitInch, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.bSizerMeasurements.Add( bSizerMeasurementsAverage, 1, wx.EXPAND, 5 )
		
		self.refreshResultsGrids()
	
	# refreshResultsGrids
	#
	def refreshResultsGrids(self):
		self.bSizerMeasurements.Layout()
		self.panelScrolled.SetupScrolling()
		widget = self.panelScrolled
		widget.Layout()
		widget.Refresh()
		while widget.GetParent():
			widget = widget.GetParent()
			widget.Layout()
			widget.Refresh()
			if widget.IsTopLevel():
				break
	
	# showMeasurement
	# @Purpose:
	#	Show a measurement with measurement # from the memory
	def showMeasurement(self, meas_num):	
		# display the data in the measurement grid
		self.gridMeasurements.SetCellValue(meas_num, 0, long(meas_num))
		self.gridMeasurements.SetCellValue(meas_num, 1, self.gFC_Rad[meas_num])
		self.gridMeasurements.SetCellValue(meas_num, 2, self.gCC_Foc[meas_num])
		self.gridMeasurements.SetCellValue(meas_num, 3, self.gFC_CCDMI[meas_num])
		self.gridMeasurements.SetCellValue(meas_num, 4, self.gCE_Foc[meas_num])
		self.gridMeasurements.SetCellValue(meas_num, 5, self.gFC_CEDMI[meas_num])
		# display stats and variation
		self.updateMeasurementStatsVariation()
		self.refreshResultsGrids()
		
	# updateMeasurementStatsVariation
	# @Purpose:
	#	update the grid display for measurement stats and variation
	def updateMeasurementStatsVariation(self):
		valid_FCRad = []
		valid_CCFoc = []
		valid_CCDMI = []
		valid_CEFoc = []
		valid_CEDMI = []
		# setup for valid data...
		for i in range(len(self.gFC_Rad)):
			if self.gFC_Rad[i] != None:
				valid_FCRad.append(self.gFC_Rad[i])
				valid_CCFoc.append(self.gCC_Foc[i])
				valid_CCDMI.append(self.gFC_CCDMI[i])
				valid_CEFoc.append(self.gCE_Foc[i])
				valid_CEDMI.append(self.gFC_CEDMI[i])
		
		# display statistics
		if len(valid_FCRad) > 0:
			# average
			self.gridMeasurementsStats.SetCellValue(0, 1, numpy.average(valid_FCRad))
			self.gridMeasurementsStats.SetCellValue(0, 2, numpy.average(valid_CCFoc))
			self.gridMeasurementsStats.SetCellValue(0, 3, numpy.average(valid_CCDMI))
			self.gridMeasurementsStats.SetCellValue(0, 4, numpy.average(valid_CEFoc))
			self.gridMeasurementsStats.SetCellValue(0, 5, numpy.average(valid_CEDMI))
			# std
			self.gridMeasurementsStats.SetCellValue(1, 1, numpy.std(valid_FCRad))
			self.gridMeasurementsStats.SetCellValue(1, 2, numpy.std(valid_CCFoc))
			self.gridMeasurementsStats.SetCellValue(1, 3, numpy.std(valid_CCDMI))
			self.gridMeasurementsStats.SetCellValue(1, 4, numpy.std(valid_CEFoc))
			self.gridMeasurementsStats.SetCellValue(1, 5, numpy.std(valid_CEDMI))
			if self.staticTextMeasurementsRadiusTitle.GetLabel() == "Focus Corrected Radius:" and self.gDMI_Wave != 0:		# FC measurements
				# std (wv)
				self.gridMeasurementsStats.SetCellValue(2, 1, numpy.std(valid_FCRad)/self.gDMI_Wave)
				self.gridMeasurementsStats.SetCellValue(2, 3, numpy.std(valid_CCDMI)/self.gDMI_Wave)
				self.gridMeasurementsStats.SetCellValue(2, 5, numpy.std(valid_CEDMI)/self.gDMI_Wave)
			else:
				self.gridMeasurementsStats.SetCellValue(2, 1, 0.0)
				self.gridMeasurementsStats.SetCellValue(2, 3, 0.0)
				self.gridMeasurementsStats.SetCellValue(2, 5, 0.0)
			# display the average radius in different units
			self.textCtrlMeasurementsAverageValueMM.SetValue("%0.6f" % numpy.average(valid_FCRad))
			self.textCtrlMeasurementsAverageValueInch.SetValue("%0.6f" % (numpy.average(valid_FCRad) / 25.4))
		else:
			# average
			self.gridMeasurementsStats.SetCellValue(0, 1, 0.0)
			self.gridMeasurementsStats.SetCellValue(0, 2, 0.0)
			self.gridMeasurementsStats.SetCellValue(0, 3, 0.0)
			self.gridMeasurementsStats.SetCellValue(0, 4, 0.0)
			self.gridMeasurementsStats.SetCellValue(0, 5, 0.0)
			# std
			self.gridMeasurementsStats.SetCellValue(1, 1, 0.0)
			self.gridMeasurementsStats.SetCellValue(1, 2, 0.0)
			self.gridMeasurementsStats.SetCellValue(1, 3, 0.0)
			self.gridMeasurementsStats.SetCellValue(1, 4, 0.0)
			self.gridMeasurementsStats.SetCellValue(1, 5, 0.0)
			# std (wv)
			self.gridMeasurementsStats.SetCellValue(2, 1, 0.0)
			self.gridMeasurementsStats.SetCellValue(2, 3, 0.0)
			self.gridMeasurementsStats.SetCellValue(2, 5, 0.0)
			# display the average radius in different units
			self.textCtrlMeasurementsAverageValueMM.SetValue("%0.6f" % 0.0)
			self.textCtrlMeasurementsAverageValueInch.SetValue("%0.6f" % 0.0)
		# display the variations
		for meas_num in range(self.gridMeasurements.GetNumberRows()):
			if self.gFC_Rad[meas_num] == None:		# removed row
				attr = gridlib.GridCellAttr()
				attr.SetBackgroundColour('BLACK')
				attr.SetTextColour('DARK GREY')
				self.gridMeasurementsVariations.SetRowAttr(meas_num, attr)
			else:
				attr = gridlib.GridCellAttr()
				attr.SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ))
				attr.SetTextColour('BLACK')
				self.gridMeasurementsVariations.SetRowAttr(meas_num, attr)
				d_fcrad = 0.0
				d_ccdmi = 0.0
				d_cedmi = 0.0
				if self.staticTextMeasurementsRadiusTitle.GetLabel() == "Focus Corrected Radius:" and self.gDMI_Wave != 0:		# FC measurements
					d_fcrad = (self.gFC_Rad[meas_num] - numpy.average(valid_FCRad)) / self.gDMI_Wave
					d_ccdmi = (self.gFC_CCDMI[meas_num] - numpy.average(valid_CCDMI)) / self.gDMI_Wave
					d_cedmi = (self.gFC_CEDMI[meas_num] - numpy.average(valid_CEDMI)) / self.gDMI_Wave
				self.gridMeasurementsVariations.SetCellValue(meas_num, 0, long(meas_num))
				self.gridMeasurementsVariations.SetCellValue(meas_num, 1, self.gFC_Rad[meas_num] - numpy.average(valid_FCRad))
				self.gridMeasurementsVariations.SetCellValue(meas_num, 2, d_fcrad)
				self.gridMeasurementsVariations.SetCellValue(meas_num, 3, self.gFC_CCDMI[meas_num] - numpy.average(valid_CCDMI))
				self.gridMeasurementsVariations.SetCellValue(meas_num, 4, d_ccdmi)
				self.gridMeasurementsVariations.SetCellValue(meas_num, 5, self.gFC_CEDMI[meas_num] - numpy.average(valid_CEDMI))
				self.gridMeasurementsVariations.SetCellValue(meas_num, 6, d_cedmi)
				
		# compute CTE compensation
		if self.cmdParams.part_info.cte != 0.0 and self.cmdParams.part_info.target_temp != 0.0:
			self.sCTE_Cmp_Rad = numpy.average(valid_FCRad) * \
							(1.0 + self.cmdParams.part_info.cte * \
							(self.cmdParams.part_info.target_temp - self.weatherStation.partTemperature))
		else:
			self.sCTE_Cmp_Rad = 0.0
	
	# deleteMeasurements
	# @Purpose:
	#	Delete existing displayed results
	def deleteMeasurements(self):
		try:
			# delete the titles
			numMeasurementsItems = range(len(self.bSizerMeasurements.GetChildren()))
			numMeasurementsItems.reverse()
			for i in numMeasurementsItems:
				self.bSizerMeasurements.Remove(i)
			
			self.staticTextMeasurementsRadiusTitle.Destroy()
			self.gridMeasurements.Destroy()
			self.staticlineMeasurements1.Destroy()
			self.gridMeasurementsStats.Destroy()
			self.staticlineMeasurements2.Destroy()
			self.staticTextMeasurementsVariationTitle.Destroy()
			self.gridMeasurementsVariations.Destroy()
			self.staticTextMeasurementsAverageTitle.Destroy()
			self.textCtrlMeasurementsAverageValueMM.Destroy()
			self.staticTextMeasurementsAverageUnitMM.Destroy()
			self.textCtrlMeasurementsAverageValueInch.Destroy()
			self.staticTextMeasurementsAverageUnitInch.Destroy()
			
			# reset all measured values
			self.gDMI_rd = [None for i in range(2*self.max_meas)]		# 20 entries place holder
			self.gFocus_Zrn = [None for i in range(2*self.max_meas)]	# 20 entries place holder
			self.gFC_Rad = [None for i in range(self.max_meas)]			# 10 entries place holder
			self.gFC_CCDMI = [None for i in range(self.max_meas)]		# 10 entries place holder
			self.gFC_CEDMI = [None for i in range(self.max_meas)]		# 10 entries place holder
			self.gCC_Foc = [None for i in range(self.max_meas)]			# 10 entries place holder
			self.gCE_Foc = [None for i in range(self.max_meas)]			# 10 entries place holder
		except AttributeError, e:
			if self.debug:
				self.printBuffer.writePrintOutFlush(traceback.format_exc())
			pass					# do nothing if no need to delete!
			
		# refresh the panel after delete...
		self.refreshResultsGrids()
	
	# setDMIStatus
	# @Purpose:
	#	Set the DMI status message
	# @Inputs:
	#	dmistatus: 
	#		'ERROR' - RED text
	#		'WARNING' - ORANGE text
	#		'READING' - YELLOW text
	#		'A-OK' - GREEN text
	def setDMIStatus(self, dmistatus):
		if dmistatus == 'ERROR':
			self.staticTextStatusContent.SetLabel("ERROR")
			self.staticTextStatusContent.SetForegroundColour('RED')
		elif dmistatus == 'WARNING':
			self.staticTextStatusContent.SetLabel("WARNING")
			self.staticTextStatusContent.SetForegroundColour('ORANGE')
		elif dmistatus == 'READING':
			self.staticTextStatusContent.SetLabel("READING")
			self.staticTextStatusContent.SetForegroundColour('YELLOW')
		else:			# OK
			self.staticTextStatusContent.SetLabel("A-OK")
			self.staticTextStatusContent.SetForegroundColour('GREEN')
		
		widget = self.staticTextStatusContent
		while widget != None:
			widget.Layout()
			widget.Update()
			if widget == self.panelScrolled:
				widget.SetupScrolling()
			widget = widget.GetParent()

	# setWeatherStationStatus:
	# @Purpose:
	#	probe and set the weather station status
	def setWeatherStationStatus(self):
		if self.weatherStation.isConnected:
			self.staticTextWeatherStationStatus.SetLabel("OK")
			self.staticTextWeatherStationStatus.SetForegroundColour('GREEN')
			if not self.ws_timer.IsRunning():			# start the weather station timer if it stopped
				self.ws_timer.Start(300000)
		else:
			self.staticTextWeatherStationStatus.SetLabel("Offline")
			self.staticTextWeatherStationStatus.SetForegroundColour('RED')
			if self.ws_timer.IsRunning():				# stop the weather station timer if it started
				self.ws_timer.Stop()

	
	# popErrorBox:
	# @Purpose:
	#   pop up Error Box with set title and message
	def popErrorBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_ERROR)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
	
	# popAlertBox:
	# @Purpose:
	#   pop up Warning Box with set title and message
	def popAlertBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_WARNING)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

	# popInfoBox:
	# @Purpose:
	#   pop up Information Box with set title and message
	def popInfoBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked
	
	# popInfoOKBox:
	# @Purpose:
	#   pop up Information Box with set title and message (only OK button)
	def popInfoOKBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_INFORMATION)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

	# popYesNoBox:
	# @Purpose:
	#	pop an Yes / No Box with title and message
	def popYesNoBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.YES | wx.NO | wx.ICON_INFORMATION)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked
	
	# popRetryBox:
	# @Purpose:
	#	pop up a Retry Box with title and message
	def popRetryBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.YES | wx.NO | wx.ICON_ERROR)
		clicked = dlg.ShowModal()
		dlg.Destroy()
		return clicked


