#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
env_plots2.py
	This program (env_plots2) runs a graph display with control for different environment data
Usage:
	$> python env_database.env_plots2.env_plots2
Author:
	Charlie Chen <cchen@zygo.com>
"""

import ConfigParser
import datetime
import os
import matplotlib
import matplotlib.lines
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from optparse import OptionParser
import platform
import re
import time
import wx
import wx.aui
from wx.lib.scrolledpanel import ScrolledPanel
from wx_extensions.statusbar import StatusBarGauge
from wx_extensions.windows import FrameBase

import env_database
from env_database.envdb import EnvDB
from env_database.env_plots2.controls import PanelControlContents
import env_database.env_plots2
PROGRAM_VERSION = env_database.env_plots2.__version__


###########################################################################
## Class FrameMain
###########################################################################

class FrameMain ( FrameBase ):
	
	def __init__( self, parent, newSession, config="env_plots2_last_config.cfg" ):
		if re.search('Windows', platform.architecture()[1]):
			os_tmp_dir = "C:/temp/"
		elif re.search('ELF', platform.architecture()[1]):
			os_tmp_dir = "/tmp/"

		self.baseDir = os.path.dirname(env_database.env_plots2.__file__)+"/"
		if config != "env_plots2_last_config.cfg":				# non-default config
			self.lastConfig = config
		else:
			self.lastConfig = os_tmp_dir + config
		newSession = newSession or (not os.path.exists(self.lastConfig))		# setup new session if the last config doesn't exist.
	
		FrameBase.__init__ ( self, parent, id = wx.ID_ANY, title = u"EnvPlots2", pos = wx.DefaultPosition, size = wx.Size( 1600,900 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.menubarMain = wx.MenuBar( 0 )
		self.menuConfigurationMain = wx.Menu()
		self.menuItemNewConfiguration = wx.MenuItem( self.menuConfigurationMain, wx.ID_ANY, u"New Configuration", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuConfigurationMain.AppendItem( self.menuItemNewConfiguration )
		
		self.menuItemLoadConfiguration = wx.MenuItem( self.menuConfigurationMain, wx.NewId(), u"Load Configuration...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuConfigurationMain.AppendItem( self.menuItemLoadConfiguration )
		
		self.menuItemSaveConfiguration = wx.MenuItem( self.menuConfigurationMain, wx.NewId(), u"Save Configuration...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuConfigurationMain.AppendItem( self.menuItemSaveConfiguration )
		
		self.menubarMain.Append( self.menuConfigurationMain, u"Configurations" ) 
		
		self.menuAboutMain = wx.Menu()
		self.menuItemAbout = wx.MenuItem( self.menuAboutMain, wx.NewId(), u"About...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuAboutMain.AppendItem( self.menuItemAbout )
		
		self.menubarMain.Append( self.menuAboutMain, u"About" ) 
		
		self.SetMenuBar( self.menubarMain )
		
		self.statusBarMain = StatusBarGauge(self)
		self.SetStatusBar(self.statusBarMain)
		bSizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.splitterWindowMain = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL )
		self.splitterWindowMain.SetMinimumPaneSize( 50 )
		
		self.panelFigures = wx.Panel( self.splitterWindowMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,  wx.TAB_TRAVERSAL )
		bSizerPanelFigures = wx.BoxSizer( wx.VERTICAL )
		
		self.auinotebookFigures = wx.aui.AuiNotebook( self.panelFigures, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_TOP|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TAB_MOVE|wx.aui.AUI_NB_SCROLL_BUTTONS  )
		self.panelTemperature = wx.Panel( self.auinotebookFigures, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPanelTemperature = wx.BoxSizer( wx.VERTICAL )
		
		### setup canvas display (Temperature)
		self.figureTemperature = Figure()
		self.axesTemperature = self.figureTemperature.add_subplot(111)
		self.axesTemperature.grid(color='gray', linestyle='dashed')
		
		self.canvasTemperature = FigureCanvas(self.panelTemperature, wx.ID_ANY, self.figureTemperature)
		
		bSizerPanelTemperature.Add(self.canvasTemperature, 1, wx.LEFT | wx.TOP | wx.EXPAND, 0)
		
		self.toolbarTemperature = NavigationToolbar2Wx(self.canvasTemperature)
		self.toolbarTemperature.Realize()
		bSizerPanelTemperature.Add(self.toolbarTemperature, 0, wx.LEFT | wx.EXPAND, 0)
		self.toolbarTemperature.Show()
		### end setup canvas display
		
		self.panelTemperature.SetSizer( bSizerPanelTemperature )
		self.panelTemperature.Layout()
		bSizerPanelTemperature.Fit( self.panelTemperature )
		self.auinotebookFigures.AddPage( self.panelTemperature, u"Temperature", True, wx.NullBitmap )
		
		self.panelPressureHumidity = wx.Panel( self.auinotebookFigures, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPanelPressureHumidity = wx.BoxSizer( wx.VERTICAL )
		
		### setup canvas display (Pressure & Humidity)
		self.figurePressureHumidity = Figure()
		self.axesPressureHumidity = self.figurePressureHumidity.add_subplot(111)
		self.axesPressureHumidity.grid(color='gray', linestyle='dashed')
		
		self.canvasPressureHumidity = FigureCanvas(self.panelPressureHumidity, wx.ID_ANY, self.figurePressureHumidity)
		
		bSizerPanelPressureHumidity.Add(self.canvasPressureHumidity, 1, wx.LEFT | wx.TOP | wx.EXPAND, 0)
		
		self.toolbarPressureHumidity = NavigationToolbar2Wx(self.canvasPressureHumidity)
		self.toolbarPressureHumidity.Realize()
		bSizerPanelPressureHumidity.Add(self.toolbarPressureHumidity, 0, wx.LEFT | wx.EXPAND, 0)
		self.toolbarPressureHumidity.Show()
		### end setup canvas display
		
		self.panelPressureHumidity.SetSizer( bSizerPanelPressureHumidity )
		self.panelPressureHumidity.Layout()
		bSizerPanelPressureHumidity.Fit( self.panelPressureHumidity )
		self.auinotebookFigures.AddPage( self.panelPressureHumidity, u"Pressure & Humidity", False, wx.NullBitmap )
		
		bSizerPanelFigures.Add( self.auinotebookFigures, 1, wx.EXPAND |wx.ALL, 0 )
		
		self.panelFigures.SetSizer( bSizerPanelFigures )
		self.panelFigures.Layout()
		bSizerPanelFigures.Fit( self.panelFigures )
		
		# setup control panel
		self.controlPanel = wx.CollapsiblePane(self.splitterWindowMain, label="Show Control Panel", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.onControlPanelChanged, self.controlPanel)
		self.controlPanelContents = None
		# pre-load the last config (if there is any)
		if newSession:
			self.makeControlPanelContent(self.controlPanel.GetPane())
		else:
			self.loadConfig(self.lastConfig)
		
		self.splitterWindowMain.SplitHorizontally( self.panelFigures, self.controlPanel, -1 )
		bSizerMain.Add( self.splitterWindowMain, 1, wx.EXPAND, 0 )
		
		self.SetSizer( bSizerMain )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.onClose )
		self.Bind( wx.EVT_MENU, self.onNewConfiguration, id = self.menuItemNewConfiguration.GetId() )
		self.Bind( wx.EVT_MENU, self.onLoadConfiguration, id = self.menuItemLoadConfiguration.GetId() )
		self.Bind( wx.EVT_MENU, self.onSaveConfiguration, id = self.menuItemSaveConfiguration.GetId() )
		self.Bind( wx.EVT_MENU, self.onAbout, id = self.menuItemAbout.GetId() )
		
		# Setup Icon
		self.SetIcon(wx.Icon(self.baseDir+"icons/sensor32x32.jpg", wx.BITMAP_TYPE_JPEG, 32, 32))
	
	def __del__( self ):
		pass
		
	# plot:
	# @Purpose:
	#	update the plot figure from the control panel.
	# @Inputs:
	#	probesMap = dictionary:
	#				key = ID (from control panel)
	#				value = (probeName, probeAlias, lineColor)
	#	startTime = None or String
	#	endTime = None or String
	def plot(self, probesMap, startTime, endTime):
		# clear the figure
		probeLinesListTemp = []
		probeLabelAndLastValueTemp = []
		probeLinesListPH = []
		probeLabelAndLastValuePH = []
		self.figureTemperature.clear()
		self.axesTemperature = self.figureTemperature.add_subplot(111)
		self.axesTemperature.grid(b=True, which='major', color='gray', linestyle='dashed')
		self.figurePressureHumidity.clear()
		self.axesPressureHumidity = self.figurePressureHumidity.add_subplot(111)
		self.axesPressureHumidity.grid(b=True, which='major', color='gray', linestyle='dashed')
		axesHumidity = None
		timeformat = "%Y-%m-%d %H:%M:%S"
		db = EnvDB()
		havePlottedTemp = False
		havePlottedPH = False
		
		for pID in probesMap.keys():
			############################ NEW DB FORMAT ##############################
			# results = db.getProbeValues([(probesMap[pID][0], probesMap[pID][1])], startTime, endTime)
			############################ NEW DB FORMAT ##############################
			
			############################ OLD DB FORMAT ##############################
			results = db.getProbeValues([(probesMap[pID][0], "*")], startTime, endTime)
			############################ OLD DB FORMAT ##############################
			if len(results) == 0:		# no results to plot
				continue

			xmin = matplotlib.dates.date2num(datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S'))
			xmax = matplotlib.dates.date2num(datetime.datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S'))		
			xdates = matplotlib.dates.date2num([i[1] for i in results])
			ydata = [i[2] for i in results]
			del results
			
			if probesMap[pID][0].startswith('P') or probesMap[pID][0].startswith('H'):
				havePlottedPH = True
				self.figurePressureHumidity.autofmt_xdate(bottom=0.18)				##### autofmt_xdate needs to be BEFORE twinx()!!!!! #####
				
				if probesMap[pID][0].startswith('P'):
					# comma required (make a tuple) for setting up legends
					l, = self.axesPressureHumidity.plot_date(xdates, ydata, marker='', linestyle='-', label=probesMap[pID][1], color=probesMap[pID][2])
					self.axesPressureHumidity.set_xlim(xmin, xmax)
				else:
					if axesHumidity == None:
						axesHumidity = self.axesPressureHumidity.twinx()
					# comma required (make a tuple) for setting up legends
					l, = axesHumidity.plot_date(xdates, ydata, marker='', linestyle='-', label=probesMap[pID][1], color=probesMap[pID][2])
					axesHumidity.set_xlim(xmin, xmax)
				probeLinesListPH.append(l)
				# probeLinesListPH.append(matplotlib.lines.Line2D([], [], color='white'))			# fake white line for display current temperature row
				probeLabelAndLastValuePH.append(probesMap[pID][1]+": "+str(ydata[-1]))				# make it single line label with value
				# probeLabelAndLastValuePH.append('End Pt: '+str(ydata[-1]))
			else:
				havePlottedTemp = True
				self.figureTemperature.autofmt_xdate(bottom=0.18)
				# comma required (make a tuple) for setting up legends
				l, = self.axesTemperature.plot_date(xdates, ydata, marker='', linestyle='-', label=probesMap[pID][1], color=probesMap[pID][2])
				self.axesTemperature.set_xlim(xmin, xmax)
				probeLinesListTemp.append(l)
				# probeLinesListTemp.append(matplotlib.lines.Line2D([], [], color='white'))			# fake white line for display current temperature row
				probeLabelAndLastValueTemp.append(probesMap[pID][1]+": "+str(ydata[-1]))			# make it single line label with value
				# probeLabelAndLastValueTemp.append('End Pt: '+str(ydata[-1]))
		
		if havePlottedPH:
			self.axesPressureHumidity.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
			self.axesPressureHumidity.legend(tuple(probeLinesListPH), tuple(probeLabelAndLastValuePH), loc='best')
			self.axesPressureHumidity.xaxis.set_label_text("Start Time: "+startTime+", End Time: "+endTime)
			self.axesPressureHumidity.yaxis.set_label_text("Pressure (mmHg)")
			if axesHumidity != None:
				axesHumidity.yaxis.set_label_text("Humidity (%)")
				axesHumidity.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
		
		if havePlottedTemp:
			self.axesTemperature.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
			#self.figureTemperature.legend(tuple(probeLinesList), tuple([probesMap[p][1] for p in probesMap.keys()]), loc='upper right')
			box = self.axesTemperature.get_position()
			self.axesTemperature.set_position([box.x0, box.y0, box.width*0.9, box.height])
			self.axesTemperature.legend(tuple(probeLinesListTemp), tuple(probeLabelAndLastValueTemp), loc='center left', bbox_to_anchor=(1.005,0.5), borderaxespad=0.)
			self.axesTemperature.xaxis.set_label_text("Start Time: "+startTime+", End Time: "+endTime)
			self.axesTemperature.yaxis.set_label_text("Temperature (Degree C)")
			
		self.refreshWidget(self.canvasPressureHumidity)
		self.refreshWidget(self.canvasTemperature)
	
	# loadConfig
	def loadConfig(self, file):
		config = ConfigParser.ConfigParser()
		config.read(file)
		if config.get('common', 'program') != 'env_plots2':
			self.popErrorBox('ERROR', 'ERROR: try to load a non-env_plots2 config file!')
			return
		# reset saved windows size:
		if config.has_option('common', 'width') and config.has_option('common', 'height'):
			self.SetSize(wx.Size(int(config.get('common', 'width')), int(config.get('common', 'height'))))
		
		# reset the control panel:
		if self.controlPanelContents != None:
			self.controlPanelContents.Destroy()
		self.makeControlPanelContent(self.controlPanel.GetPane())
		controlPanel = self.controlPanelContents
		# parse probes
		for opt in config.options('probes'):
			(group, alias, color) = config.get('probes', opt).split(',')
			controlPanel.onAddProbe(None, int(opt[1:]), group, alias, color)
		# parse time_range
		controlPanel.checkBoxStartTime.SetValue(eval(config.get('time_range', 'use_start_time')))
		controlPanel.textCtrlStartTime.SetValue(config.get('time_range', 'start_time'))
		controlPanel.checkBoxEarliest.SetValue(eval(config.get('time_range', 'use_earliest_time')))
		controlPanel.checkBoxEndTime.SetValue(eval(config.get('time_range', 'use_end_time')))
		controlPanel.textCtrlEndTime.SetValue(config.get('time_range', 'end_time'))
		controlPanel.checkBoxCurrent.SetValue(eval(config.get('time_range', 'use_current_time')))
		# parse duration
		controlPanel.textCtrlDays.SetValue(config.get('duration', 'days'))
		controlPanel.textCtrlHours.SetValue(config.get('duration', 'hours'))
		controlPanel.textCtrlMinutes.SetValue(config.get('duration', 'minutes'))
		# parse auto_update
		controlPanel.checkBoxUpdate.SetValue(eval(config.get('auto_update', 'enable')))
		controlPanel.textCtrlHoursUpdate.SetValue(config.get('auto_update', 'hours'))
		controlPanel.textCtrlMinutesUpdate.SetValue(config.get('auto_update', 'minutes'))
		controlPanel.onCheckAutoUpdate(None)
		
		# plot the loaded configurations
		controlPanel.onPlot(None)
	
	# saveConfig
	def saveConfig(self, file):
		controlPanel = self.controlPanelContents
		config = ConfigParser.ConfigParser()
		# section: common
		config.add_section('common')
		config.set('common', 'program', 'env_plots2')
		config.set('common', 'width', str(self.GetSizeTuple()[0]))
		config.set('common', 'height', str(self.GetSizeTuple()[1]))
		# section: probes
		config.add_section('probes')
		for probe in controlPanel.validProbeIDs.keys():
			(name, alias, color) = controlPanel.validProbeIDs[probe]
			exec("group = controlPanel.choiceGroup_"+str(probe)+".GetString(controlPanel.choiceGroup_"+str(probe)+".GetCurrentSelection())")
			config.set('probes', 'p'+str(probe), '%s,%s,%s' % (group, alias, color))
		# section: time_range
		config.add_section('time_range')
		config.set('time_range', 'use_start_time', str(controlPanel.checkBoxStartTime.GetValue()))
		config.set('time_range', 'start_time', controlPanel.textCtrlStartTime.GetValue())
		config.set('time_range', 'use_earliest_time', str(controlPanel.checkBoxEarliest.GetValue()))
		config.set('time_range', 'use_end_time', str(controlPanel.checkBoxEndTime.GetValue()))
		config.set('time_range', 'end_time', controlPanel.textCtrlEndTime.GetValue())
		config.set('time_range', 'use_current_time', str(controlPanel.checkBoxCurrent.GetValue()))
		# section: duration
		config.add_section('duration')
		config.set('duration', 'days', controlPanel.textCtrlDays.GetValue())
		config.set('duration', 'hours', controlPanel.textCtrlHours.GetValue())
		config.set('duration', 'minutes', controlPanel.textCtrlMinutes.GetValue())
		# section: auto_update
		config.add_section('auto_update')
		config.set('auto_update', 'enable', str(controlPanel.checkBoxUpdate.GetValue()))
		config.set('auto_update', 'hours', controlPanel.textCtrlHoursUpdate.GetValue())
		config.set('auto_update', 'minutes', controlPanel.textCtrlMinutesUpdate.GetValue())
		
		f = open(file, 'w')
		config.write(f)
		f.close()
	
	# control panel related
	def onControlPanelChanged(self, event=None):
		(w, h) = self.GetSizeTuple()
		self.refreshWidget(self.controlPanelContents)
		if self.controlPanel.IsExpanded():
			self.controlPanel.SetLabel("Hide Control Panel")
			self.splitterWindowMain.SetSashPosition(h - 300)
		else:
			self.controlPanel.SetLabel("Show Control Panel")
			self.splitterWindowMain.SetSashPosition(h)
		self.Layout()
			
	# makeControlPanelContent
	def makeControlPanelContent(self, panel):
		self.controlPanelContents = PanelControlContents(panel)
		
		bSizerBoarder = wx.BoxSizer()
		bSizerBoarder.Add(self.controlPanelContents, 1, wx.EXPAND | wx.ALL, 5)
		panel.SetSizer(bSizerBoarder)
		self.refreshWidget(panel)
		self.Layout()
	
	# Virtual event handlers, overide them in your derived class
	def onClose( self, event ):
		try:
			self.saveConfig(self.lastConfig)
		finally:
			self.Destroy()
		
	def onNewConfiguration( self, event ):
		# reset temperature plot
		self.figureTemperature.clear()
		self.axesTemperature = self.figureTemperature.add_subplot(111)
		self.axesTemperature.grid(color='gray', linestyle='dashed')
		self.refreshWidget(self.canvasTemperature)
		# reset pressure & humidity plot
		self.figurePressureHumidity.clear()
		self.axesPressureHumidity = self.figurePressureHumidity.add_subplot(111)
		self.axesPressureHumidity.grid(color='gray', linestyle='dashed')
		self.refreshWidget(self.canvasPressureHumidity)
		# reset control panel
		self.controlPanelContents.Destroy()
		self.makeControlPanelContent(self.controlPanel.GetPane())
	
	def onLoadConfiguration( self, event ):
		default_cfg_dir = os.getcwd()
		wildcard = "Environment Config File (*.cfg)|*.cfg|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", default_cfg_dir, "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetPath()
			self.loadConfig(file)
		dialog.Destroy()
	
	def onSaveConfiguration( self, event ):
		default_cfg_dir = os.getcwd()
		wildcard = "Environment Config File (*.cfg)|*.cfg|" \
					"All files (*.*)|*.*"
		dialog = wx.FileDialog(None, "Choose a file", default_cfg_dir, "", wildcard, wx.SAVE|wx.OVERWRITE_PROMPT)
		if dialog.ShowModal() == wx.ID_OK:
			file = dialog.GetPath()
			self.saveConfig(file)
		dialog.Destroy()
	
	def onAbout( self, event ):
		descriptions = \
"""
This Environment Plot Program gathers the environment data from the environment database, and then
plot the corresponding probes with corresponding time frame.
"""
		license = \
"""
(C) 2013 Zygo Corporation, all right reserved
"""
		info = wx.AboutDialogInfo()
		info.SetIcon(wx.Icon(self.baseDir+"icons/sensor.jpg", wx.BITMAP_TYPE_JPEG, 32, 32))
		info.SetName("Environment Plot Program")
		info.SetDescription(descriptions)
		info.SetLicense(license)
		info.SetVersion(PROGRAM_VERSION)
		info.SetCopyright(" (C) 2013 Zygo Corporation")
		info.SetWebSite("http://www.zygo.com")
		info.AddDeveloper("Charlie Chen <cchen@zygo.com>")
		info.AddDocWriter("Charlie Chen <cchen@zygo.com>")
		wx.AboutBox(info)	


# run
# @Purpose:
#	a python function for setting up the wxApp and this env_plots2 programs.
# @Inputs:
#	config = standard config file path
#	newSession = boolean flag indicating if it's a new session
def run(config="C:\\temp\\env_plots2_last_config.cfg", newSession=False):
	app = wx.PySimpleApp()
	frame = FrameMain(None, newSession, config)
	frame.Show(True)
	app.MainLoop()


# main function.	
if __name__ == "__main__":
	usage = "Usage: %prog [options] [config_file_path]"
	parser = OptionParser(usage=usage)
	parser.add_option("-n", "--new", dest="new",
						action="store_true",
						default=False,
						help="starting off a new session")
	(options, args) = parser.parse_args()
	
	app = wx.PySimpleApp()
	if len(args) > 0:
		frame = FrameMain(None, options.new, args[0])
	else:
		frame = FrameMain(None, options.new)
	frame.Show(True)
	app.MainLoop()
