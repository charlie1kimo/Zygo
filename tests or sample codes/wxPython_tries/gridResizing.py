import wx
import wx.grid

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300))
        
        scrolledWindow = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        scrolledWindow.SetScrollRate(5, 5)
        bSizerScrolled = wx.BoxSizer(wx.VERTICAL)
        
        #panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALL|wx.EXPAND)
        panel = wx.Panel(scrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALL|wx.EXPAND)
        bSizerPanel = wx.BoxSizer(wx.VERTICAL)
        
        #scrolledWindow = wx.ScrolledWindow(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        #scrolledWindow.SetScrollRate(5, 5)
        #bSizerScrolled = wx.BoxSizer(wx.VERTICAL)
        
        bSizerText = wx.BoxSizer(wx.HORIZONTAL)
        panel.Bind(wx.EVT_MOTION, self.OnMove)
        #self.staticText = wx.StaticText(scrolledWindow, -1, "Pos:")
        self.staticText = wx.StaticText(panel, -1, "Pos:")
        bSizerText.Add(self.staticText, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        #self.posCtrl = wx.TextCtrl(scrolledWindow, -1, "")
        self.posCtrl = wx.TextCtrl(panel, -1, "")
        bSizerText.Add(self.posCtrl, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        #grid = wx.grid.Grid(scrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALL)
        grid = wx.grid.Grid(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALL)
        grid.CreateGrid(5, 5)
        rowLabels = ["uno", "dos", "tres", "quatro", "cinco"]
        colLabels = ["one", "two", "three", "four", "five"]
        for row in range(5):
            grid.SetRowLabelValue(row, rowLabels[row])
        for col in range(5):
            grid.SetColLabelValue(col, colLabels[col])
        for row in range(5):
            for col in range(5):
                grid.SetCellValue(row, col, "(%s, %s)" % (row, col))
        
        #bSizerScrolled.Add(bSizerText, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        #bSizerScrolled.Add(grid, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        #scrolledWindow.Layout()
        #scrolledWindow.SetSizer(bSizerScrolled)
        #bSizerScrolled.Fit(grid)
        
        bSizerPanel.Add(bSizerText, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        bSizerPanel.Add(grid, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        #bSizerPanel.Add(scrolledWindow, 1, wx.EXPAND|wx.ALL, 5)
        panel.SetSizer(bSizerPanel)
        
        bSizerScrolled.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        scrolledWindow.Layout()             
        scrolledWindow.SetSizer(bSizerScrolled)
        bSizerScrolled.Fit(panel)
        
        #bSizerFrame.Add(panel, 1, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)
        #self.SetSizer(bSizerFrame)
        self.Layout()
    
    def OnMove(self, event):
        pos = event.GetPosition()
        self.posCtrl.SetValue("%s, %s" % (pos.x, pos.y))
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()