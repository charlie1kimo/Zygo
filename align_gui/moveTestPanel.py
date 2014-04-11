"""
moveTestPanel.py
    this file contains class PanelMoveTest to perform other compensators' move test.
"""

import sys
import wx
import wx.grid as gridlib
from wx_extensions.windows import ScrolledPanelBase
from wx_extensions.grid import CustomDataGrid
from wx_extensions.exceptions import handlesErrors
sys.path.append('c:/motion')
try:
    import pobtest
    HAS_POBTEST_MOD = True
except ImportError, e:
    HAS_POBTEST_MOD = False

###########################################################################
## Class PanelMoveTest
###########################################################################

class PanelMoveTest ( ScrolledPanelBase ):

    def __init__( self, parent, alignObj ):
        self.alignObj = alignObj
        ScrolledPanelBase.__init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )

        bSizerPanel = wx.BoxSizer( wx.VERTICAL )

        ##########################
        # Move Test panel title
        ##########################
        self.staticTextMoveTestTitle = wx.StaticText( self, wx.ID_ANY, u"Move Test (ID: "+self.alignObj.hexapodID+")", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextMoveTestTitle.Wrap( -1 )
        self.staticTextMoveTestTitle.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )

        bSizerPanel.Add( self.staticTextMoveTestTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        bSizerMoveGrid = wx.BoxSizer( wx.HORIZONTAL )

        ##########################
        # moveTest grid
        ##########################
        labels = ["Compensator", "POB Motion", "Solve Amounts", "Include", "Move", "Units"]
        dataTypes = [gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT+':6,9', gridlib.GRID_VALUE_BOOL, gridlib.GRID_VALUE_FLOAT+':6,9', gridlib.GRID_VALUE_STRING]
        self.moveTestGrid = CustomDataGrid(self, labels, dataTypes)
        self.updateMoveTestGrid()
        self.moveTestGrid.SetColLabelSize(30)
        self.moveTestGrid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.moveTestGrid.AutoSize()

        #####
        # Cell Attributes
        #####
        self.moveTestGrid.SetColReadOnly(0)
        self.moveTestGrid.SetColReadOnly(1)
        self.moveTestGrid.SetColReadOnly(2)
        self.moveTestGrid.SetColReadOnly(4)
        self.moveTestGrid.SetColReadOnly(5)

        bSizerMoveGrid.Add( self.moveTestGrid, 0, wx.ALL, 5 )
        ########################################## END moveTestGrid ########################################

        bSizerMoveGridControl = wx.BoxSizer( wx.VERTICAL )

        self.buttonIncludeAll = wx.Button( self, wx.ID_ANY, u"Include All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMoveGridControl.Add( self.buttonIncludeAll, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )

        self.textCtrlFactor = wx.TextCtrl( self, wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMoveGridControl.Add( self.textCtrlFactor, 0, wx.ALL, 5 )

        self.buttonFactor = wx.Button( self, wx.ID_ANY, u"Set Factor", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMoveGridControl.Add( self.buttonFactor, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )


        bSizerMoveGrid.Add( bSizerMoveGridControl, 0, wx.ALL, 5 )


        bSizerPanel.Add( bSizerMoveGrid, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.buttonMove = wx.Button( self, wx.ID_ANY, u"MOVE", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.buttonMove.SetFont( wx.Font( 14, 70, 90, 92, False, wx.EmptyString ) )
        if not HAS_POBTEST_MOD:
            self.buttonMove.SetToolTipString( u"Disabled due to \"pobtest module\" not found." )
            self.buttonMove.Enable(False)

        bSizerPanel.Add( self.buttonMove, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        self.SetSizer( bSizerPanel )
        self.Layout()

        # Connect Events
        self.moveTestGrid.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.onMoveTestGridChange )
        self.buttonIncludeAll.Bind( wx.EVT_BUTTON, self.onInclude )
        self.buttonFactor.Bind( wx.EVT_BUTTON, self.onSetFactor )
        self.buttonMove.Bind( wx.EVT_BUTTON, self.onMove )

    def __del__( self ):
        pass

    @handlesErrors
    def moveCompensators(self):
        """
        @Purpose:
            move the pob compensators; only gets call if pobtest module is presented.
            notes:
            RETRO:
                pobtest.retsphere.movex
                pobtest.retsphere.movey
                pobtest.retsphere.movez

            TRANS: (object)
                pobtest.tsxmotor.move
                pobtest.tsymotor.move
                pobtest.tszmotor.move
        """
        self.buttonMove.Enable(False)
        # functions corresponding to ordering: [xtrans_obj, ytrans_obj, ztrans_obj, xtran_retro, ytrans_retro, ztrans_retro]
        moveFuncts = [pobtest.tsxmotor.move, pobtest.tsymotor.move, pobtest.tszmotor.move,
                    pobtest.retsphere.movex, pobtest.retsphere.movey, pobtest.retsphere.movez]
        for ind in xrange(len(moveFuncts)):
            if self.moveTestGrid.GetCellValue(ind, 3):
                moveAmounts = self.moveTestGrid.GetCellValue(ind, 4)
                moveFuncts[ind](moveAmounts)
        self.getTopLevelWindow().statusBarMain.PulseStop()
        self.buttonMove.Enable(True)

    @handlesErrors
    def updateMoveTestGrid(self):
        """
        @Purpose:
            Initialize the moveTestGrid
        """
        XY_OBJECT_TO_RETRO_SCALE = -0.2
        compensators_map = {'xtrans_object': 'TS_X',
                            'ytrans_object': 'TS_Y',
                            'ztrans_object': 'TS_Z',
                            'xtrans_retro': 'RET_X',
                            'ytrans_retro': 'RET_Y',
                            'ztrans_retro': 'RET_Z'}
        compensators = ['xtrans_object', 'ytrans_object', 'ztrans_object', 'xtrans_retro', 'ytrans_retro', 'ztrans_retro']
        for ind in range(len(compensators)):
            self.moveTestGrid.SetCellValue(ind, 0, compensators[ind])           # compensators
            self.moveTestGrid.SetCellValue(ind, 1, compensators_map[compensators[ind]])
            try:
                comp_index = list(self.alignObj.usedperts).index(compensators[ind])
                solve_amounts = self.alignObj.p_radians[comp_index]
                units = self.alignObj.units_radians[comp_index]
            except ValueError, e:
                if compensators[ind] == 'xtrans_retro':
                    solve_amounts = self.moveTestGrid.GetCellValue(0, 2) * XY_OBJECT_TO_RETRO_SCALE
                    units = 'mm'
                elif compensators[ind] == 'ytrans_retro':
                    solve_amounts = self.moveTestGrid.GetCellValue(1, 2) * XY_OBJECT_TO_RETRO_SCALE
                    units = 'mm'
                else:
                    raise e
            self.moveTestGrid.SetCellValue(ind, 2, solve_amounts)               # solve amounts
            self.moveTestGrid.SetCellValue(ind, 3, False)                       # Include
            self.moveTestGrid.SetCellValue(ind, 4, 0.0)                         # move (default = 0.0)
            self.moveTestGrid.SetCellValue(ind, 5, units)                       # units
        self.refreshWidget(self.moveTestGrid)

    # Virtual event handlers, overide them in your derived class
    def onMoveTestGridChange( self, event ):
        event_row = event.GetRow()
        event_col = event.GetCol()
        if event_col == 3:                                                          # include changed
            if self.moveTestGrid.GetCellValue(event_row, event_col):                # including, copy the solve adjustment ot move
                copy_value = -1 * self.moveTestGrid.GetCellValue(event_row, 2)      # reverse the sign of move.
                self.moveTestGrid.SetCellValue(event_row, 4, copy_value)
                self.moveTestGrid.SetReadOnly(event_row, 4, False)                  # including, should be editable.
            else:
                self.moveTestGrid.SetCellValue(event_row, 4, 0.0)                   # excluding, set to default 0.0
                self.buttonIncludeAll.SetLabel("Include All")                       # include button should be include all cus we exclude one here.
                self.moveTestGrid.SetReadOnly(event_row, 4, True)                   # excluding, should NOT be editable.
        self.refreshWidget(self.moveTestGrid)

    def onInclude( self, event ):
        allIncluded = True
        for row in range(self.moveTestGrid.GetNumberRows()):
            if not self.moveTestGrid.GetCellValue(row, 3):
                allIncluded = False
                break
        if allIncluded:                                                         # excluding everything
            self.buttonIncludeAll.SetLabel("Include All")
            for row in range(self.moveTestGrid.GetNumberRows()):
                self.moveTestGrid.SetCellValue(row, 3, False)
                self.moveTestGrid.SetCellValue(row, 4, 0.0)
                self.moveTestGrid.SetReadOnly(row, 4, True)
        else:                                                                   # including everything
            self.buttonIncludeAll.SetLabel("Exclude All")
            for row in range(self.moveTestGrid.GetNumberRows()):
                self.moveTestGrid.SetCellValue(row, 3, True)
                copy_value = -1 * self.moveTestGrid.GetCellValue(row, 2)    # reverse the move sign
                self.moveTestGrid.SetCellValue(row, 4, copy_value)
                self.moveTestGrid.SetReadOnly(row, 4, False)
        self.refreshWidget(self.moveTestGrid)

    def onSetFactor( self, event ):
        factor = float(self.textCtrlFactor.GetValue())
        for row in range(self.moveTestGrid.GetNumberRows()):
            move_value = self.moveTestGrid.GetCellValue(row, 4)
            self.moveTestGrid.SetCellValue(row, 4, move_value*factor)
        self.refreshWidget(self.moveTestGrid)

    def onMove( self, event ):
        clicked = self.popInfoBox("Ensure Motor GUI program is CLOSED",
                            "Please CLOSE the MOTOR GUI PROGRAM if you haven't done so. Press OK to continue or Cancel to cancel to process.")
        if HAS_POBTEST_MOD and clicked == wx.ID_OK:
            self.getTopLevelWindow().statusBarMain.PulseStart()
            self.__startThread__(self.moveCompensators)


