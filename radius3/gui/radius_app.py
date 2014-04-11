"""
radius_app.py
	This is a custom wxApp for radius measurement program.
Author: Charlie Chen
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/4/2013	cchen	first created documentation
'''

import sys
import threading
import traceback
import wx

from radius3 import rs232
from radius3 import dmi
from radius3 import weather_station
from radius3 import phase_station
from radius3.utilities import OutputBuffer
from radius3.gui.gui_components import FrameLoading
from radius3.gui.radius_gui import FrameMain

###########################################################################
## Class AppRadius
###########################################################################
class AppRadius(wx.App):

	def __init__(self, cmdParams, printBuffer=OutputBuffer(), debug=False, redirect=False, filename=None, useBestVisual=True, clearSigInt=True):
		self.cmdParams = cmdParams
		self.printBuffer = printBuffer
		self.debug = debug
		wx.App.__init__(self, redirect, filename, useBestVisual, clearSigInt)
		
		
	def OnInit(self):
		self.frameLoading = FrameLoading(None)
		self.frameLoading.Show()
		self.SetTopWindow(self.frameLoading)
		self.printBuffer.setFrame(self.frameLoading)
		self.printBuffer.printOutAndFlush()
		self.startThread(self.init_system)
		# need the setup part information gui in the main thread
		
		self.MainLoop()
		
		self.frameMain = FrameMain(None, self.cmdParams, self.dmi, self.ws, self.ps, self.printBuffer, self.debug)
		self.frameMain.Show()
		self.SetTopWindow(self.frameMain)
		return True
	
	def startThread(self, funct, *args):
		thread = threading.Thread(target=funct, args=args)
		thread.start()
		
	# some useful functions:
	# init_system()
	def init_system(self):
		try:
			self.frameLoading.staticTextInfo.SetLabel("...Initializing DMI Station...")
			self.dmi = dmi.DMI(self.cmdParams.dmi_info, self.printBuffer, self.debug)
			#self.printBuffer.printOutAndFlush()
			self.frameLoading.gaugeLoading.SetValue(25)
		except Exception, e:
			self.printBuffer.writePrintOutFlush("ERROR: Cannot initialize DMI. Check connection to DMI.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: Cannot initialize DMI.\n Check connection to DMI.")
			sys.exit(-1)
		try:
			self.frameLoading.staticTextInfo.SetLabel("...Initializing Phase Station...")
			self.ps = phase_station.PhaseStation(self.cmdParams.phase_info, self.printBuffer, self.debug)
			#self.printBuffer.printOutAndFlush()
			self.frameLoading.gaugeLoading.SetValue(50)
		except Exception, e:
			self.dmi.close()
			self.ws.close()
			self.printBuffer.writePrintOutFlush("ERROR: Cannot initialize Phase Station. Check connection to Phase Station.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: Cannot initialize Phase Station.\n Check connection to Phase Station.")
			sys.exit(-1)
		try:
			self.frameLoading.staticTextInfo.SetLabel("...Initializing Weather Station...")
			self.ws = weather_station.WeatherStation(self.cmdParams.ws_info, self.dmi.cts_in, self.printBuffer, self.debug)
			self.ws.updateWeather()
			#self.printBuffer.printOutAndFlush()
			self.frameLoading.gaugeLoading.SetValue(75)
		except Exception, e:
			self.printBuffer.writePrintOutFlush("ERROR: Cannot initialize Weather Station. Check Weather Station Setup; using default weather values.")
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			self.popErrorBox("ERROR", "ERROR: Cannot initialize Weather Station.\n Check Weather Station Setup; using default weather values.")
		
		self.frameLoading.gaugeLoading.SetValue(100)
		self.frameLoading.Destroy()
			
	# popErrorBox:
	#   pop up Error Box with set title and message
	def popErrorBox(self, title, msg):
		dlg = wx.MessageDialog(None, msg, title,
							wx.OK | wx.ICON_ERROR)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

