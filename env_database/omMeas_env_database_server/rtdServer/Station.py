#! !/usr/bin/env python
# file: omMeas/rtdServer/Station.py

"""
This file handles the data structures that repersent a station.
"""

# author: glc

#=====================================================================#

#import Probes
import SensorCache
import time

#=====================================================================#

class Station:
    """
    The class Station contains information regarding a test station.
    """
    def __init__ (self, temperatureProbes = dict(),
            pressureProbes=dict(), humidityProbes=dict(), name=None):
        self.pressureProbes        = pressureProbes
        self.temperatureProbes     = temperatureProbes
        self.humidityProbes        = humidityProbes
        self.name                  = name

    def averageProbes(probeList):
        """
        averageProbes(probeList) -> float or None
        returns the average the list of probes passed in.  This routine
        is not intended to be called outside the Station class
        """
        ret = None
        if len(probeList):
            val = 0.0
            count = 0
            for probe in probeList:
                probeTuple = SensorCache.findSensor(probe.getCacheName())
                if probeTuple is not None and not probeTuple [3]:
                    try:
                        val += float(probeTuple [0])
                        count += 1
                    except ValueError, err:
                        print ("Value Error on float() call in Station::averageProbes")
                        print ("Probe name: %s" % probe.getName())
                        print ("Probe list: %s" % str(probeList))
                        print ("Sensor Cache: %s" % str(SensorCache.sensorTbl))
                        print (err)
                        raise err
                else:
                    print ("Bad probe tuple for probe %s: %s" %
                                                (probe.getName(), probeTuple))
            if count > 0:
                ret =  val/float(count)
            else:
                print ("no valid values in Station's probe list")
        else:
            print ("station::Probe list is empty")
        return ret
    averageProbes = staticmethod (averageProbes)

    def getMaxAge(self):
        """
        getMaxAge() -->float or None
        returns the maximum age of all the probes
        """
        maxAge = 0
        for probe in (self.temperatureProbes +self.pressureProbes
                            +self.humidityProbes):
            probeTuple = SensorCache.findSensor(probe.getCacheName())
            if probeTuple is not None and not probeTuple [3]:
                age = time.time() -probeTuple[1]
                if age > maxAge:
                    maxAge = age
        return float(maxAge)

    def getPressure(self):
        """
        getPressure() -->float or None
        returns the average of the pressure probes
        """
        print ("*** Station.getPressure()")
        return self.averageProbes(self.pressureProbes)

    def getHumidity(self):
        """
        getHumidity() -> float or None
        returns the average of the humidity probes
        """
        print ("*** Station.getHumidity()")
        return self.averageProbes(self.humidityProbes)

    def getTemperature(self):
        """
        getTemperature() ->float or None
        returns the average of the temperature probes
        """
        print ("*** Station.getTemperature()")
        return self.averageProbes(self.temperatureProbes)

    def getName(self):
        """
        getName() ->string or None
        returns the name of the station
        """
        return self.name
