#! !/usr/bin/env python
# file: omMeas/wexLib/DiconGp700Switch.py


"""
This file implements the Dicon Gp700 Switch class used by the
wavelength server.
"""

# author: glc

#=====================================================================#

import time
import Device

#=====================================================================#

TRACE = __name__ == "__main__"
#TRACE = True

#=====================================================================#

def trace(s):
    if TRACE:
        print s

#=====================================================================#

# TODO: should this be an is-a or has-a relashionship?

class DiconGp700Switch(Device.Device):
    """
    The DiconGp700Switch class implements that controler for the
    Dicon Gp700 fiber optic Switch.
    """

#---------------------------------------------------------------------#

    def __init__(self, address):
        self.name = "Dicon Gp700 fiber optic switch"
        trace ("DiconGp700Switch.__init__(%s)" % address)
        Device.Device.__init__(self, address)
        self.setRS232Defaults (baud = 1200)
        try:    # if this open fails then try later
            self.openDevice()
        except Device.DeviceError:
            pass

#---------------------------------------------------------------------#

    def openDevice(self):
        trace ("DiconGp700Switch.openDevice()")
        Device.Device.openDevice(self)
        self.sendCmdAndRecvResponse("SERIAL:OPEN", False)

#---------------------------------------------------------------------#

    def writeString (self, s):
        trace ("DiconGp700Switch.writeCmd(%s)" % s)
        s = s +"\n"
        Device.Device.writeString (self, s)

#---------------------------------------------------------------------#

    def close(self):
        trace ("DiconGp700Switch.close()")
        self.sendCmdAndRecvResponse("SERIAL:CLOSE", False)
        Device.Device.close(self)

#---------------------------------------------------------------------#

    def setMswitch (self, module, outputChanel, inputChanel = None):
        trace ("DiconGp700Switch.setMswitch()")
        if not self.isOpen():
            self.openDevice()
        eggs = "M%s %s" % (str (module), str (outputChanel))
        if inputChanel != None:
            eggs = eggs +", %s" % str (inputChanel)
        self.sendCmdAndRecvResponse(eggs, False)

            # "*OPC?" means wait until done...
        self.sendCmdAndRecvResponse("*OPC?")

#---------------------------------------------------------------------#

    def getUnitInfo(self):
        trace ("DiconGp700Switch.getUnitInfo()")
        if not self.isOpen():
            self.openDevice()
        results = dict()
        results ["ID"] = self.sendCmdAndRecvResponse("*IDN?").strip()
        results["Configuration"]=self.sendCmdAndRecvResponse("SYST:CONF?").strip()
        dateStr = self.sendCmdAndRecvResponse("SYST:DATE?").strip()
        timeStr = self.sendCmdAndRecvResponse("SYST:TIME?").strip()
        dateTokens = dateStr.split(",")
        timeTokens = timeStr.split(",")
        results["Mux clock"] = "%s-%s-%s %s:%s:%s" % (
                        dateTokens[0].strip(), dateTokens[1].strip(),
                        dateTokens[2].strip(), timeTokens[0].strip(),
                        timeTokens[1].strip(), timeTokens[2].strip())
        return results

#=====================================================================#

if __name__ == "__main__":
    try:
        opticalSwitch = DiconGp700Switch ("RS232 4 1200")
#        opticalSwitch = DiconGp700Switch("TCP rotr5sr1:2000")
#        opticalSwitch = DiconGp700Switch("TCP nowhere:2000")
    except Device.DeviceError, x:
        print "switch create() threw: ", str(x)
        print "   We're out of here"
        raise
    try:
        print opticalSwitch.getUnitInfo()
    except Device.DeviceError, x:
        print "opticalSwitch.getUnitInfo() threw: ", str(x)
    for i in range(8):
        try:
            print "sending M1 %i" % (i +1)
            opticalSwitch.setMswitch (1, i +1)
        except Device.DeviceError, x:
            print "opticalSwitch.setMswitch() threw: ", str(x)
        
    for i in range(2):
        time.sleep(1)
        print '.',
    print
    try:
        print opticalSwitch.getUnitInfo()
    except Device.DeviceError, x:
        print "opticalSwitch.getUnitInfo() threw: ", str(x)
    for i in range(8):
        try:
            print "sending M1 %i" % (i +1)
            opticalSwitch.setMswitch (1, i +1)
        except Device.DeviceError, x:
            print "opticalSwitch.setMswitch() threw: ", str(x)
    try:
        opticalSwitch.setMswitch (1, 3)
    except Device.DeviceError, x:
        print "opticalSwitch.setMswitch() threw: ", str(x)
    try:
        opticalSwitch.close()
    except Device.DeviceError, x:
        print "opticalSwitch.close() threw: ", str(x)
