# -*- coding: utf-8 -*- 
"""
control.py
	env_plots2 Environment Plots control panel classes
Author: Charlie Chen
"""

import array
import matplotlib.colors as matplotlibColors
import random
import re
import time
import traceback
import wx
import wx.combo
from wx_extensions.windows import ScrolledPanelBase
from env_database.envdb import EnvDB

###########################################################################
## Exception extensions
###########################################################################
class InvalidTimeException(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: InvalidTimeException; expression = %s; %s\n" % (repr(self.expr), self.msg)

###########################################################################
## decorators
###########################################################################
def handlesError(funct, *args):
	def wrapper(self, *args):
		try:
			funct(self, *args)
		except InvalidTimeException, e:
			msg = "ERROR: invalid input time format, please follow \'yyyy-mm-dd hh:MM:ss' in start time / end time OR enter valid numbers in durations."
			self.popErrorBox("ERROR", msg)
			print traceback.format_exc()
		except Exception, e:
			if funct.__name__ == "onCheckAutoUpdate":
				msg = "ERROR: cannot read input update intervals; make sure they are numbers"
				self.checkBoxUpdate.SetValue(False)
			else:
				msg = "ERROR: Exception thrown in %s()." % funct.__name__
			self.popErrorBox("ERROR", msg)
			print traceback.format_exc()
	return wrapper		
			

###########################################################################
## Class PanelControlContents
###########################################################################
class PanelControlContents ( ScrolledPanelBase ):
	
	def __init__( self, parent ):
		self.probesButtonMask = 999
		self.validProbeIDs = {}
		self.probeID = 0
		self.numProbes = 0
		self.timeFormat = "%Y-%m-%d %H:%M:%S"
		self.choiceGroupChoices = self.setupGroupChoice()
		self.choiceAliasChoices = []
		self.choiceColorChoices = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'pink', 'Add...']
		self.choiceColorBitmap = self.setupDefaultChoiceColorBitmap()
		timenow = time.time()
	
		ScrolledPanelBase.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
		
		### Timers ###
		self.auto_update_timer = wx.Timer(self, wx.NewId())
		##############
		
		self.SetMinSize( wx.Size( 1000,200 ) )
		
		bSizerPanelControlContents = wx.BoxSizer( wx.HORIZONTAL )
		
		self.bSizerLeft = wx.BoxSizer( wx.VERTICAL )
		
		self.gSizerProbes = wx.GridSizer( 1, 4, 0, 5 )
		
		self.staticTextGroup = wx.StaticText( self, wx.ID_ANY, u"Group", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextGroup.Wrap( -1 )
		self.gSizerProbes.Add( self.staticTextGroup, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 0 )
		
		self.staticTextAlias = wx.StaticText( self, wx.ID_ANY, u"Alias", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextAlias.Wrap( -1 )
		self.gSizerProbes.Add( self.staticTextAlias, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 0 )
		
		self.staticTextColor = wx.StaticText( self, wx.ID_ANY, u"Color", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextColor.Wrap( -1 )
		self.gSizerProbes.Add( self.staticTextColor, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 0 )
		
		self.staticTextRemove = wx.StaticText( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextRemove.Wrap( -1 )
		self.gSizerProbes.Add( self.staticTextRemove, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 0 )
		
		self.bSizerLeft.Add( self.gSizerProbes, 0, wx.EXPAND, 5 )
		
		bSizerButtons = wx.BoxSizer( wx.HORIZONTAL )
		
		self.buttonAddProbe = wx.Button( self, wx.ID_ANY, u"Add Probe", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerButtons.Add( self.buttonAddProbe, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonPlot = wx.Button( self, wx.ID_ANY, u"Plot", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerButtons.Add( self.buttonPlot, 1, wx.ALL, 5 )
		
		self.bSizerLeft.Add( bSizerButtons, 0, wx.EXPAND, 5 )
		
		bSizerPanelControlContents.Add( self.bSizerLeft, 1, wx.EXPAND, 5 )
		
		self.bSizerRight = wx.BoxSizer( wx.VERTICAL )
		
		fgSizerTime = wx.FlexGridSizer( 2, 5, 0, 0 )
		fgSizerTime.SetFlexibleDirection( wx.BOTH )
		fgSizerTime.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.checkBoxStartTime = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkBoxStartTime.SetToolTipString( u"check to use entered start time" )
		fgSizerTime.Add( self.checkBoxStartTime, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextStartTime = wx.StaticText( self, wx.ID_ANY, u"Start Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextStartTime.Wrap( -1 )
		fgSizerTime.Add( self.staticTextStartTime, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlStartTime = wx.TextCtrl( self, wx.ID_ANY, time.strftime(self.timeFormat, time.localtime(timenow-2*24*60*60)), wx.DefaultPosition, wx.Size( 125,-1 ), 0 )
		fgSizerTime.Add( self.textCtrlStartTime, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextStartTimeFormat = wx.StaticText( self, wx.ID_ANY, u"(yyyy-mm-dd hh:MM:ss)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextStartTimeFormat.Wrap( -1 )
		fgSizerTime.Add( self.staticTextStartTimeFormat, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.checkBoxEarliest = wx.CheckBox( self, wx.ID_ANY, u"Use Earliest Time", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerTime.Add( self.checkBoxEarliest, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.checkBoxEndTime = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkBoxEndTime.SetValue(True)
		self.checkBoxEndTime.SetToolTipString( u"check to use entered end time" )
		fgSizerTime.Add( self.checkBoxEndTime, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextEndTime = wx.StaticText( self, wx.ID_ANY, u"End Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextEndTime.Wrap( -1 )
		fgSizerTime.Add( self.staticTextEndTime, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.textCtrlEndTime = wx.TextCtrl( self, wx.ID_ANY, time.strftime(self.timeFormat, time.localtime(timenow)), wx.DefaultPosition, wx.Size( 125,-1 ), 0 )
		fgSizerTime.Add( self.textCtrlEndTime, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextEndTimeFormat = wx.StaticText( self, wx.ID_ANY, u"(yyyy-mm-dd hh:MM:ss)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextEndTimeFormat.Wrap( -1 )
		fgSizerTime.Add( self.staticTextEndTimeFormat, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.checkBoxCurrent = wx.CheckBox( self, wx.ID_ANY, u"Use Current Time", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerTime.Add( self.checkBoxCurrent, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.bSizerRight.Add( fgSizerTime, 0, wx.EXPAND|wx.ALL, 5 )
		
		bSizerFunctions = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizerDuration = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Duration" ), wx.VERTICAL )
		
		bSizerDays = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextDays = wx.StaticText( self, wx.ID_ANY, u"Days:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDays.Wrap( -1 )
		self.staticTextDays.SetToolTipString( u"single check the time checkbox above to use the checked time with duration" )
		bSizerDays.Add( self.staticTextDays, 0, wx.ALL, 5 )
		
		self.textCtrlDays = wx.TextCtrl( self, wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerDays.Add( self.textCtrlDays, 0, wx.ALL, 5 )
		
		sbSizerDuration.Add( bSizerDays, 0, wx.EXPAND, 5 )
		
		bSizerHours = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextHours = wx.StaticText( self, wx.ID_ANY, u"Hours:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHours.Wrap( -1 )
		self.staticTextHours.SetToolTipString( u"single check the time checkbox above to use the checked time with duration" )
		bSizerHours.Add( self.staticTextHours, 0, wx.ALL, 5 )
		
		self.textCtrlHours = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerHours.Add( self.textCtrlHours, 0, wx.ALL, 5 )
		
		sbSizerDuration.Add( bSizerHours, 0, wx.EXPAND, 5 )
		
		bSizerMinutes = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextMinutes = wx.StaticText( self, wx.ID_ANY, u"Minutes:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMinutes.Wrap( -1 )
		self.staticTextMinutes.SetToolTipString( u"single check the time checkbox above to use the checked time with duration" )
		bSizerMinutes.Add( self.staticTextMinutes, 0, wx.ALL, 5 )
		
		self.textCtrlMinutes = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerMinutes.Add( self.textCtrlMinutes, 0, wx.ALL, 5 )
		
		sbSizerDuration.Add( bSizerMinutes, 0, wx.EXPAND, 5 )
		
		bSizerFunctions.Add( sbSizerDuration, 0, wx.ALL, 5 )
		
		sbSizerUpdate = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Update Intervals" ), wx.VERTICAL )
		
		self.checkBoxUpdate = wx.CheckBox( self, wx.ID_ANY, u"Check to Auto-update", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizerUpdate.Add( self.checkBoxUpdate, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizerHoursUpdate = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextHoursUpdate = wx.StaticText( self, wx.ID_ANY, u"Hours:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextHoursUpdate.Wrap( -1 )
		self.staticTextHoursUpdate.SetToolTipString( u"check the auto-update checkbox for automatic updating plots with update time intervals" )
		bSizerHoursUpdate.Add( self.staticTextHoursUpdate, 0, wx.ALL, 5 )
		
		self.textCtrlHoursUpdate = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerHoursUpdate.Add( self.textCtrlHoursUpdate, 0, wx.ALL, 5 )
		
		sbSizerUpdate.Add( bSizerHoursUpdate, 1, wx.EXPAND, 5 )
		
		bSizerMinutesUpdate = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextMinutesUpdate = wx.StaticText( self, wx.ID_ANY, u"Minutes:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextMinutesUpdate.Wrap( -1 )
		self.staticTextMinutesUpdate.SetToolTipString( u"check the auto-update checkbox for automatic updating plots with update time intervals" )
		bSizerMinutesUpdate.Add( self.staticTextMinutesUpdate, 0, wx.ALL, 5 )
		
		self.textCtrlMinutesUpdate = wx.TextCtrl( self, wx.ID_ANY, u"5", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerMinutesUpdate.Add( self.textCtrlMinutesUpdate, 0, wx.ALL, 5 )
		
		sbSizerUpdate.Add( bSizerMinutesUpdate, 1, wx.EXPAND, 5 )
		
		bSizerFunctions.Add( sbSizerUpdate, 0, wx.ALL, 5 )
		
		self.bSizerRight.Add( bSizerFunctions, 0, wx.EXPAND, 5 )
		
		bSizerPanelControlContents.Add( self.bSizerRight, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizerPanelControlContents )
		self.Layout()
		self.SetupScrolling()
		bSizerPanelControlContents.Fit( self )
		
		# Connect Events
		self.buttonAddProbe.Bind( wx.EVT_BUTTON, self.onAddProbe )
		self.buttonPlot.Bind( wx.EVT_BUTTON, self.onPlot )
		self.checkBoxUpdate.Bind( wx.EVT_CHECKBOX, self.onCheckAutoUpdate )
		self.Bind(wx.EVT_TIMER, self.onAutoUpdateTimer, self.auto_update_timer)
		self.textCtrlHoursUpdate.Bind( wx.EVT_TEXT, self.onAutoUpdateTimeChange )
		self.textCtrlMinutesUpdate.Bind( wx.EVT_TEXT, self.onAutoUpdateTimeChange )
	
	def __del__( self ):
		pass
	
	# setupGroupChoice
	# @Purpose:
	#	get the list of groups (stations) in DB .
	# @Output:
	#	list of groups...
	def setupGroupChoice(self):
		db = EnvDB()
		retlist = db.getStations()
		return retlist
	
	# setupDefaultChoiceColorBitmap
	# @Purpose:
	#	setup the default color bitmap in the color choice combox box
	# @Output:
	#	return the list of bitmaps created according to self.choiceColorChoices
	def setupDefaultChoiceColorBitmap(self):
		listBitmaps = []
		for i in xrange(len(self.choiceColorChoices)):
			if i == len(self.choiceColorChoices) - 1:
				break
			newBitmap = self.createColorBitmap(self.choiceColorChoices[i])
			listBitmaps.append(newBitmap)		
		return listBitmaps
	
	# createColorBitmap
	# @Purpose:
	#	create and return a color bitmap given the color name
	# @Inputs:
	#	colorName = color name existing in matplotlib.colors.cnames (color name database)
	# @Outputs:
	#	a wx.Bitmap object
	def createColorBitmap(self, colorName):
		width = 30
		height = 10
		bpp = 3		# bytes per pixel
		bytes = array.array('B', [0] * width * height * bpp)
		alphaBytes = array.array('B', [255] * width * height)	# required for Linux (must have alpha array on Linux)
		for y in xrange(height):
			for x in xrange(width):
				offset = y*width*bpp + x*bpp
				hexString = matplotlibColors.cnames[colorName]
				r = int(hexString[1:3], 16)
				g = int(hexString[3:5], 16)
				b = int(hexString[5:7], 16)
				bytes[offset] = r
				bytes[offset+1] = g
				bytes[offset+2] = b
		return wx.BitmapFromBuffer(width, height, bytes, alphaBytes)
	
	# Virtual event handlers, overide them in your derived class
	def onRemoveProbe( self, event ):
		indexToRemove = (event.GetEventObject().GetId() - self.probesButtonMask - 3) / 4
		exec("self.gSizerProbes.Remove(self.choiceGroup_"+str(indexToRemove)+")")
		exec("self.gSizerProbes.Remove(self.choiceAlias_"+str(indexToRemove)+")")
		exec("self.gSizerProbes.Remove(self.choiceColor_"+str(indexToRemove)+")")
		exec("self.gSizerProbes.Remove(self.buttonRemove_"+str(indexToRemove)+")")
		self.gSizerProbes.SetRows(self.gSizerProbes.GetRows()-1)

		# disconnect Events
		exec("self.choiceGroup_"+str(indexToRemove)+".Unbind(wx.EVT_CHOICE)")
		exec("self.choiceAlias_"+str(indexToRemove)+".Unbind(wx.EVT_CHOICE)")
		exec("self.choiceColor_"+str(indexToRemove)+".Unbind(wx.EVT_COMBOBOX)")
		exec("self.buttonRemove_"+str(indexToRemove)+".Unbind(wx.EVT_BUTTON)")
		
		exec("self.choiceGroup_"+str(indexToRemove)+".Destroy()")
		exec("self.choiceAlias_"+str(indexToRemove)+".Destroy()")
		exec("self.choiceColor_"+str(indexToRemove)+".Destroy()")
		exec("self.buttonRemove_"+str(indexToRemove)+".Destroy()")
		
		del self.validProbeIDs[indexToRemove]
		self.numProbes -= 1
		self.bSizerLeft.Layout()
		self.bSizerRight.Layout()
		self.refreshWidget(self)
	
	@handlesError
	def onAddProbe( self, event, probeID=None, group=None, alias=None, color=None ):
		# add a specific probe
		if probeID != None:
			self.probeID = probeID
			
		# setup specific color here becauase we can use written methods to create bitmaps
		# we add the specific color to the system, and create bitmap here.
		if color != None and (color not in self.choiceColorChoices):
			self.choiceColorChoices.insert(len(self.choiceColorChoices)-1, color)
			self.choiceColorBitmap = self.setupDefaultChoiceColorBitmap()
	
		self.gSizerProbes.SetRows(self.gSizerProbes.GetRows()+1)
		
		exec("self.choiceGroup_"+str(self.probeID)+" = wx.Choice( self, self.probesButtonMask+self.probeID*4, wx.DefaultPosition, wx.DefaultSize, self.choiceGroupChoices, 0 )")
		exec("self.gSizerProbes.Add( self.choiceGroup_"+str(self.probeID)+", 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 0 )")
		
		exec("self.choiceAlias_"+str(self.probeID)+" = wx.Choice( self, self.probesButtonMask+self.probeID*4+1, wx.DefaultPosition, wx.DefaultSize, self.choiceAliasChoices, 0 )")
		exec("self.gSizerProbes.Add( self.choiceAlias_"+str(self.probeID)+", 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 0 )")
		
		exec("self.choiceColor_"+str(self.probeID)+" = wx.combo.BitmapComboBox( self, self.probesButtonMask+self.probeID*4+2, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=self.choiceColorChoices, style=wx.CB_READONLY )")
		for i in xrange(len(self.choiceColorBitmap)):
			exec("self.choiceColor_"+str(self.probeID)+".SetItemBitmap( i, self.choiceColorBitmap[i] )")
		
		# if we are loading a specific color:
		if color != None:
			exec("self.choiceColor_"+str(self.probeID)+".SetSelection( self.choiceColor_"+str(self.probeID)+".FindString(color))")
		# random color chooser:
		else:
			if self.probeID < len(self.choiceColorBitmap):
				exec("self.choiceColor_"+str(self.probeID)+".SetSelection( self.probeID )")
			else:
				exec("self.choiceColor_"+str(self.probeID)+".SetSelection( len(self.choiceColorChoices)-1 )")
				self.onAddOrSelectColor(None, self.probeID)
				
		exec("self.gSizerProbes.Add( self.choiceColor_"+str(self.probeID)+", 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 0 )")
		
		exec("self.buttonRemove_"+str(self.probeID)+" = wx.Button( self, self.probesButtonMask+self.probeID*4+3, u\"Remove\", wx.DefaultPosition, wx.DefaultSize, 0 )")
		exec("self.gSizerProbes.Add( self.buttonRemove_"+str(self.probeID)+", 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 0 )")
		
		# preset new probe to be the last used group
		lastProbeID = None
		if group == None and len(self.validProbeIDs) > 0:
			lastProbeID = sorted(self.validProbeIDs.keys())[-1]
			probeIDEntries = self.validProbeIDs[lastProbeID]
			if probeIDEntries != None:
				exec("group = self.choiceGroup_"+str(lastProbeID)+".GetString(self.choiceGroup_"+str(lastProbeID)+".GetCurrentSelection())")
			else:
				lastProbeID = None
		
		# setting up if we are adding a specific probe:
		# putting group and alias at here BECAUSE group and alias widget need to EXIST FIRST!!!
		if group != None:
			exec("self.choiceGroup_"+str(self.probeID)+".SetSelection(self.choiceGroup_"+str(self.probeID)+".FindString(group))")
			self.onSelectGroup(event, self.probeID)
		if alias != None:
			exec("self.choiceAlias_"+str(self.probeID)+".SetSelection(self.choiceAlias_"+str(self.probeID)+".FindString(alias))")
			self.onSelectAlias(event, self.probeID)
		else:
			if lastProbeID != None:
				exec("aliasIndex = self.choiceAlias_"+str(lastProbeID)+".GetCurrentSelection()")
				exec("counts = self.choiceAlias_"+str(lastProbeID)+".GetCount()")
				if aliasIndex + 1 < counts:
					aliasIndex += 1
				exec("self.choiceAlias_"+str(self.probeID)+".SetSelection(aliasIndex)")
				self.onSelectAlias(event, self.probeID)
		
		# Connect Events
		exec("self.choiceGroup_"+str(self.probeID)+".Bind( wx.EVT_CHOICE, self.onSelectGroup )")
		exec("self.choiceAlias_"+str(self.probeID)+".Bind( wx.EVT_CHOICE, self.onSelectAlias )")
		exec("self.choiceColor_"+str(self.probeID)+".Bind( wx.EVT_COMBOBOX, self.onAddOrSelectColor )")
		exec("self.buttonRemove_"+str(self.probeID)+".Bind( wx.EVT_BUTTON, self.onRemoveProbe )")
		
		# refresh widgets
		self.bSizerLeft.Layout()
		self.bSizerRight.Layout()
		self.refreshWidget(self)
		
		if lastProbeID == None and probeID == None:			# only set to None when adding brand new probes, not loading from config!
			self.validProbeIDs[self.probeID] = None
		self.probeID += 1
		self.numProbes += 1
	
	@handlesError
	def onPlot( self, event ):
		# check input time format
		timeFormat = '\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d'
		if not self.checkBoxEarliest.IsChecked() and ( not re.match(timeFormat, self.textCtrlStartTime.GetValue()) ):
			raise InvalidTimeException("startTime = "+self.textCtrlStartTime.GetValue(), "ERROR: Invalid Start Time.")
		if not self.checkBoxCurrent.IsChecked() and ( not re.match(timeFormat, self.textCtrlEndTime.GetValue()) ):
			raise InvalidTimeException("endTime = "+self.textCtrlEndTime.GetValue(), "ERROR: Invalid End Time.")
		
		# get Durations
		if not re.match('\d+', self.textCtrlDays.GetValue()):
			raise InvalidTimeException("days = "+self.textCtrlDays.GetValue(), "ERROR: Invalid Duration day.")
		if not re.match('\d+', self.textCtrlHours.GetValue()):
			raise InvalidTimeException("hours = "+self.textCtrlHours.GetValue(), "ERROR: Invalid Duration hour.")
		if not re.match('\d+', self.textCtrlMinutes.GetValue()):
			raise InvalidTimeException("minutes = "+self.textCtrlMinutes.GetValue(), "ERROR: Invalid Duration minute.")
		days = int(self.textCtrlDays.GetValue())
		hours = int(self.textCtrlHours.GetValue())
		minutes = int(self.textCtrlMinutes.GetValue())
		durations = days*24*3600 + hours*3600 + minutes*60
		
		# setup end time
		endTimeNotSet = False
		if self.checkBoxCurrent.IsChecked():
			endTime = time.time()
		elif self.checkBoxEndTime.IsChecked():
			endTime = time.mktime(time.strptime(self.textCtrlEndTime.GetValue(), self.timeFormat))
		else:
			endTimeNotSet = True
			endTime = None
		# setup start time
		if self.checkBoxEarliest.IsChecked():
			if endTimeNotSet:
				raise InvalidTimeException('self.checkBoxEarliest.IsChecked() and endTimeNotSet', "ERROR: Earliest time with Duration combination is NOT allowed.")
			startTime = None
		elif self.checkBoxStartTime.IsChecked():
			startTime = time.mktime(time.strptime(self.textCtrlStartTime.GetValue(), self.timeFormat))
			if endTimeNotSet:
				endTime = startTime + durations
		else:
			if endTimeNotSet:
				startTime = None
			else:
				startTime = endTime - durations
		
		if startTime != None:
			startTime = time.strftime(self.timeFormat, time.localtime(startTime))
			self.textCtrlStartTime.SetValue(startTime)
		if endTime != None:
			endTime = time.strftime(self.timeFormat, time.localtime(endTime))
			self.textCtrlEndTime.SetValue(endTime)
		
		### try to plot whole time range warning...
		if startTime == None and endTime == None:
			if self.popInfoBox("time range is large...", "INFO: time range is not set, this will plot large amount of information!!! Continue?") == wx.ID_CANCEL:
				return
		
		# get the top level frame
		topLevelFrame = self
		while not topLevelFrame.IsTopLevel():
			topLevelFrame = topLevelFrame.GetParent()
		topLevelFrame.plot(self.validProbeIDs, startTime, endTime)

	@handlesError
	def onCheckAutoUpdate( self, event ):
		# get frame widget
		widget = self
		while widget.GetParent():
			if widget.IsTopLevel():
				break
			widget = widget.GetParent()
		
		if self.checkBoxUpdate.IsChecked():
			widget.statusBarMain.PulseStart()
			if self.auto_update_timer.IsRunning():
				self.auto_update_timer.Stop()
			# updateInterval in milli-seconds
			updateInterval = (3600 * int(self.textCtrlHoursUpdate.GetValue()) + \
							60 * int(self.textCtrlMinutesUpdate.GetValue()) ) * 1000
			self.auto_update_timer.Start(updateInterval)			
			if not self.checkBoxCurrent.IsChecked():
				self.checkBoxCurrent.SetValue(True)
		else:
			widget.statusBarMain.PulseStop()
			self.auto_update_timer.Stop()
		
	def onAutoUpdateTimer( self, event ):
		self.onPlot(event)
		event.Skip()
		
	def onSelectGroup( self, event, probeID=None ):
		if probeID != None:
			index = probeID
		else:
			index = (event.GetEventObject().GetId() - self.probesButtonMask) / 4
			
		exec("group = self.choiceGroup_"+str(index)+".GetString(self.choiceGroup_"+str(index)+".GetCurrentSelection())")
		db = EnvDB()
		listProbes = db.getProbesInStation([group])
		listProbes = [p[1] for p in listProbes]
		aliases = db.getProbeAliases(listProbes)
		aliases = [a[1] for a in aliases]
		exec("self.choiceAlias_"+str(index)+".SetItems(aliases)")
		
	def onSelectAlias( self, event, probeID=None ):
		if probeID != None:
			index = probeID
		else:
			index = (event.GetEventObject().GetId() - self.probesButtonMask - 1) / 4
			
		exec("group = self.choiceGroup_"+str(index)+".GetString(self.choiceGroup_"+str(index)+".GetCurrentSelection())")
		exec("alias = self.choiceAlias_"+str(index)+".GetString(self.choiceAlias_"+str(index)+".GetCurrentSelection())")
		exec("color = self.choiceColor_"+str(index)+".GetStringSelection()")
		db = EnvDB()
		probe_results = db.getProbeWithStationAndAlias(group, alias)
		if len(probe_results) != 0:
			this_probe = probe_results[0]			# assume one entry matched only
			self.validProbeIDs[index] = (this_probe, alias, color)
	
	def onAddOrSelectColor( self, event, probeID=None, color=None ):
		if probeID != None:
			index = probeID
		else:
			index = (event.GetEventObject().GetId() - self.probesButtonMask - 2) / 4
		
		exec("selectAdd = self.choiceColor_"+str(index)+".GetSelection() == self.choiceColor_"+str(index)+".GetCount()-1")
		if not selectAdd:	# not selecting adding color, setting color.
			if index in self.validProbeIDs and self.validProbeIDs[index] != None:
				exec("self.validProbeIDs[index] = (self.validProbeIDs[index][0], self.validProbeIDs[index][1], self.choiceColor_"+str(index)+".GetString(self.choiceColor_"+str(index)+".GetSelection()))")
			return
		
		colorDB = matplotlibColors.cnames.keys()
		if len(self.choiceColorChoices) > len(colorDB):			# prevent keep adding till full then infinite loop
			return
		
		# add a specific color or a random color
		if color != None:
			choice = color
		else:				# add a new random color
			choice = 'red'
			while choice in self.choiceColorChoices:
				choice = random.choice(colorDB)
		
		newBitmap = self.createColorBitmap(choice)
		# setup the current combo box
		exec("self.choiceColor_"+str(index)+".Insert(choice, newBitmap, self.choiceColor_"+str(index)+".GetCount()-1)")
		exec("self.choiceColor_"+str(index)+".SetSelection(self.choiceColor_"+str(index)+".GetCount()-2)")
		# setup the system-wide color list
		self.choiceColorChoices.insert(len(self.choiceColorChoices)-1, choice)
		self.choiceColorBitmap.append(newBitmap)
		# update the validProbeIDs map
		if index in self.validProbeIDs and self.validProbeIDs[index] != None:
			self.validProbeIDs[index] = (self.validProbeIDs[index][0], self.validProbeIDs[index][1], choice)
	
	def onAutoUpdateTimeChange( self, event ):
		if self.checkBoxUpdate.IsChecked():
			self.onCheckAutoUpdate(event)
	
