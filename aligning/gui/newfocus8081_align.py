# -*- coding: utf-8 -*- 

import os
import re
import sys
import time
import wx
from wx_extensions.windows import FrameBase
from wx_extensions.windows import ScrolledPanelBase
from aligning.stage import NewFocus8081Stage

###########################################################################
## Class FrameMain
###########################################################################

class FrameMain ( FrameBase ):
	
	def __init__( self, parent, stage ):
		self.__savedPositionFile__ = os.path.dirname(__file__)+"/.savedPositions.txt"
		self.stage = stage
		self.savedPositions = []
		self.__parsedSavedPositions__()
		FrameBase.__init__( self, parent, id = wx.ID_ANY, title = u"NewFocus 8081 Stage Aligning App", pos = wx.DefaultPosition, size = wx.Size( 600,750 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizerFrameMain = wx.BoxSizer( wx.VERTICAL )
		
		self.panelMain = ScrolledPanelBase( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerPanelMain = wx.BoxSizer( wx.VERTICAL )
		
		self.staticTextTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"NewFocus 8081 Stage Aligning", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTitle.Wrap( -1 )
		self.staticTextTitle.SetFont( wx.Font( 14, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerPanelMain.Add( self.staticTextTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		sbSizerDispaly = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"Displays" ), wx.HORIZONTAL )
		
		fgSizerDisplayDisplacements = wx.FlexGridSizer( 5, 3, 0, 0 )
		fgSizerDisplayDisplacements.SetFlexibleDirection( wx.BOTH )
		fgSizerDisplayDisplacements.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextDisplayXtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Xtrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXtransTitle.Wrap( -1 )
		self.staticTextDisplayXtransTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXtransTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayXtransValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXtransValue.Wrap( -1 )
		self.staticTextDisplayXtransValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXtransValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayXtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXtransUnits.Wrap( -1 )
		self.staticTextDisplayXtransUnits.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextDisplayYtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Ytrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayYtransTitle.Wrap( -1 )
		self.staticTextDisplayYtransTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayYtransTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayYtransValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayYtransValue.Wrap( -1 )
		self.staticTextDisplayYtransValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayYtransValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayYtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayYtransUnits.Wrap( -1 )
		self.staticTextDisplayYtransUnits.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayYtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Ztrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZtransTitle.Wrap( -1 )
		self.staticTextDisplayZtransTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZtransTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZtransValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZtransValue.Wrap( -1 )
		self.staticTextDisplayZtransValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZtransValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZtransUnits.Wrap( -1 )
		self.staticTextDisplayZtransUnits.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextDisplayXrotTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Xrot:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXrotTitle.Wrap( -1 )
		self.staticTextDisplayXrotTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXrotTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayXrotValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXrotValue.Wrap( -1 )
		self.staticTextDisplayXrotValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXrotValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayXrotUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"rad", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayXrotUnits.Wrap( -1 )
		self.staticTextDisplayXrotUnits.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayXrotUnits, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZrotTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Zrot:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZrotTitle.Wrap( -1 )
		self.staticTextDisplayZrotTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZrotTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZrotValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZrotValue.Wrap( -1 )
		self.staticTextDisplayZrotValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZrotValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayZrotUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"rad", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayZrotUnits.Wrap( -1 )
		self.staticTextDisplayZrotUnits.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayDisplacements.Add( self.staticTextDisplayZrotUnits, 0, wx.ALL, 5 )
		
		
		sbSizerDispaly.Add( fgSizerDisplayDisplacements, 1, wx.EXPAND, 5 )
		
		self.staticlineDisplaySep = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		sbSizerDispaly.Add( self.staticlineDisplaySep, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizerDisplayMotorSteps = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizerDisplayMotorSteps.SetFlexibleDirection( wx.BOTH )
		fgSizerDisplayMotorSteps.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextDisplayPx1Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"px1:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPx1Title.Wrap( -1 )
		self.staticTextDisplayPx1Title.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPx1Title, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPx1Value = wx.StaticText( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPx1Value.Wrap( -1 )
		self.staticTextDisplayPx1Value.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPx1Value, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPx2Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"px2:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPx2Title.Wrap( -1 )
		self.staticTextDisplayPx2Title.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPx2Title, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPx2Value = wx.StaticText( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPx2Value.Wrap( -1 )
		self.staticTextDisplayPx2Value.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPx2Value, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPyTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"py:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPyTitle.Wrap( -1 )
		self.staticTextDisplayPyTitle.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPyTitle, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPyValue = wx.StaticText( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPyValue.Wrap( -1 )
		self.staticTextDisplayPyValue.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPyValue, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPz1Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"pz1:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPz1Title.Wrap( -1 )
		self.staticTextDisplayPz1Title.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPz1Title, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPz1Value = wx.StaticText( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPz1Value.Wrap( -1 )
		self.staticTextDisplayPz1Value.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPz1Value, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPz2Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"pz2:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPz2Title.Wrap( -1 )
		self.staticTextDisplayPz2Title.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPz2Title, 0, wx.ALL, 5 )
		
		self.staticTextDisplayPz2Value = wx.StaticText( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplayPz2Value.Wrap( -1 )
		self.staticTextDisplayPz2Value.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerDisplayMotorSteps.Add( self.staticTextDisplayPz2Value, 0, wx.ALL, 5 )
		
		
		sbSizerDispaly.Add( fgSizerDisplayMotorSteps, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizerPanelMain.Add( sbSizerDispaly, 1, wx.ALL|wx.EXPAND, 5 )

		radioBoxChangeByChoices = [ u"SI units", u"motor steps" ]
		self.radioBoxChangeBy = wx.RadioBox( self.panelMain, wx.ID_ANY, u"Change By", wx.DefaultPosition, wx.DefaultSize, radioBoxChangeByChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxChangeBy.SetSelection( 0 )
		bSizerPanelMain.Add( self.radioBoxChangeBy, 0, wx.ALL, 5 )
		
		sbSizerChange = wx.StaticBoxSizer( wx.StaticBox( self.panelMain, wx.ID_ANY, u"Change Values" ), wx.HORIZONTAL )
		
		fgSizerChangeDisplacements = wx.FlexGridSizer( 5, 3, 0, 0 )
		fgSizerChangeDisplacements.SetFlexibleDirection( wx.BOTH )
		fgSizerChangeDisplacements.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextChangeXtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Xtrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeXtransTitle.Wrap( -1 )
		self.staticTextChangeXtransTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeXtransTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangeXtrans = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangeXtrans.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.textCtrlChangeXtrans, 0, wx.ALL, 5 )
		
		self.staticTextChangeXtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeXtransUnits.Wrap( -1 )
		self.staticTextChangeXtransUnits.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeXtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextChangeYtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Ytrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeYtransTitle.Wrap( -1 )
		self.staticTextChangeYtransTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeYtransTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangeYtrans = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangeYtrans.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.textCtrlChangeYtrans, 0, wx.ALL, 5 )
		
		self.staticTextChangeYtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeYtransUnits.Wrap( -1 )
		self.staticTextChangeYtransUnits.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeYtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextChangeZtransTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Ztrans:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeZtransTitle.Wrap( -1 )
		self.staticTextChangeZtransTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeZtransTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangeZtrans = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangeZtrans.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.textCtrlChangeZtrans, 0, wx.ALL, 5 )
		
		self.staticTextChangeZtransUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeZtransUnits.Wrap( -1 )
		self.staticTextChangeZtransUnits.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeZtransUnits, 0, wx.ALL, 5 )
		
		self.staticTextChangeXrotTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Xrot:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeXrotTitle.Wrap( -1 )
		self.staticTextChangeXrotTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeXrotTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangeXrot = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangeXrot.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.textCtrlChangeXrot, 0, wx.ALL, 5 )
		
		self.staticTextChangeXrotUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"rad", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeXrotUnits.Wrap( -1 )
		self.staticTextChangeXrotUnits.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeXrotUnits, 0, wx.ALL, 5 )
		
		self.staticTextChangeZrotTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"Zrot:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeZrotTitle.Wrap( -1 )
		self.staticTextChangeZrotTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeZrotTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangeZrot = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0.000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangeZrot.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.textCtrlChangeZrot, 0, wx.ALL, 5 )
		
		self.staticTextChangeZrotUnits = wx.StaticText( self.panelMain, wx.ID_ANY, u"rad", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangeZrotUnits.Wrap( -1 )
		self.staticTextChangeZrotUnits.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeDisplacements.Add( self.staticTextChangeZrotUnits, 0, wx.ALL, 5 )
		
		
		sbSizerChange.Add( fgSizerChangeDisplacements, 1, wx.EXPAND, 5 )
		
		self.staticlineChangeValuesSep = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		sbSizerChange.Add( self.staticlineChangeValuesSep, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizerChangeMotorSteps = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizerChangeMotorSteps.SetFlexibleDirection( wx.BOTH )
		fgSizerChangeMotorSteps.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.staticTextChangePx1Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"px1:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangePx1Title.Wrap( -1 )
		self.staticTextChangePx1Title.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeMotorSteps.Add( self.staticTextChangePx1Title, 0, wx.ALL, 5 )
		
		self.textCtrlChangePx1 = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangePx1.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlChangePx1.Enable(False)
		
		fgSizerChangeMotorSteps.Add( self.textCtrlChangePx1, 0, wx.ALL, 5 )
		
		self.staticTextChangePx2Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"px2:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangePx2Title.Wrap( -1 )
		self.staticTextChangePx2Title.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeMotorSteps.Add( self.staticTextChangePx2Title, 0, wx.ALL, 5 )
		
		self.textCtrlChangePx2 = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangePx2.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlChangePx2.Enable(False)
		
		fgSizerChangeMotorSteps.Add( self.textCtrlChangePx2, 0, wx.ALL, 5 )
		
		self.staticTextChangePyTitle = wx.StaticText( self.panelMain, wx.ID_ANY, u"py:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangePyTitle.Wrap( -1 )
		self.staticTextChangePyTitle.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeMotorSteps.Add( self.staticTextChangePyTitle, 0, wx.ALL, 5 )
		
		self.textCtrlChangePy = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangePy.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlChangePy.Enable(False)
		
		fgSizerChangeMotorSteps.Add( self.textCtrlChangePy, 0, wx.ALL, 5 )
		
		self.staticTextChangePz1Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"pz1:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangePz1Title.Wrap( -1 )
		self.staticTextChangePz1Title.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeMotorSteps.Add( self.staticTextChangePz1Title, 0, wx.ALL, 5 )
		
		self.textCtrlChangePz1 = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangePz1.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlChangePz1.Enable(False)
		
		fgSizerChangeMotorSteps.Add( self.textCtrlChangePz1, 0, wx.ALL, 5 )
		
		self.staticTextChangePz2Title = wx.StaticText( self.panelMain, wx.ID_ANY, u"pz2:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextChangePz2Title.Wrap( -1 )
		self.staticTextChangePz2Title.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizerChangeMotorSteps.Add( self.staticTextChangePz2Title, 0, wx.ALL, 5 )
		
		self.textCtrlChangePz2 = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textCtrlChangePz2.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
		self.textCtrlChangePz2.Enable(False)
		
		fgSizerChangeMotorSteps.Add( self.textCtrlChangePz2, 0, wx.ALL, 5 )
		
		
		sbSizerChange.Add( fgSizerChangeMotorSteps, 1, wx.EXPAND, 5 )
		
		
		bSizerPanelMain.Add( sbSizerChange, 0, wx.ALL|wx.EXPAND, 5 )
		
		gSizerControls = wx.GridSizer( 3, 2, 0, 0 )
		
		self.buttonMove = wx.Button( self.panelMain, wx.ID_ANY, u"MOVE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonMove.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		gSizerControls.Add( self.buttonMove, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonStop = wx.Button( self.panelMain, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonStop.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		gSizerControls.Add( self.buttonStop, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonSavePosition = wx.Button( self.panelMain, wx.ID_ANY, u"Save Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonSavePosition.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		gSizerControls.Add( self.buttonSavePosition, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonSelectPositions = wx.Button( self.panelMain, wx.ID_ANY, u"Select Positions (0)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonSelectPositions.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		gSizerControls.Add( self.buttonSelectPositions, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.buttonZeroAllChanges = wx.Button( self.panelMain, wx.ID_ANY, u"Zero All Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonZeroAllChanges.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		
		gSizerControls.Add( self.buttonZeroAllChanges, 0, wx.ALL|wx.EXPAND, 5 )

		"""
		self.buttonSetZeroMotorSteps = wx.Button( self.panelMain, wx.ID_ANY, u"Set ZERO Motor Steps", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonSetZeroMotorSteps.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
		self.buttonSetZeroMotorSteps.SetToolTipString( u"Sets current positions as ZERO motor steps" )
		
		gSizerControls.Add( self.buttonSetZeroMotorSteps, 0, wx.ALL|wx.EXPAND, 5 )
		"""
		
		
		bSizerPanelMain.Add( gSizerControls, 0, wx.EXPAND, 5 )
		
		
		self.panelMain.SetSizer( bSizerPanelMain )
		self.panelMain.Layout()
		self.panelMain.SetupScrolling()
		bSizerPanelMain.Fit( self.panelMain )
		bSizerFrameMain.Add( self.panelMain, 1, wx.EXPAND |wx.ALL, 0 )
		
		
		self.SetSizer( bSizerFrameMain )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.radioBoxChangeBy.Bind( wx.EVT_RADIOBOX, self.onSelectChangeBy )
		self.textCtrlChangeXtrans.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangeYtrans.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangeZtrans.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangeXrot.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangeZrot.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangePx1.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangePx2.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangePy.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangePz1.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.textCtrlChangePz2.Bind( wx.EVT_TEXT_ENTER, self.onChangePositionValuesEnter )
		self.buttonMove.Bind( wx.EVT_BUTTON, self.onMove )
		self.buttonStop.Bind( wx.EVT_BUTTON, self.onStop )
		self.buttonSavePosition.Bind( wx.EVT_BUTTON, self.onSavePosition )
		self.buttonSelectPositions.Bind( wx.EVT_BUTTON, self.onSelectionPositions )
		self.buttonZeroAllChanges.Bind( wx.EVT_BUTTON, self.onZeroAllChanges )
		#self.buttonSetZeroMotorSteps.Bind( wx.EVT_BUTTON, self.onSetZeroMotorSteps )
	
	def __del__( self ):
		pass

	def __parsedSavedPositions__(self):
		if os.path.exists(self.__savedPositionFile__):
			fHandle = open(self.__savedPositionFile__, 'r')
			for entry in fHandle:
				self.savedPositions.append(entry)
			fHandle.close()

	def enableControlButtons(self, enable):
		"""
		@Purpose:
			Enable the control buttons or not
		@Inputs:
			(bool) enable = True for enabling all control buttons, False otherwise
		"""
		self.buttonMove.Enable(enable)
		self.buttonSelectPositions.Enable(enable)
		self.buttonSavePosition.Enable(enable)
		self.buttonZeroAllChanges.Enable(enable)
		#self.buttonSetZeroMotorSteps.Enable(enable)

	def move(self):
		self.enableControlButtons(False)
		if self.radioBoxChangeBy.GetSelection() == 0:
			changes = [float(self.textCtrlChangeXtrans.GetValue()),
						float(self.textCtrlChangeYtrans.GetValue()),
						float(self.textCtrlChangeZtrans.GetValue()),
						float(self.textCtrlChangeXrot.GetValue()),
						float(self.textCtrlChangeZrot.GetValue())]
			self.stage.translateX(changes[0])
			self.stage.translateY(changes[1])
			self.stage.translateZ(changes[2])
			self.stage.rotateX(changes[3])
			self.stage.rotateZ(changes[4])
		else:
			changes = {'px1': int(self.textCtrlChangePx1.GetValue()),
						'px2': int(self.textCtrlChangePx2.GetValue()),
						'py': int(self.textCtrlChangePy.GetValue()),
						'pz1': int(self.textCtrlChangePz1.GetValue()),
						'pz2': int(self.textCtrlChangePz2.GetValue())}
			for motor in changes.keys():
				self.stage.moveMotor(motor, changes[motor])
		self.updateDisplay()
		self.onZeroAllChanges(None)
		self.enableControlButtons(True)
	
	def updateDisplay(self):
		"""
		@Purpose:
			update the display values
		@Inputs:
			(list) SI_units_changes = list of changes in SI units
		"""
		motorPositions = self.stage.getMotorPositions()
		positions = self.stage.getPositions()
		self.staticTextDisplayPx1Value.SetLabel("%d"%motorPositions[0])
		self.staticTextDisplayPx2Value.SetLabel("%d"%motorPositions[1])
		self.staticTextDisplayPyValue.SetLabel("%d"%motorPositions[2])
		self.staticTextDisplayPz1Value.SetLabel("%d"%motorPositions[3])
		self.staticTextDisplayPz2Value.SetLabel("%d"%motorPositions[4])
		self.staticTextDisplayXtransValue.SetLabel("%0.6f"%positions[0])
		self.staticTextDisplayYtransValue.SetLabel("%0.6f"%positions[1])
		self.staticTextDisplayZtransValue.SetLabel("%0.6f"%positions[2])
		self.staticTextDisplayXrotValue.SetLabel("%0.6f"%positions[3])
		self.staticTextDisplayZrotValue.SetLabel("%0.6f"%positions[4])

	# Virtual event handlers, overide them in your derived class
	def onClose( self, event ):
		threadID = self.__startThread__(self.stage.__del__)
		threadMap = self.__getThreadMap__()
		# start the progress (pulse) dialog
		pulseDialog = wx.ProgressDialog("Closing...", 
										"Moving Motors to ZERO steps, Please Wait...",
										maximum=100,
										parent=self,
										style=wx.PD_APP_MODAL)
		while threadMap[threadID].isAlive():
			pulseDialog.Pulse()
			time.sleep(0.01)
		pulseDialog.Destroy()
		self.Destroy()

	def onSelectChangeBy( self, event ):
		if self.radioBoxChangeBy.GetSelection() == 0:
			self.textCtrlChangeXtrans.Enable(True)
			self.textCtrlChangeYtrans.Enable(True)
			self.textCtrlChangeZtrans.Enable(True)
			self.textCtrlChangeXrot.Enable(True)
			self.textCtrlChangeZrot.Enable(True)
			self.textCtrlChangePx1.Enable(False)
			self.textCtrlChangePx2.Enable(False)
			self.textCtrlChangePy.Enable(False)
			self.textCtrlChangePz1.Enable(False)
			self.textCtrlChangePz2.Enable(False)
		else:
			self.textCtrlChangeXtrans.Enable(False)
			self.textCtrlChangeYtrans.Enable(False)
			self.textCtrlChangeZtrans.Enable(False)
			self.textCtrlChangeXrot.Enable(False)
			self.textCtrlChangeZrot.Enable(False)
			self.textCtrlChangePx1.Enable(True)
			self.textCtrlChangePx2.Enable(True)
			self.textCtrlChangePy.Enable(True)
			self.textCtrlChangePz1.Enable(True)
			self.textCtrlChangePz2.Enable(True)

	def onChangePositionValuesEnter( self, event ):
		self.buttonSelectPositions.SetLabel("Select Positions (0)")

	def onMove( self, event ):
		self.__startThread__(self.move)
	
	def onStop( self, event ):
		self.stage.abortAll()
		self.updateDisplay()
		self.enableControlButtons(True)
	
	def onSavePosition( self, event ):
		commentDlg = wx.TextEntryDialog(self, "Optional: Please enter a comment on this position.", "Enter a comment for this position.", "")
		if commentDlg.ShowModal() == wx.ID_OK:
			comment = commentDlg.GetValue()
			pos = tuple(self.stage.getMotorPositions())
			savedEntry = str(pos)+";"+comment
			self.savedPositions.append(savedEntry)
			fHandle = open(self.__savedPositionFile__, 'a')
			fHandle.write(savedEntry+'\n')
			fHandle.close()
	
	def onSelectionPositions( self, event ):
		choiceDlg = wx.SingleChoiceDialog(self, "Please Select a position to setup the changes.", "Select a Position", self.savedPositions, wx.CHOICEDLG_STYLE)
		choiceDlg.SetSize(wx.Size(700, 300))
		if choiceDlg.ShowModal() == wx.ID_OK:
			ind = choiceDlg.GetSelection()
			entry = self.savedPositions[ind]
			motorPos = eval(entry.split(';')[0])
			# set them up
			self.radioBoxChangeBy.SetSelection(1)
			self.onSelectChangeBy(event)
			self.textCtrlChangePx1.SetValue(str(motorPos[0]))
			self.textCtrlChangePx2.SetValue(str(motorPos[1]))
			self.textCtrlChangePy.SetValue(str(motorPos[2]))
			self.textCtrlChangePz1.SetValue(str(motorPos[3]))
			self.textCtrlChangePz2.SetValue(str(motorPos[4]))
			self.buttonSelectPositions.SetLabel("Select Positions ("+str(ind)+")")
	
	def onZeroAllChanges( self, event ):
		self.textCtrlChangeXtrans.SetValue("0.000000")
		self.textCtrlChangeYtrans.SetValue("0.000000")
		self.textCtrlChangeZtrans.SetValue("0.000000")
		self.textCtrlChangeXrot.SetValue("0.000000")
		self.textCtrlChangeZrot.SetValue("0.000000")
		self.textCtrlChangePx1.SetValue("0")
		self.textCtrlChangePx2.SetValue("0")
		self.textCtrlChangePy.SetValue("0")
		self.textCtrlChangePz1.SetValue("0")
		self.textCtrlChangePz2.SetValue("0")
		self.onChangePositionValuesEnter(event)

	"""
	def onSetZeroMotorSteps( self, event ):
		popUpOK = self.popInfoBox('Set Zero Motor Steps at current position', 'Setting Zero Motor Steps at Current Position!\nAre you sure to continue?')
		if popUpOK != wx.ID_OK:
			return
		else:
			self.stage.zeroMotorPositions()
			self.updateDisplay()
	"""


# Main
if __name__ == "__main__":
	controllers = [str(sys.argv[1]), str(sys.argv[2])]
	stage = NewFocus8081Stage(controllers)
	app = wx.PySimpleApp()
	frame = FrameMain(None, stage)
	frame.Show(True)
	app.MainLoop()