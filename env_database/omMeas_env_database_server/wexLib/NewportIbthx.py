#! !/usr/bin/env python
# file: omMeas/wexLib/NewportIbthx.py


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

class NewportIbthx(Device.Device):
    """
    The NewportIbthx class implements that controler for the
    Newport Ibthx Thermometer/Barometer/Hygrometer.
    """

#---------------------------------------------------------------------#

    def __init__(self, address):
        self.name = "Newport Ibthx Thermometer/Barometer/Hygrometer"
        trace ("NewportIbthx.__init__(%s)" % address)
        Device.Device.__init__(self, address)
        self.setTcpDefaults (timeout = 5)
        try:    # if this open fails then try later
            self.openDevice()
        except Device.DeviceError:
            pass
        self.currTemperature = self.tempTimestamp = None
        self.currPressure = self.presTimestamp = None
        self.currHumidity = self.humiTimestamp = None

#---------------------------------------------------------------------#

    def writeString (self, s):
        trace ("NewportIbthx.writeCmd(%s)" % s)
        s = '*' +s +"\r"
        Device.Device.writeString (self, s)

#---------------------------------------------------------------------#

    def getPressure(self, maxAge = 1.0):
        """
        getPressure(maxAge = 1.0) --> float
        This routine returns the current pressure mesurment.
        maxAge is the maximum allowable age (in seconds) of the
        pressure data.
        """
        trace ("NewportIbthx.getPressure()")
        if not self.isOpen():
            self.openDevice()
        if (maxAge > 0.1 and self.presTimestamp and self.currPressure):
            now = time.time()
            if self.presTimestamp +maxAge > now:
                return self.currPressure
        s = self.sendCmdAndRecvResponse('SRHm')
        try:
            self.currPressure = float (s)
        except (ValueError, TypeError):
            raise Device.DeviceError (("Cannot parse Newport Pressure"
                                                    " value: %s") % s)
        self.presTimestamp = time.time()
        return self.currPressure

#---------------------------------------------------------------------#

    def getTemperature(self, maxAge = 1.0):
        """
        getTemperature(maxAge = 1.0) --> float
        This routine returns the current temperature mesurment.
        maxAge is the maximum allowable age (in seconds) of the
        temperature data.
        """
        trace ("NewportIbthx.getTemperature()")
        if not self.isOpen():
            self.openDevice()
        if (maxAge > 0.1 and self.tempTimestamp and
                                               self.currTemperature):
            now = time.time()
            if self.tempTimestamp +maxAge > now:
                return self.currTemperature
        s = self.sendCmdAndRecvResponse('SRTC')
        try:
            self.currTemperature = float (s)
        except (ValueError, TypeError):
            raise Device.DeviceError (("Cannot parse Newport "
                                        "temperature value: %s") % s)
        self.tempTimestamp = time.time()
        return self.currTemperature

#---------------------------------------------------------------------#

    def getHumidity(self, maxAge = 1.0):
        """
        getHumidity(maxAge = 1.0) --> float
        This routine returns the current Humidity mesurment.
        maxAge is the maximum allowable age (in seconds) of the
        temperature data.
        """
        trace ("NewportIbthx.getHumidity()")
        if not self.isOpen():
            self.openDevice()
        if (maxAge > 0.1 and self.humiTimestamp and self.currHumidity):
            now = time.time()
            if self.humiTimestamp +maxAge > now:
                return self.currHumidity
        s = self.sendCmdAndRecvResponse('SRH2')
        try:
            self.currHumidity = float (s)
        except (ValueError, TypeError):
            raise Device.DeviceError (("Cannot parse Newport "
                                        "Humidity value: %s") % s)
        self.humiTimestamp = time.time()
        return self.currHumidity

#---------------------------------------------------------------------#

if __name__ == "__main__":
    try:
        guage = NewportIbthx ("TCP rotr5wx1:2000")
#        guage = NewportIbthx ("TCP nowhere:2000")
    except Device.DeviceError, x:
        print "guage create threw: ", str(x)
        print "   We're out of here"
        raise
    for i in range(2):
        time.sleep(1)
        print '.',
    print
    try:
        print guage.getTemperature()
    except Device.DeviceError, x:
        print "guage.getTemperature() threw: ", str(x)
    try:
        print guage.getPressure()
    except Device.DeviceError, x:
        print "guage.getPressure() threw: ", str(x)
    try:
        print guage.getHumidity()
    except Device.DeviceError, x:
        print "guage.getHumidity() threw: ", str(x)
    for i in range(10):
        time.sleep(1)
        print '.',
    print
    try:
        print guage.getTemperature()
    except Device.DeviceError, x:
        print "guage.getTemperature() threw: ", str(x)
    try:
        print guage.getPressure()
    except Device.DeviceError, x:
        print "guage.getPressure() threw: ", str(x)
    try:
        print guage.getHumidity()
    except Device.DeviceError, x:
        print "guage.getHumidity() threw: ", str(x)
    try:
        guage.close()
    except Device.DeviceError, x:
        print "guage.close() threw: ", str(x)

