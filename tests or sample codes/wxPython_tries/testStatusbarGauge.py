import wx
import wx.grid
from wx_extensions.statusbar import StatusBarGauge

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.count = 0

        wx.StaticText(self, -1, "This example shows the wx.Gauge control.", (45, 15))

        self.g1 = wx.Gauge(self, -1, 50, (110, 50), (250, 25))
        self.g2 = wx.Gauge(self, -1, 50, (110, 95), (250, 25))

        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1

        if self.count >= 50:
            self.count = 0

        self.g1.SetValue(self.count)
        self.g2.Pulse()

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300))
        
        bSizerFrame = wx.BoxSizer(wx.VERTICAL)
        
        #panel = TestPanel(self)
        panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.ALL|wx.EXPAND)
        bSizerPanel = wx.BoxSizer(wx.VERTICAL)
        
        bSizerText = wx.BoxSizer(wx.HORIZONTAL)
        panel.Bind(wx.EVT_MOTION, self.OnMove)
        #self.staticText = wx.StaticText(scrolledWindow, -1, "Pos:")
        self.staticText = wx.StaticText(panel, -1, "Pos:")
        bSizerText.Add(self.staticText, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        #self.posCtrl = wx.TextCtrl(scrolledWindow, -1, "")
        self.posCtrl = wx.TextCtrl(panel, -1, "")
        bSizerText.Add(self.posCtrl, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        bSizerPanel.Add(bSizerText, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        btnPulseStart = wx.Button( panel, wx.ID_ANY, "Pulse Start!", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerPanel.Add(btnPulseStart, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        btnPulseStop = wx.Button( panel, wx.ID_ANY, "Pulse Stop!", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerPanel.Add(btnPulseStop, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        panel.SetSizer(bSizerPanel)
        
        self.statusBarMain = StatusBarGauge(self)
        self.SetStatusBar(self.statusBarMain)
        
        bSizerFrame.Add(panel, 1, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)
        self.SetSizer(bSizerFrame)
        self.Layout()
        
        #self.timer = wx.Timer(self)
        #self.percent = 0
        #self.timer.Start(100)
        
        btnPulseStart.Bind(wx.EVT_BUTTON, self.onPulseStart)
        btnPulseStop.Bind(wx.EVT_BUTTON, self.onPulseStop)
        #self.Bind(wx.EVT_TIMER, self.onTimer)
    
    def OnMove(self, event):
        pos = event.GetPosition()
        self.posCtrl.SetValue("%s, %s" % (pos.x, pos.y))
        
    def onPulseStart(self, event):
        self.statusBarMain.PulseStart()
        
    def onPulseStop(self, event):
        self.statusBarMain.PulseStop()
        
    def onTimer(self, event):
        if self.percent > 100:
            self.percent = 0
        else:
            self.percent += 1
        
        self.statusBarMain.SetGaugeValue(self.percent)
        print self.percent
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()