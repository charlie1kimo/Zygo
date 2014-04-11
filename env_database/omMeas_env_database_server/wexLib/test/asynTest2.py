#!/usr/bin/env python

import threading
import omMeas.wexLib.asynSched as asch
import time

# This is the simplest case: one thread sending a message to another thrad
# Thread1.TmrA (periodic)
#	on fire: send message Thread2.ActionA


# PQ demo: Thread2 is a server, and "calls back" Thread1 with the result
# Thread1.TmrP	(periodic)
#	on fire: send message Thread2.ActionP
# Thread2.ActionP
#	start one-shot delay timer TmrQ
# Thread2.TmrQ
#	on fire: send message Thread1.ActionQ
# Thread1.ActionQ
#	print message

def pract(who, what):
    print "%2d: %15s: %s" % (time.time() % 60, who, what)

class testFsm1:
    def __init__(self,asch,fsm2):
	self.asch = asch
	self.fsm2 = fsm2
	tmrA = self.asch.createTimer("TmrA", self)
	tmrA.startTmr(9, True)
	tmrP = self.asch.createTimer("TmrP", self)
	tmrP.startTmr(5, True)
	
    def handle_timer(self, tmrName, tmrObj):
	if tmrName == "TmrA":
	    pract("Fsm1.TmrA", "Requesting Fsm2.ActionA")
	    self.fsm2.asch.put_callback( 
		self.fsm2.ActionA, ("first arg", 200, "third arg"))
	
	elif tmrName == "TmrP":
	    pract("Fsm1.TmrP", "Requesting Fsm2.ActionP")
	    self.fsm2.asch.put_callback( 
		self.fsm2.ActionP, (self.asch, self.ActionQ, (5, "hello")))

    def ActionQ(self, arg1, arg2):
	pract("Fsm1.ActionQ", " %s %s" % (arg1, arg2))


class testFsm2:
    def __init__(self,asch):
	self.asch = asch

    def ActionA(self, arg1, arg2, arg3):
	pract("Fsm2.ActionA", "got %s %s %s" % (arg1, arg2, arg3))
	

    def ActionP(self, cbAsch, cbFunc, cbArgs):
	pract("Fsm2.ActionP", "starting TmrQ")
	tmrQ = self.asch.createTimer("TmrQ", self)
	tmrQ.extra_cbAsch = cbAsch
	tmrQ.extra_cbFunc = cbFunc
	tmrQ.extra_cbArgs = cbArgs
	tmrQ.startTmr(2, False)
	
    def handle_timer(self, tmrName, tmrObj):
	if tmrName == "TmrQ":
	    pract("Fsm2.TmrQ", "invoking callback (Fsm1.ActionQ)")
	    tmrObj.extra_cbAsch.put_callback( 
		tmrObj.extra_cbFunc, tmrObj.extra_cbArgs)


class testServerThread1(threading.Thread):
    def __init__(self,fsm2):
	#print "ServerThread1: init start"
	threading.Thread.__init__(self)
	self.asch = asch.asynScheduler(self.getName())
	self.wakeup = self.asch.getWakeup()
	self.fsm1 = testFsm1(self.asch, fsm2)
	#print "ServerThread1: init done"
	
    def run(self):
	#print "ServerThread1: main loop start"
	self.asch.loop()
	#print "ServerThread1: main loop done"


class testServerThread2(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)
	self.asch = asch.asynScheduler(self.getName())
	self.wakeup = self.asch.getWakeup()
	self.fsm2 = testFsm2(self.asch)
	
    def run(self):
	self.asch.loop()

class testConsoleReader(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)

    def run(self):
	while True:
	    str = raw_input("Cmd> ")
	    if str == "quit":
		print "Got quit cmd"
	    else:
		print "Unknown command"
	
#mySched = asch.asynScheduler()
print "MainApp: start"
conReader = testConsoleReader()
serverThread2 = testServerThread2()
serverThread1 = testServerThread1(serverThread2.fsm2)

serverThread2.start()
serverThread1.start()

conReader.start()

#serverThread1.join()

#mySched.loop()
