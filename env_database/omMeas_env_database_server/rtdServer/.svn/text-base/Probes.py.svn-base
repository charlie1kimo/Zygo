#! !/usr/bin/env python
# file: omMeas/rtdServer/Probes.py

"""
This file implements the probes used by the enviroment server.

Differences between Devices and Probes.
A Device is a physical object (i.e. "something you can kick"); a Probe
is something that returns a measurment.  Some devices, like the Newport
iBTHX support multiple Probes since they can measure different values.
Probes usually have an associated device (but not always--the Default
Device doesn't have an associated device).
"""

# author: glc

#=====================================================================#

#import wx                           #The wx Gui stuff
#import threading, Queue
import time
import random, math
import string

import Config
import omMeas.wexLib.Device as Device

#=====================================================================#

class ProbeError(EnvironmentError):
    """
    This exception class is used when any of the probe classes need to
    throw an exception.
    """
    def __init__(self, why):
        if not why:
            why = "Probe error"
        EnvironmentError.__init__(self, 0, why)

#=====================================================================#

class AbstractProbe:
    """
    Abstract probe is an abstract class that all measurement probe
    objects inherit from.
    """
    def __init__(self, name, units, cacheName = None):
        """
        __init__(self, name, units) --> None
        The abstract probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        """
        self.name = name
        self.units = units
        self.cacheName = cacheName
        if cacheName is None:
            self.cacheName = name
    def getValue(self):
        """
        getValue() --> float
        The derived classes will overload this routine to return the
        probe value.
        """
        assert 0, "abstract probe"
    def getName(self):
        """
        getName() --> string
        Returns the object name. This value is used when the probe
        value is displayed for debugging.
        """
        return self.name
    def getCacheName(self):
        """
        getCacheName() --> string
        Returns the name used by the SensorCache name.
        """
        return self.cacheName
    def getUnits(self):
        """
        getUnits() --> string
        Returns the class units. This value is used when the probe
        value is displayed for debugging.
        """
        return self.units
    def lockProbe(self):
        """
        lockProbe() --> None
        This routine will lock a mutex if the probe cannot support
        parallel access. The derived classes will overload this routine
        to if the probe cannot support parallel access to the probe.
        """
        pass
    def unlockProbe(self):
        """
        unlockProbe() --> None
        This routine will unlock a mutex if the probe cannot support
        parallel access. The derived classes will overload this routine
        to if the probe cannot support parallel access to the probe.
        """
        pass
    def display(self,value):
        """
        display(value) --> None
        This routine displays the probe value for debugging.
        """
        pass
#        print ("  %s: %s %s" %(self.getName(), str(value),
#                                                   self.getUnits()))

#=====================================================================#

class DefaultProbe(AbstractProbe):
    """
    DefaultProbe is a "probe" where all measurements are defined by the
    the config file.
    """
    def __init__(self, name, units, token):
        """
        __init__(self, name, units, token) --> None
        The default probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        token   a string containing the value to be returned and
                optionally an error ammount.  This string is in the
                format
                "<value> [<space> +/- <error> [%]] | [<space><delay>]".
        """
        if token is None or token == "":
            raise ParseError (name +" missing <value> in "
                                            "DefaultProbe.__init__()")
        AbstractProbe.__init__(self, name, units)
        tokens = token.strip().split(None, 1)
        self.value = float (tokens [0])
        self.error = 0
        self.delay = 0.1
        if len(tokens) != 1:
            s = tokens [1].strip()
            delayStr = errorStr = ""
            tokens = s.split(None, 1)

            if s[0] in string.digits:
                delayStr = tokens[0]
                if len(tokens) > 1:
                    errorStr += tokens[1]
            else:
                errorStr = tokens[0]
                if len(tokens) > 1:
                    delayStr = tokens[1]

            try:
                if len(delayStr) > 0:
                    self.delay = float (delayStr)
                if len(errorStr) > 0:
                    percent = (errorStr[-1] == '%')
                    if percent:     # is error a % of value?
                        self.error = float(errorStr[3:-1])
                    else:
                        self.error = float(errorStr[3:])

                    if percent:     # make error dependent of value
                        self.error *= self.value/100.0
            except ValueError:
                raise ParseError (self.name +" bad parameter in "
                                            "DefaultProbe.__init__()")

#---------------------------------------------------------------------#

    def getValue(self):
        """
        getValue() --> float
        Return the value defined from the config file.
        """
        time.sleep (self.delay)
        if self.error:
            randNum = 3.0*(random.random() +random.random()
                       +random.random() -1.5)
            delta = self.error*randNum
        else:
            delta = 0
        value = self.value +delta
        self.display(value)
        return value

#=====================================================================#

class Mensor2400Probe(AbstractProbe):
    """
    Mensor2400Probe is a probe where all measurements are made by the
    Mensor 2400 Barometer.
    """
#    myMutex = threading.Condition()

    def __init__(self, name, units, probeId):
        """
        __init__(self, name, units) --> None
        The Mensor 2400 probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        probeId     a string containing the probe Id
        """
        AbstractProbe.__init__(self, name, units)
        self.probeId = probeId.capitalize()

#---------------------------------------------------------------------#

    def getValue(self):
        """
        getValue() --> float
        Return the value measured by the barometer.
        """
        try:
            myMemsor = Config.mensorBarometer.get(self.probeId)
            if myMemsor == None:
                raise ProbeError ("Cannot find Mensor Barometer named "
                                                      +self.probeId)
            value = myMemsor.getPressure()
        except Device.DeviceError, err:
            raise ProbeError (err.strerror)
        self.display(value)
        return value

#---------------------------------------------------------------------#

    def lockProbe(self):
        """
        lockProbe() --> None
        This routine will lock a mutex since several stations share
        the barometer.
        """
#        Mensor2400Probe.myMutex.acquire()
        myMemsor = Config.mensorBarometer.get(self.probeId)
        if myMemsor == None:
            raise ProbeError ("Cannot find Mensor Barometer named "
                                                      +self.probeId)
        myMemsor.lockDevice()
 
#---------------------------------------------------------------------#

    def unlockProbe(self):
        """
        unlockProbe() --> None
        This routine will unlock a mutex since several stations share
        the barometer.
        """
#        Mensor2400Probe.myMutex.release()
        myMemsor = Config.mensorBarometer.get(self.probeId)
        if myMemsor == None:
            raise ProbeError ("Cannot find Mensor Barometer named "
                                                      +self.probeId)
        myMemsor.unlockDevice()

#=====================================================================#

class OmegaDp251Probe(AbstractProbe):
    """
    OmegaDp251Probe is a probe where all measurements are made by the
    Omega DP251 Thermometer.
    """
#    myMutex = threading.Condition()

    def __init__(self, name, units, probeId):
        """
        __init__(self, name, units) --> None
        The Omega DP251 probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        probeId     a string containing the probe Id
        """
        AbstractProbe.__init__(self, name, units)
        self.probeId = probeId.capitalize()

#---------------------------------------------------------------------#

    def getValue(self):
        """
        getValue() --> float
        Return the value measured by the Omega Thermometer.
        """
        try:
            myOmega = Config.omegaThermometer.get(self.probeId)
            if myOmega == None:
                raise ProbeError ("Cannot find Omega Thermometer named "
                                                      +self.probeId)
            value = myOmega.getTemperature()
        except Device.DeviceError, err:
            raise ProbeError (err.strerror)
        self.display(value)
        return value

#---------------------------------------------------------------------#

    def lockProbe(self):
        """
        lockProbe() --> None
        This routine will lock a mutex since several stations share
        the thermometer.
        """
#        OmegaDp251Probe.myMutex.acquire()
        myOmega = Config.omegaThermometer.get(self.probeId)
        if myOmega == None:
            raise ProbeError ("Cannot find Omega Thermometer named "
                                                      +self.probeId)
        myOmega.lockDevice()

#---------------------------------------------------------------------#

    def unlockProbe(self):
        """
        unlockProbe() --> None
        This routine will unlock a mutex since several stations share
        the thermometer.
        """
#        OmegaDp251Probe.myMutex.release()
        myOmega = Config.omegaThermometer.get(self.probeId)
        if myOmega == None:
            raise ProbeError ("Cannot find Omega Thermometer named "
                                                      +self.probeId)
        myOmega.unlockDevice()

#=====================================================================#

class NewportIbthxProbe(AbstractProbe):
    """
    NewportIbthxProbe is a probe where all measurements are made by the
    Newport Ibthx Thermometer/Barometer/Hygrometer.
    """
#    myMutex = threading.Condition()

    def __init__(self, name, units, probeType, probeId):
        """
        __init__(self, name, units, probeType) --> None
        The Newport Ibthx probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        probeType   a string containing the type of data that is to be
                    returned.  (temperature, pressure, Humidity)
        probeId     a string containing the probe Id
        minValue, maxValue
                Minimum and maximum allowed values
        """
        AbstractProbe.__init__(self, name, units)
        self.probeType = probeType.lower()
        self.probeId = probeId.capitalize()

#---------------------------------------------------------------------#

    def getValue(self):
        """
        getValue() --> float
        Return the value measured by the Newport sensor.
        """
        try:
            myIbthx = Config.newportIbthx.get(self.probeId)
            if myIbthx == None:
                raise ProbeError ("Cannot find Newport probe named "
                                                      +self.probeId)
            if self.probeType == "temperature":
                value = myIbthx.getTemperature()
            elif self.probeType == "pressure":
                value = myIbthx.getPressure()
            elif self.probeType == "humidity":
                value = myIbthx.getHumidity()
        except Device.DeviceError, err:
            raise ProbeError (err.strerror)
        self.display(value)
        return value

#---------------------------------------------------------------------#

    def lockProbe(self):
        """
        lockProbe() --> None
        This routine will lock a mutex since several stations share
        the sensor.
        """
#        NewportIbthxProbe.myMutex.acquire()
        myIbthx = Config.newportIbthx.get(self.probeId)
        if myIbthx == None:
            raise ProbeError ("Cannot find Newport probe named "
                                                      +self.probeId)
        myIbthx.lockDevice()

#---------------------------------------------------------------------#

    def unlockProbe(self):
        """
        unlockProbe() --> None
        This routine will unlock a mutex since several stations share
        the sensor.
        """
#        NewportIbthxProbe.myMutex.release()
        myIbthx = Config.newportIbthx.get(self.probeId)
        if myIbthx == None:
            raise ProbeError ("Cannot find Newport probe named "
                                                      +self.probeId)
        myIbthx.unlockDevice()

#=====================================================================#

class NiboxProbe(AbstractProbe):
    """
    RtdProbe is a probe where all measurements are supplied by the
    Rtd Server.
    """
    def __init__(self, name, units, niBoxProbeName):
        """
        __init__(self, name, units, rtdName, token) --> None
        The Rtd probe constructor.
        name    The name of the probe. This value is used when the
                probe value is displayed for debugging
        units   the units that the probe data is measured in.  This
                value is used when the probe value is displayed for
                debugging.
        niBoxProbeName
                Name used by the nibox to store data in the Cache
        minValue, maxValue
                Minimum and maximum allowed values
        """
        print ("NiboxProbe::__init__(%s, %s)" % (name, units))
        AbstractProbe.__init__(self, name, units, niBoxProbeName)
#        self.rtdName = rtdName
#        self.sensorList = []
#        sensorNameList = token.split(',')
#        for sensorName in sensorNameList:
#            self.sensorList.append (sensorName.strip())
#        self.myQueue = Queue.Queue()

#---------------------------------------------------------------------#

    def getValue(self):
        """
        getValue() --> None
        Tne Niboxs push the values into the cache so this routines
        doesn't need to return anything.
        """
        return None
