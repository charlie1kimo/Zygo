"""
displayPanel.py
    This module / class handles the displaying panel.
"""

import re
import wx
from wx_extensions.windows import ScrolledPanelBase

###########################################################################
## Class PanelDisplayFields
###########################################################################

class PanelDisplayFields (ScrolledPanelBase):
    
    def __init__(self, parent, alignObj, mode):
        self.parent = parent
        self.topWindow = self.getTopWindow()
        self.mode = mode
        self.setAlignObj(alignObj, mode)
        (self.terms, self.params) = self.parseFieldsData()
        self.diff = self.parseDiffData()
        ##### custom params notes #####
        self.paramsNotes = {'z5': 'weights must be 0', 'z6': 'weights must be 0'}
        
        ScrolledPanelBase.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CLIP_CHILDREN|wx.FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL)
        #wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.FULL_REPAINT_ON_RESIZE|wx.TAB_TRAVERSAL)
        
        boxSizerPanelSection = wx.BoxSizer( wx.HORIZONTAL )

        ######### LEFT PANEL ##########
        self.boxSizerPanelDisplay = wx.BoxSizer(wx.VERTICAL)        
        #self.scrolledWindowPanelDisplay = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        #self.scrolledWindowPanelDisplay.SetScrollRate(5, 5)
        #boxSizerScrolled = wx.BoxSizer(wx.VERTICAL)
        
        #self.panelContent = wx.Panel(self.scrolledWindowPanelDisplay, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.EXPAND|wx.ALL)
        #boxSizerContent = wx.BoxSizer(wx.VERTICAL)
        
        ##########################
        # 1st display grid label
        ##########################
        self.staticTextTitleDisplay = wx.StaticText(self, wx.ID_ANY, "Measured Dependent Variables and Weights", wx.DefaultPosition, wx.DefaultSize, wx.EXPAND)
        self.staticTextTitleDisplay.Wrap(-1)
        self.staticTextTitleDisplay.SetFont(wx.Font(18, 70, 90, 92, False, wx.EmptyString))
        self.boxSizerPanelDisplay.Add(self.staticTextTitleDisplay, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        #######################################
        # 1st display fields / parameters grid
        #######################################
        self.gridDisplayScrolledPanel = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.EXPAND)
        
        # Grid
        self.gridDisplayScrolledPanel.CreateGrid(len(self.params), len(self.terms)*2+1)     # (col + 1) cus of notes
        self.gridDisplayScrolledPanel.EnableEditing(self.gridEditable)
        self.gridDisplayScrolledPanel.EnableGridLines(True)
        self.gridDisplayScrolledPanel.EnableDragGridSize(False)
        self.gridDisplayScrolledPanel.SetMargins(0, 0)
        
        # Columns
        self.gridDisplayScrolledPanel.EnableDragColMove(False)
        self.gridDisplayScrolledPanel.EnableDragColSize(True)
        self.gridDisplayScrolledPanel.SetColLabelSize(30)
        self.gridDisplayScrolledPanel.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        
        # Rows
        self.gridDisplayScrolledPanel.EnableDragRowSize(True)
        self.gridDisplayScrolledPanel.SetRowLabelSize(80)
        self.gridDisplayScrolledPanel.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        
        # Label Appearance
        for row in range(len(self.params)):
            self.gridDisplayScrolledPanel.SetRowLabelValue(row, self.params[row])
        for col in range(len(self.terms)):
            self.gridDisplayScrolledPanel.SetColLabelValue(col*2, self.terms[col])
            self.gridDisplayScrolledPanel.SetColLabelValue(col*2+1, 'weights')
        # finish labeling notes on last
        self.gridDisplayScrolledPanel.SetColLabelValue(len(self.terms)*2, 'notes')
        
        # fill the content
        self.updateMeasuredData()
        
        # Cell Defaults
        self.gridDisplayScrolledPanel.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.boxSizerPanelDisplay.Add(self.gridDisplayScrolledPanel, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
        # Cell autoSize
        self.gridDisplayScrolledPanel.AutoSize()
        # Cell Change event
        self.gridDisplayScrolledPanel.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.onDisplayCellChange)
        # Cell background color hack (make cells background = panel background for beauty)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.gridDisplayScrolledPanel.SetDefaultCellBackgroundColour(color)
        # relayout
        self.refreshWidget(self.gridDisplayScrolledPanel)
        
        ##########################
        # 2nd display grid label
        ##########################
        self.staticTextTitleDisplayDiff = wx.StaticText(self, wx.ID_ANY, "Key Differences", wx.DefaultPosition, wx.DefaultSize, wx.EXPAND)
        self.staticTextTitleDisplayDiff.Wrap(-1)
        self.staticTextTitleDisplayDiff.SetFont(wx.Font(18, 70, 90, 92, False, wx.EmptyString))
        self.boxSizerPanelDisplay.Add(self.staticTextTitleDisplayDiff, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        ###############################
        # 2nd display difference grid
        ###############################
        self.gridDisplayDiffScrolledPanel = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.EXPAND)
        
        # Grid
        self.gridDisplayDiffScrolledPanel.CreateGrid(len(self.diff), 2)
        self.gridDisplayDiffScrolledPanel.EnableEditing(self.gridEditable)
        self.gridDisplayDiffScrolledPanel.EnableGridLines(True)
        self.gridDisplayDiffScrolledPanel.EnableDragGridSize(False)
        self.gridDisplayDiffScrolledPanel.SetMargins(0, 0)
        
        # Columns
        self.gridDisplayDiffScrolledPanel.EnableDragColMove(False)
        self.gridDisplayDiffScrolledPanel.EnableDragColSize(True)
        self.gridDisplayDiffScrolledPanel.SetColLabelSize(30)
        self.gridDisplayDiffScrolledPanel.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        # set value column (index 0 column non-editable)
        colAttr = wx.grid.GridCellAttr()
        colAttr.SetReadOnly(True)
        self.gridDisplayDiffScrolledPanel.SetColAttr(0, colAttr)
        
        # Rows
        self.gridDisplayDiffScrolledPanel.EnableDragRowSize(True)
        self.gridDisplayDiffScrolledPanel.SetRowLabelSize(200)
        self.gridDisplayDiffScrolledPanel.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        
        # Label Appearance
        for row in range(len(self.diff)):
            self.gridDisplayDiffScrolledPanel.SetRowLabelValue(row, self.diff[row])
        self.gridDisplayDiffScrolledPanel.SetColLabelValue(0, 'value')
        self.gridDisplayDiffScrolledPanel.SetColLabelValue(1, 'weights')
        
        # fill the content
        self.updateDiffData()
        
        # Cell Defaults
        self.gridDisplayDiffScrolledPanel.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.boxSizerPanelDisplay.Add(self.gridDisplayDiffScrolledPanel, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
        # Cell autoSize
        self.gridDisplayDiffScrolledPanel.AutoSize()
        # Cell Change event
        self.gridDisplayDiffScrolledPanel.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.onDiffCellChange)
        # Cell background color hack (make cells background = panel background for beauty)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.gridDisplayDiffScrolledPanel.SetDefaultCellBackgroundColour(color)
        # relayout
        self.refreshWidget(self.gridDisplayScrolledPanel)

        boxSizerPanelSection.Add( self.boxSizerPanelDisplay, 1, wx.EXPAND |wx.ALL, 5 )
        ############# LEFT PANEL ##############

        ############# RIGHT PANEL #############
        self.bSizerPanelControl = wx.BoxSizer( wx.VERTICAL )
        
        boxSizerPanelSection.Add( self.bSizerPanelControl, 0, wx.EXPAND, 5 )
        ############ RIGHT PANEL ##############
        
        self.SetSizer(boxSizerPanelSection)
        self.Layout()
        self.SetupScrolling()
        boxSizerPanelSection.Fit(self)
    
    def __del__(self):
        pass
    
    def setAlignObj(self, alignObj, mode):
        self.alignObj = alignObj
        self.gridEditable = True
        if mode == 'z':
            self.values = self.alignObj.z
        elif mode == 'res':
            self.values = self.alignObj.res
            self.gridEditable = False
    
    def getTopWindow(self):
        topWindow = self.parent
        p = self.parent.GetParent()
        while p != None:
            p = p.GetParent()
            topWindow = topWindow.GetParent()
        return topWindow
    
    #######################################
    # onDisplayCellChange: 
    #   callback function for changing a cell in measured data grid
    #   TODO:
    #       1. self.alignObj.weights elements are INT ---> keep INT for now.
    #######################################
    def onDisplayCellChange(self, event):
        debug = False
        if debug:
            print "b4:"
            print "allterms: ", self.alignObj.allterms
            print "z: ", self.alignObj.z
            print "allterms: ", self.alignObj.weights
    
        row = event.GetRow()
        col = event.GetCol()
        term = self.terms[col/2] + "_" + self.params[row]
        i = list(self.alignObj.allterms).index(term)
        value = self.gridDisplayScrolledPanel.GetCellValue(event.GetRow(), event.GetCol())
        if col % 2 == 0:            # changing z values
            self.topWindow.setStatusMessage("changed "+term+" z value from "+str(self.alignObj.z[i])+" to "+value)
            self.alignObj.z[i] = value                      # value is string CONVERTED in numpy
        else:                       # changing weights
            self.topWindow.setStatusMessage("changed "+term+" weights from "+str(self.alignObj.weights[i])+" to "+value)
            self.alignObj.weights[i] = int(value)         # int

        # updated the parameters, need to reset previous solutions
        self.alignObj.p = None
        
        if debug:
            print "af:"
            print "allterms: ", self.alignObj.allterms
            print "z: ", self.alignObj.z
            print "allterms: ", self.alignObj.weights
        
        event.Skip()
        
    ###########################################
    # onDiffCellChange:
    #   callback function for change a cell in key difference grid
    ###########################################
    def onDiffCellChange(self, event):
        debug = False
        if debug:
            print "b4:"
            print "allterms: ", self.alignObj.allterms
            print "z: ", self.alignObj.z
            print "allterms: ", self.alignObj.weights
    
        row = event.GetRow()
        col = event.GetCol()
        term = self.diff[row]
        i = list(self.alignObj.allterms).index(term)
        value = self.gridDisplayDiffScrolledPanel.GetCellValue(event.GetRow(), event.GetCol())
        if col == 0:                # changing z value
            self.topWindow.setStatusMessage("changed "+term+" z value from "+str(self.alignObj.z[i])+" to "+value)
            self.alignObj.z[i] = value
        else:                       # changing weights
            self.topWindow.setStatusMessage("changed "+term+" weights from "+str(self.alignObj.weights[i])+" to "+value)
            self.alignObj.weights[i] = int(value)         # int
            
        if debug:
            print "af:"
            print "allterms: ", self.alignObj.allterms
            print "z: ", self.alignObj.z
            print "allterms: ", self.alignObj.weights        
        event.Skip()
     
    # parseFiledsData:
    #   returning (terms, params)
    #       terms = list of terms (rows)
    #       params = list of parameters (cols)
    def parseFieldsData(self):
        terms = self.alignObj.allterms
        
        allterms = []
        params = []
        for i in range(len(terms)):
            if not re.search('-', terms[i]):
                tempList = terms[i].split('_')
                tempTerm = tempList[0] + "_" + tempList[1]
                tempParam = tempList[2]
                if not tempTerm in allterms:
                    allterms.append(tempTerm)
                if not tempParam in params:
                    params.append(tempParam)
                
        return (allterms, params)
    
    # parseDiffData:
    #   parse the key difference terms out from the alignObj
    #   return:
    #       diff = a list contains the name of all the key difference terms
    def parseDiffData(self):
        terms = self.alignObj.allterms
        diff = []
        for term in terms:
            if re.search('-', term):
                diff.append(term)
                
        return diff
    
    # updateMeasuredData:
    #   update the measured data grid
    #   return: N/A
    def updateMeasuredData(self):
        for col in range(len(self.terms)):
            term = self.terms[col]
            for row in range(len(self.params)):
                term = self.terms[col]
                term = term + "_" + self.params[row]
                i = list(self.alignObj.allterms).index(term)
                self.gridDisplayScrolledPanel.SetCellValue(row, col*2, '%0.2f' % self.values[i])
                self.gridDisplayScrolledPanel.SetCellValue(row, col*2+1, '%d' % self.alignObj.weights[i])

        # setup the notes column
        col = self.gridDisplayScrolledPanel.GetNumberCols()-1
        for row in range(len(self.params)):
            if self.paramsNotes.has_key(self.params[row]):
                self.gridDisplayScrolledPanel.SetCellValue(row, col, self.paramsNotes[self.params[row]])
        self.gridDisplayScrolledPanel.AutoSize()
    
    # updateDiffData:
    #   update the key difference data grid
    #   return: N/A
    def updateDiffData(self):
        specialTerm = "ztrans_obj - ztrans_ret"
        for row in range(len(self.diff)):
            i = list(self.alignObj.allterms).index(self.diff[row])
            if self.diff[row] == specialTerm:
                self.gridDisplayDiffScrolledPanel.SetCellValue(row, 0, '%0.5f' % self.alignObj.zt_obj_zt_ret)
            else:
                self.gridDisplayDiffScrolledPanel.SetCellValue(row, 0, '%0.2f' % self.values[i])
            self.gridDisplayDiffScrolledPanel.SetCellValue(row, 1, '%d' % self.alignObj.weights[i])
        self.gridDisplayDiffScrolledPanel.AutoSize()


###########################################################################
## Class PanelStartingVars
###########################################################################
class PanelStartingVars(PanelDisplayFields):
    def __init__(self, parent, alignObj, mode):
        # inherited construction
        PanelDisplayFields.__init__(self, parent, alignObj, mode)
        panelSizer = self.GetSizer()

        ######### ADD RIGHT PANEL control button ##########
        self.staticTextControlTitle = wx.StaticText( self, wx.ID_ANY, u"Controls", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextControlTitle.Wrap( -1 )
        self.staticTextControlTitle.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
        self.bSizerPanelControl.Add( self.staticTextControlTitle, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
        
        self.staticlineControlSep = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        self.bSizerPanelControl.Add( self.staticlineControlSep, 0, wx.EXPAND |wx.ALL, 5 )

        self.buttonPlotSensitivities = wx.Button( self, wx.ID_ANY, u"Plot Sensitivities", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.buttonPlotSensitivities.SetFont( wx.Font( 10, 70, 90, 90, False, wx.EmptyString ) )
        self.bSizerPanelControl.Add( self.buttonPlotSensitivities, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.refreshWidget(self.buttonPlotSensitivities)
        ###################################################

        # added parameters display at the bottom
        fgSizerParams = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizerParams.SetFlexibleDirection( wx.BOTH )
        fgSizerParams.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.staticTextTrackLength = wx.StaticText( self, wx.ID_ANY, u"Measured Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextTrackLength.Wrap( -1 )
        self.staticTextTrackLength.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
        
        fgSizerParams.Add( self.staticTextTrackLength, 0, wx.ALL, 5 )
        
        self.staticTextTrackLengthValue = wx.StaticText( self, wx.ID_ANY, str(self.alignObj.tracklength), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextTrackLengthValue.Wrap( -1 )
        self.staticTextTrackLengthValue.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )

        fgSizerParams.Add( self.staticTextTrackLengthValue, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.staticTextTargetTrackLength = wx.StaticText( self, wx.ID_ANY, u"Target Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextTargetTrackLength.Wrap( -1 )
        self.staticTextTargetTrackLength.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
        
        fgSizerParams.Add( self.staticTextTargetTrackLength, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.staticTextTargetTrackLengthValue = wx.StaticText( self, wx.ID_ANY, str(self.alignObj.target_tracklength), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextTargetTrackLengthValue.Wrap( -1 )
        self.staticTextTargetTrackLengthValue.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )

        fgSizerParams.Add( self.staticTextTargetTrackLengthValue, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.boxSizerPanelDisplay.Add( fgSizerParams, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.ALL, 5 )

        self.Layout()
        self.SetupScrolling()
        panelSizer.Fit(self)
        self.getTopLevelWindow().Layout()

        # Connect Events
        self.buttonPlotSensitivities.Bind( wx.EVT_BUTTON, self.onPlotSensitivities )

    # Virtual event handlers, overide them in your derived class
    def onPlotSensitivities( self, event ):
        self.alignObj.plot_sens()


###########################################################################
## Class PanelResidual
###########################################################################
class PanelResidual(PanelDisplayFields):
    def __init__(self, parent, alignObj, mode):
        # inherited construction
        PanelDisplayFields.__init__(self, parent, alignObj, mode)
        panelSizer = self.GetSizer()

        # change the variables and weights title:
        self.staticTextTitleDisplay.SetLabel("Predicted Residual Dependent Variables and Weights")

        # added parameters display at the bottom
        fgSizerParams = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizerParams.SetFlexibleDirection( wx.BOTH )
        fgSizerParams.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.staticTextNewTrackLength = wx.StaticText( self, wx.ID_ANY, u"New Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextNewTrackLength.Wrap( -1 )
        self.staticTextNewTrackLength.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
        
        fgSizerParams.Add( self.staticTextNewTrackLength, 0, wx.ALL, 5 )
        
        if self.alignObj.new_tracklength == None:
            newTrackLengthValue = str(self.alignObj.new_tracklength)
        else:
            newTrackLengthValue = '%0.6f' % self.alignObj.new_tracklength
        self.staticTextNewTrackLengthValue = wx.StaticText( self, wx.ID_ANY, newTrackLengthValue, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextNewTrackLengthValue.Wrap( -1 )
        self.staticTextNewTrackLengthValue.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )

        fgSizerParams.Add( self.staticTextNewTrackLengthValue, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.staticTextDeltaTargetTrackLength = wx.StaticText( self, wx.ID_ANY, u"Delta Target Track Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextDeltaTargetTrackLength.Wrap( -1 )
        self.staticTextDeltaTargetTrackLength.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )
        
        fgSizerParams.Add( self.staticTextDeltaTargetTrackLength, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        if self.alignObj.dtarget_tracklength == None:
            deltaTargetTrackLengthValue = str(self.alignObj.dtarget_tracklength)
        else:
            deltaTargetTrackLengthValue = '%0.6f' % self.alignObj.dtarget_tracklength
        self.staticTextDeltaTargetTrackLengthValue = wx.StaticText( self, wx.ID_ANY, deltaTargetTrackLengthValue, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticTextDeltaTargetTrackLengthValue.Wrap( -1 )
        self.staticTextDeltaTargetTrackLengthValue.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )

        fgSizerParams.Add( self.staticTextDeltaTargetTrackLengthValue, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        
        self.boxSizerPanelDisplay.Add( fgSizerParams, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.ALL, 5 )

        self.Layout()
        self.SetupScrolling()
        panelSizer.Fit(self)
        self.getTopLevelWindow().Layout()