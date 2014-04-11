# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.aui
import wx.animate

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 478,577 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.menuBar = wx.MenuBar( 0 )
		self.menuGames = wx.Menu()
		self.menuItemRollDice = wx.MenuItem( self.menuGames, wx.ID_ANY, u"&Roll a Dice", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuGames.AppendItem( self.menuItemRollDice )
		
		self.menuItemBlackJack = wx.MenuItem( self.menuGames, wx.ID_ANY, u"&Black Jack", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuGames.AppendItem( self.menuItemBlackJack )
		
		self.menuBar.Append( self.menuGames, u"Games" ) 
		
		self.menuAbout = wx.Menu()
		self.menuItemAuthor = wx.MenuItem( self.menuAbout, wx.ID_ANY, u"Author", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuAbout.AppendItem( self.menuItemAuthor )
		
		self.menuBar.Append( self.menuAbout, u"About..." ) 
		
		self.SetMenuBar( self.menuBar )
		
		boxSizerFrame = wx.BoxSizer( wx.HORIZONTAL )
		
		self.auinotebookFrame = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
		
		boxSizerFrame.Add( self.auinotebookFrame, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.SetSizer( boxSizerFrame )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.onMenuAbout, id = self.menuItemAuthor.GetId() )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onMenuAbout( self, event ):
		event.Skip()
	

###########################################################################
## Class panelRollDice
###########################################################################

class panelRollDice ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )
		
		boxSizerRollDice = wx.BoxSizer( wx.VERTICAL )
		
		self.bitmapRollingDice = wx.animate.AnimationCtrl( self, wx.ID_ANY, wx.animate.NullAnimation, wx.DefaultPosition, wx.DefaultSize, wx.animate.AC_DEFAULT_STYLE )
		self.bitmapRollingDice.LoadFile( u"C:\\Users\\cchen\\Documents\\wxPython tries\\pics\\dices\\rolling-dice.gif" )
		
		self.bitmapRollingDice.Play()
		boxSizerRollDice.Add( self.bitmapRollingDice, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.butonRoll = wx.Button( self, wx.ID_ANY, u"Roll!", wx.DefaultPosition, wx.DefaultSize, 0 )
		boxSizerRollDice.Add( self.butonRoll, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.staticTextDisplay = wx.StaticText( self, wx.ID_ANY, u"Get It Rolling!", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.staticTextDisplay.Wrap( -1 )
		self.staticTextDisplay.SetFont( wx.Font( 22, 71, 94, 92, False, wx.EmptyString ) )
		
		boxSizerRollDice.Add( self.staticTextDisplay, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.SetSizer( boxSizerRollDice )
		self.Layout()
		boxSizerRollDice.Fit( self )
		
		# Connect Events
		self.butonRoll.Bind( wx.EVT_BUTTON, self.onRoll )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onRoll( self, event ):
		number = random.choice([1, 2, 3, 4, 5, 6])
		self.resultText.SetLabel("You Got: %d" % number)
			
		diceImg = self.picDir + 'dice-%d.png' % number
		dicePic = wx.StaticBitmap(self, wx.NewId(), 
							wx.BitmapFromImage(wx.Image(diceImg, wx.BITMAP_TYPE_PNG)))
		self.GetSizer().Replace(self.dicePic, dicePic)
		self.dicePic.Destroy()
		self.dicePic = dicePic	
	

