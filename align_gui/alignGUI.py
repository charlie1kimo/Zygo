"""
alignGUI: 
    User interface for align control over the MET5 POB hexapod system.
"""

import os
import re
import time
import traceback
import wx
import wx.aui
import wx.grid
import wx.lib.scrolledpanel

from wx_extensions.windows import FrameBase
from wx_extensions.statusbar import StatusBarGauge
from wx_extensions.exceptions import handlesErrors
import align_py.resultPanel as resultPanel
import align_py.inputPanel as inputPanel
from align_py.displayPanel import PanelStartingVars,PanelResidual
from align_py.hexapodPositionsPanel import PanelHexapodPositions
from align_py.hexapod_actuator.actuator_wx import HexapodActuatorWxScrolledPanel

import align_py
import align_py.align as align
from align_py.met5hexapod import Hexalign
from align_py.hexapod_actuator.picomotor import PicomotorWebException
try:
    import align_py.hexapod_actuator as hexapod_actuator
    from align_py.hexapod_actuator.actuator import HexaPodActuator
    IMPORT_HEXAPOD_ACTUATOR_FAIL = False
except Exception, e:
    IMPORT_HEXAPOD_ACTUATOR_FAIL = True

PROGRAM_VERSION = align_py.__version__

###########################################################################
## Class frameMain
###########################################################################

class FrameMain(FrameBase):
    
    def __init__(self, parent):
        self.actuator = None
        self.alignObj = None
        self.hexapodObj = None
        FrameBase.__init__(self, parent, id = wx.ID_ANY, title = "Hexapod Align Program", pos = wx.DefaultPosition, size = wx.Size(1400,800), style = wx.DEFAULT_FRAME_STYLE|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        self.statusBarMain = StatusBarGauge(self)
        self.SetStatusBar(self.statusBarMain)
        self.menuBarMain = wx.MenuBar(0)

        self.menuMainFile = wx.Menu()
        self.menuItemMainFileOpen = wx.MenuItem(self.menuMainFile, wx.ID_ANY, "Open..."+ "\t" + "O", "Open a file openning dialog", wx.ITEM_NORMAL)
        self.menuMainFile.AppendItem(self.menuItemMainFileOpen)
        self.menuBarMain.Append(self.menuMainFile, "&File") 
        
        self.menuMainRun = wx.Menu()
        self.menuItemDebug = wx.MenuItem( self.menuMainRun, wx.ID_ANY, u"Debug", "Turn ON / OFF Debug mode", wx.ITEM_CHECK )
        self.menuMainRun.AppendItem( self.menuItemDebug ) 
        self.menuBarMain.Append(self.menuMainRun, "&Run")
        
        self.menuMainHelp = wx.Menu()
        self.menuItemMainHelp = wx.MenuItem(self.menuMainHelp, wx.ID_ANY, "&About...", "Version and author information", wx.ITEM_NORMAL)
        self.menuMainHelp.AppendItem(self.menuItemMainHelp)
        
        self.menuBarMain.Append(self.menuMainHelp, "&Help") 
        
        self.SetMenuBar(self.menuBarMain)
        
        boxSizerMain = wx.BoxSizer(wx.VERTICAL)
        
        self.auiNotebookMain = wx.aui.AuiNotebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE)
        
        tabInput = inputPanel.PanelInput(self)
        self.auiNotebookMain.AddPage(tabInput, "Input")
        
        boxSizerMain.Add(self.auiNotebookMain, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panelControl = wx.Panel(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(800,40), style=wx.TAB_TRAVERSAL)
        boxSizerPanelControl = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonPanelControlSolve = wx.Button(self.panelControl, id=wx.ID_ANY, label="Set / Solve")
        self.buttonPanelControlSolve.SetFont( wx.Font( 10, 70, 90, 92, False, wx.EmptyString ) )

        boxSizerPanelControl.Add(self.buttonPanelControlSolve, 1, wx.EXPAND | wx.ALL, )
        self.panelControl.Bind(wx.EVT_BUTTON, self.clickOnSolve, self.buttonPanelControlSolve)
        
        #self.buttonPanelControlUpdate = wx.Button(self.panelControl, id=wx.ID_ANY, label="Update")
        #boxSizerPanelControl.Add(self.buttonPanelControlUpdate, 1, wx.EXPAND | wx.ALL, 5)
        #self.panelControl.Bind(wx.EVT_BUTTON, self.clickOnUpdate, self.buttonPanelControlUpdate)
        
        self.panelControl.SetSizer(boxSizerPanelControl)
        boxSizerMain.Add(self.panelControl, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(boxSizerMain)
        self.Layout()
        #self.Bind(wx.EVT_SIZE, self.onSize)

        # Connects other events
        self.Bind( wx.EVT_MENU, self.OnDebugSelection, id = self.menuItemDebug.GetId() )
        self.Bind( wx.EVT_MENU, self.onAbout, id = self.menuItemMainHelp.GetId() )
        
        self.Centre(wx.BOTH)

        # icon
        self.baseDir = os.path.dirname(align_py.__file__) + "/"
        self.SetIcon(wx.Icon(self.baseDir+"icons/icon-48x48.ico", wx.BITMAP_TYPE_ICO))

        ##### Setup actuator object #####
        if not IMPORT_HEXAPOD_ACTUATOR_FAIL:
            motorControllers = ['8742-10140', '8742-10159']
            NI_config_file = os.path.dirname(hexapod_actuator.__file__) + '/NI_composite_capgauge.config'
            try:
                self.actuator = HexaPodActuator(NI_config_file, motorControllers)
            except PicomotorWebException, e:
                help_message = \
"""
ERROR: FAIL to communicate to Picomotor Controller; make sure the controller is online.

"""
                self.popErrorBox('ERROR: HexaPodActuator Initialize Error', help_message + traceback.format_exc())
                traceback.print_exc()
                self.statusBarMain.SetStatus('ERROR', True)
            except Exception, e:
                help_on_error_message = \
"""
ERROR: FAIL to communicate to the capgauge controller; make sure the controller chassis is reserved by following steps:

1. Open "Measurement & Automation Explorer" program from Desktop
2. From the left pannel, navigate through "My System" -> "Devices and Interfaces" -> "Network Devices"
3. Under "Network Devices", find the controller named "cDAQ9181-17F2591"
4. Left click on "cDAQ9181-17F2591"
5. Left click on "Reserve Chassis" on the right panel, if prompt asking if override, click yes.
6. Restart the program and see if this solves the problem.

If it still doesn't solve the problem. Contact me (Charlie Chen) @ <cchen@zygo.com>

"""
                self.popErrorBox('ERROR: HexaPodActuator Initialize Error', help_on_error_message + traceback.format_exc())
                traceback.print_exc()
                self.statusBarMain.SetStatus('ERROR', True)
        ##################################
    
    def __del__(self):
        pass

    @handlesErrors
    def addTab(self, page, tabName):
        """
        @Purpose:
            add a tab to AuiNotebook with given tabName
        @Inputs:
            page = (wx.Panel) page to add
            tabName = (str) page's tab name
        """
        self.auiNotebookMain.AddPage(page, tabName)
        self.auiNotebookMain.SetSelection(self.auiNotebookMain.GetPageCount()-1)
        self.refreshWidget(page)

    @handlesErrors
    def deleteTab(self, tabName):
        """
        @Purpose:
            delete a tab with given tabName. Do nothing if the tabName is not found.
        @Inputs:
            tabName = (str) tab name to delete
        """
        for p in range(self.auiNotebookMain.GetPageCount()):
            if tabName == self.auiNotebookMain.GetPageText(p):
                pg = self.auiNotebookMain.GetPage(p)
                self.auiNotebookMain.RemovePage(p)
                pg.Destroy()
                break
    
    @handlesErrors
    def clickOnSolve(self, event):
        currSelect = self.auiNotebookMain.GetPageText(self.auiNotebookMain.GetSelection())
        # if selecting "Adjust Hexapod" tab
        if currSelect == "Adjust Hexapod":
            page = self.auiNotebookMain.GetPage(self.auiNotebookMain.GetSelection())
            page.onSolve()
        # if selecting input tab
        if currSelect == "Input":
            startflag = True
            page = self.auiNotebookMain.GetPage(self.auiNotebookMain.GetSelection())

            ### handles field coordinates input values
            fieldCoord = page.textCtrlFieldCoord.GetValue()
            if len(fieldCoord) == 0:
                self.alignObj = align.Align()
            else:
                self.alignObj = align.Align(field_coord=fieldCoord)

            # track lengths (have to do it before scenario first b/c alignObj limitation...GRR)
            trackLength = page.textCtrlMeasuredTrackLength.GetValue()
            targetTrackLength = page.textCtrlTargetTrackLength.GetValue()
            if trackLength != "None" and targetTrackLength != "None":
                self.alignObj.set_tracklength(float(trackLength))
                self.alignObj.set_target_tracklength(float(targetTrackLength))
            # save the hexapod ID, and create the hexapod object:
            self.alignObj.hexapodID = re.sub('\s', '', page.textCtrlHexapodID.GetValue())
            if not bool(self.alignObj.hexapodID):          # empty ID string
                self.popAlertBox("Hexapod ID Required.", "Please fill a valid hexapod ID!")
                return
            if self.hexapodObj == None or self.hexapodObj.hexopod_id != self.alignObj.hexapodID:
                self.hexapodObj = Hexalign(hexopod_id=self.alignObj.hexapodID)
                if self.actuator != None:
                    page.buttonReset.Enable(True)

            if page.radioButtonScenario.GetValue():
                # check all the boxes filled
                if not page.textCtrlScenarioFile.GetValue() or not page.textCtrlScenarioColumn.GetValue():
                    self.popAlertBox("Information Required", "Please fill all necessary information for Scenario mode!")
                    startflag = False
                # good to go
                trialfilename = page.textCtrlScenarioFile.GetValue().encode('ascii', 'ignore')              # trialfilename MUST BE ASCII STRING; default input = Unicode
                column_name = page.textCtrlScenarioColumn.GetValue()
                self.alignObj.set_trial_colum(colum_name=column_name)
                self.alignObj.make_z_from_scenario(trialfilename)
            if page.radioButtonGntSet.GetValue():
                if not page.textCtrlGntSetRoot.GetValue() or not page.textCtrlGntSetExt.GetValue():
                    self.popAlertBox("Information Required", "Please fill all necessary information for Gntset mode!")
                    startflag = False
                root = page.textCtrlGntSetRoot.GetValue().encode('ascii', 'ignore')                         # change to ascii encoding
                ext = page.textCtrlGntSetExt.GetValue().encode('ascii', 'ignore')                           # change to ascii encoding
                self.alignObj.make_z_from_GntSet(root, ext)
            if page.radioButtonZernikes.GetValue():
                if not page.textCtrlZernikesFile.GetValue():
                    self.popAlertBox("Information Required", "Please fill all ncessary information for Zernikes mode!")
                    startflag = False
            if page.radioButtonStartAllZeros.GetValue():
                self.alignObj.make_z_zero()

            # generate the starting tab / remove all other tabs (starting over)
            if startflag:
                for p in reversed(range(self.auiNotebookMain.GetPageCount())):
                    if not p == self.auiNotebookMain.GetSelection():
                        pg = self.auiNotebookMain.GetPage(p)
                        self.auiNotebookMain.RemovePage(p)
                        pg.Destroy()
                self.Layout()
                self.Refresh()
                tabPositions = PanelHexapodPositions(self, self.alignObj, self.hexapodObj, self.actuator)
                self.addTab(tabPositions, "Hexapod Positions")
                tabStart = PanelStartingVars(self, self.alignObj, 'z')
                self.addTab(tabStart, "Starting Variables")
        # otherwise
        else:
            if currSelect == "Results":         # only do update_A (update array at the Results tab)
                self.alignObj.update_A()
            needUpdateDict = {'Residual': True, 'Results': True}
            self.alignObj.solve()
            pCounts = self.auiNotebookMain.GetPageCount()

            for p in range(pCounts):                        # search the update pages
                page = self.auiNotebookMain.GetPage(p) 
                if self.auiNotebookMain.GetPageText(p) == "Residual":
                    page.setAlignObj(self.alignObj, page.mode)
                    page.updateMeasuredData()
                    page.updateDiffData()
                    needUpdateDict["Residual"] = False
                elif self.auiNotebookMain.GetPageText(p) == "Results":
                    page.setAlignObj(self.alignObj)
                    page.updateData()
                    needUpdateDict["Results"] = False
            if currSelect == "Starting Variables":
                for uPage in needUpdateDict:                    # update the pages
                    if needUpdateDict[uPage]:
                        if uPage == "Residual":
                            tabDisplay = PanelResidual(self, self.alignObj, 'res')
                            self.addTab(tabDisplay, "Residual")
                        elif uPage == "Results":
                            tabResult = resultPanel.PanelResults(self, self.alignObj)       
                            self.addTab(tabResult, "Results")
                self.auiNotebookMain.SetSelection(self.auiNotebookMain.GetPageCount()-1)
                    
        event.Skip()

    def setStatusMessage(self, msg):
        self.statusBarMain.SetStatus(msg, False)
    
    def onSize(self, event):
        panel = self.auiNotebookMain.GetPage(self.auiNotebookMain.GetSelection())
        self.refreshWidget(panel)

    def OnDebugSelection( self, event ):
        for ind in range(self.auiNotebookMain.GetPageCount()):
            panel = self.auiNotebookMain.GetPage(ind)
            if isinstance(panel, HexapodActuatorWxScrolledPanel):
                if self.menuItemDebug.IsChecked():
                    panel.__debug__ = True
                else:
                    panel.__debug__ = False

        event.Skip()

    def onAbout( self, event ):
        descriptions = \
"""
This Hexapod Align Program Provides a graphical user interface to perform the alignment calculations and movement.
It calculates the hexapod legs alignment values under different settings and then perform the real hexapod legs move.
"""
        license = \
"""
(C) 2013 Zygo Corporation, all right reserved
"""
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(self.baseDir+"icons/icon-48x48.ico", wx.BITMAP_TYPE_ICO))
        info.SetName("Hexapod Align Program")
        info.SetDescription(descriptions)
        info.SetLicense(license)
        info.SetVersion(PROGRAM_VERSION)
        info.SetCopyright(" (C) 2013 Zygo Corporation")
        info.SetWebSite("http://www.zygo.com")
        info.AddDeveloper("Charlie Chen <cchen@zygo.com>, Bob Kestner <bkestner@zygo.com>")
        info.AddDocWriter("Charlie Chen <cchen@zygo.com>")
        wx.AboutBox(info)   

        
# Main
if __name__ == "__main__":  
        app = wx.PySimpleApp()
        frame = FrameMain(None)
        frame.Show(True)
        app.MainLoop()