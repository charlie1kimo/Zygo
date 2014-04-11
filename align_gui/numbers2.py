import os,sys
import wx
import  wx.lib.scrolledpanel as scrolled
import align
import numpy

class NumberControl(wx.Panel):
    '''
    Panel which contains the text label, value nad check box for
    NumbersPanel.
    '''
    def __init__(self,parent,cntrl_label,value,mode):
        wx.Panel.__init__(self,parent,-1)
        hbox=wx.FlexGridSizer(cols=3,vgap=5,hgap=5)

        self.name=name=wx.StaticText(self,label=cntrl_label,size=(120,28),style=wx.ALIGN_RIGHT)
        font = wx.Font(13, wx.SWISS, wx.NORMAL, wx.NORMAL)
        name.SetFont(font)
        hbox.Add(name)
        
        self.ctl_value=ctl_value=wx.TextCtrl(self,-1,'%.5f'%value,size=(100,28), style=wx.TE_CENTER)
        ctl_value.SetFont(font)
        hbox.Add(ctl_value)
        
        self.chk=chk=wx.CheckBox(self, -1)
        chk.SetValue(bool(mode))
        hbox.Add(chk,1,wx.ALIGN_CENTER)
        
        self.SetSizer(hbox)
        hbox.Fit(self)
    def get_value(self):
        n = str(self.name.GetLabelText()).strip()
        v=float(self.ctl_value.GetValue().strip())
        mode=self.chk.GetValue()
        return (n,v,mode)
    def set_value(self,cntrl_label,value,mode):
        self.name.SetLabel(cntrl_label)
        self.ctl_value.SetValue('%.5f'%value)
        self.chk.SetValue(bool(mode))

class NumbersPanel(scrolled.ScrolledPanel):
    '''
    Panel which lays out the NUmberControl objects for the
    NumbersDialog.
    '''
    def __init__(self,parent,data_obj):
        '''
        
        '''
        scrolled.ScrolledPanel.__init__(self, parent, -1,size=(300, 400),
                                        style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        vbox = wx.FlexGridSizer(cols=1,vgap=5,hgap=5)
        
        data_list=zip(data_obj.usedperts,data_obj.p,data_obj.force)
        self.control_list=[]
        for data in data_list:
            num = NumberControl(self,data[0],data[1],data[2])
            self.control_list.append(num)
            vbox.Add(num)
        self.SetSizer(vbox)
        vbox.Fit(self)
        self.SetAutoLayout(1)
        self.SetupScrolling()
    def get_value(self):
        out=[]
        for data in self.control_list:
            out.append(data.get_value())
        data_out=zip(*out)
        data_out=[list(data_out[0]),list(data_out[1]),list(data_out[2])]
        return data_out
    def set_value(self,data_obj):
        data_list=zip(data_obj.usedperts,data_obj.p,data_obj.force)
        for i in range(len(self.control_list)):
            self.control_list[i].set_value(data_list[i][0],data_list[i][1],data_list[i][2])

class NumbersDialog(wx.Dialog):
    '''
    The dialog for entering numbers and using the Align class's solve method to calculate
    new numbers.
    '''
    def __init__(self,parent,data_obj):
        x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        wx.Dialog.__init__(self,parent,-1,"Numbers Dialog",pos=((x/2.)-375,(y/2.)-250),size=(1500,800))
        
        b_sizer=wx.FlexGridSizer(cols=2,hgap=5,vgap=5)
        
        self.data_obj=data_obj
        self.numbers_list=NumbersPanel(self,data_obj)
        b_sizer.Add(self.numbers_list,1,wx.EXPAND)
        
        font = wx.Font(13, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.update_btn=wx.Button(self,-1,'Update',size=(85,-1))
        self.update_btn.SetFont(font)
        self.Bind(wx.EVT_BUTTON, self.onUpdateClick, self.update_btn)
        self.done_btn=wx.Button(self,-1,'Done',size=(85,-1))
        self.done_btn.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.onDoneClick, self.done_btn)
        self.function2_btn=wx.Button(self,-1,'Function2',size=(85,-1))
        self.function2_btn.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.onFunction2Click, self.function2_btn)
        self.function3_btn=wx.Button(self,-1,'Function3',size=(85,-1))
        self.function3_btn.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.onFunction3Click, self.function3_btn)
        
        btn_sizer=wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(self.update_btn)
        btn_sizer.Add(self.done_btn)
        btn_sizer.Add(self.function2_btn)
        btn_sizer.Add(self.function3_btn)
        
        b_sizer.Add(btn_sizer)
        self.SetSizer(b_sizer)
        
        b_sizer.Fit(self)
        self.Raise()
        self.ShowModal()
    def set_value(self,data_obj):
        '''
        Passes the data_obj to the NumbersPanel.
        '''
        self.numbers_list.set_value(data_obj)
    def onUpdateClick(self,event):
        '''
        Runs solve method of data_obj and updates the values
        in the dialog.
        '''
        data_out=self.numbers_list.get_value()
        #self.data_obj.usedperts=data_out[0]
        #self.data_obj.p= numpy.array(data_out[1])
        for i in range(len(data_out[2])):
            if data_out[2][i]:
                data_out[2][i]=data_out[1][i]
            else:
                data_out[2][i]=None
        self.data_obj.force=data_out[2]
        self.data_obj.solve()
        self.data_obj.makenewA()
        self.data_obj.disp_solve()
        self.set_value(self.data_obj)

    def onDoneClick(self,event):
        '''
        Close dialog window.
        '''
        self.EndModal(0)
    def onFunction2Click(self,event):
        '''
        Runs function2 method of data_obj and updates the values
        in the dialog.
        '''
        
        wx.CallAfter(self.data_obj.plot_sens)
        self.set_value(self.data_obj)
    def onFunction3Click(self,event):
        '''
        Runs function3 method of data_obj and updates the values
        in the dialog.
        '''
        data_out=self.numbers_list.get_value()
        #self.data_obj.usedperts=data_out[0]
        #self.data_obj.p= numpy.array(data_out[1])
        for i in range(len(data_out[2])):
            if data_out[2][i]:
                data_out[2][i]=data_out[1][i]
            else:
                data_out[2][i]=None
        self.data_obj.force=data_out[2]
        self.data_obj.function3()
        self.set_value(self.data_obj)

def numbers(data,parent = None):
    """
    sample code for loading numbers.
    """
    #globs['username']=username
    
    if parent == None:
        app = wx.PySimpleApp(redirect=False)  # Create app object if not called from called from within another object.
    dlg = NumbersDialog(parent,data)
    dlg.Destroy()
    if parent==None:
        app.MainLoop()
    return


if __name__ == "__main__":
    d=[
       ['ajjjjjjjaa','bbb','ccc','aaa','bbb','ccc','aaa','bbb','ccc','aaa','bbb','ccc'],
       [1,2,3,4,5,6,7,8,9,10,11,12],
       [True,False,False,True,False,False,True,False,False,True,False,False]
       ]
    data = align.Align()
    data.set_trial_colum(colum_name='scenario4')
    data.make_z_from_scenario()
    data.solve()
    data.disp_solve()
    numbers(data)
    
