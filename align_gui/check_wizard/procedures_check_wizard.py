"""
procedures_check_wizard.py
	This module contains the wizard to do the procedures check
"""

import os
import re
import sys
import wx
import wx.wizard

###########################################################################
## Class ProceduresCheckWizardPage
###########################################################################
class ProceduresCheckWizardPage( wx.wizard.PyWizardPage ):
	def __init__(self, parent, title, contents):
		"""
		@Purpose:
			constructor
		@Inputs:
			(wxWindows) parent
			(str) title
			(str) contents
		"""
		self.next = self.prev = None
		wx.wizard.PyWizardPage.__init__(self, parent)

		bSizerPage = wx.BoxSizer( wx.VERTICAL )
		self.sizer = bSizerPage
		
		self.staticTextTitle = wx.StaticText( self, wx.ID_ANY, title, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextTitle.Wrap( -1 )
		self.staticTextTitle.SetFont( wx.Font( 52, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizerPage.Add( self.staticTextTitle, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticlineSep = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerPage.Add( self.staticlineSep, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.staticTextContents = wx.StaticText( self, wx.ID_ANY, contents, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextContents.Wrap( -1 )
		self.staticTextContents.SetFont( wx.Font( 26, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizerPage.Add( self.staticTextContents, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		self.SetSizer( bSizerPage )
		self.Layout()
		bSizerPage.Fit( self )

	def SetNext(self, next):
		self.next = next

	def SetPrev(self, prev):
		self.prev = prev

	def GetNext(self):
		return self.next

	def GetPrev(self):
		return self.prev

###########################################################################
## Class ProceduresCheckWizard
###########################################################################

class ProceduresCheckWizard ( wx.wizard.Wizard ):
	def __init__( self, parent, procListFile ):
		self.procListFile = procListFile

		wx.wizard.Wizard.__init__ ( self, parent, id = wx.ID_ANY, title = u"MET5 POB Operation Checklist Wizard", bitmap = wx.NullBitmap, pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetPageSize(wx.Size(1280, 720))
		self.SetSizeHintsSz( wx.Size(1024, 768), wx.Size(1920, 1200) )
		self.pages = []

		self.__parseProcFile__()

		self.Centre( wx.BOTH )

	def __parseProcFile__(self):
		"""
		@Purpose:
			private function to parse the procesure files
		"""
		fHandle = open(self.procListFile, "r")
		allContents = ""
		for line in fHandle:
			if not re.match("^#", line):
				allContents += line
		contentsList = allContents.split("$")
		fHandle.close()
		
		for contents in contentsList:
			contents = contents.strip()
			if len(contents) > 0:
				(title, content) = contents.split(":")
				newPage = ProceduresCheckWizardPage(self, title, content)
				self.AddPage(newPage)
		
	def AddPage(self, page):
		if self.pages:
			previous_page = self.pages[-1]
			page.SetPrev(previous_page)
			previous_page.SetNext(page)
		self.pages.append(page)

	def Run(self):
		self.RunWizard(self.pages[0])
	
	def __del__( self ):
		pass
	

if __name__ == "__main__":
	cwd = os.path.dirname(os.path.abspath(__file__)) + "/"
	app = wx.PySimpleApp()
	if len(sys.argv) > 1:
		procName = sys.argv[1]
	else:
		procName = "procedures.txt"
	procFileName = cwd + procName
	wiz = ProceduresCheckWizard(None, procFileName)
	wiz.Run()
	wiz.Destroy()
	app.MainLoop()
