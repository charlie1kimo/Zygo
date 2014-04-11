#!/usr/bin/env python

import wx
from finddir import finddir
import radiusb2 as rb2

Parent = None
WLS = 'N'
path = finddir()
user = ''

app = wx.PySimpleApp()
dialog = rb2.GetUserInfo(Parent, WLS, path, user)
dialog.ShowModal()
if Parent == None:
	app.MainLoop

