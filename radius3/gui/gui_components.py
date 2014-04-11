"""
gui_components.py
	This file contains all the other GUI components that supports the
	major radius measurement GUI program
Author: Charlie Chen
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/4/2013	cchen	first created documentation
'''

import os
import re
import wx

import radius3.utilities as utilities
from finddir import finddir

###########################################################################
## Class FrameOutputBuffered
#	Abstract class for supporting output buffer wx.Frame
###########################################################################	
class FrameOutputBuffered(wx.Frame):
	def __init__(self):
		self.out_buffer = None
		
	def __set_out_buffer__(self, child):
		self.out_buffer = child
		

###########################################################################
## Class FrameLoading
###########################################################################
class FrameLoading ( FrameOutputBuffered ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Initializing...", pos = wx.DefaultPosition, size = wx.Size( 500,200 ), style = wx.CLIP_CHILDREN|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
			
		self.SetSizeHintsSz( wx.Size( 500,150 ), wx.Size( 500,300 ) )
		
		bSizerLoading = wx.BoxSizer( wx.VERTICAL )
		
		self.panelLoading = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL|wx.EXPAND )
		bSizerPanelLoading = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextInfo = wx.StaticText( self.panelLoading, wx.ID_ANY, u"...Initializing Radius Measurement Program...", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE  )
		self.staticTextInfo.Wrap( -1 )
		self.staticTextInfo.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPanelLoading.Add( self.staticTextInfo, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.gaugeLoading = wx.Gauge( self.panelLoading, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL|wx.GA_SMOOTH )
		bSizerPanelLoading.Add( self.gaugeLoading, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.textCtrlLog = wx.TextCtrl( self.panelLoading, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		bSizerPanelLoading.Add( self.textCtrlLog, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.panelLoading.SetSizer( bSizerPanelLoading )
		self.panelLoading.Layout()
		bSizerPanelLoading.Fit( self.panelLoading )
		bSizerLoading.Add( self.panelLoading, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.SetSizer( bSizerLoading )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# setting out_buffer
		self.__set_out_buffer__(self.textCtrlLog)
	
	def __del__( self ):
		pass
		

###########################################################################
## Class FramePartPrompt
###########################################################################
class DialogPartPrompt ( wx.Dialog ):
	
	def __init__( self, parent, cmdParameters ):
		# setup parts information:
		self.cmdParams = cmdParameters
		self.materialDict = {}
		self.materialList = []
		
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Setup Part Information", pos = wx.DefaultPosition, size = (700, 400), style = wx.DEFAULT_DIALOG_STYLE )
		self.SetSizeHintsSz( (700, 400), wx.DefaultSize )
		
		bSizerPartPrompt = wx.BoxSizer( wx.VERTICAL )
		
		self.panelPart = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPartPanel = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextTitle = wx.StaticText( self.panelPart, wx.ID_ANY, u"Part Information", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTitle.Wrap( -1 )
		self.staticTextTitle.SetFont( wx.Font( 14, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerPartPanel.Add( self.staticTextTitle, 0, wx.ALL, 5 )
		
		self.staticlineSepLine = wx.StaticLine( self.panelPart, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPartPanel.Add( self.staticlineSepLine, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizerContents = wx.FlexGridSizer( 8, 2, 5, 5 )
		fgSizerContents.AddGrowableCol( 1 )
		fgSizerContents.SetFlexibleDirection( wx.BOTH )
		fgSizerContents.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.staticTextOmasePath = wx.StaticText( self.panelPart, wx.ID_ANY, u"Omase Path:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextOmasePath.Wrap( -1 )
		fgSizerContents.Add( self.staticTextOmasePath, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		bSizerOmasePath = wx.BoxSizer( wx.HORIZONTAL )
		
		self.textCtrlOmasePath = wx.TextCtrl( self.panelPart, wx.ID_ANY, self.cmdParams.part_info.omase_path, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerOmasePath.Add( self.textCtrlOmasePath, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonOmasePathFinddir = wx.Button( self.panelPart, wx.ID_ANY, u"Find DIR", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerOmasePath.Add( self.buttonOmasePathFinddir, 0, wx.ALL, 5 )
		
		fgSizerContents.Add( bSizerOmasePath, 1, wx.EXPAND, 5 )
		
		self.staticTextBookTitle = wx.StaticText( self.panelPart, wx.ID_ANY, u"Book Title:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextBookTitle.Wrap( -1 )
		fgSizerContents.Add( self.staticTextBookTitle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlBookTitle = wx.TextCtrl( self.panelPart, wx.ID_ANY, self.cmdParams.part_info.book_title, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlBookTitle, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextPartID = wx.StaticText( self.panelPart, wx.ID_ANY, u"Part ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextPartID.Wrap( -1 )
		fgSizerContents.Add( self.staticTextPartID, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textCtrlPartID = wx.TextCtrl( self.panelPart, wx.ID_ANY, self.cmdParams.part_info.id, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlPartID, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextOperator = wx.StaticText( self.panelPart, wx.ID_ANY, u"Operator:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextOperator.Wrap( -1 )
		fgSizerContents.Add( self.staticTextOperator, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlOperator = wx.TextCtrl( self.panelPart, wx.ID_ANY, self.cmdParams.part_info.user, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlOperator, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextGlassTypeCTE = wx.StaticText( self.panelPart, wx.ID_ANY, u"Glass Type / CTE:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextGlassTypeCTE.Wrap( -1 )
		fgSizerContents.Add( self.staticTextGlassTypeCTE, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		bSizerGlassTypeCTE = wx.BoxSizer( wx.HORIZONTAL )

		self.choiceGlassType = wx.Choice( self.panelPart, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.materialList, 0 )
		self.setupMaterialList()
		if len(self.cmdParams.part_info.glass_type) > 0:
			self.choiceGlassType.SetSelection(self.materialList.index(self.cmdParams.part_info.glass_type))
		else:
			self.choiceGlassType.SetSelection( len(self.materialList)-1 )
		bSizerGlassTypeCTE.Add( self.choiceGlassType, 1, wx.ALL, 5 )
		
		self.textCtrlCTE = wx.TextCtrl( self.panelPart, wx.ID_ANY, "%0.2e" % self.cmdParams.part_info.cte, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerGlassTypeCTE.Add( self.textCtrlCTE, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizerContents.Add( bSizerGlassTypeCTE, 1, wx.EXPAND, 5 )
		
		self.staticTextTargetTemp = wx.StaticText( self.panelPart, wx.ID_ANY, u"Report Temperature: (C)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTargetTemp.Wrap( -1 )
		fgSizerContents.Add( self.staticTextTargetTemp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlTargetTemp = wx.TextCtrl( self.panelPart, wx.ID_ANY, repr(self.cmdParams.part_info.target_temp), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlTargetTemp, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextPartRadius = wx.StaticText( self.panelPart, wx.ID_ANY, u"Part Radius (mm)[CC (+), CX (-)]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextPartRadius.Wrap( -1 )
		fgSizerContents.Add( self.staticTextPartRadius, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlPartRadius = wx.TextCtrl( self.panelPart, wx.ID_ANY, repr(self.cmdParams.part_info.part_radius), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlPartRadius, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticTextTSRadius = wx.StaticText( self.panelPart, wx.ID_ANY, u"Transmission Sphere Radius (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTSRadius.Wrap( -1 )
		fgSizerContents.Add( self.staticTextTSRadius, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlTSRadius = wx.TextCtrl( self.panelPart, wx.ID_ANY, repr(self.cmdParams.part_info.ts_radius), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerContents.Add( self.textCtrlTSRadius, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizerPartPanel.Add( fgSizerContents, 1, wx.EXPAND, 5 )
		
		bSizerButtons = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizerButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonOK = wx.Button( self.panelPart, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerButtons.Add( self.buttonOK, 0, wx.ALL, 5 )
		
		bSizerButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonCancel = wx.Button( self.panelPart, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerButtons.Add( self.buttonCancel, 0, wx.ALL, 5 )
		
		bSizerButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		bSizerPartPanel.Add( bSizerButtons, 0, wx.EXPAND, 5 )
		
		self.panelPart.SetSizer( bSizerPartPanel )
		self.panelPart.Layout()
		bSizerPartPanel.Fit( self.panelPart )
		bSizerPartPrompt.Add( self.panelPart, 1, wx.EXPAND |wx.ALL, 0 )
		
		self.SetSizer( bSizerPartPrompt )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.buttonOmasePathFinddir.Bind( wx.EVT_BUTTON, self.onFindDir )
		self.choiceGlassType.Bind( wx.EVT_CHOICE, self.onChoiceGlassType )
		self.buttonOK.Bind( wx.EVT_BUTTON, self.onPartOK )
		self.buttonCancel.Bind( wx.EVT_BUTTON, self.onPartCancel )
	
	def __del__( self ):
		pass
	
	# Virtual event handlers, overide them in your derived class
	def onClose(self, event):
		self.onPartCancel(event)

	# setupMaterialList:
	# @Purpose:
	#	setup material list...
	def setupMaterialList(self):
		# read materials list:
		materialDict = utilities.getMaterialCTE()	
		materialList = materialDict.keys()
		materialList.sort()
		materialList.append('Custom')									# put 'Custom' at the end of the list...
		self.materialList = materialList
		materialDict['Custom'] = {'CTE': '0.0', 'N632.8': '-1'}			# mimic the tagfile read structure...
		self.materialDict = materialDict
		# setup the choice list...
		self.choiceGlassType.SetItems(materialList)

	# setupPartParams:
	# @Purpose:
	#	setup prefilled parts parameters
	def setupPartParams(self):
		path = finddir(parent = self)
		if path == None:						# user canceled.
			return

		# read the part master config
		masterCFG = utilities.readPartMasterCfg(path, self)

		# setup the pre-filled information:
		if masterCFG != None:
			self.textCtrlOmasePath.SetValue(path)
			self.textCtrlBookTitle.SetValue(masterCFG['Booktitle'])
			self.choiceGlassType.SetSelection(self.choiceGlassType.FindString(masterCFG['SubMatl']))
			self.textCtrlCTE.SetValue(self.materialDict[self.materialList[self.choiceGlassType.GetCurrentSelection()]]['CTE'])
			self.textCtrlPartRadius.SetValue(str(masterCFG['part_radius']))

	def onChoiceGlassType( self, event ):
		if self.choiceGlassType.GetCurrentSelection() == len(self.materialList) - 1:		# end (Custom)
			self.textCtrlCTE.SetEditable(True)
		else:
			self.textCtrlCTE.SetEditable(False)
			self.textCtrlCTE.SetValue(self.materialDict[self.materialList[self.choiceGlassType.GetCurrentSelection()]]['CTE'])
		event.Skip()
		
	def onPartOK( self, event ):
		isOK = True
		# data validation
		if len(self.textCtrlOmasePath.GetValue()) > 0:							# performing a formal measurement
			if len(self.textCtrlBookTitle.GetValue()) == 0:
				self.popAlertBox("Book Title Required", "Please Enter Book Title.")
				isOK = False
			if len(self.textCtrlPartID.GetValue()) == 0:
				self.popAlertBox("Part ID Required", "Please Enter Part ID.")
				isOK = False
			if len(self.textCtrlOperator.GetValue()) == 0:
				self.popAlertBox("Operator Name Required", "Please Enter Operator Name.")
				isOK = False
			if len(self.textCtrlCTE.GetValue()) == 0:
				self.popAlertBox("Glass Type Required", "Please Select Glass Type or Select Custom and enter CTE Manually.")
				isOK = False
			if len(self.textCtrlTargetTemp.GetValue()) == 0:
				self.popAlertBox("Target Temperature Required", "Please Enter Target Measuring Temperature.")
				isOK = False
			if self.cmdParams.wave_shift:				# if it's a wave_shift station, then part radius and ts radius are required.
				if len(self.textCtrlPartRadius.GetValue()) == 0:
					self.popAlertBox("Wave Shift Station requires Part Radius", "Please Enter Part Radius.")
					isOK = False
				if lne(self.textCtrlTSRadius.GetValue()) == 0:
					self.popAlertBox("Wave Shift Station requires TS Radius", "Please Enter Transmission Radius.")
					isOK = False
		else:																	# performing a lousy quick measurement
			self.choiceGlassType.SetSelection(len(self.materialList)-1)
			self.textCtrlCTE.SetValue('0.0')
		
		if isOK:
			# setup partName and surface
			if len(self.textCtrlOmasePath.GetValue()) == 0: 			# None part case
				partName = ""
				surface = ""
			else:
				(partName, surface) = utilities.getPartNameAndSurface(self.textCtrlOmasePath.GetValue())
			self.cmdParams.part_info.omase_path = self.textCtrlOmasePath.GetValue()
			self.cmdParams.part_info.book_title = self.textCtrlBookTitle.GetValue()
			self.cmdParams.part_info.name = partName
			self.cmdParams.part_info.surface = surface
			self.cmdParams.part_info.id = self.textCtrlPartID.GetValue()
			self.cmdParams.part_info.user = self.textCtrlOperator.GetValue()
			self.cmdParams.part_info.glass_type = self.materialList[self.choiceGlassType.GetCurrentSelection()]
			self.cmdParams.part_info.cte = float(self.textCtrlCTE.GetValue())
			self.cmdParams.part_info.target_temp = float(self.textCtrlTargetTemp.GetValue())
			self.cmdParams.part_info.part_radius = float(self.textCtrlPartRadius.GetValue())
			self.cmdParams.part_info.ts_radius = float(self.textCtrlTSRadius.GetValue())
			self.cmdParams.part_info.initialized = True
			self.Destroy()
		event.Skip()

	def onFindDir( self, event ):
		self.setupPartParams()
		event.Skip()
	
	def onPartCancel( self, event ):
		if not self.cmdParams.part_info.initialized:
			self.popAlertBox("Part Information Incompleted", "WARNING: Part Information is NOT SET!")
		self.Destroy()
		event.Skip()
	
	# popAlertBox:
	#   pop up Error Box with set title and message
	def popAlertBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_WARNING)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

	# popErrorBox:
	#   pop up Error Box with set title and message
	def popErrorBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_ERROR)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			
			
###########################################################################
## Class DialogNoCatEyePrompt
###########################################################################
class DialogNoCatEyePrompt ( wx.Dialog ):
	
	def __init__( self, parent ):
		self.parent = parent
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Setup NO cat eye measurement", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizerNoCatEyePrompt = wx.BoxSizer( wx.VERTICAL )
		
		self.panelNoCatEye = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPanel = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextTitle = wx.StaticText( self.panelNoCatEye, wx.ID_ANY, u"No Cat Eye Measurement Parameters Setup", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTitle.Wrap( -1 )
		self.staticTextTitle.SetFont( wx.Font( 14, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerPanel.Add( self.staticTextTitle, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self.panelNoCatEye, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPanel.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizerTrasmission = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextTransmission = wx.StaticText( self.panelNoCatEye, wx.ID_ANY, u"Transmission Sphere Offset:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTransmission.Wrap( -1 )
		bSizerTrasmission.Add( self.staticTextTransmission, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlTransmission = wx.TextCtrl( self.panelNoCatEye, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerTrasmission.Add( self.textCtrlTransmission, 3, wx.ALL|wx.EXPAND, 5 )
		
		bSizerPanel.Add( bSizerTrasmission, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizerGap = wx.BoxSizer( wx.HORIZONTAL )
		
		self.staticTextGap = wx.StaticText( self.panelNoCatEye, wx.ID_ANY, u"Gap Offset:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.staticTextGap.Wrap( -1 )
		bSizerGap.Add( self.staticTextGap, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.textCtrlGap = wx.TextCtrl( self.panelNoCatEye, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerGap.Add( self.textCtrlGap, 3, wx.ALL|wx.EXPAND, 5 )
		
		bSizerPanel.Add( bSizerGap, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizerButtons = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizerButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.buttonOK = wx.Button( self.panelNoCatEye, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerButtons.Add( self.buttonOK, 1, wx.ALL, 5 )
		
		
		bSizerButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		bSizerPanel.Add( bSizerButtons, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.panelNoCatEye.SetSizer( bSizerPanel )
		self.panelNoCatEye.Layout()
		bSizerPanel.Fit( self.panelNoCatEye )
		bSizerNoCatEyePrompt.Add( self.panelNoCatEye, 1, wx.EXPAND |wx.ALL, 0 )
		
		self.SetSizer( bSizerNoCatEyePrompt )
		self.Layout()
		bSizerNoCatEyePrompt.Fit( self )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.buttonOK.Bind( wx.EVT_BUTTON, self.onButtonOK )
	
	def __del__( self ):
		pass
	
	# Virtual event handlers, overide them in your derived class
	def onButtonOK( self, event ):
		# data validation
		isOK = True
		if len(self.textCtrlTransmission.GetValue()) == 0:
			self.popAlertBox("Trasmission Sphere Offset Required", "Please Enter Transmission Sphere Offset.")
			isOK = False
		if len(self.textCtrlGap.GetValue()) == 0:
			self.popAlertBox("Gap Offset Required", "Please Enter Gap Offset.")
			isOK = False
			
		if isOK:
			try:
				self.parent.sTS_Offset = float(self.textCtrlTransmission.GetValue())
				self.parent.sGap_Offset = float(self.textCtrlGap.GetValue())
				self.Destroy()
			except Exception, e:
				self.popAlertBox("Not valid number inputs!", "Please enter numbers in offsets.")
				isOK = False
		event.Skip()
	
	# popAlertBox:
	#   pop up Error Box with set title and message
	def popAlertBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_WARNING)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			
