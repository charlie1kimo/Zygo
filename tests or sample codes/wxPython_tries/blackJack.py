"""
black jack game and black jack host
"""

import os
import random

class blackJack():
	def __init__(self):
		self.picDir = os.getcwd() + '\\pics\\playingCards\\'
		self.deck = self.createDeck()			# deck is a list of String [D1, S2] = ]diamond Ace, Spade 2]
	
	# return a list of cards (Strings)
	def createDeck(self):
		deck = []
		for i in range(1, 14):
			deck.append('S'+str(i))
			deck.append('H'+str(i))
			deck.append('D'+str(i))
			deck.append('C'+str(i))
		
		return deck
	
	def refreshDeck(self):
		self.deck = self.createDeck()
	
	# return a String list as hands
	def giveHands(self):
		firstCard = random.choice(self.deck)
		self.deck.remove(firstCard)
		secondCard = random.choice(self.deck)
		self.deck.remove(secondCard)
		
		return [firstCard, secondCard]
		
	def giveCard(self):
		card = random.choice(self.deck)
		self.deck.remove(card)
		
		return card
		
class blackJackPlayer():
	def __init__(self, blackJackGame):
		self.blackJackGame = blackJackGame
		self.getHands()
		
	def getHands(self):
		self.hand = self.blackJackGame.giveHands()
		
	def getCurrentPoints(self):
		pts = 0
		numAces = 0
		for i in self.hand:
			n = int(i[1:])
			if n > 9:
				pts += 10
			elif n == 1:
				numAces += 1
			else:
				pts += n
				
		while numAces > 0:
			if pts + 11 > 21:
				pts += 1
			else:
				pts += 11
			numAces -= 1
		
		return pts
			
	def getCard(self):
		card = self.blackJackGame.giveCard()
		self.hand.append(card)
		return card
		
	def replay(self):
		self.hand = []
		self.getHands()
		
	