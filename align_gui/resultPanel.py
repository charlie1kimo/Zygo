"""
resultPanel:
    Contains PanelResult class and ResultGrid for displaying the Result panel and grids
"""

import wx
from wx_extensions.windows import ScrolledPanelBase
from adjustHexapodPanel import PanelAdjustHexapod
from moveTestPanel import PanelMoveTest

###########################################################################
## Class PanelResults
###########################################################################

class PanelResults (ScrolledPanelBase):
    
    def __init__(self, parent, alignObj):
        self.alignObj = alignObj
    
        ScrolledPanelBase.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CLIP_CHILDREN|wx.FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL)
        boxSizerSection = wx.BoxSizer(wx.HORIZONTAL)

        boxSizerContent = wx.BoxSizer(wx.VERTICAL)
        
        ##########################
        # result grid label
        ##########################
        self.staticTextTitle = wx.StaticText(self, wx.ID_ANY, "Compensator Results", wx.DefaultPosition, wx.DefaultSize, wx.EXPAND)
        self.staticTextTitle.Wrap(-1)
        self.staticTextTitle.SetFont(wx.Font(18, 70, 90, 92, False, wx.EmptyString))
        boxSizerContent.Add(self.staticTextTitle, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        ##########################
        # result grid
        ##########################
        self.gridResult = ResultGrid(self, self.alignObj)
        
        # Grid
        #self.gridResult.CreateGrid(len(self.usedperts), 4)
        self.gridResult.EnableEditing(True)
        self.gridResult.EnableGridLines(True)
        self.gridResult.EnableDragGridSize(False)
        self.gridResult.SetMargins(0, 0)
        
        # Columns
        self.gridResult.EnableDragColMove(False)
        self.gridResult.EnableDragColSize(True)
        #self.gridResult.SetColLabelSize(100)
        self.gridResult.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        
        # Rows
        self.gridResult.EnableDragRowSize(True)

        # Cell background color hack (make cells background = panel background for beauty)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.gridResult.SetDefaultCellBackgroundColour(color)
        
        # Cell Defaults
        self.gridResult.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.gridResult.SetFocus()
        self.gridResult.AutoSize()
        boxSizerContent.Add(self.gridResult, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        # Add data...
        self.updateData()
        # refresh grid widget
        self.refreshWidget(self.gridResult)

        boxSizerSection.Add(boxSizerContent, 1, wx.EXPAND|wx.ALL, 5)

        ##########################
        # control buttons
        ##########################
        boxSizerControls = wx.BoxSizer(wx.VERTICAL)

        self.staticTextControlsTitle = wx.StaticText(self, wx.ID_ANY, "Controls", wx.DefaultPosition, wx.DefaultSize, wx.ALL)
        self.staticTextControlsTitle.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
        boxSizerControls.Add(self.staticTextControlsTitle, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)

        self.staticlineControlSep = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        boxSizerControls.Add( self.staticlineControlSep, 0, wx.EXPAND|wx.ALL, 5 )

        self.buttonPlotFieldVectors = wx.Button(self, id=wx.ID_ANY, label="Plot Field Vectors")
        self.buttonPlotFieldVectors.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
        boxSizerControls.Add(self.buttonPlotFieldVectors, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)

        self.buttonAdjustHexapod = wx.Button(self, id=wx.ID_ANY, label="Adjust Hexapod")
        self.buttonAdjustHexapod.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
        boxSizerControls.Add(self.buttonAdjustHexapod, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)

        self.buttonMoveTest = wx.Button(self, id=wx.ID_ANY, label="Move Test")
        self.buttonMoveTest.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
        boxSizerControls.Add(self.buttonMoveTest, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)

        boxSizerSection.Add(boxSizerControls, 0, wx.EXPAND|wx.ALL, 5)
        ##########################
        
        self.SetSizer(boxSizerSection)
        self.Layout()
        self.SetupScrolling()
        boxSizerSection.Fit(self)

        # Connect Events
        self.Bind(wx.EVT_BUTTON, self.onPlotFieldVectors, self.buttonPlotFieldVectors)
        self.Bind(wx.EVT_BUTTON, self.onAdjustHexapod, self.buttonAdjustHexapod)
        self.Bind(wx.EVT_BUTTON, self.onMoveTest, self.buttonMoveTest)
    
    def __del__( self ):
        pass
        
    def setAlignObj(self, alignObj):
        self.alignObj = alignObj
        self.gridResult.setAlignObj(alignObj)
        
    def updateData(self):
        self.gridResult.setAlignObj(self.alignObj)
        self.gridResult.updateData()
        self.refreshWidget(self.gridResult)

    # event method
    def onPlotFieldVectors(self, event):
        self.alignObj.set_astig_vectors()

    def onAdjustHexapod(self, event):
        topWindow = self.getTopLevelWindow()
        topWindow.deleteTab("Adjust Hexapod")       # delete before proceed
        hexapodObj = topWindow.hexapodObj
        page = PanelAdjustHexapod(topWindow, self.alignObj, hexapodObj, topWindow.actuator)
        topWindow.addTab(page, "Adjust Hexapod")
        event.Skip()

    def onMoveTest(self, event):
        topWindow = self.getTopLevelWindow()
        topWindow.deleteTab("Move Test")
        page = PanelMoveTest(topWindow, self.alignObj)
        topWindow.addTab(page, "Move Test")
        event.Skip()

        
###########################################################################
## Class ResultGrid
###########################################################################
class ResultGrid(wx.grid.Grid):

    def __init__(self, parent, alignObj):
        self.parent = parent
        self.setAlignObj(alignObj)
        self.nameCol = 0
        self.adjCol = 1
        self.fixCol = 2
        self.cb = None         # initialization for the check box values!
        self.topWindow = self.getTopWindow()
        
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.EXPAND|wx.ALL)

        self.SetTable(ResultDataTable(self.alignObj), True)	# True for destroy table when grid is done
        self.RowLabelSize = 1
        self.ColLabelSize = 30
        
        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.SetColAttr(self.fixCol,attr)
        self.SetColSize(self.fixCol,20)
        self.SetDefaultCellFont(wx.Font(12, 70, 90, 90, False, wx.EmptyString))
        
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onMouse)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.onCellChange)
    
    ########
    # void return type
    ########
    def setAlignObj(self, alignObj):
        self.alignObj = alignObj
        self.p = self.alignObj.p_radians
        self.usedperts = self.alignObj.usedperts
        self.amounts = self.alignObj.amounts_radians
    
    #########
    # void return type
    #   update the data
    #########
    def updateData(self):
        self.GetTable().setAlignObj(self.alignObj)
        self.GetTable().updateData()
        self.AutoSize()
            
    def getTopWindow(self):
        topWindow = self.parent
        p = self.parent.GetParent()
        while p != None:
            p = p.GetParent()
            topWindow = topWindow.GetParent()
        return topWindow
        
    # BUGGY CODES
    def onMouse(self, evt):
        if evt.Col == self.fixCol:
            wx.CallLater(100, self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        self.cb.Value = not self.cb.Value
        self.afterCheckBox(self.cb.Value)

    def onCellSelected(self, evt):
        if evt.Col == self.fixCol:
            wx.CallAfter(self.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == self.fixCol:
            self.cb = evt.Control
            self.cb.WindowStyle |= wx.WANTS_CHARS
            self.cb.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()

    def onKeyDown(self, evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.DisableCellEditControl()
                self.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.GridCursorRow < (self.NumberRows-1):
                self.DisableCellEditControl()
                self.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.GridCursorCol > 0:
                self.DisableCellEditControl()
                self.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.GridCursorCol < (self.NumberCols-1):
                self.DisableCellEditControl()
                self.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self, evt):
        self.afterCheckBox(evt.IsChecked())
        evt.Skip()

    def afterCheckBox(self, isChecked):
        debug = False
        if debug:
            print "b4: ", self.alignObj.force
    
        row = self.GridCursorRow
        name = self.GetCellValue(row, self.nameCol)
        value = self.GetCellValue(row, self.adjCol)
        if isChecked:
            self.topWindow.setStatusMessage('%s is fixed to %s' % (name, value))
            self.alignObj.force[row] = float(value)
        else:
            self.topWindow.setStatusMessage('%s sets to None' % name)
            self.alignObj.force[row] = None
            
        if debug:
            print "af: ", self.alignObj.force
            
    def onCellChange(self, evt):
        row = self.GridCursorRow
        col = self.GridCursorCol
        name = self.GetCellValue(row, self.nameCol)
        if col == self.adjCol:
            if self.cb.Value:
                value = self.GetCellValue(row, col)
                self.topWindow.setStatusMessage('%s is fixed to %s' % (name, value))
                self.alignObj.force[row] = float(value)
        evt.Skip()
        
###########################################################################
## Class ResultDataTable
###########################################################################
class ResultDataTable(wx.grid.PyGridTableBase):

    def __init__(self, alignObj):
        self.setAlignObj(alignObj)
        self.updateData()
        
        wx.grid.PyGridTableBase.__init__(self)
        self.colLabels = ['Compensator', 'Solve Amounts', 'Fix', 'Sen Seed', 'Units']
        self.dataTypes = [wx.grid.GRID_VALUE_STRING,
                            wx.grid.GRID_VALUE_STRING,
                            wx.grid.GRID_VALUE_BOOL,
                            wx.grid.GRID_VALUE_STRING,
                            wx.grid.GRID_VALUE_STRING]
    
    #--------------------------------------------------
    # required methods for wxPyGridTableBase interfaces
    def GetNumberRows(self):
        return len(self.data)
        
    def GetNumberCols(self):
        return len(self.data[0])
    
    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True
    
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''
    
    def SetValue(self, row, col, value):
        self.data[row][col] = value
    
    def GetColLabelValue(self, col):
        return self.colLabels[col]
        
    def GetTypeName(self, row, col):
        return self.dataTypes[col]
    
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False
    
    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)
    
    #------------------
    # custom functions
    def setAlignObj(self, alignObj):
        self.alignObj = alignObj
        self.p = self.alignObj.p_radians
        self.usedperts = self.alignObj.usedperts
        self.amounts = self.alignObj.amounts_radians
        self.units = self.alignObj.units_radians
    
    def updateData(self):
        self.data = []
        for i in range(len(self.usedperts)):
            r = []
            r.append(self.usedperts[i])         # usedperts name
            r.append("%0.9f" % self.p[i])       # adjustment
            if self.alignObj.force[i] == None:  # fixed?
                r.append(0)
            else:
                r.append(1)
            r.append("%0.9f" % self.amounts[i]) # sens amounts
            r.append(self.units[i])             # units
            self.data.append(r)