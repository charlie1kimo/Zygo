"""
dialogs.py:
	dialogs.py contains extensions for wx.Dialogs class.
	These classes are useful utilities for dialoging.
"""

import wx

###########################################################################
## Class DialogProgress
###########################################################################

class DialogProgress ( wx.Dialog ):
	
	def __init__( self, parent, title="In Progress..." ):
		self.log = ""

		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = wx.Size( 500,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextStatus = wx.StaticText( self, wx.ID_ANY, u"Action In Progress...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextStatus.Wrap( -1 )
		self.staticTextStatus.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer4.Add( self.staticTextStatus, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.gaugeProgress = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.gaugeProgress.SetValue( 0 ) 
		bSizer4.Add( self.gaugeProgress, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlLog = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,100 ), wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer4.Add( self.textCtrlLog, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass

	###########################################
	# @Purpose:
	#	Private method for handling the destroy timer events
	###########################################
	def __onDestroyTimer__(self, event):
		if self.IsModal():
			if self.closeInSecs == 0:
				self.destroyTimer.Stop()
				self.Destroy()
			else:
				self.SetStatus("Finished. Close in %d seconds..." % self.closeInSecs)
				self.closeInSecs -= 1
		else:
			self.destoryTimer.Stop()

	###########################################
	# @Purpose:
	#	Append the log message to the log area
	# @Input:
	#	(str) msg = log message to append
	###########################################
	def AppendLog(self, msg):
		self.log += msg + '\n'
		self.textCtrlLog.SetValue(self.log)

	###########################################
	# @Purpose:
	#	Automatically close the dialog (if opened) after given seconds
	# @Inputs:
	#	(int) secs = seconds to wait before close
	###########################################
	def AutoClose(self, secs):
		if self.IsModal():
			self.destroyTimer = wx.Timer(self, wx.NewId())
			self.Bind(wx.EVT_TIMER, self.__onDestroyTimer__, self.destroyTimer)
			self.destroyTimer.Start(1000)			# update per seconds
			self.closeInSecs = secs

	###########################################
	# @Purpose:
	#	Get the progress bar value
	# @Outpus:
	#	(int) progress value
	###########################################
	def GetProgressValue(self):
		return self.gaugeProgress.GetValue()

	###########################################
	# @Purpose:
	#	Set the status message to this dialog
	# @Inputs:
	#	(str) status = status message
	###########################################
	def SetStatus(self, status):
		self.staticTextStatus.SetLabel(status)

	###########################################
	# @Purpose:
	#	Set the progress bar value
	# @Inputs:
	#	(int) value = progress value
	###########################################
	def SetProgressValue(self, value):
		self.gaugeProgress.SetValue(value)

