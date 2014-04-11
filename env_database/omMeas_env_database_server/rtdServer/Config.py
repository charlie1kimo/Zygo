#! !/usr/bin/env python
# file: omMeas\rtdServer\Config.py

"""
This GUI implements the Config processing of the server.

The Config module reads the config file(s) [just the file defined on
the command line for now] and initilizes the various probes and
stations.
"""

# author: glc

#=====================================================================#

import ConfigParser
import logging
import Probes
import Station
import omMeas.wexLib.Device as Device

#=====================================================================#

port = 6217         # what port do we listen to for connections
pollFreq_s = 60
niBoxInfo = dict()  # list of avilable niBox information
rtdProbeInfo = dict()  #
thermometer = None
stations = dict()

humidityProbes = dict()
pressureProbes = dict()
temperatureProbes = dict()

mensorBarometer = dict()
newportIbthx = dict()
omegaThermometer = dict()

#=====================================================================#

TRACE = __name__ == "__main__"
#TRACE = True

#=====================================================================#

def trace(s):
    if TRACE:
        print s

#=====================================================================#

class ConfigError(AttributeError):
    """
    This exception class is used when the Config class need to throw
    an exception (i.e. bad config file).
    """
    def __init__(self, why = None):
        if why == None:
            why = "Config error"
        AttributeError.__init__(self, why)

#=====================================================================#

def logConfigError(msg):
    trace ("logConfigError(%s)" % msg)
    logging.error (msg)
    raise ConfigError(msg)

#=====================================================================#

def readFile (filename):
    global port, pollFreq_s, niBoxInfo, probeInfo, thermometer
    global mensorBarometer, newportIbthx, omegaThermometer

    trace ("readFile()")
    config = ConfigParser.RawConfigParser()
    try:
        filesRead = config.read (filename)
    except ConfigParser.ParsingError, msg:
        logConfigError ("Unable to process config file: %s " %
                                                        msg.message)
    if not filesRead:
        logConfigError ("Unable to read " +filename)
    else:
        print "Read " +filename
        for section in config.sections():
            print "  Section:", section.capitalize()
            if section.capitalize() == "Server":
                for option in config.options(section):
                    if option.lower() == "port":
                        try:
                            port = config.getint(section, option)
                        except ValueError:
                            s = config.get(section, option)
                            print ("Bad port value: %s" % s)
                            logConfigError("Bad port value: %s" % s)
                    elif option.lower() == "pollfreq":
                        try:
                            pollFreq_s = config.getint(section, option)
                        except ValueError:
                            s = config.get(section, option)
                            print ("Bad port value: %s" % s)
                            logConfigError("Bad pollFreq value: %s"% s)
                    elif option.capitalize() == "thermometer":
                        thermometer = config.get(section, option)
            elif section.capitalize().startswith("Nibox"):
                niBoxName = niBoxAddress = niBoxPort = None
                niBoxMasterDir = niBoxMasterFile = None
                niBoxBackupFile = None
                niBoxTargetDir = niBoxTargetFile = None
                for option in config.options(section):
                    if option.lower() == "name":
                        niBoxName = config.get(section, option).lower()
                    elif option.lower() == "address":
                        niBoxAddress = config.get(section, option)
                    elif option.lower() == "port":
                        try:
                            niBoxPort = config.getint(section, option)
                        except ValueError:
                            s = config.get(section, option)
                            print ("Bad niBox port value: %s" % s)
                            logConfigError("Bad niBox port value: %s"
                                                                % s)
                    elif option.lower() == "masterdir":
                        niBoxMasterDir = config.get(section, option)
                    elif option.lower() == "masterfile":
                        niBoxMasterFile= config.get(section, option)
                    elif option.lower() == "backupfile":
                        niBoxBackupFile= config.get(section, option)
                    elif option.lower() == "targetdir":
                        niBoxTargetDir = config.get(section, option)
                    elif option.lower() == "targetfile":
                        niBoxTargetFile= config.get(section, option)
                if niBoxName != None:
                    niBoxInfo [niBoxName] = (niBoxAddress, niBoxPort,
                                    niBoxMasterDir, niBoxMasterFile,
                                    niBoxBackupFile, niBoxTargetDir,
                                    niBoxTargetFile)
                else:
                    print ("missing name entry for %s" % section)
            elif section.capitalize() in ["Probes", "Wires"]:
                for option in config.options(section):
                    rtdProbeInfo [option.lower()] = config.get(section,
                                                                option)
#            elif section.capitalize() == "Thermometer":
#                for option in config.options(section):
#                    if option.capitalize() == "Omegadp251":
#                        import omMeas.wexLib.OmegaDp251Thermometer as Omega
#                        thermometer = Omega.OmegaDp251Thermometer(
#                                        config.get(section, option))
            elif section.capitalize().startswith ("Mensor2400"):
                import omMeas.wexLib.Mensor2400Barometer as Mensor
                address = config.get (section, "address")
                mensorBarometer[section.capitalize()]=Mensor.Mensor2400Barometer(address)
            elif section.capitalize().startswith ("Omegadp251"):
                import omMeas.wexLib.OmegaDp251Thermometer as Omega
                address = config.get (section, "address")
                omegaThermometer[section.capitalize()]=Omega.OmegaDp251Thermometer(address)
            elif section.capitalize().startswith ("Newportibthx"):
                import omMeas.wexLib.NewportIbthx as Newport
                address = config.get (section, "address")
                newportIbthx[section.capitalize()]=Newport.NewportIbthx(address)
            elif section.capitalize() in ("Pressure", "Humidity",
                                                "Temperature"):
                pass
            elif section.capitalize().startswith("Station"):
                pass
        createProbes(config)
        createStations(config)
        if thermometer != None:
            thermometer = temperatureProbes [thermometer.lower ()]

#=====================================================================#

def createProbes (config):
    """
    createProbes(config) ==> None

    For each type of probe createProbes() will create a list of
    probes. These lists are then used by createStations() to
    create and initilize the work stations.
    """
    trace(createProbes)
    global pressureProbes, temperatureProbes, humidityProbes

    for section in config.sections():
        if config.has_option (section, "range"):
            tokens = config.get (section, "range").strip().split(',')
            try:
                minValue = float (tokens[0])
            except (TypeError, ValueError, IndexError):
                minValue = None
            try:
                maxValue = float (tokens[1])
            except (TypeError, ValueError, IndexError):
                maxValue = None
        else:
            minValue = maxValue = None
            
        if section.capitalize() == "Pressure":
            for option in config.options (section):
                if option.lower() != "range":
                    pressureProbes[option.lower()]=createProbe(config,
                                            section, option, "mmHg")
        elif section.capitalize() == "Humidity":
            for option in config.options (section):
                if option.lower() != "range":
                    humidityProbes[option.lower()]=createProbe(config,
                                                section, option, "%")
        elif section.capitalize() == "Temperature":
            for option in config.options (section):
                if option.lower() != "range":
                    temperatureProbes[option.lower()]=createProbe(config,
                                                section, option, "C")

#=====================================================================#

def createProbe (config, section, option, units):
    """
    createProbe(config, section, option, units, minValue, maxValue)
                                                            ==> a probe

    Creates a probe based on the config file info based in section
    and option.  It assignes the name "<section>.<option>" and the
    units <units>.

    section is the type of probe. e.g. Pressure
    option is the identifier used by the station section
    units is the units that the data is measued in. e.g. mmHg
    """
    trace ("createProbe(%s, %s, %s)" % (section, option,units))
    configStr = config.get (section, option)
    tokens = configStr.split (None, 1)
    if ("Temperature" == section.capitalize()):
        name = "T." +option
    elif ("Pressure" == section.capitalize()):
        name = "P." +option
    elif ("Humidity" == section.capitalize()):
        name = "H." +option
    else:
        name = section +'.' +option     # should never happen
    if tokens [0].capitalize() == "Default":
        return Probes.DefaultProbe(name, units, tokens [1])
    elif tokens [0].capitalize().startswith ("Mensor2400"):
        if not mensorBarometer.has_key (tokens [0].capitalize()):
            logConfigError("Cannot have a Mensor 2400 probe without a "
                                        "Mensor 2400 Config section")
        return Probes.Mensor2400Probe (name, units, tokens [0])
    elif tokens [0].capitalize().startswith ("Omegadp251"):
        if not omegaThermometer.has_key (tokens [0].capitalize()):
            logConfigError("Cannot have an Omega Dp251 probe without "
                                       "an Omega Dp251 Config section")
        return Probes.OmegaDp251Probe (name, units, tokens [0])
    elif tokens [0].capitalize().startswith ("Newportibthx"):
        if not newportIbthx.has_key (tokens [0].capitalize()):
            logConfigError("Cannot have a Newport iBTHX probe without "
                                    "a Newport iBTHX Config section")
        return Probes.NewportIbthxProbe (name, units, section,
                                                            tokens [0])
    elif tokens [0].capitalize() == "Nibox":
        niBoxProbeName = getRtdProbeInfo().get(option.lower())
        if niBoxProbeName == None:
            niBoxProbeName = option
        return Probes.NiboxProbe(name, units, "T." +niBoxProbeName)
    else:
        logConfigError ("%s.%s unknown probe type (%s) in "
                "Config.createProbe()" % (section, option, tokens [0]))
    assert 0, "This statement should not be reached!"

#=====================================================================#

def getProbeList(probeNames, probeMap):
    """
    getProbeList(probeNames, probeMap) --> list of probes

    probeName   a comma delimited string of probe names
    probeMap    one of the global probe dictionary

    getProbeList() will parse the list probe names and locate the
    requested probe in the dictionary.  It will then add the probe to
    the probeList; returning the probe list when it is finished.
    """
    trace ("getProbeList(%s)" %probeNames)
    probeList = []
    probeNameList = probeNames.split(',')
    for probeName in probeNameList:
        probe = probeMap.get(probeName.strip().lower())
        if probe:
            probeList.append (probe)
        else:
            print "Unable to find %s in %s" %(probeName,str(probeMap))
    return probeList

#=====================================================================#

def createStations (config):
    """
    createStations(config) ==> None

    For each station defined in the config file createStations()
    will create a station object and populate it with the correct
    list of probes.  It will then add the new station to the
    dictionary of stations.
    """
    trace ("createStations()")
    for section in config.sections():
        if section.capitalize().startswith("Station"):
            myPressureProbes = myHumidityProbes = []
            myTemperatureProbes= []
            name = section.capitalize()
            for option in config.options (section):
                value = config.get (section, option)
                opt = option.capitalize()
                if opt == "Name":
                    name = value.capitalize()
                elif opt == "Temperature":
                    myTemperatureProbes = getProbeList (value,
                                            temperatureProbes)
                elif opt == "Pressure":
                    myPressureProbes = getProbeList (value,
                                            pressureProbes)
                elif opt == "Humidity":
                    myHumidityProbes = getProbeList (value,
                                            humidityProbes)
            stations [name] = Station.Station(myTemperatureProbes,
                            myPressureProbes, myHumidityProbes, name)

#=====================================================================#

def getPort():
    return port

def getPollFreq_s():
    return pollFreq_s

def getThermometer():
    return thermometer

def getNiBoxInfo():
    return niBoxInfo

def getRtdProbeInfo():
    return rtdProbeInfo

def getStations():
    return stations

def getProbes():
    allProbes = (temperatureProbes.values() +pressureProbes.values()
                                            +humidityProbes.values())
##    print "Config.getProbes(): %s"% str (allProbes)
##    print "  temperatureProbes: %s" % str (temperatureProbes)
##    print "  pressureProbes   : %s" % str (pressureProbes)
##    print "  humidityProbes   : %s" % str (humidityProbes)
    return allProbes
#    return temperatureProbes +pressureProbes +humidityProbes

#=====================================================================#

if __name__ == "__main__":
    readFile("rtdConfig.ini")
    print ("\ngetPort:         %s" % str(getPort()))
    print ("\ngetPollFreq_s:   %s" % str(getPollFreq_s()))
    print ("\ngetThermometer:  %s" % str(getThermometer()))
    print ("\ngetNiBoxInfo:    %s" % str(getNiBoxInfo()))
    print ("\ngetRtdProbeInfo: %s" % str(getRtdProbeInfo()))
    print ("\ngetStations:     %s" % str(getStations()))
    print ("\ngetProbes:")
    for probe in getProbes():
        print ("  Probe name, cache name: %s, %s" % (probe.getName(),
                                                probe.getCacheName()))
