# -*- coding: utf-8 -*- 
"""
test_align_gui.py
    This program implements a GUI for test align for MET5/R1
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/11/2013   cchen   first created
'''

import wx
import wx.grid as gridlib
from wx_extensions.windows import FrameBase
from wx_extensions.windows import ScrolledPanelBase
from wx_extensions.grid import CustomDataGrid
from sc_testalignpy import testalign

###########################################################################
## Class FrameMain
###########################################################################

class FrameMain ( FrameBase ):
    
    def __init__( self, parent ):
        self.testAlignObj = None
    
        FrameBase.__init__ ( self, parent, id = wx.ID_ANY, title = u"test align gui", pos = wx.DefaultPosition, size = wx.Size( 900,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizerFrameMain = wx.BoxSizer( wx.VERTICAL )
        
        self.panelMain = ScrolledPanelBase( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerPanelMain = wx.BoxSizer( wx.VERTICAL )
        
        bSizerFile = wx.BoxSizer( wx.HORIZONTAL )
        
        self.staticTextFileNameRoot = wx.StaticText( self.panelMain, wx.ID_ANY, u"File Name Root:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextFileNameRoot.Wrap( -1 )
        bSizerFile.Add( self.staticTextFileNameRoot, 0, wx.ALL, 5 )
        
        self.textCtrlFileNameRoot = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"ytesta", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlFileNameRoot.SetMinSize( wx.Size( 150,-1 ) )
        
        bSizerFile.Add( self.textCtrlFileNameRoot, 0, wx.ALL, 5 )
        
        self.staticTextExtension = wx.StaticText( self.panelMain, wx.ID_ANY, u"Extension:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextExtension.Wrap( -1 )
        bSizerFile.Add( self.staticTextExtension, 0, wx.ALL, 5 )
        
        self.textCtrlExtension = wx.TextCtrl( self.panelMain, wx.ID_ANY, u"dat", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerFile.Add( self.textCtrlExtension, 0, wx.ALL, 5 )
        
        bSizerPanelMain.Add( bSizerFile, 0, wx.EXPAND, 5 )
        
        bSizerMode = wx.BoxSizer( wx.HORIZONTAL )
        
        self.radioBoxModeChoices = [ u"b", u"c", u"cghz", u"nocgh" ]
        self.radioBoxMode = wx.RadioBox( self.panelMain, wx.ID_ANY, u"Mode", wx.DefaultPosition, wx.DefaultSize, self.radioBoxModeChoices, 1, wx.RA_SPECIFY_ROWS )
        self.radioBoxMode.SetSelection( 0 )
        bSizerMode.Add( self.radioBoxMode, 0, wx.ALL, 5 )
        
        self.buttonFileUpdate = wx.Button( self.panelMain, wx.ID_ANY, u"UPDATE", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMode.Add( self.buttonFileUpdate, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.textCtrlOutput = wx.TextCtrl( self.panelMain, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMode.Add( self.textCtrlOutput, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.buttonWriteReport = wx.Button( self.panelMain, wx.ID_ANY, u"Write Report", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMode.Add( self.buttonWriteReport, 0, wx.ALL|wx.EXPAND, 5 )
        
        bSizerPanelMain.Add( bSizerMode, 0, wx.EXPAND, 5 )
        
        self.staticlineSep1 = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizerPanelMain.Add( self.staticlineSep1, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizerGrids = wx.BoxSizer( wx.HORIZONTAL )
        
        # Grid data
        dataLabels = ['Variables', 'Input Values (nm)', 'Residual Values (nm)', 'Weights']
        dataTypes = [gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT+':6,2', gridlib.GRID_VALUE_FLOAT+':6,2', gridlib.GRID_VALUE_FLOAT+':6,1']
        self.gridData1 = CustomDataGrid(self.panelMain, dataLabels, dataTypes)
        
        # Cell1 Defaults
        self.gridData1.SetDefaultCellFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
        self.gridData1.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_TOP )
        bSizerGrids.Add( self.gridData1, 0, wx.ALL, 5 )
        self.gridData1.Hide()
        
        self.staticlineGridSep = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizerGrids.Add( self.staticlineGridSep, 0, wx.EXPAND |wx.ALL, 5 )
        
        # Cell2 Defaults
        dataLabels = ['Compensator', 'Force', 'Solve Amount', 'Unit', 'Exclude Move']
        dataTypes = [gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT+':6,5', gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_BOOL]
        self.gridData2 = CustomDataGrid(self.panelMain, dataLabels, dataTypes)
        
        self.gridData2.SetDefaultCellFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
        self.gridData2.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_TOP )
        bSizerGrids.Add( self.gridData2, 0, wx.ALL, 5 )
        self.gridData2.Hide()
        self.setupDataTable()
        
        bSizerPanelMain.Add( bSizerGrids, 1, wx.EXPAND, 5 )
        
        self.staticlineSep2 = wx.StaticLine( self.panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizerPanelMain.Add( self.staticlineSep2, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizerControl = wx.BoxSizer( wx.HORIZONTAL )
        
        self.buttonSolve = wx.Button( self.panelMain, wx.ID_ANY, u"SOLVE", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerControl.Add( self.buttonSolve, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.buttonMove = wx.Button( self.panelMain, wx.ID_ANY, u"MOVE", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerControl.Add( self.buttonMove, 1, wx.ALL|wx.EXPAND, 5 )
        
        bSizerPanelMain.Add( bSizerControl, 0, wx.EXPAND, 5 )
        
        self.panelMain.SetSizer( bSizerPanelMain )
        self.panelMain.Layout()
        bSizerPanelMain.Fit( self.panelMain )
        bSizerFrameMain.Add( self.panelMain, 1, wx.EXPAND |wx.ALL, 0 )
        
        self.SetSizer( bSizerFrameMain )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.buttonFileUpdate.Bind( wx.EVT_BUTTON, self.onFileUpdate )
        self.buttonWriteReport.Bind( wx.EVT_BUTTON, self.onWriteReport )
        self.gridData1.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.onChangeParams )
        self.gridData2.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.onChangeParams )
        self.buttonSolve.Bind( wx.EVT_BUTTON, self.onSolve )
        self.buttonMove.Bind( wx.EVT_BUTTON, self.onMove )
    
    def __del__( self ):
        pass
    
    
    def setupDataTable(self):
        # formating the column sizes (for fitting labels)
        readonlyColAttr = gridlib.GridCellAttr()
        readonlyColAttr.SetReadOnly(True)
        readonly1Cols = [0,1,2]
        readonly2Cols = [0,2,3]
        for col in readonly1Cols:
            self.gridData1.SetColAttr(col, readonlyColAttr)
        for col in readonly2Cols:
            self.gridData2.SetColAttr(col, readonlyColAttr)
        self.gridData1.SetRowLabelSize(1)
        self.gridData2.SetRowLabelSize(1)
        self.excludeList = []                   # reset exclude list
        self.refreshWidget(self.gridData1)
        self.refreshWidget(self.gridData2)
        
    def updateDataTable(self):
        for varInd in range(len(self.testAlignObj.allterms)):
            self.gridData1.SetCellValue(varInd, 0, self.testAlignObj.allterms[varInd])
            self.gridData1.SetCellValue(varInd, 1, self.testAlignObj.meas_variables[varInd])
            if self.testAlignObj.res == None:
                self.gridData1.SetCellValue(varInd, 2, 0.0)
            else:
                self.gridData1.SetCellValue(varInd, 2, self.testAlignObj.res[varInd])
            self.gridData1.SetCellValue(varInd, 3, float(self.testAlignObj.weights[varInd]))
            
        for cInd in range(len(self.testAlignObj.usedperts)):
            self.gridData2.SetCellValue(cInd, 0, self.testAlignObj.usedperts[cInd])
            self.gridData2.SetCellValue(cInd, 1, str(self.testAlignObj.force[cInd]))
            if self.testAlignObj.p == None:
                self.gridData2.SetCellValue(cInd, 2, 0.0)
            else:
                self.gridData2.SetCellValue(cInd, 2, self.testAlignObj.p[cInd])
            self.gridData2.SetCellValue(cInd, 3, self.testAlignObj.sens[self.testAlignObj.usedperts[cInd]]['units'])
            if self.testAlignObj.usedperts[cInd] in self.excludeList:
                self.gridData2.SetCellValue(cInd, 4, True)
            else:
                self.gridData2.SetCellValue(cInd, 4, False)
            
        self.gridData1.Show()
        self.gridData2.Show()
        self.gridData1.AutoSize()
        self.gridData2.AutoSize()
        self.refreshWidget(self.gridData1)
        self.refreshWidget(self.gridData2)
    
    # Virtual event handlers, overide them in your derived class
    def onFileUpdate( self, event ):
        fileRoot = self.textCtrlFileNameRoot.GetValue()
        fileExt = self.textCtrlExtension.GetValue()
        modeSelect = self.radioBoxModeChoices[self.radioBoxMode.GetSelection()]
        if len(fileRoot) == 0 or len(fileExt) == 0:
            self.popErrorBox('ERROR', 'ERROR: file name root or file extension CANNOT be EMPTY!')
            return
        
        self.testAlignObj = testalign.TestAlign(force=modeSelect)
        self.testAlignObj.get_gsmeas_variables(fileRoot, fileExt)
        self.textCtrlOutput.SetValue(self.testAlignObj.writename)
        
        self.gridData1.ClearTable()             # clear before proceed.
        self.gridData2.ClearTable()             # clear.
        self.updateDataTable()
        self.setupDataTable()
        
    def onWriteReport( self, event ):
        if self.testAlignObj != None:
            self.testAlignObj.write(self.textCtrlOutput.GetValue())
    
    def onChangeParams( self, event ):
        row = event.GetRow()
        col = event.GetCol()
        
        if event.GetEventObject() == self.gridData1:        # update weights
            self.testAlignObj.weights[row] = self.gridData1.GetCellValue(row, col)
            self.testAlignObj.set_weights(self.testAlignObj.weights)
        else:
            if col == 1:                                    # update force
                forceData = self.gridData2.GetCellValue(row, col)
                if forceData == 'None':
                    forceData = None
                else:
                    forceData = float(forceData)
                self.testAlignObj.force[row] = forceData
                self.testAlignObj.set_force(self.testAlignObj.force)
            elif col == 4:                                  # update exclude move list
                if self.gridData2.GetCellValue(row, col):
                    self.excludeList.append(self.gridData2.GetCellValue(row, 0))
                else:
                    self.excludeList.remove(self.gridData2.GetCellValue(row, 0))
    
    def onSolve( self, event ):
        self.testAlignObj.solve()
        self.updateDataTable()
        event.Skip()
    
    def onMove( self, event ):
        self.testAlignObj.move_solve(exclude=self.excludeList)
        self.updateDataTable()
        event.Skip()
    
    
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = FrameMain(None)
    frame.Show(True)
    app.MainLoop()


