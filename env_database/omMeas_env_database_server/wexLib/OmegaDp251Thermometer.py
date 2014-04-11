#! !/usr/bin/env python
# file: omMeas/wexLib/OmegaDp251Thermometer.py


"""
This file implements the Omega digital Thermometer class used by the
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

class OmegaDp251Thermometer(Device.Device):
    """
    The OmegaDp251Thermometer class implements that controler for the
    Omega Dp251 Thermometer.
    """

#---------------------------------------------------------------------#

    def __init__(self, address):
        self.name = "Omega Dp251 Thermometer"
        trace ("OmegaDp251Thermometer.__init__(%s)" % address)
        Device.Device.__init__(self, address)
        self.setRS232Defaults (baud = 19200, stopbits = 2)
        try:
            self.openDevice()
        except Device.DeviceError:
            pass
        self.currentTemperature = self.timestamp = None

#---------------------------------------------------------------------#

    def openDevice(self):
        trace ("OmegaDp251Thermometer.openDevice()")
        Device.Device.openDevice(self)
        self.sendCmdAndRecvResponse("U0", False)
        time.sleep(0.1) #short nap while the Thermometer thinks.
        self.sendCmdAndRecvResponse("P0", False)

#---------------------------------------------------------------------#

    def writeString (self, s):
        trace ("OmegaDp251Thermometer.writeCmd(%s)" % s)
        s = s +"\r\n"
        Device.Device.writeString (self, s)

#---------------------------------------------------------------------#

    def getTemperature(self, maxAge = 1.0):
        """
        getTemperature(maxAge = 1.0) --> float
        This routine returns the current temperature mesurment.
        maxAge is the maximum allowable age (in seconds) of the
        temperature data.
        """
        trace ("OmegaDp251Thermometer.getTemperature()")
        if not self.isOpen():
            self.openDevice()
        if (maxAge > 0.1 and self.timestamp and
                                            self.currentTemperature):
            now = time.time()
            if self.timestamp +maxAge > now:
                return self.currentTemperature
        s = self.sendCmdAndRecvResponse('T')
        if s == None or len(s) == 0:
            return None
        s = s[1:].strip()[:-1]
        try:
            self.currentTemperature = float (s)
        except (ValueError, TypeError):
            raise Device.DeviceError (("Cannot parse Omega "
                                        "temperature value: %s") % s)
        self.timestamp = time.time()
        return self.currentTemperature

#=====================================================================#

if __name__ == "__main__":
    try:
#        thermometer = OmegaDp251Thermometer ("RS232 1 19200 8n2")
#        thermometer = OmegaDp251Thermometer ("RS232 2")
        thermometer = OmegaDp251Thermometer ("TCP rotr5sr1:2000")
#        thermometer = OmegaDp251Thermometer ("TCP nowhere:2000")
    except Device.DeviceError, x:
        print "thermometer create threw: ", str(x)
        print "   We're out of here"
        raise
    for i in range(2):
        time.sleep(1)
        print '.',
    print
    try:
        print thermometer.getTemperature()
    except Device.DeviceError, x:
        print "thermometer.getTemperature() threw: ", str(x)
    for i in range(10):
        time.sleep(1)
        print '.',
    print
    try:
        print thermometer.getTemperature()
    except Device.DeviceError, x:
        print "thermometer.getTemperature() threw: ", str(x)
    try:
        thermometer.close()
    except Device.DeviceError, x:
        print "thermometer.close() threw: ", str(x)
