
import traceback
import socket
import asyncore
import sched
import time
import os
import threading
import Queue

class ExitLoop(Exception):
    pass

class asynStream(asyncore.dispatcher):
    def __init__(self, asch, sock=None, maxrx=-1):
	asyncore.dispatcher.__init__(self, sock, asch.sockMap)
	self.asch = asch	# asynScheduler
	self.maxrx = maxrx
	self.rxbuf = ""
	self.txbuf = ""

    def getRxStr(self,sublen):
	rs1 = self.rxbuf[0:sublen]
	self.rxbuf = self.rxbuf[sublen:]
	return (rs1)

    def fatalProto(self, msg):
	# This should almost always be overriden by the child class
	print "asynStream: Fatal error in protocol: %s" % msg
	self.close()
	self.rxbuf = ""
	self.txbuf = ""
	
    def procRxOne(self):
	fatalProto(self, "Unhandled procRxOne")
	# returns 1 if work done and thus more work possible, else 0
	return 0

    def procRxAll(self):
	while ( self.procRxOne() ):
	    pass
	if ( self.maxrx >=0 and len(self.rxbuf) > self.maxrx ):
	    self.fatalProto(self, "Rx message too long or malformed")

    def handle_read(self):
	# ideally we would loop the recv until no more data.
	# but the design of the underlying asyncore doesn't allow this:
	# it assumes fatal error if the read never returns data
	# thus we have to go all the way back to the select loop
	# and then get reinvoked.
	rxstr = self.recv(8192)
	self.rxbuf += rxstr
	self.procRxAll()
	
    def writable(self):
	return ( len(self.txbuf) > 0 )

    def handle_write(self):
	sentCnt = self.send(self.txbuf)
	self.txbuf = self.txbuf[sentCnt:]


# TCP client (performs initial connection, and sends 
# single byte for each wakeup request
# Note that generally we are called from a different thread than the
# one that hosts our select loop. Thus we can't use the writable/txbuf
# mechanism to send data. Instead, we have to send it directly.
class asynWakeupClient(asynStream):
    def __init__(self, asch, name, serverHost, serverPort):
	asynStream.__init__(self,asch)
	self.name = name
	self.create_socket( socket.AF_INET, socket.SOCK_STREAM)
	# by pre-loading the txbuf, we get the connect event
	self.txbuf += "1"
	print "%s: WakeupClient: connecting to %d" % (name, serverPort)
	self.connect( (serverHost, serverPort) )
	self.readyB = False
	self.sendLock = threading.Lock()

    def handle_connect(self):
	print "%s: WakeupClient: ready" % self.name
	self.readyB = True
	pass

    def procRxAll(self):
	print "Wacky: got rx data on WakeupClient -- should never happen"
	# above happens if server closes connection on us

    def send_wakeup(self):
	if not self.readyB:
	    raise RuntimeError, "%s: Wakeup client isn't ready yet" % self.name

	# invoked by higher layer to wakeup our server
	# this needs to be mutex protected
	
	self.sendLock.acquire()
	if self.send("1") == 0:
	    print "Buffer full -- probably ok?"
	self.sendLock.release()
    

class asynWakeupServer(asynStream):
    def __init__(self, wakeupHandler, asch, sock):
	asynStream.__init__(self, asch, sock)
	self.wakeupHandler = wakeupHandler
	self.asch = asch
	print "%s: WakeupServer: ready" % self.asch.name

    def procRxAll(self):
	# clear everything we have
	self.rxbuf = ""
	self.wakeupHandler.handle_wakeup()

    def handle_close(self):
	self.close()
	# treat this as normal case, we are just shutting down

class asynWakeupListener(asyncore.dispatcher):
    def __init__(self, asch, wakeupHandler, sock=None):
	asyncore.dispatcher.__init__(self, sock, asch.sockMap)
	self.asch = asch
	self.wakeupHandler = wakeupHandler
	self.serverObj = None
	# TBD: only create if not already created!
	self.create_socket( socket.AF_INET, socket.SOCK_STREAM)

    def bind_in_range(self, serverHost, serverPortBase, serverPortLen=1):
	self.serverHost = serverHost
	self.serverPort = None
	for pidx in range(serverPortLen):
	    portNum = serverPortBase + pidx
	    try:
	        self.bind( (serverHost, portNum) )
	    except socket.error:
		#traceback.print_exc()
		continue
	    break
	else:
	    raise RuntimeError, "No port available for wakeup server"
	self.serverPort = portNum

    def handle_accept(self):
	cliSock, cliAddr = self.accept()
	self.close()	# we don't want any more clients
	self.serverObj = asynWakeupServer(self.wakeupHandler, self.asch, cliSock)

    def writable(self):
	return(False)

    def handle_read(self):
	# called as side-effect of accept notification
	pass

    def handle_connect(self):
	# not sure why we need this...
	pass


class asynWakeup:
    def __init__(self, asch, name):
	self.name = name
	self.serverHost = "localhost"
	self.serverPortBase = 6700
	self.serverPortLen = 100
	self.msgQueue = Queue.Queue(1000)

	self.listenObj = asynWakeupListener( asch, self)
	self.listenObj.bind_in_range( self.serverHost, self.serverPortBase,
		self.serverPortLen)
	self.listenObj.listen(1)
	portNum = self.listenObj.serverPort
	print "%s: Wakeup server listening on %d" % (name, portNum)
	self.clientObj = asynWakeupClient( asch, name, self.serverHost, portNum)
	
    def send_wakeup(self):
	self.clientObj.send_wakeup()
	
    def handle_wakeup(self):
	# Invoked when our server detects a wakeup event
	#print "asynSched: got wakeup request"
	while 1:
	    msg = None
	    try:
		msg = self.msgQueue.get(False)
	    except Queue.Empty:
		break
	    msgCat = msg['cat']
	    if msgCat == 'func':
		#print "Got function message from queue"
		args = msg['argsRef']
		msg['funcRef'](*args)
	    else:
		print "%s: Bogus message category: %s" % (self.name, msgCat)

    def put_callback(self, func, args):
	msg = dict(cat='func', funcRef=func, argsRef=args)
	self.msgQueue.put(msg, False)
	self.clientObj.send_wakeup()
	# TBD: could optimize the above: we don't need to send wakeup
	# if we know a prior one is already pending
		
class asynScheduler(sched.scheduler):
    def __init__(self, name):
	sched.scheduler.__init__(self, time.time, self.delayFunc)
	# sockmap below is used by the asyncore functions to track
	# arguments to the select/poll calls. This argument must be
	# passed to the init call of all asyncore.dispatchers running
	# in the same thread
	self.name = name
	self.sockMap = {}

	self.finalFireSecs = 60
	self.wakeupObj = None
	self.stopLoopB = False

    def getWakeup(self):
	if ( self.wakeupObj is None ):
	    self.wakeupObj = asynWakeup(self, self.name)
	return self.wakeupObj

    def delayFunc(self, delaySecs):
	if ( self.stopLoopB ):
	    raise ExitLoop, "Exiting mainloop from delay"
	if delaySecs == 0:
	    #print "DBG: delay of zero"
	    pass
	else:
	    #print "DBG: delay of %.4f" % delaySecs
	    # asyncore.loop(delaySecs, False, None, 1)
	
	    if self.sockMap:
	        asyncore.poll(delaySecs, self.sockMap)
	    else:
		time.sleep(delaySecs)

    # the scheduler requires there to be at least one schedule event,
    # or it doesn't run anything. Here, we setup a fake event
    # that just keeps rescheduleing itself. In any real program
    # there will always be timers in the future, but sometimes in the 
    # trivial case, there is nothing and we need this fake one
    def finalFire(self):
	# reschedule another one
	self.finalEventId = self.enter(self.finalFireSecs, 0, 
		self.finalFire, ())

    def killFinalFire(self):
	id = self.finalEventId
	self.finalEventId = None
	self.cancel(id)
	
    def loop(self):
	self.finalFire() 	# setup initial timer
	try:
	    self.run()
	except ExitLoop:
	    print "AsynSched: ExitLoop exception"
	    pass
	self.killFinalFire()
    
    def stopLoop(self):
	self.stopLoopB = 1

    def put_callback(self, func, args):
	w = self.getWakeup()
	w.put_callback(func, args)
	

    def createTimer(self, name, dispatcher):
	tmrObj = asynTimer(name, dispatcher, self)
	return tmrObj

class asynTimer:
    def __init__(self, name, dispatcher, asch):
	self.name = name
	self.dispatcher = dispatcher
	self.asch = asch
	self.evtId = None

    def stopTmr(self):
	# ideally, we would know how much time has already expired,
	# so that the timer could be restarted. That is possible, but
	# not something I'm going to worry about until needed.
	if self.evtId is not None:
	    self.asch.cancel(self.evtId)
	    self.evtId = None
	#print "stop timer %s" % self.name

    def startTmr(self, delaySecs, recurB=False, priority=0):
	self.stopTmr()
	self.delaySecs = delaySecs
	self.recurB = recurB
	self.priority = priority
	self.evtId = self.asch.enter(delaySecs, priority,  self.fireEvt, ())
	#print "start timer %s, %f" % (self.name, delay)
	if ( delaySecs < 0.1 ):
	    raise RuntimeError, "bogus delay value"

    def fireEvt(self):
	self.evtId = None
	if self.recurB:
	    # this approach leads to slipping time base -- should really
	    # use absolute time base
	    self.evtId = self.asch.enter(self.delaySecs, 
		self.priority, self.fireEvt, ())
	self.dispatcher.handle_timer(self.name,self)

