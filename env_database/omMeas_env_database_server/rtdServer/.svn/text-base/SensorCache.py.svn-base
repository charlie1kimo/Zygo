#! !/usr/bin/env python
# file: omMeas/rtdServer/SensorCache.py

"""
.
"""


# original author: kw
# rewrite author: glc

#=====================================================================#

import time

    # sensorTbl is a map, indexed by canonical sensor name
    # the value is a tuple:
    #   [0] last reading of sensor
    #   [1] time sensor was last updated
    #   [2] calSerial value or None
    #   [3] is error
sensorTbl = {}

#=====================================================================#

def canonName(name):
    # TBD, convert lower-case
    return(name.lower())

def updateSensor(name, reading, rdTime=None, calSerial=None,
                                                    isError=False):
#    print ("*** SensorCache.updateSensor(%s, %s, %s, %s, %s)" %
#                        (name, reading, rdTime, calSerial, isError))
    if rdTime is None:
        rdTime = time.time()
    sensorTbl [canonName(name)] = (reading, rdTime, calSerial, isError)
#    print "    %s" % str(sensorTbl)

def findSensor(name):
#    print ("*** SensorCache.findSensor(%s)" % name)
    return sensorTbl.get (canonName(name))

def clearCache():
#    print ("*** SensorCache.clearCache()")
    sensorTbl.clear()
#    print ("    %s" % str(sensorTbl))

def getKeys():
#    print ("*** SensorCache.getKeys()")
#    print ("    %s" % str(sensorTbl))
    return sensorTbl.keys()
