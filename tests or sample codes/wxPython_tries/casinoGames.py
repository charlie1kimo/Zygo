"""
Casino Games: A GUI with selective casino games
"""

import blackJack
import os
import random
import time
import wx
import wx.animate

class blackJackPanel(wx.Panel):
	def __init__(self, parent):
		# images path
		self.picDir = os.getcwd() + '/pics/playingCards/'
		wx.Panel.__init__(self, parent, wx.NewId(), name='blackJackPanel')
		self.bj = None
		self.host = None
		self.guest = None
		self.hostBox = None
		self.guestBox = None
		self.sizer = None
		self.topWindow = self.getTopWindow()
		
		# refresh Host
		hiddenCard = self.picDir + '155.png'
		items = []
		for i in range(2):
			hiddenCardImg = wx.StaticBitmap(self, wx.NewId(), 
							wx.BitmapFromImage(wx.Image(hiddenCard, wx.BITMAP_TYPE_PNG)))
			items.append(hiddenCardImg)
		self.hostBox = self.makeStaticBoxSizer("Host\'s Hand", items)
		
		# refresh Guest
		if self.bj == None:
			self.bj = blackJack.blackJack()
			self.host = blackJack.blackJackPlayer(self.bj)
			self.guest = blackJack.blackJackPlayer(self.bj)
		else:
			self.bj.refreshDeck()
			self.host.replay()
			self.guest.replay()

		items = []
		for card in self.guest.hand:
			imgPath = self.picDir + self.getCardImgName(card)
			img = wx.StaticBitmap(self, wx.NewId(), 
							wx.BitmapFromImage(wx.Image(imgPath, wx.BITMAP_TYPE_PNG)))
			items.append(img)
		self.guestBox = self.makeStaticBoxSizer("Guest\'s Hand", items)
		
		# Controls
		self.hitButton = wx.Button(self, wx.NewId(), "Hit!", size=(100, 30))
		self.Bind(wx.EVT_BUTTON, self.onHit, self.hitButton)
		self.stopButton = wx.Button(self, wx.NewId(), "Stop!", size=(100, 30))
		self.Bind(wx.EVT_BUTTON, self.onStop, self.stopButton)
		newGameButton = wx.Button(self, wx.NewId(), "New Game!", size=(100, 30))
		self.Bind(wx.EVT_BUTTON, self.onNewGame, newGameButton)
		items = [self.hitButton, self.stopButton, newGameButton]
		self.controlBox = self.makeStaticBoxSizer("Control", items, wx.VERTICAL)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.hostBox, 0, wx.ALL, 10)
		sizer.Add(self.guestBox, 0, wx.ALL, 10)
		sizer.Add(self.controlBox, 0, wx.ALL, 10)
		self.sizer = sizer
		self.SetSizer(sizer)
		self.sizer.Fit(self)
		
	def makeStaticBoxSizer(self, boxLabel, items, orientation=wx.HORIZONTAL):
		box = wx.StaticBox(self, wx.NewId(), boxLabel)
		sizer = wx.StaticBoxSizer(box, orientation)
		for i in items:
			sizer.Add(i, 0, wx.ALL, 2)
			
		return sizer

	# card is a String input
	# return a String of image name
	def getCardImgName(self, card):
		if card[0] == 'D':
			return '1%02d.png' % (int(card[1:]))
		elif card[0] == 'C':
			return '1%d.png' % (13*1 + int(card[1:]))
		elif card[0] == 'H':
			return '1%d.png' % (13*2 + int(card[1:]))
		else:
			return '1%d.png' % (13*3 + int(card[1:]))
			
	def getTopWindow(self):
		topWindow = self.GetParent()
		p = self.GetGrandParent()
		while p != None:
			p = p.GetParent()
			topWindow = topWindow.GetParent()
		return topWindow
	
	def onHit(self, event):
		card = self.guest.getCard()
		imgPath = self.picDir + self.getCardImgName(card)
		img = wx.StaticBitmap(self, wx.NewId(), 
						wx.BitmapFromImage(wx.Image(imgPath, wx.BITMAP_TYPE_PNG)))
		self.guestBox.Add(img, 0, wx.ALL, 2)
		self.guestBox.Fit(self)
		self.Sizer.Fit(self)
		self.Refresh()
		
		currPts = self.guest.getCurrentPoints()
		if currPts > 20 or len(self.guest.hand) > 4:
			if currPts == 21 or len(self.guest.hand) > 4:
				self.topWindow.statusBar.SetStatusText("YEAH! You WON! Another Game?")
			else:
				self.topWindow.statusBar.SetStatusText("Awwwwwww. You LOSE! Another Game?")
			self.hitButton.Enable(False)
			self.stopButton.Enable(False)
		
	def onStop(self, event):
		self.hitButton.Enable(False)
		self.stopButton.Enable(False)
		guestPts = self.guest.getCurrentPoints()
		if guestPts == 21:
			self.topWindow.statusBar.SetStatusText("YEAH! You WON! Another Game?")
			self.hitButton.Enable(False)
			self.stopButton.Enable(False)
		else:
			for i in range(2):
				self.hostBox.Remove(0)
			
			hostPts = self.host.getCurrentPoints()
			while hostPts < guestPts and hostPts < 22 and len(self.host.hand) < 5:
				card = self.host.getCard()
				hostPts = self.host.getCurrentPoints()
			
			for card in self.host.hand:
				imgPath = self.picDir + self.getCardImgName(card)
				img = wx.StaticBitmap(self, wx.NewId(), 
							wx.BitmapFromImage(wx.Image(imgPath, wx.BITMAP_TYPE_PNG)))
				self.hostBox.Add(img, 0, wx.ALL, 2)
			self.hostBox.Fit(self)
			self.Sizer.Fit(self)
			self.Refresh()
			
			if hostPts == guestPts:
				self.topWindow.statusBar.SetStatusText("Meh, Tied. Another Game?")
			elif hostPts < 22 and (hostPts > guestPts or len(self.host.hand) > 4):
				self.topWindow.statusBar.SetStatusText("Awwwwwww. You LOSE! Another Game?")
			else:
				self.topWindow.statusBar.SetStatusText("YEAH! You WON! Another Game?")
		
	def onNewGame(self, event):
		self.topWindow.refreshBlackJack()

class rollDicePanel(wx.Panel):
	def __init__(self, parent):
		# get the images		
		self.picDir = os.getcwd() + '/pics/dices/'
		imageName = 'rolling-dice.gif'
		imagePath = self.picDir + imageName
	
		wx.Panel.__init__(self, parent, wx.NewId(), name='CompareDicePanel')
		sizer = wx.BoxSizer(wx.VERTICAL)
		# GIF animation toolbox: wx.animate
		diceWidget = wx.animate.GIFAnimationCtrl(self, wx.NewId(), imagePath)
		diceWidget.GetPlayer().UseBackgroundColour(True)
		diceWidget.Play()
		self.dicePic = diceWidget
		sizer.Add(diceWidget)
		
		rollButton = wx.Button(self, wx.NewId(), "ROLL!", size=(50,50), name="rollButton")
		self.Bind(wx.EVT_BUTTON, self.clickOnRollButton, rollButton)
		sizer.Add(rollButton, flag=wx.EXPAND)
		
		resultText = wx.StaticText(self, wx.NewId(), "Let's get it rolling!", size=(50, 50),
									style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE, name="resultText")
		font = wx.Font(18, family=wx.FONTFAMILY_MODERN, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)
		resultText.SetFont(font)
		self.resultText = resultText
		sizer.Add(resultText, flag=wx.EXPAND)
		self.SetSizer(sizer)
		self.Fit()
		
	def clickOnRollButton(self, event):
		number = random.choice([1, 2, 3, 4, 5, 6])
		self.resultText.SetLabel("You Got: %d" % number)
		self.resultText.style = wx.ALIGN_CENTRE
			
		diceImg = self.picDir + 'dice-%d.png' % number
		dicePic = wx.StaticBitmap(self, wx.NewId(), 
							wx.BitmapFromImage(wx.Image(diceImg, wx.BITMAP_TYPE_PNG)))
		self.GetSizer().Replace(self.dicePic, dicePic)
		self.dicePic.Destroy()
		self.dicePic = dicePic	
		

class mainFrame(wx.Frame):
	def __init__(self):
		# timer
		self.time = time.time()
	
		wx.Frame.__init__(self, None, wx.NewId(), 'Welcome to the Casino!', size=(800, 500), name='mainFrame')
		# MenuBar and Menu
		menuBar = wx.MenuBar()
		menuAbout = wx.Menu()
		menuItemAuthor = menuAbout.Append(wx.NewId(), "&Author", "Author information")
		menuBar.Append(menuAbout, "&About...")
		self.Bind(wx.EVT_MENU, self.clickOnMenuAboutAuthor, menuItemAuthor)
		self.SetMenuBar(menuBar)
		
		# StatusBar
		self.statusBar = self.CreateStatusBar()
		
		# Notebook (e.g. Tabs)
		panel = wx.Panel(self)
		self.panel = panel
		nb = wx.Notebook(panel)
		self.nb = nb
		
		tab1 = rollDicePanel(nb)
		tab2 = blackJackPanel(nb)
		
		nb.AddPage(tab1, "rollDice")
		nb.AddPage(tab2, "blackJack")
		nb.SetSelection(1)
		
		sizer = wx.BoxSizer()
		sizer.Add(nb, 1, wx.EXPAND)
		panel.SetSizer(sizer)
		panel.Fit()
		self.Fit()
		
	def clickOnMenuAboutAuthor(self, event):
		self.statusBar.SetStatusText("This program is developed by Charlie Chen")
		
	def refreshBlackJack(self):
		newGame = blackJackPanel(self.nb)
		tab = self.nb.GetPage(1)
		tab.Destroy()
		self.nb.RemovePage(1)
		self.nb.InsertPage(1,newGame, "blackJack")
		self.statusBar.SetStatusText("")
		self.nb.SetSelection(1)
		self.Refresh()
		
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = mainFrame()
	frame.Show()
	app.MainLoop()