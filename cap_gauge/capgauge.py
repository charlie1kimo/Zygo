
import numpy
import os
from ctypes import *

class CapgaugeException(Exception):
    """
    @Purpose:
        Custom Exception for the Capgauge class
    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
    
    def __str__(self):
        return "ERROR: CapgaugeException; expression = %s; %s\n" % (repr(self.expr), self.msg)


class CompositeCapgauge(object):
    ################# class variables ####################
    taskID = 0
    ######################################################
    """
    @Purpose:
        Define a multi-channel capgauge object that performs different National Instrument Capgauge operations.
    """
    def __init__(self, channels, config, name="A Composite Capgauge Sensor"):
        """
        @Purpose:
            Constructor of a CompositeCapgauge object
        @Inputs:
            (list) channels = list of integers of channels that are in this CompositeCapgauge
            (str) config = National Instrument configuration path
        """
        ################ constants ###############
        self.DAQmxConstants = {
            ####### TerminalConfig #############
            'DAQmx_Val_Cfg_Default': -1,                # default terminal config
            'DAQmx_Val_RSE': 10083,                     # referenced single-ended mode
            'DAQmx_Val_NRSE': 10078,                    # non-referenced single-ended mode
            'DAQmx_Val_Diff': 10106,                    # differential mode
            'DAQmx_Val_PseudoDiff': 12529,              # pseudo-differential mode
            ####################################
            ############ Units #################
            'DAQmx_Val_Volts': 10348,                   # units in volts
            'DAQmx_Val_FromCustomScale': 10065,         # units with custom scale
            ####################################
            ### Acquire samples at the clock ###
            'DAQmx_Val_Rising': 10280,                  # at rising
            'DAQmx_Val_Falling': 10171,                 # at falling
            ####################################
            ### Sampling data points options ###
            'DAQmx_Val_FiniteSamps': 10178,             # finite data points sampling
            'DAQmx_Val_ContSamps': 10123,               # continuous sampling
            'DAQmx_Val_HWTimedSinglePoint': 12522,      # continuous sampling using hardware timeout
            ####################################
            ############# Timeouts #############
            'DAQmx_Val_WaitInfinitely': -1,             # infinitely timeout
            ####################################
            ########### Fill mode ##############
            'DAQmx_Val_GroupByChannel': 0,              # grouped by channel (non-interleaved)
            'DAQmx_Val_GroupByScanNumber': 1            # grouped by scan number (interleaved)
            ####################################
        }
        ##########################################
        ############ National Instrument Driver DLL ###############
        self.dll = windll.LoadLibrary("nicaiu.dll")   # NI's DAQmx driver
        ###########################################################

        ################ class instance variables #################
        self.taskName = name
        self.channels = channels
        self.fillMode = 'DAQmx_Val_GroupByScanNumber'       # default to interleaved
        self.parameters = {} 
        self.taskHandle = c_int(self.__class__.taskID)
        self.__class__.taskID += 1
        ##################################################
        self.__parseConfig__(config)
        if self.parameters.has_key('fillMode'):
            self.fillMode = self.parameters['fillMode']

        ##### calling C control library #####
        # creating a DAQmx Task #
        returnValue = self.dll.DAQmxCreateTask(self.taskName, byref(self.taskHandle))
        if returnValue < 0:
            errMsg = self.__getDAQmxError__(returnValue)
            raise CapgaugeException('self.dll.DAQmxCreateTask(self.taskName, byref(self.taskHandle))', \
                "ERROR: calling DAQmx function: %s FAILED. \n Error message: %s" % ('DAQmxCreateTask', errMsg))
        #####################################

        terminalConfig = self.parameters['terminalConfig']
        minVal = c_double(self.parameters['minVal'])
        maxVal = c_double(self.parameters['maxVal'])
        units = self.parameters['units']
        customScaleName = self.parameters['customScaleName']
        physicalChannels = ""
        for c_ind in range(len(channels)):
            physicalChannel = self.parameters['physicalChannel'] + str(channels[c_ind])
            physicalChannels += physicalChannel
            if c_ind < len(channels)-1:
                physicalChannels += ", "

        #physicalChannels = self.parameters['physicalChannel'] + str(0) + ":" + str(len(channels)-1)
        channelName = "%i composite channels" % len(channels)

        ### create channels attach to the task ###
        returnValue = self.dll.DAQmxCreateAIVoltageChan(self.taskHandle, physicalChannels, channelName, terminalConfig, minVal, maxVal, units, customScaleName)
        if returnValue < 0:
            errMsg = self.__getDAQmxError__(returnValue)
            raise CapgaugeException('self.dll.DAQmxCreateAIVoltageChan(self.taskHandle, physicalChannels, channelName, terminalConfig, minVal, maxVal, units, customScaleName)', \
                "ERROR: calling DAQmx function: %s FAILED. \n Error message: %s" % ('DAQmxCreateAIVoltageChan', errMsg))
        ##########################################

    def __del__(self):
        """
        @Purpose:
            destructor
        """
        returnValue = self.dll.DAQmxClearTask(self.taskHandle)

    def __parseConfig__(self, config):
        """
        @Purpose:
            Private function for parsing the configuration file.
        @Inputs:
            (str) config = National Instrument configuration path.
        """
        f = open(config, 'r')
        for line in f:
            line = line.rstrip('\n')
            if len(line) == 0:
                continue
            splitResult = line.split('=')
            key = splitResult[0].lstrip().rstrip()
            value = splitResult[1].lstrip().rstrip()
            if key == 'terminalConfig' or key == 'units':
                self.parameters[key] = self.DAQmxConstants[value]
            elif key == 'samples':
                self.parameters[key] = int(value)
            elif key == 'minVal' or key == 'maxVal':
                self.parameters[key] = float(value)
            elif key == 'customScaleName':
                if value == 'None':
                    self.parameters[key] = None
                else:
                    self.parameters[key] = value
            else:
                self.parameters[key] = value

    def __getDAQmxError__(self, errorCode):
        """
        @Purpose:
            Private function to get the error information from the DAQmx library.
        @Inputs:
            (int) errorCode = error code
        @Outputs:
            (str) errorString
        """
        buffer_size = 256
        string_buffer = create_string_buffer(buffer_size)
        returnValue = self.dll.DAQmxGetErrorString(errorCode, string_buffer, c_uint32(buffer_size))
        if returnValue != 0:
            raise CapgaugeException('returnValue = self.dll.DAQmxGetErrorString(errorCode, string_buffer, c_uint32(buffer_size))', \
                        'ERROR: __getDAQmxError__(errorCode) processing error code FAILED!')
        return string_buffer.value

    def isDataInterleaved(self):
        """
        @Purpose:
            Return is the sampling data is interleaved between channels or not.
        @Outputs:
            True if it's interleaved; False otherwise.
        """
        return self.fillMode == 'DAQmx_Val_GroupByScanNumber'

    def getSampleRates(self):
        """
        @Purpose:
            reads the sample rates of the system.
        @Outputs:
            (float) system sample rates.
        """
        retval = c_double(0)
        returnValue = self.dll.DAQmxGetSampClkRate(self.taskHandle, byref(retval))
        return retval.value

    def samplesData(self, number, rates=0.0):
        """
        @Purpose:
            samples given "number" of data with given sampling rates
        @Inputs:
            (int) number = how many data point to sample
            (float) rates = sampling rate in samples/seconds
        @Outpus:
            (list) sampled data (raw data in units defined)
        """
        timeout = c_double(self.DAQmxConstants['DAQmx_Val_WaitInfinitely'])
        fillMode = self.DAQmxConstants[self.fillMode]
        sampsRead = c_int(0)
        reserved = None

        if rates != 0.0:
            ### Setting up sampling rates in DAQmx ###
            returnValue = self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(rates), \
                self.DAQmxConstants['DAQmx_Val_Rising'], self.DAQmxConstants['DAQmx_Val_FiniteSamps'], c_uint64(number))
            if returnValue < 0:
                errMsg = self.__getDAQmxError__(returnValue)
                raise CapgaugeException("self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(rates), \
                    self.DAQmxConstants['DAQmx_Val_Rising'], self.DAQmxConstants['DAQmx_Val_FiniteSamps'], c_uint64(number))", \
                    "ERROR: calling DAQmx function: %s FAILED. \n Error message: %s" % ('DAQmxCreateAIVoltageChan', errMsg))
            ############################################

        UINT_ARRAY = c_double*(number*len(self.channels))
        sample_value = UINT_ARRAY()
        ### Actually reading the data from DAQmx ###
        returnValue = self.dll.DAQmxReadAnalogF64(self.taskHandle, number, timeout, fillMode, sample_value, number*len(self.channels), byref(sampsRead), reserved)
        if returnValue < 0:
            errMsg = self.__getDAQmxError__(returnValue)
            raise CapgaugeException("self.dll.DAQmxReadAnalogF64(self.taskHandle, number, timeout, fillMode, sample_value, number, byref(sampsRead), reserved)", \
                "ERROR: calling DAQmx function: %s FAILED. \n Error message: %s" % ('DAQmxCreateAIVoltageChan', errMsg))
        ############################################

        if sampsRead.value != number:      # raise exceptions
            raise CapgaugeException("returnValue = self.dll.DAQmxReadAnalogF64(self.taskHandle, number, timeout, fillMode, sample_value, number, byref(sampsRead), reserved)", \
                "ERROR in samplesData: command to sample %d reads but capgauge only returns %d reads!" % (number, sampsRead.value))

        """
        if rates != 0.0:        # reset
            ### Resetting sampling rates through DAQmx ###
            returnValue = self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(0.0), \
                self.DAQmxConstants['DAQmx_Val_Rising'], self.DAQmxConstants['DAQmx_Val_FiniteSamps'], c_uint64(number))
            if returnValue < 0:
                errMsg = self.__getDAQmxError__(returnValue)
                raise CapgaugeException("self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(0.0), \
                    self.DAQmxConstants['DAQmx_Val_Rising'], self.DAQmxConstants['DAQmx_Val_FiniteSamps'], c_uint64(number))", \
                    "ERROR: calling DAQmx function: %s FAILED. \n Error message: %s" % ('DAQmxCreateAIVoltageChan', errMsg))
            ###############################################
        """

        return sample_value

    def readPositions(self, slope=25, piston=0, feedback=-1):
        """
        @Purpose:
            read CompositeCapgauge positions with given voltage to position translation.
            assuming linear correlation between voltage (raw units) and micron (position units):
                position (micron) = slope (micron/V) * voltage (V) + piston (micron)
        @Inputs:
            (float) slope = linear slope (micron/V)
            (float) piston = linear offset (micron)
            (int) feedback = feedback variable to reverse the direction of capgauge reading or not.
        @Outputs:
            (list) positions.
        """
        if self.parameters.has_key('samples'):
            samples = self.parameters['samples']
        else:
            samples = 1000

        if self.parameters.has_key('samplingRate'):
            sampling_rate = self.parameters['samplingRate']
        else:
            sampling_rate = 1000

        rawData = self.samplesData(samples, sampling_rate)
        averaged_data = numpy.zeros(len(self.channels))
        data_in_channel = [[] for i in range(len(self.channels))]
        if self.isDataInterleaved():            # if interleaved
            for i in range(len(rawData)):
                averaged_data[(i%len(self.channels))] += rawData[i]
                data_in_channel[(i%len(self.channels))].append(rawData[i])
            averaged_data /= float(samples)
        else:                                                   # fillMode = grouping mode (non-interleaved)
            for c in range(len(self.channels)):
                averaged_data[c] = sum(rawData[c*samples:(c+1)*samples]) / float(samples)
                data_in_channel[c] = rawData[c*samples:(c+1)*samples]

        if self.parameters.has_key('stdTolerance'):
            std_data = [0 for i in range(len(self.channels))]
            for i in range(len(self.channels)):
                std_data[i] = numpy.std(data_in_channel[i])
                if std_data[i] > self.parameters['stdTolerance']:
                    print "WARNING: channel#%d STD: %0.6f exceeded tolerance setting: %0.6f" % (i, std_data[i], self.parameters['stdTolerance'])

        retVal = (averaged_data * slope + piston) * feedback
        return retVal



class Capgauge(object):
    """ Define a Lion Precision Capacitive Sensor class (Cap_Sensor) using a National Instruments 9205 A/D.
    The NI 9205 A/D is setup for: 1) differential voltage sampling, 2) single A/D sample per read
    
    These classes are built upon the National Instruments dll that implements their universal A/D functionality
    with the DAQmx library.  This dll is functional under Python through the use of "ctypes."  This wraps the
    DAQmx functionality to make the C dll functions callable from Python.
    
    The cap sensors may be used in either the calibrated or uncalibrated (default) mode.  In either case the A/D
    reads the Lion cap gauge voltage a user specified N times, averages those voltage readings,
    and converts that average to position in mm by applying the appropriate coefficients D
    for a second order polynomial fit. Voltage V is converted to displacement D as:
     
                                D = D2*V^2 + D1*V + D0 (in mm)
    
    The reported cap gauge position may be set by the operator by using the class' set_position() method.
    
    A/D configuration parameters and Cap Gauge calibration coefficients are read from config files at Class
    creation time.  Optionally, these parameters may be read in at object instantiation time if the user provides an
    overriding config file.
    
    Capgauge's supported methods (defined with the method below)
    
    __init__()
    read_position()
    use_calibrated_coefficients()
    
    Authored by Dennis Hancock
    Apr-Jul 2012

    UPDATES:
    9-24-2013   cchen:
        update the default Capgauge constructor behavior. Adding default config to look for config file in the same directory
        with the module.
    7-15-2013   cchen:
        read_position now takes 2 additional arguments: slope and piston
        slope is the linear equation slope of voltage to distance
        piston is the linear equation offset of voltage to distance
    """
    
    taskHandle_num = 0
    """ *** DEPRECATED *** POLYNOMIAL FIT
    UNCALIBRATED_D2 = 0.0     # "nominal" uncalibrated coefficients for converting a cap gauge voltage to
    UNCALIBRATED_D1 = -0.100  # position in mm.
    UNCALIBRATED_D0 = 1.250   # position = D2*voltage^2 + D1*voltage + D0
    """
    
    ni_dictionary = {}   #  Parameter definitions dictionary for the setup of the 9205 A/D digitizer card.
    defaultConfig = os.path.dirname(os.path.abspath(__file__)) + "/National Instruments 9205 Config.txt"

    #for line in open("National Instruments 9205 Config.txt"):    # hardwired for M1 test but over-rideable in __init__()
    #    parts = line.split('=')
    #    if len(parts) > 1:    # don't process blank lines
    #        ni_dictionary[parts[0].strip(" ")] = (parts[1].rstrip()).strip(" ")

    cap_sensor_dictionary = {}  #  Calibrated coefficient definitions dictionary for the Lion cap sensors; key is serial number
    
    #for line in open("Lion Cap Sensor Calibration Coefficients Config.txt"):  # hardwired for M1 test but over-rideable in __init__()
    #    parts = line.split(':')
    #    if len(parts) > 1:    # don't process blank lines
    #        cap_sensor_dictionary[parts[0].strip(" ")] = (parts[1].rstrip()).strip(" ")
    #del parts
    #del line

    def __init__(self,ad_channel_number,serial_number=None,name="An UnNamed Lion Capacitive Gauge Sensor",
                 ni_config_file = defaultConfig,cap_sensor_config_file = None,
                 use_Lion_derived_calibration_coefficients = False):
        """
        Define parameters for using NI 9205 in differential mode to obtain a single sample per read.  Also define
        the cap gauge coefficients to convert voltage to position in mm.  
        Inputs:
              ad_channel_number:  NanoPZ actuator channel the cap gauge is attached to. 
              serial_number:  part number of calibrated Lion cap guage.  Used as key into cap_sensor_config_file to
                              obtain second order calibration coefficients
              name:  an optional user provided user name (as a string) to identify the cap gauge
              ni_config_file:  if provided, overrides the "hardwired" file used at Class creation time to provide
                               NI 9205 A/D config parameters
              cap_sensor_config_file:  if provided, overrides the "hardwired" file used at Class creation time
                                       to provide voltage to position calibration coefficients.  The coefficients
                                       are appropriate for a second order polynomial fit and return voltage in
                                       "mm."  The config file keys are the cap gauge serial numbers 
              use_Lion_derived_calibration_coefficients: if TRUE, use the calibration coefficients found in the
                                                         cap_sensor_config_file.  If FALSE use the "generic"
                                                         uncalibrated coefficients UNCALIBRATED_D2,UNCALIBRATED_D1,
                                                         and UNCALIBRATED_D0.
        """
        ############ National Instrument Driver DLL ###############
        self.dll = windll.LoadLibrary("nicaiu.dll")   # NI's DAQmx driver
        ###########################################################
        
        self.taskName = name
        #self.use_Lion_derived_calibration_coefficients = use_Lion_derived_calibration_coefficients

        if ni_config_file:      # Parameter definitions for the setup of the 9205 A/D digitizer card.
            for line in open(ni_config_file):
                parts = line.split('=')
                if len(parts) > 1:    # don't process blank lines
                    Capgauge.ni_dictionary[parts[0].strip(" ")] = (parts[1].rstrip()).strip(" ")
               
        #if cap_sensor_config_file:    # Parameter definitions for the setup of the 9205 A/D digitizer card.
        #    for line in open(cap_sensor_config_file):
        #        parts = line.split(':')
        #        if len(parts) > 1:    # don't process blank lines
        #            Capgauge.cap_sensor_dictionary[parts[0].strip(" ")] = (parts[1].rstrip()).strip(" ")

        self.terminalConfig = int(Capgauge.ni_dictionary['terminalConfig'])   # DAQmx_AI_TermCfg constant (10106)from NIDAQmx.h for differential input channel read
#        self.terminalConfig = 10083                                            # DAQmx_AI_TermCfg constant from NIDAQmx.h for single-ended input channel read
        self.minVal = c_double(float(Capgauge.ni_dictionary['minVal']))     # suitable extremum values for NI 9205 A/D; min=-10.0v, max = +10.0v
        self.maxVal = c_double(float(Capgauge.ni_dictionary['maxVal'])) 
        self.units = int(Capgauge.ni_dictionary['units'])   # DAQmx_Val_Volts constant (10348)from NIDAQmx.h to measure volts
        if Capgauge.ni_dictionary['customScaleName'].lower() == 'none':
            self.customScaleName = None
        else:
            self.customScaleName = Capgauge.ni_dictionary['customScaleName']
        
#       Create an NI task using the configuration parameters defined in the __init__ function
        self.ad_channel_number = ad_channel_number
        self.taskHandle = c_int(Capgauge.taskHandle_num)
        Capgauge.taskHandle_num += 1
#        self.physicalChannel = "cDAQ9181-16FC143Mod1/ai" + str(self.ad_channel_number)
        self.physicalChannel = Capgauge.ni_dictionary['physicalChannel'] + str(self.ad_channel_number)
        self.channelName = "ai" + str(self.ad_channel_number)
        returnValue = self.dll.DAQmxCreateTask(self.taskName, byref(self.taskHandle))
        returnValue = self.dll.DAQmxCreateAIVoltageChan(self.taskHandle, self.physicalChannel, self.channelName, self.terminalConfig, self.minVal, self.maxVal, self.units, self.customScaleName)
        
#        Define the parameters for the 9205 to obtain 1 sample which is read in a group.

        self.timeout = c_double(-1)    # -1 to wait infinitely for the sample to be read
        if Capgauge.ni_dictionary.has_key('samples'):
            self.samples = int(Capgauge.ni_dictionary['samples'])    # number of samples to read with DAQmxReadAnalogF64 function
        else:
            self.samples = 4000          # number of samples to read with DAQmxReadAnalogF64 function
        self.sampsRead = c_int(0)      # actual number of samples read by call to DAQmxReadAnalogF64 function
        self.fillMode = 0              # Read the samples grouped in channels( not grouped by scan);DAQmx_Val_GroupByChannel
        self.UINT_ARRAY_30 = c_double*(self.samples)
        self.sample_value = self.UINT_ARRAY_30()  # returned sampled value from A/D channel
        self.reserved = None
        
        self.serial_number = serial_number
        #self.use_calibrated_coefficients(use_Lion_derived_calibration_coefficients)
        """
        if (bool(self.serial_number) & self.use_Lion_derived_calibration_coefficients):
            parts = Capgauge.cap_sensor_dictionary[self.serial_number].split(' ')
            self.d2 = float(parts[0])  # voltage^2 calibration coefficient
            self.d1 = float(parts[1])  # voltage^1 calibration coefficient
            self.d0 = float(parts[2])  # voltage^0 calibration coefficient
        elif (bool(self.serial_number) & ~self.use_Lion_derived_calibration_coefficients):


        # *** DEPRECATED ***
        self.d2 = self.UNCALIBRATED_D2
        self.d1 = self.UNCALIBRATED_D1
        self.d0 = self.UNCALIBRATED_D0

        else:
            self.d2 = 0.0
            self.d1 = 0.0
            self.d0 = 0.0
        """
        self.position = None   # used to store instance's last reading in mm

    def __del__(self):
        returnValue = self.dll.DAQmxClearTask(self.taskHandle)

    def get_sample_rates(self):
        """
        @Purpose:
            reads the sample rates of the system.
        @Outputs:
            (float) system sample rates.
        """
        retval = c_double(0)
        returnValue = self.dll.DAQmxGetSampClkRate(self.taskHandle, byref(retval))
        return retval.value

    def samples_data(self, number, rates=0.0):
        """
        @Purpose:
            samples the raw voltage reading from the capgauge.
        @Inputs:
            (int) number = number of samples to read
            (float) rates = sampling rates in samples/seconds (default = 0.0; unlimited)
        @Outpus:
            (list) list of voltages sampled.
        """
        if rates != 0.0:
            DAQmx_Val_Rising = 10280
            DAQmx_Val_FiniteSamps = 10178
            returnValue = self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(rates), DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, c_uint64(number))
        UINT_ARRAY = c_double*number
        sample_value = UINT_ARRAY()
        returnValue = self.dll.DAQmxReadAnalogF64(self.taskHandle, number, self.timeout, self.fillMode, sample_value, number, byref(self.sampsRead), self.reserved)
        if self.sampsRead.value != number:      # raise warnings
            print "WARNING: command to sample %d reads but capgauge only returns %d reads!" % (number, self.sampsRead.value)

        if rates != 0.0:        # reset
            returnValue = self.dll.DAQmxCfgSampClkTiming(self.taskHandle, None, c_double(0.0), DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, c_uint64(number))

        return sample_value
        
    def read_position(self, slope, piston):
        """ 
        Obtain (self.samples) sample voltage(s) from the 9205 and average, convert to position in "mm. Return position value.
        The returned position is offset by self.position_offset which is set in instance's
        set_position() method to effectuate manual override of reported cap sensor displacement.
        
        Output:
           Return the displacement of the cap sensor in mm.  The coefficients have already been
           appropriately selected for either 'calibrated read' or 'uncalibrated read.

        UPDATE:
        now read_position take 2 arguments:
        slope = linear slope of voltage to distance linear equation (mm / V)
        piston = linear offset of voltage to distance linear equation (mm)
        *** d = slope * voltage + piston ***
        """
        voltage = 0.0
        
        returnValue = self.dll.DAQmxReadAnalogF64(self.taskHandle, self.samples, self.timeout, self.fillMode,self.sample_value, self.samples, byref(self.sampsRead), self.reserved)
        if self.sampsRead.value == 0:           # reading 0 samples, something's wrong
            raise CapgaugeException('returnValue = self.dll.DAQmxReadAnalogF64(self.taskHandle, self.samples, self.timeout, self.fillMode,self.sample_value, self.samples, byref(self.sampsRead), self.reserved)',
                                "ERROR: Error in reading National Instrument Device.\n Check the National Instrument config settings?")

        voltage = sum(self.sample_value) / float(self.sampsRead.value)
        #print voltage, returnValue  
        
        # DEPRECATED POLYNOMIAL FIT
        #self.position = self.d2*voltage*voltage + self.d1*voltage + self.d0 # in mm
        self.position = slope * voltage + piston
        return self.position
    
    def use_calibrated_coefficients(self,proposition = False):
        """
        Lion cap gauges may be operated as calibrated sensors or uncalibrated
        sensors.  This method is used to set this state variables,
        self.use_lion_derived_calibration_coefficients.
        
        If a cap gauge is present (self.serial_number is TRUE), the
        the calibrated coefficients will be applied to converting all voltage
        readings to position if self.use_Lion_derived_calibration_coefficients is
        TRUE.  If this latter variable is FALSE, then use the "generic"
        UNCALIBRATED coefficients.

        *** DEPRECATED ***
        """
        self.use_Lion_derived_calibration_coefficients = proposition
        if (bool(self.serial_number) & proposition):
            parts = Capgauge.cap_sensor_dictionary[self.serial_number].split(' ')
            self.d2 = float(parts[0])  # voltage^2 calibration coefficient
            self.d1 = float(parts[1])  # voltage^1 calibration coefficient
            self.d0 = float(parts[2])  # voltage^0 calibration coefficient
        elif (bool(self.serial_number) & ~proposition):
            self.d2 = self.UNCALIBRATED_D2
            self.d1 = self.UNCALIBRATED_D1
            self.d0 = self.UNCALIBRATED_D0
        else:
            self.d2 = 0.0
            self.d1 = 0.0
            self.d0 = 0.0
       