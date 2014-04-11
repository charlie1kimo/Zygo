#! !/usr/bin/env python
# file: omMeas/rtdServer/probePoller.py

"""
This class implements a poller that every so often reads and stores
the current probe values.
"""

# author: glc

import Config
import DbHandler
import Probes
import SensorCache

#======================================================================#

class ProbePoller:

#----------------------------------------------------------------------#

    def __init__(self, asch):
        self.asch = asch        # asynScheduler

        print ("ProbePoller:__init__(): set freq %f sec" %
                                                Config.getPollFreq_s())
        self.myTimer = asch.createTimer('ProbePoller', self)
        self.myTimer.startTmr(Config.getPollFreq_s(), True)

#----------------------------------------------------------------------#

    def handle_timer(self,tmrName,tmrObj):
#        print "ProbePoller:handle_timer()"
        listOfParams = []
        nowStr = DbHandler.getTimeStr ()
        probes = Config.getProbes()
#        print "  handle_timer(): %s" % probes
        for probe in probes:
            name  = probe.getName ()
            try:
                value = probe.getValue()
                    # is this value from one of the niboxes?
                    #   if yes then ignore
                if value is not None:
                    SensorCache.updateSensor(name, str(value))
                    listOfParams.append ((name, nowStr, value))
            except Probes.ProbeError, err:
                print "   %s: Probe error: %s" % (name, str(err))
                print "      %s" % err.message
                SensorCache.updateSensor(name, str(err), isError=True)

        DbHandler.insertValues (listOfParams)
