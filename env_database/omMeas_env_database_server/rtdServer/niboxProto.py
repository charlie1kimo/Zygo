#! !/usr/bin/env python
# file: omMeas/rtdServer/nibox.py

"""
.
"""

# original author: kw
# rewrite author: glc

#=====================================================================#

import traceback
import asyncore, socket
import omMeas.wexLib.asynSched as asynSched
import struct
import time
import DbHandler
import SensorCache

##import pyodbc
##dbTimestampFormat = "%Y/%m/%d %H:%M:%S"     #mySQL timestamp format
###dbTimestampFormat = "%d/%b/%Y %H:%M:%S"    #ms access timestamp format

import logging

StateConnStall = dict(name='connStall') # hold-off before trying to start again
StateConnPend = dict(name='connPend')   # did connect(), waiting for complete
StateRecvHdr =  dict(name='recvHdr')
StateRecvBody = dict(name='recvBody')
StateRecvDead = dict(name='connDead')

#======================================================================#

class niboxReader(asynSched.asynStream):

#----------------------------------------------------------------------#

    def __init__(self, asch, niboxName, host, port=2055):
        asynSched.asynStream.__init__(self, asch)
        self.asch = asch        # asynScheduler
##        try:
##            self.db = pyodbc.connect("DSN=OmMeas")
##        except pyodbc.Error:
##            self.db = None
##        self.sqlStmt = "INSERT INTO SensorValues VALUES (?,?,?)"

        self.autoRestartB = 1
        self.niboxName = niboxName      # for serving data
        if host == None:
            host = "localhost"
        self.serverHost = host
        if port == None:
            port = 2055
        self.serverPort = port

        # After initiating connect(), wait this long before declaring error
        self.ConnPendTmr =  asch.createTimer('ConnPend', self)
        self.ConnPendSecs = 10

        # After error, we close connection and wait this long
        # before trying to connect again
        self.ConnStallTmr = asch.createTimer('ConnStall', self)
        self.ConnStallSecs = 60

        # Wait at most this long between each row (and for first row)
        self.DataRowTmr = asch.createTimer('DataRow', self)
        self.DataRowSecs = 150
        
        self.stateName = StateConnPend['name']

        self.startConn()

#----------------------------------------------------------------------#

    def _dbgMsg(self,msg):
#       print "DBG: %-8s: %s" % (self.stateName, msg)
        pass

#----------------------------------------------------------------------#

    def gotoState(self,st):
        self.stateName = st['name']

#----------------------------------------------------------------------#

    def isState(self,st):
        return self.stateName == st['name']

#----------------------------------------------------------------------#

    def fatalProto(self,msg):
        print "Fatal error in protocol: %s" % msg
        logging.error ("Fatal error in protocol: %s" % msg)
        self.close()
        self.ConnStallTmr.stopTmr()
        self.ConnPendTmr.stopTmr()
        self.DataRowTmr.stopTmr()

        if ( self.autoRestartB ):
            self.gotoState(StateConnStall)
            self.ConnStallTmr.startTmr(self.ConnStallSecs)
        else:
            self.gotoState(StateConnDead)

#----------------------------------------------------------------------#

    def startConn(self):
        # XXX: should really trap exceptions?
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print self.serverHost #DEBUG
        print self.serverPort  #DEBUG
        self.connect( (self.serverHost, self.serverPort) )
        self.ackstr = "\0\0\0\4" + "\0\0\0\0"
        self.ackstr = "\0\0\0\1" + "0"
        self.rxbuf = ""
        self.txbuf = ""
        self.gotoState(StateConnPend)
        self.ConnPendTmr.startTmr( self.ConnPendSecs)

#----------------------------------------------------------------------#

    def handle_connect(self):
        self._dbgMsg("Connected.")
        self.gotoState(StateRecvHdr)
        self.ConnPendTmr.stopTmr()
        self.DataRowTmr.startTmr( self.DataRowSecs)
        print "NIBOX: Connected to server %s: (%s:%d)" % (
                self.niboxName, self.serverHost, self.serverPort)
        logging.info ("NIBOX: Connected to server %s: (%s:%d)" % (
                self.niboxName, self.serverHost, self.serverPort))

#----------------------------------------------------------------------#

    def handle_close(self):
        self.fatalProto("NIBOX shutdown TCP connection.")

#----------------------------------------------------------------------#

    def handle_expt(self):
        #was there a socket error?
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        self.fatalProto("Got exception condition on socket -- don't understand this: %s" % str (err))

#----------------------------------------------------------------------#

    def handle_error(self):
        print "Software Error in NIBOX Reader!"
        logging.error ("Software Error in NIBOX Reader!")
        traceback.print_exc()
        self.fatalProto("SOFTWARE ERROR")

#----------------------------------------------------------------------#

    def procRxRow(self, rowStr):
        # format of rowStr is
        #<boardNum>,<unknown>,<date>,<time>,<val>,...,<val>,<calSerial>
        self._dbgMsg("Got: %s" % rowStr)
        self.DataRowTmr.startTmr( self.DataRowSecs)
#        print rowStr
        els = rowStr.strip().split(',')
#        row_idx1 = els[0]
        try:
            row_brdIdx = int(els[0])
        except:
            print "Error converting board index --%s--" % els[0]
            logging.error ("Error converting board index --%s--" %
                                                                els[0])
            return(0)
        row_date = els[2]   # %m-%d-%y format
        row_time = els[3]   # %H:%M:%S format
        niTime = time.strptime ("%s %s" % (row_date, row_time),
                                                    "%m-%d-%y %H:%M:%S")
#       row_reads = els[4:]
        if els [-1].strip()[0] == '-':
            calSerial = els[-1].strip()
            row_reads = els[4:-1]
        else:
            calSerial = None
            row_reads = els[4:]

#        nowStr = time.strftime (dbTimestampFormat)
#        print row_date, row_time, time.strftime (dbTimestampFormat)
##        nowStr = time.strftime (dbTimestampFormat, niTime)
#        nowStr = DbHandler.getTimeStr (niTime)
        nowStr = DbHandler.getTimeStr ()
        listOfParams = []
        for chanIdx in range(len(row_reads)):
            rdStr = row_reads[chanIdx].strip()
            if len(rdStr)==0: 
                continue
            self._dbgMsg("CHAN=%d, VAL=%s" % (chanIdx, rdStr))
            sName = "%s.%d.%d" % (self.niboxName, row_brdIdx, chanIdx)
            try:
                listOfParams.append ((sName, nowStr, float(rdStr)))
                SensorCache.updateSensor("T." +sName, rdStr,
                                                calSerial = calSerial)
            except ValueError:
                listOfParams.append ((sName, nowStr, 0.0))
                SensorCache.updateSensor("T." +sName,
                                "ValueError: %s" % rdStr,
                                calSerial = calSerial, isError = True)
                print ("Bad value for %s: %s" % (sName, rdStr))
                print ("   " +str(rowStr))

        DbHandler.insertValues (listOfParams)

#----------------------------------------------------------------------#

    def procRxOne(self):
        # returns 1 if work done and thus more work possible
        if self.isState(StateRecvHdr):
            if len(self.rxbuf) < 4:
                return 0
            rxlenstr = self.getRxStr(4)
            #print "rxlenstr = --%d--%d--%d--%d--" % (ord(rxlenstr[0]), ord(rxlenstr[1]), ord(rxlenstr[2]), ord(rxlenstr[3]))

            rxlen, = struct.unpack(">l", rxlenstr)
            self._dbgMsg("hdr rxlen = %d" % rxlen)
            if ( rxlen < 0 or rxlen > 10000 ):
                self.fatalProto("length in header bogus: %d" % rxlen)
                return
            self.curRxLen = rxlen
            self.gotoState(StateRecvBody)

        if self.isState(StateRecvBody):
            if len(self.rxbuf) >= self.curRxLen:
                if self.curRxLen > 0:
                    datastr = self.getRxStr(self.curRxLen)
                    self.procRxRow(datastr)
                self.gotoState(StateRecvHdr)
                self.txbuf += self.ackstr
                return 1
            else:
                self._dbgMsg("Waiting %d" % (self.curRxLen - len(self.rxbuf)) )

        return 0

#----------------------------------------------------------------------#

    def writable(self):
        return ( self.isState(StateConnPend) or len(self.txbuf) > 0 )

#----------------------------------------------------------------------#

    def handle_timer(self,tmrName,tmrObj):
        if ( tmrName == 'ConnStall' and self.isState(StateConnStall) ):
            self.startConn()
        elif ( tmrName == 'ConnPend' and self.isState(StateConnPend) ):
            self.fatalProto("NIBOX server didn't accept TCP connection within timeout.")
        elif ( tmrName == 'DataRow' ):
            self.fatalProto("NIBOX server didn't send next data row within timeout.")
        else:
            raise KeyError, 'Unexpected timer %s in state %s' % (
                tmrName, self.stateName)
        # print "GOT tmr event %s" % tmrName
        
