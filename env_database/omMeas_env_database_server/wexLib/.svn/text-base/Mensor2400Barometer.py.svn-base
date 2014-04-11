#! !/usr/bin/env python
# file: omMeas/wexLib/Mensor2400Barometer.py


"""
This file implements the Mensor digital barometer class used by the
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

class Mensor2400Barometer(Device.Device):
    """
    The Mensor2400Barometer class implements that controler for the
    Mensor 2400 Barometer.
    """

#---------------------------------------------------------------------#

    def __init__(self, address):
        self.name = "Mensor 2400 barometer"
        trace ("Mensor2400Barometer.__init__(%s)" % address)
        Device.Device.__init__(self, address)
        try:    # if this open fails then try later
            self.openDevice()
        except Device.DeviceError:
            pass
        self.currentPressure = self.timestamp = None

#---------------------------------------------------------------------#

    def openDevice(self):
        trace ("Mensor2400Barometer.openDevice()")
        Device.Device.openDevice(self)
        self.sendCmdAndRecvResponse("NULL 0")
        self.sendCmdAndRecvResponse("PEAK 0")
        self.sendCmdAndRecvResponse("U 19")

#---------------------------------------------------------------------#

    def writeString (self, s='?'):
        trace ("Mensor2400Barometer.writeCmd(%s)" % s)
        s = "#*" +s +"\r\n"
        Device.Device.writeString (self, s)

#---------------------------------------------------------------------#

    def getPressure(self, maxAge = 1.0):
        """
        getPressure(maxAge = 1.0) --> float
        This routine returns the current pressure mesurment.
        maxAge is the maximum allowable age (in seconds) of the
        pressure data.
        """
        trace ("Mensor2400Barometer.getPressure()")
        if not self.isOpen():
            self.openDevice()
        if (maxAge > 0.1 and self.timestamp and self.currentPressure):
            now = time.time()
            if self.timestamp +maxAge > now:
                return self.currentPressure
        s = self.sendCmdAndRecvResponse('?').split()[1]
        try:
            self.currentPressure = float (s)
        except (ValueError, TypeError):
            raise Device.DeviceError (("Cannot parse Mensor Barometer"
                                                    " value: %s") % s)
        self.timestamp = time.time()
        return self.currentPressure

#---------------------------------------------------------------------#

    def getUnitInfo(self,):
        trace ("Mensor2400Barometer.getUnitInfo()")
        if not self.isOpen():
            self.openDevice()
        results = dict()
        results ["ID"] = self.sendCmdAndRecvResponse("ID?")[2:].strip()
        s = self.sendCmdAndRecvResponse("DC?")[2:].strip()
        results["CalibrationDate"]= s
        return results

#=====================================================================#

if __name__ == "__main__":
    try:
#        barometer = Mensor2400Barometer ("RS232 1 9600 8n1")
#        barometer = Mensor2400Barometer ("RS232 2")
        barometer = Mensor2400Barometer ("TCP rotr5sr1:2000")
#        barometer = Mensor2400Barometer ("TCP nowhere:2000")
    except Device.DeviceError, x:
        print "barometer create threw: ", str(x)
        print "   We're out of here"
        raise
    try:
        print barometer.getPressure()
    except Device.DeviceError, x:
        print "barometer.getPressure() threw: ", str(x)
    try:
        print barometer.getUnitInfo()
    except Device.DeviceError, x:
        print "barometer.getUnitInfo() threw: ", str(x)
    for i in range(10):
        time.sleep(1)
        print '.',
    print
    try:
        print barometer.getPressure()
    except Device.DeviceError, x:
        print "barometer.getPressure() threw: ", str(x)
    try:
        print barometer.getUnitInfo()
    except Device.DeviceError, x:
        print "barometer.getUnitInfo() threw: ", str(x)
    try:
        barometer.close()
    except Device.DeviceError, x:
        print "barometer.close() threw: ", str(x)
