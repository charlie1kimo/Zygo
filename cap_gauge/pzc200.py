import os
import socket
import pickle
import time
import numpy as np
import math

#########################################################################################

class Pzc200(object):
    """ 
    Class definition for a Newport PZC200 controller which exercises up to 8 PZA12 actuators. 
    All class methods are defined on page 38 of Newport's NanoPZ User's Manual which defines
    commands for movement, get status, select switchbox channel, etc.  The methods we use most 
    often have their own docsting as seen below. 
    
    Additionally this class establishes a socket connection using standard TCP/IP.
    
    Inputs:
    IP Address of assigned NewportUS Microserver Ethernet to RS-232/RS-485 converter
    Port of assigned NewportUS Microserver
    Controller_Address: Pre-loaded controller address of PZC200 ranging from 1 to 255
    Name: text string given for preferred choice of controller's name
    
    Outputs: class PZC200 returns an instance of a Newport PZC200 class
    
    Authored by Dennis Hancock
    Apr-Jul 2012
    """
    MAX_NB_SOCKETS = 32 # maximum number of controllers/sockets a PZC200 controller can accomodate
    sockets = {}     # socket structure on each open socket
    nbSockets = 0    # counts number of open sockets and stores in class variable
    
    # Initialization Function
    def __init__ (self,ip_address,port,name="Pzc200 Socket Connection",timeout=5):
        """
        Instantiates a Pzc200 controller class.
        
        Inputs:
        
           ip_address of NewportUS (not Newport Inc) i.Server MicroServer
           port: port number of NewportUS i.Server MicroServer
           name: user provided description of controller as a string
           timeout:  time in milliseconds before Ethernet channel times out on send/receive
        """
        self.ip_address = ip_address
        self.port = port
        self.controller_name = name
        self.timeout = timeout
        self.TCP_ConnectToServer()
        self.TCP_SetTimeout()
        
    # ScanSwitchboxSet:  
    def ScanSwitchboxSet(self,pzc200_controller_address):
        """
        For a Pzc200 controller with address pzc200_controller_address, scan all 8 channels and see
        which ones have attached NanoPZ12 actuators.
        """
        command = str(pzc200_controller_address) + 'BX'
        returnString = self.SendOnly(command)
        time.sleep(2.750)
        return returnString
        
    # ScanSwitchboxGet:  
    def ScanSwitchboxGet(self,pzc200_controller_address):
        """
        For a Pzc200 controller with address pzc200_controller_address, read which channels
        have attached NanoPZ12 actuator
        """
        command = str(pzc200_controller_address) + 'BX' + '?'
        returnString = self.SendAndReceive(command)
        time.sleep(0.100)
        return returnString

    # RestoreSettingsToEEPROM:
    def RestoreSettingsToEEPROM(self,pzc200_controller_address):
        """
        Re-store controller address, switchbox settings, etc to internal EEPROM of Pzc200 controller
        """
        command = str(pzc200_controller_address) + 'BZ'
        returnString = self.SendOnly(command)
        time.sleep(2.750)
        return returnString

    # SelectSwitchboxChannelSet:
    def SelectSwitchboxChannelSet(self,pzc200_controller_address,switchbox_channel):
        """
        Select which one of channels 1 thru 8 to actuate as designed by switchbox_channel.
        This actuator is assigned to Pzc200 controller with address pzc200_controller_address
        """
        command = str(pzc200_controller_address) + 'MX' + str(switchbox_channel)
        returnString = self.SendOnly(command)
        time.sleep(0.300)
        return returnString

    # SelectSwitchboxChannelGet:
    def SelectSwitchboxChannelGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'MX' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # ZeroPositionSet:
    def ZeroPositionSet(self,pzc200_controller_address):
        """
        This function doesn't seem to work
        """
        command = str(pzc200_controller_address) + 'OR'
        returnString = self.SendOnly(command)
        return returnString

    # HardwareStatusGet:
    def HardwareStatusGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'PH' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # ControllerReset:
    def ControllerReset(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'RS'
        returnString = self.SendOnly(command)
        time.sleep(0.100)
        return returnString

    # ControllerAddressSet:
    def ControllerAddressSet(self, pzc200_controller_address,value):
        command = str(pzc200_controller_address) + 'SA' + str(value)
        returnString = self.SendOnly(command)
        time.sleep(0.100)
        return returnString

    # SaveSettingsToEEPROM:
    def SaveSettingsToEEPROM(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'SM'
        returnString =  self.SendOnly(command)
        time.sleep(2.750)
        return returnString

    # ReadErrorCode:
    def ReadErrorCode(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'TE' + '?'
        returnString = self.SendAndReceive(command)
        return returnString
 
    # ControllerStatusGet:
    def ControllerStatusGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'TS' + '?'
        returnString = self.SendAndReceive(command)
        try:
            return returnString[0]
        except TypeError:
            print 'Position Move Error'
            return "Q"

    # ControllerFirmwareGet
    def ControllerFirmwareGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'VE' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # ActuatorDescriptionSet:
    def ActuatorDescriptionSet(self, pzc200_controller_address, actuator_name):
        command = str(pzc200_controller_address) + 'ID' + actuator_name
        returnString = self.SendOnly(command)
        return returnString

    # ActuatorDescriptionGet:
    def ActuatorDescriptionGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'ID' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # StartJogMotionSet:
    def StartJogMotionSet(self,pzc200_controller_address, value):
        command = str(pzc200_controller_address) + 'JA' + str(value)
        returnString = self.SendOnly(command)
        return returnString

    # StartJogMotionGet:
    def StartJogMotionGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'JA' + '?'
        returnString = self.SendAndReceive(command)
        return returnString
 
    # MotorOn:
    def MotorOn(self,pzc200_controller_address):
        """
        Turns on power to motor selected by SelectSwitchboxChannelSet command and currently
        selected Pzc200 controller (controller_address)
        """
        command = str(pzc200_controller_address) + 'MO'
        returnString = self.SendOnly(command)
        time.sleep(0.275)
        return returnString

    # MotorOff:
    def MotorOff(self,pzc200_controller_address):
        """
        Turns off motor selected by SelectSwitchboxChannelSet command and currently
        selected Pzc200 controller (controller_address)
        """
        command = str(pzc200_controller_address) + 'MF'
        returnString = self.SendOnly(command)
        time.sleep(0.275)
        return returnString

    # PositionRelativeSet:
    def PositionRelativeSet(self, pzc200_controller_address,num_of_steps):
        """
        Moves PZA12 actuator relative to current position by num_of_steps of step increments.
        This actuator is associated with Pzc200 controller with address pzc200_controller_address
        """
        command = str(pzc200_controller_address) + 'PR' + str(num_of_steps)
        returnString = self.SendOnly(command)
        time.sleep(0.12)
        while(1):
            returnString = self.ControllerStatusGet(pzc200_controller_address)
            if returnString == "Q":break

        return returnString
  
    # LeftLimitSet:
    def LeftLimitSet(self,pzc200_controller_address,left_limit):
        command = str(pzc200_controller_address) + 'SL' + str(left_limit)
        returnString = self.SendOnly(command)
        return returnString

    # LeftLimitGet:
    def LeftLimitGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'SL' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # RightLimitSet:
    def RightLimitSet(self,pzc200_controller_address,right_limit):
        command = str(pzc200_controller_address) + 'SR' + str(right_limit)
        returnString = self.SendOnly(command)
        return returnString  

    # RightLimitGet:
    def RightLimitGet(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'SR' + '?'
        returnString = self.SendAndReceive(command)
        return returnString  

    # StopMotion:
    def StopMotion(self,pzc200_controller_address):
        command = sstr(pzc200_controller_address) + 'ST'
        returnString = self.SendOnly(command)

    # ReadErrorCode:
    def ReadErrorCode(self,pzc200_controller_address):
        command = str(pzc200_controller_address) + 'TE' + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    # ReadCurrentPosition:
    def ReadCurrentPosition(self,pzc200_controller_address, switchbox_channel):
        command = str(pzc200_controller_address) + 'TP' + str(switchbox_channel) + '?'
        returnString = self.SendAndReceive(command)
        return returnString

    #SendOnly(self)
    def SendOnly(self,command):
        """
        Only send ASCII encoded Pzc200 command to controller.
        """
        if(self.socketId == -1):
            return -1
        
        try:
            self.sockets[self.socketId].send(command + chr(13) + chr(10))  
        except socket.error:
            print 'Recieving Socket Connection Errors, Retry.' #self.sockets
            self.sockets[self.socketId].close()
            del self.sockets[self.socketId]
            Pzc200.nbSockets -= 1
            self.TCP_ConnectToServer()
            self.sockets[self.socketId].send(command + chr(13) + chr(10)) 
            #print self.nbSockets, self.sockets        
        
        return'999'

    # Send command and get return; override Channel method
    def SendAndReceive (self,command):
        """
        Send ASCII encoded Pzc200 command to controller and read controller's response
        """
        if(self.socketId == -1):
            return -1
        
        try:
            self.sockets[self.socketId].send(command + chr(13) + chr(10))
            ret = self.sockets[self.socketId].recv(16)
        except socket.timeout:
            #raw_input('Socket timeout.\nPress Enter to continue.')
            return -2
        except socket.error (errNb, errString):
            print 'Socket error : ' + errString
            return -2

        i = ret.find(' ')
        j = ret.find(chr(13) + chr(10))
        return ret[i+1:j]


    # TCP_ConnectToServer
#    def TCP_ConnectToServer (self, self.IP_address, self.port, self.timeOut):
    def TCP_ConnectToServer (self):
        """
        Establish a socket connection to the NewportUS i.MicroServer RS-232/RS-485 converter
        """
        if (Pzc200.nbSockets >= self.MAX_NB_SOCKETS):
            return -1
        socketId = Pzc200.nbSockets
        self.socketId = socketId
        Pzc200.nbSockets += 1
        
        try:
            Pzc200.sockets[socketId] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Pzc200.sockets[socketId].connect((self.ip_address, self.port))
            Pzc200.sockets[socketId].settimeout(self.timeout)
            Pzc200.sockets[socketId].setblocking(1)
        except socket.error:
            return -1
        
    # TCP_SetTimeout
    def TCP_SetTimeout (self):
        if (self.socketId > -1):
            Pzc200.sockets[self.socketId].settimeout(self.timeout)

    # TCP_CloseSocket
    def TCP_CloseSocket (self):
        if (self.socketId >= 0 and self.socketId < self.MAX_NB_SOCKETS):
            try:
                Pzc200.sockets[self.socketId].close()
                Pzc200.nbSockets -= 1
                Pzc200.socketId = -1
            except socket.error:
                pass
    # reeset Pzc200 controllers from XPS GPIO command for function reset
    def Power_reset(self):
        pass
#########################################################################################

class Pza12(object):
    """
    This class instantiates and defines the methods for a Newport PZA12 piezo linear actuator.  In general
    these methods allow you to move a PZA12 actuator in a relative or absolute mode, turn their motors
    on/off, get/set the internal software position of the actuator, and save/load the parameters of operation.
    
    The methods of this class are:
        __init__()
        move()       # this is a relative move
        move_abs()
        check_position()
        get_position()
        set_position()
        reset_position()
        use_position_sensors()
        motor_on()
        motor_off()
        get_move_units()
        set_move_units()
        get_controller_address()
        get_channel_number()
        save()
        load()
    """
 
    unitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    U_STEPS_MM = 100000
    MAX_POSITION_IN_U_STEPS = 600000  # these limits assume the NanoPZ is mechanically set to midrange when M1/M2 mechanisms are setup
    MIN_POSITION_IN_U_STEPS = -600000 # at its mid-range
    MAX_CAP_SENSOR_DISPLACEMENT = 2.250  # maximum value of displacement for Lion cap gauge sensor in 'Lo' sensitivity mode; in mm
    MIN_CAP_SENSOR_DISPLACEMENT = 0.250  # minimum value of displacement for Lion cap gauge sensor in 'Lo" sensitivity mode; in mm
    CAP_SENSOR_FEEDBACK_POSITION_TOLERANCE  = 0.000050   # 50 nm
    CAP_SENSOR_FEEDBACK_CONVERGENCE_TRIES = 10           # maximum number of attempts to reach position convergence using cap gauge sensor feedback
    
    #tip_tilt_translate_coordinates_dictionary = {}
    #
    #for line in open("M1 Tip Tilt Translate Actuator Coordinates Config.txt"):  # hardwired for M1 test for convenience, but over-rideable in __init__()
    #    parts = line.split(':')
    #    if len(parts) > 1:    # don't process blank lines
    #        tip_tilt_translate_coordinates_dictionary[parts[0].strip(" ")] = (parts[1].rstrip()).strip(" ")
    #del parts
    #del line

    def __init__(self,pzc200_controller_instance,pzc200_controller_address,switchbox_channel,position_sensor=None,
                 initial_position=0,name="An UnNamed Pza12 NanoPz Actuator",units="mm",report_position_sensor = True,
                 label = '', readlastpos = True, correction = None, correction_minus = None):
        """
        This constructor instantiates a PZA12 linear actuator.
        
        The inputs to this method are:
        
           pzc200_controller_instance:  the controller instance that describes the Pzc200 controller which drives this PZA12 actuator.
           pzc200_controller_address:  the address of the pzc200_controller_instance; ranges in value from 1:255.
           switchbox_channel:  the channel this PZA12 actuator is attached to; ranges in value from 1:8.
           position_sensor:  if a cap sensor is desired to be attached to this PZA12 actuator, it is specified with the names given to the
                       Cap Sensor instances which must be defined before the PZA12 instances are defined (e.g. cux,clz1,cuz3,etc.)
           initial_position: an optional input parameter setting the position of the actuator in mm.  Range of motion of a PZA12
                             actuator is nominally +6.25mm/-6.25mm; ???? +1.00mm/-1.00mm for PZA12s with associated Cap Sensor and 
                             +6.25mm/-6.25mm for PZA12s not associated with a Cap Gauge ????
           name: an optional string entered by user to describe this actuator.
           units: an optionally entered string that specifies the linear dimensional units to be used for this actuator instance.
           tip_tilt_translate_coefficients_config_file: always read at class definition time and inputs the x,y,z design positions in mm
                             of the PZA12 tips in the M1 mechanical design.
           label = label used for Gui display purposes
           readlastpos = Reads last position if stored.  Overrides initial position input.
           correction = scaling factor to motor movements can be a number (linear correction) or a list of polinomial coefficients
           correction_minus = negative direction correction if the correction is not sysmetric.  Only checked if correction != None (can be 0).
        """
        self.label = label
        self.controller = pzc200_controller_instance
        self.pzc200_controller_address = pzc200_controller_address
        self.switchbox_channel = switchbox_channel
        self.position_sensor = position_sensor
        self.name = name
        self.loop_count = 1   # used to terminate loop control of reading cap gauges when self. use_position_sensor_feedback is True
        self.loop_convergence_result = True    # used to properly report state of loop convergence when self.use_position_sensor_feedback is True
        self.use_position_sensors(False)     # internally sets self.use_position_sensor_feedback to FALSE (default;) call this line before setting self.position below
        if position_sensor and report_position_sensor:
            self.report_position_sensor = True
        else:
            self.report_position_sensor = False

        self.current_move_units = units      # units for commanded motion; may be different than "mm"
        self.internal_units = "mm"           # This is just to assert that self.position is stored with Pza12 instance
                                             # as "mm" and otherwise is not used in the program
        if not readlastpos or not self.load_position(): 
            self.position = initial_position
        self.offset = 0.0        
        self.update_position()        
        
        #Read and reformat correction files.
        self.correctionplus = None
        self.correctionminus = None
        if correction != None:
            if type(correction) in [float, int]:
                if float(correction) != 0.0:
                    self.correctionplus = {9999.0: [0,correction]}
            elif type(correction) in [list, tuple]:
                c2 = []
                for i in correction:
                    c2.append(float(i))    #Note will raise an error if it cant float the input
                self.correctionplus = {9999.0: c2}
            elif type(correction) is dict:
                self.correctionplus = {}
                for i in correction.keys():
                    if type(correction[i]) in [float, int]:
                        self.correctionplus[float(i)] = [0,correction[i]]
                    elif type(correction[i]) in [list, tuple]:
                        c2 = []
                        for j in correction[i]:
                            c2.append(float(j))    #Note will raise an error if it cant float the input
                        self.correctionplus[float(i)] = c2
                
            
            if correction_minus == None:
                self.correctionminus = self.correctionplus
            else:
                if type(correction_minus) in [float, int]:
                    if float(correction_minus) != 0.0:
                        self.correctionminus = {9999.0: [0,correction_minus]}
                elif type(correction_minus) in [list, tuple]:
                    c2 = []
                    for i in correction_minus:
                        c2.append(float(i))   #Note will raise an error if it cant float the input            
                    self.correctionminus = {9999.0: c2}
                elif type(correction_minus) is dict:
                    self.correction_minus = {}
                    for i in correction_minus.keys():
                        if type(correction_minus[i]) in [float, int]:
                            self.correction_minus[float(i)] = [0,correction_minus[i]]
                        elif type(correction_minus[i]) in [list, tuple]:
                            c2 = []
                            for j in correction_minus[i]:
                                c2.append(float(j))    #Note will raise an error if it cant float the input
                            self.correction_minus[float(i)] = c2                    
        if self.correctionplus:
            self.correctionpluskeys = self.correctionplus.keys()
            self.correctionpluskeys.sort()
        if self.correctionminus:
            self.correctionminuskeys = self.correctionminus.keys()
            self.correctionminuskeys.sort()
                    
    
    def move(self,amount,units='mm'):
        """
        Method to move a Pza12 actuator in relative mode.  The Pzc200 controller makes the actual call for motion.
        This is the only method used in the program that actually commands a Pza12 to move.
        First, the commanded position is first bounds-checked.  If the desired position will be within
        actuator range, the move method returns 'TRUE'; if not, FALSE (and the position is not updated.)
        Second, the appropriate channel is selected, it's motor turned on, and the actuator is commanded 
        to move.  Subsequently, the motor is turned off and the current position is updated in software.
        
        Inputs:
             amount:  value of linear displacement requested
             units:  optional units of 'amount.'  Default is 'mm.'
        Outputs:
             TRUE if motion was commanded & self.use_position_sensor_feedback is False.
             FALSE if motion was not commanded & self.use_position_sensor_feedback is False.
             TRUE if motion was commanded, desired position was attained, and self.use_position_sensor_feedback is True
             FALSE if motion was not commanded and/or desired position was not attained, and self.use_position_sensor_feedback is True
        """
#        print amount,self.correctionpluskeys
        #Apply movement correction before position checks and movement
        original_amount = amount
        if amount > 0 and self.correctionplus:
            for j in self.correctionpluskeys:
                if amount <= j:
                    a2 = 0
                    for i in range(len(self.correctionplus[j])):
                        a2 = a2 + (self.correctionplus[j][i] * (amount ** i))
                    amount = a2
                    break
        elif amount < 0 and self.correctionminus:
            for j in self.correctionminuskeys:
                if (-1 * amount) <= j:
                    a2 = 0
                    for i in range(len(self.correctionminus[j])):
                        a2 = a2 + (self.correctionminus[j][i] * (abs(amount) ** i))
                    amount = -1 * a2        
                    break
#        print amount,self.correctionplus
        if self.check_position(amount,units):    # bounds checking
            self.current_move_units = units
            amount *= self.unitvalues[units]          # amount is now in "mm"
            if self.switchbox_channel:  #Will not switch if channel 0, aka no switch box.
                self.controller.SelectSwitchboxChannelSet(self.pzc200_controller_address,self.switchbox_channel)
            self.controller.MotorOn(self.pzc200_controller_address)
            num_steps = int(self.U_STEPS_MM*amount)  # in PZA12 microsteps
            self.controller.PositionRelativeSet(self.pzc200_controller_address,num_steps)
            self.controller.MotorOff(self.pzc200_controller_address)
            
            if self.position_sensor and self.report_position_sensor: 
                current_position = self.position_sensor.read_position(1)
                delta = (self.position + original_amount) - current_position  # difference between desired position and current position as read from cap gauge
                self.position = current_position
                if self.use_position_sensor_feedback:
                    if np.abs(delta) > self.CAP_SENSOR_FEEDBACK_POSITION_TOLERANCE:
                        self.loop_convergence_result = False
                    else:
                        self.loop_convergence_result = True
                else:
                    self.loop_convergence_result = True

                if (bool(self.use_position_sensor_feedback) & bool(self.loop_count < self.CAP_SENSOR_FEEDBACK_CONVERGENCE_TRIES)):  # use cap sensor to drive actuator to initial desired position
                    if np.abs(delta) > self.CAP_SENSOR_FEEDBACK_POSITION_TOLERANCE:
                        self.loop_count += 1
                        self.move(delta,"mm")
                
                self.loop_count = 1
                self.save_position()
                return self.loop_convergence_result
            else:
                self.position += amount              # self.position stored in "mm" despite self.current_move_units value
                self.save_position()
                return True
                
            
        else:
            return False
                           
    def move_abs(self,desired_absolute_position,units='mm'):
        """
        Move to a position that is an absolute position that's referenced to self.initial_position set at instance creation time; in "mm."
        Resulting position if first checked to see if it's within the range of the PZA12.
        
        Inputs:
              desired_absolute_position:  position of actuator tip with respect to assumed self.initial_position as origin.
              units:  optional value of units of 'desired_absolute_position.'  Default value is 'mm.'
        """
        amount = desired_absolute_position*self.unitvalues[units] - self.position
        self.move(amount,units=units)
                    
    def check_position(self,amount,units):  # amount input is always a relative move quantity
        """
        This method checks to see if the resulting motion will be within the range of the PZA12 actuator and the
        Cap Sensor if present.  Presently,
        this function works because it's assumed that the actuator is initially set to the middle of its travel range.
        Inputs:
             amount: value of proposed relative motion.  Always adjusted to mm in this method.
             units:  units of 'amount.'  
        Output:
             TRUE if commanded move will be within range of PZA12.
             FALSE if commanded move will exceed the range of the PZA12.
        """
        proposed_ending_position = self.position + amount*self.unitvalues[units]
        
        if self.position_sensor:    # if cap gauges are present, always guard against running them into the wall
            #current_position_sensor_position = self.position_sensor.read_position(10)
            #proposed_ending_position = current_position_sensor_position + amount*self.unitvalues[units]
            if((proposed_ending_position < self.MIN_CAP_SENSOR_DISPLACEMENT) |
               (proposed_ending_position > self.MAX_CAP_SENSOR_DISPLACEMENT)):
                print 'Axis movement limits exceeded.  Move canceled'
                return False

        proposed_ending_position_in_u_steps = int(self.U_STEPS_MM*proposed_ending_position)
        if (((proposed_ending_position_in_u_steps)>self.MAX_POSITION_IN_U_STEPS) |  
            ((proposed_ending_position_in_u_steps)<self.MIN_POSITION_IN_U_STEPS)):
            print 'Axis movement limits exceeded.  Move canceled'
            return False    # commanded motion will exceed PZA12 range
        else:
            return True    # commanded motion is valid

    def update_position(self,units="mm"):
        """
        Return current position of Pza12 actuator in user requested units
        Inputs:
              units of optionally requested position variable.  Default value is 'mm.'
        Outputs:
              position of PZA12 actuator in requested units.  'mm' is default units value.
        """

        if self.position_sensor and self.report_position_sensor:
            position = self.position_sensor.read_position(3)
            self.position = position
        else:
            position = self.position
        
        return (position + self.offset)/self.unitvalues[units]  

    def get_position(self,units="mm"):
        """
        Return current stored position of Pza12 actuator in user requested units
        Inputs:
              units of optionally requested position variable.  Default value is 'mm.'
        Outputs:
              position of PZA12 actuator in requested units.  'mm' is default units value.
        """
        return (self.position + self.offset)/self.unitvalues[units] 

    def set_position(self,requested_position,units="mm"):
        """
        Sets the Pza12's self.position of the actuator instance in mm, overriding user specified units value.
        This does not move the PZA12 actuator, but instead sets the internal software position variable.
        
        Inputs:
             requested_position:  value of desired internally software position of PZA12 actuator
             units:  units of optinally requested position variable.  Default value is 'mm.'
        Output:
             None
        """
        self.offset = self.unitvalues[units]*requested_position - self.position
        
    def reset_position(self):
        """
        Resets self.offset to zero so that reported position from using self.get_position reflects the "true" mechanical position of the PZA12.
        Inputs:
            None
        Ouputs:
            None
        """
        self.offset = 0.0

    def use_position_sensors(self,proposition = False):
        """
        Even though a cap gauge may be associated with a NanoPZ actuator at PZA12 instancing
        time, it does not necessarily have to be used in reading PZA12 positions during
        moves, etc.  This functionality is established with this method.  If proposition = FALSE (default)
        then the cap gauges will be disregarded.  If proposition = TRUE, then the cap gauges
        will be used to read PZA12 positions.
        
        Input:
             proposition:  TRUE if you want to use the cap gauge attached to the PZA12.
                           FALSE if you do not want to use the cap gauge attached to the PZA12 for correcting motions.
        Output:
             None
        """
        self.use_position_sensor_feedback = proposition
                
    def report_position_sensors(self,proposition = True):
        """
        Even though a cap gauge may be associated with a NanoPZ actuator at PZA12 instancing
        time, it does not necessarily have to be used in reading PZA12 positions during
        moves, etc.  This functionality is established with this method.  If proposition = FALSE (default)
        then the cap gauges will be disregarded.  If proposition = TRUE, then the cap gauges
        will be used to read PZA12 positions.
        
        Input:
             proposition:  TRUE if you want to use the cap gauge attached to the PZA12.
                           FALSE if you do not want to use the cap gauge attached to the PZA12.
        Output:
             None
        """
        self.report_position_sensor = proposition

    def motor_on(self):
        """
        Turn on the motor power to the motor for this PZA12 actuator.
        Inputs:
              None
        Outputs:
              None
        """
        self.controller.MotorOn(self.pzc200_controller_address)

    def motor_off(self):
        """
        Turn off the motor power to the motor for this PZA12 actuator.
        Inputs:
              None
        Outputs:
              None
        """
        self.controller.MotorOff(self.pzc200_controller_address)

    def get_move_units(self):
        """
        Return the PZA12's instance variable holding the last commanded units value for a move.
        Input:
             None
        Output:
             self.current_move_units.
        """
        return self.current_move_units
    
    def set_move_units(self,units):
        """
        Set the PZA12's instance variable holding the last commanded units value for a move.
        Input:
             units from the Zygo canonical 'unitvalues' units array.
        Output:
             self.current_move_units.
        """
        self.current_move_units = units
                        
    def get_controller_address(self):
        """
        Return the Pzc200 controller address of the controller that is driving this PZA12 actuator.  Valid range is 1:255.
        Input:
             None
        Output:
             self.pzc200_controller_address
        """
        return self.pzc200_controller_address
    
    def get_channel_number(self):
        """
        Return the switchbox (Pzc200-SB) channel to which the PZA12 is attached.  Valid range is 1:8.
        Input:
             None
        Output:
             self.switchbox_channel
        """
        return self.switchbox_channel
            
    def load_position(self, filename = 'PzaPos.txt'):
        a = self._open_save_file(filename)
        if a.has_key(self.name.upper()):
            self.position = float(a[self.name.upper()])
            return True
        else:
            return False
    
    def save_position(self, filename = 'PzaPos.txt'):
        """Recreate the saved position file with the current motor position"""      
        a = self._open_save_file(filename)
        a[self.name.upper()] = str(self.position)
        f = open(filename, 'w')
        for i in a.keys():
            f.write(i + ' = ' + a[i] + '\n')
        f.close()
    
    def _open_save_file(self, filename = 'PzaPos.txt'):
        """Opens a file containing saved Pza Positions and returns a dictionary of contents."""
        if os.path.isfile(filename):
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            positions = {}
            for line in lines:
                a = line.strip().split('=')
                if len(a) == 2:
                    positions[a[0].upper().strip()] = a[1].strip()
            return positions
        else:
            return {}
    
    def save(self,filename):
        """
        Save a Pza12 instance to the named file 'filename'
        Input:
             filename desired to store PZA12 instance.
        Output:
             None to calling method; file stored to disk.
        """
        file = open(filename,'wb')
        pickle.dump(self,file)
        file.close()
        
    def load(self,filename):
        """
        Retrive a previously stored Pza12 instance to memory from the named file 'filename'
        Input:
             filename:  desired file of stored PZA12 instance.
        Output:
             None
        """
        file = open(filename,'rb')
        self = pickle.load(filename)
        file.close()
#########################################################################################



#########################################################################################

class GroupMovements(object):

    linearunitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    angularunitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self, xmotor = None, ymotor = None, zmotor1 = None, zmotor2 = None, zmotor3 = None, zmotor1_position = None, 
                 zmotor2_position = None, zmotor3_position = None,rmotor = None, stack_height = 0.0,
                 base_rotation = 0.0, xflip = False, yflip = False, zflip = False, rflip = False,
                 tiltflip = False, reportxflip = False):
        """
        Inputs:
            xmotor              -- X axis motor object
            ymotor              -- Y axis motor object
            zmotor1             -- Z axis motor object
            zmotor2             -- Z axis motor object
            zmotor3             -- Z axis motor object
            zmotor1_position    -- Contact position of the Z1 motor (x,y)
            zmotor2_position    -- Contact position of the Z2 motor (x,y)
            zmotor3_position    -- Contact position of the Z3 motor (x,y)
            stack_height (0.0)  -- Distance from the Z motor plane to the optic vertex.
            rmotor (None)       -- Rotation axis motor object
            base_rotation (0.0) -- A rotation offset of the x,y coordinate system
            xflip (False)       -- Inverts X motor motions
            yflip (False)       -- Inverts Y motor motions
            zflip (False)       -- Inverts Z motor motions
            
        Calculation assumptions
            all coordinates are relative to the plane defined by the Z motors, tilting about the origin x,y = 0,0
            the 3 Z motors define a unique plane (they are not co-linear).
            all motors move in an ordinate direction (no skew)
            
        Functions:
            check_origins() -- Check to see if all motors have been origined
            origin(ask = True) -- Origin motors, ask has command line prompts
            get_position(axis = None) -- Return dictionary of all current axis positions
                                      -- axis returns float value for 1 axis.
            update_position() -- Updates group positions reading stored motor positions
            movex(amount, units = 'mm') -- move a relative amount in X direction on screen
            movex_abs(amount, units = 'mm') -- move an absolute amount in X direction on screen
            movey(amount, units = 'mm') -- move a relative amount in Y direction on screen
            movey_abs(amount, units = 'mm') -- move an absolute amount in Y direction on screen   
            movez(amount, units = 'mm') -- move a relative amount in Z direction
            movez_abs(amount, units = 'mm') -- move an absolute amount in Z direction
            rotate(amount, units = 'deg') -- rotate a relative amount CW on screen is +
            rotate_abs(amount, units = 'deg') -- rotate an absolute amount CW on screen is +  
            tiltx(amount, units = 'deg', fixedxy = False) -- tilt a relative amount in X direction on screen
            tiltx_abs(amount, units = 'deg', fixedxy = False) -- tilt an absolute amount in X direction on screen
            tilty(amount, units = 'deg', fixedxy = False) -- tilt a relative amount in Y direction on screen
            tilty_abs(amount, units = 'deg', fixedxy = False) -- tilt an absolute amount in Y direction on screen  
            z_position_sensors_status(report = None, use = None) -- check and update cap gauge use for Z axis
            
            _calculate_current_xy() --  use update_position
            _calculate_current_tilt_z() -- use update_position
            _tip_tilt_z_motions(rotation, tilt, oldtilt, fixedxy = False, check = False) -- Use x,y tilt commands
            
        """
        #Check to make sure that all z motors and positions are present
        for i in [zmotor1, zmotor2, zmotor3, zmotor1_position, zmotor2_position, zmotor3_position]:
            if i == None:
                raise ValueError, "All Z motors and Z positions must be specified"
                
        #Copy input variables to self.
        self.xmotor = xmotor
        self.ymotor = ymotor  
        self.zmotor1 = zmotor1  
        self.zmotor2 = zmotor2  
        self.zmotor3 = zmotor3
        self.rmotor = rmotor 
        self.base_rotation = float(base_rotation)
        if xflip:
            self.xflip = -1
        else:
            self.xflip = 1
        if yflip:
            self.yflip = -1
        else:
            self.yflip = 1
        if zflip:
            self.zflip = -1
        else:
            self.zflip = 1
        if rflip:
            self.rflip = -1
        else:
            self.rflip = 1 
        if tiltflip:
            self.tiltflip = -1
        else:
            self.tiltflip = 1  
        if reportxflip:
            self.reportxflip = -1
        else:
            self.reportxflip = 1            
        self.zmotor1_position = zmotor1_position
        self.zmotor2_position = zmotor2_position
        self.zmotor3_position = zmotor3_position
        self.stack_height = stack_height
        self.check_origins()
        
        #Calculate the current tilt relative to the nominal motor plane
        self.position = {}
        self.update_position()
        
        #Check to see if the individual motors have position sensors
        self.zpositionsensors = False
        for i in [self.zmotor1,self.zmotor2,self.zmotor3]:
            if hasattr(i, 'position_sensor') and i.position_sensor:
                self.zpositionsensors = True
                break   #True if any motor has a position sensor
        self.xypositionsensors = False
        for i in [self.xmotor,self.ymotor]:
            if hasattr(i, 'position_sensor') and i.position_sensor:
                self.xypositionsensors = True
                break   #True if any motor has a position sensor                

    def check_origins(self):
        """Check the origin status for each motor, and create two groups of pass / fail."""
        #self.ishomed = True
        for i in [self.xmotor,self.ymotor, self.zmotor1,self.zmotor2,self.zmotor3,self.rmotor] :
            if hasattr(i, 'ishomed'):
                if not i.ishomed:
                    self.ishomed = False
                    break
                else:
                    self.ishomed = True
    
    def origin(self, ask = True):
        """Origin all motors connected to group motion object.
        Optional ask before origining each motor"""
        if hasattr(self, 'ishomed'):
            grouphome = self.ishomed
        else:
            grouphome = False
        
        for i in [self.xmotor,self.ymotor, self.zmotor1,self.zmotor2,self.zmotor3,self.rmotor] :
            if hasattr(i, 'ishomed'):
                if ask:
                    designator = ' '
                    if hasattr(i, 'label'):
                        designator = designator + i.label + ' '
                    elif hasattr(i, 'name'):
                        designator = designator + i.name + ' '                      
                    if raw_input('Origin motor '+designator+'? (y/N):  ').strip()[0].upper() == 'Y':
                        i.origin()
                elif not grouphome:
                    if not i.ishomed:
                        i.origin()
                else:
                    i.origin()
        self.check_origins() 
        self.update_position()
    
    def get_position(self, axis = None):
        """Return a dictionary of all axis positions or the value of the specified axis
        Does not currently support units.""" 
        
        if axis == None:
            return self.position 
        else:
            return self.position[axis]
    
    def update_position(self):
        """Read all motors, and update all of the current positions
        *** add a flag to have individual motors read sensors."""
        if (not hasattr(self, 'ishomed')) or self.ishomed:
            if self.rmotor:
                self.position['rotation'] = self.rflip*self.rmotor.get_position() #+self.base_rotation
            else:
                self.position['rotation'] = 0.0 #self.base_rotation
            self._calculate_current_xy()
            self._calculate_current_tilt_z()  
        
    def movex(self, amount, units = 'mm'):
        """Moves a specified relative amount in the x direction"""
        
        if not self.xmotor or not self.ymotor:
            return
        
        rotrad = (self.rflip * self.position['rotation']*self.xflip*self.yflip  + self.base_rotation ) * math.pi/180.0
        xmotormotion = amount * self.linearunitvalues[units] * self.xflip * math.cos(rotrad)
        ymotormotion = - amount * self.linearunitvalues[units] * self.yflip * math.sin(rotrad)*self.rflip #***Adding rflip is a short term (WRONG) solution to make it work.
        #print rotrad*180/math.pi, xmotormotion, ymotormotion
        if self.xmotor.check_position(xmotormotion,"mm") & self.ymotor.check_position(ymotormotion,"mm"):
            self.xmotor.move(xmotormotion)
            self.ymotor.move(ymotormotion)
            self.position['xpos'] = self.position['xpos'] +amount*self.linearunitvalues[units]
            return True
        else:
            return False
        
    def movex_abs(self, amount, units = 'mm'):
        """Moves a specified absolute amount in the x directin"""
        
        amount = (amount*self.linearunitvalues[units]) - self.position['xpos']
        return self.movex(amount)
    
    def movey(self, amount, units = 'mm'):
        """Moves a specified relative amount in the y direction"""
        
        if not self.xmotor or not self.ymotor:
            return        
        
        rotrad = ( self.rflip * self.position['rotation']*self.xflip*self.yflip + self.base_rotation ) * math.pi/180.0
        xmotormotion = amount * self.linearunitvalues[units] * self.xflip * math.sin(rotrad)*self.rflip #***Adding rflip is a short term (WRONG) solution to make it work.
        ymotormotion = amount * self.linearunitvalues[units] * self.yflip * math.cos(rotrad)
        #print rotrad*180/math.pi, xmotormotion, ymotormotion
        if self.xmotor.check_position(xmotormotion,"mm") & self.ymotor.check_position(ymotormotion,"mm"):
            self.xmotor.move(xmotormotion)
            self.ymotor.move(ymotormotion)
            self.position['ypos'] = self.position['ypos'] +amount*self.linearunitvalues[units]
            return True
        else:
            return False

    def movey_abs(self, amount, units = 'mm'):
        """Moves a specified absolute amount in the y directin"""
        
        amount = (amount*self.linearunitvalues[units]) - self.position['ypos']
        return self.movey(amount)
    
    def movez(self, amount, units = 'mm', check = False):
        """Moves a specified relative amount in the z direction"""
        
        moveamount = amount * self.linearunitvalues[units] * self.zflip
        if check:
            return moveamount
        if ((self.zmotor1.check_position(moveamount,"mm") & self.zmotor2.check_position(moveamount,"mm") & self.zmotor3.check_position(moveamount,"mm"))):
            self.zmotor1.move(moveamount)
            self.zmotor2.move(moveamount)
            self.zmotor3.move(moveamount)
            self.position['zpos'] = self.position['zpos'] + amount * self.linearunitvalues[units]
            return True
        else:
            return False
    
    def movez_abs(self, amount, units = 'mm'):
        """Moves a specified absolute amount in the z directin"""
        
        amount = (amount * self.linearunitvalues[units]) - self.position['zpos']
        return self.movez(amount)            
    
    def rotate(self, amount, units = 'deg'):
        """Moves a rotation stage a relative amount, and recalculates current positions and tilts"""
        if self.rmotor:
            if self.rmotor.move(self.rflip*amount*self.angularunitvalues[units]):
                self.update_position()
            else:
                return False
        else:
            return False
    
    def rotate_abs(self, amount, units = 'deg'):
        """Moves a rotation stage an absolute amount offset by the base rotation, 
        and recalculates current positions and tilts"""
        if self.rmotor:
            if self.rmotor.move_abs(self.rflip*amount*self.angularunitvalues[units]):
                self.update_position()
            else:
                return False
        else:
            return False    
    
    def _calculate_current_xy(self):
        """Calculates the x,y coordinates for the specified rotation angle."""
        
        if not self.xmotor or not self.ymotor:
            return        
        
        xpos = self.xflip*self.xmotor.get_position()
        ypos = self.yflip*self.ymotor.get_position() 
        
        rotrad = (self.rflip * self.position['rotation'] + self.base_rotation )* math.pi/180.0
        xposprime = xpos*math.cos(rotrad)-ypos*math.sin(rotrad)
        yposprime = ypos*math.cos(rotrad)+xpos*math.sin(rotrad)
        
        self.position['xpos'] = xposprime
        self.position['ypos'] = yposprime
        
        return xposprime,yposprime
    
    def _calculate_current_tilt_z(self):
        """Calclates the tilt movements, and adjusts the 3 Z axis
        Inputs:
            rotation -- tilt axis rotation relative to x axis in degrees
        """
        
        #form of p is [ x, y, z]
        p1 = list(self.zmotor1_position) + [self.zmotor1.get_position()]
        p2 = list(self.zmotor2_position) + [self.zmotor2.get_position()]
        p3 = list(self.zmotor3_position) + [self.zmotor3.get_position()]
        
        #Calculating Plane in form ax + by + cz + d = 0
        a = (p2[1]-p1[1])*(p3[2]-p1[2]) - (p2[2]-p1[2])*(p3[1]-p1[1])
        b = (p2[2]-p1[2])*(p3[0]-p1[0]) - (p2[0]-p1[0])*(p3[2]-p1[2])
        c = (p2[0]-p1[0])*(p3[1]-p1[1]) - (p2[1]-p1[1])*(p3[0]-p1[0])
        d = -p1[0]*a - p1[1]*b - p1[2]*c
        
        #Rotating Plane in x,y
        rotrad = (self.position['rotation'] + self.base_rotation ) * math.pi/180.0
        aprime = a*math.cos(rotrad)-b*math.sin(rotrad)
        bprime = b*math.cos(rotrad)+a*math.sin(rotrad)
        
        #Calculating tilt and Z
        #Assuming that tilt origin is at x = y = 0 for Z calculation
        xtilt = - self.xflip * self.reportxflip * (180.0/math.pi )*math.atan(aprime / c)
        ytilt = - self.yflip *(180.0/math.pi )*math.atan(bprime / c)
        zpos =  - self.zflip * d / c
        
        self.position['xtilt'] = xtilt
        self.position['ytilt'] = ytilt
        self.position['zpos'] = zpos
        
        return xtilt, ytilt, zpos
        
        
    def _tip_tilt_z_motions(self, rotation, tilt, oldtilt, fixedxy = False, check = False):    
        """Calclates the tilt movements, and adjusts the 3 Z axis
        Inputs:
            rotation -- tilt axis rotation relative to x axis in degrees
            tilt -- the new relative tilt desired along that axis in degrees
            oldtilt -- the current tilt along the specified axis
            fixedxy (False) -- False -- only move z, 
                               True -- also move xyto keep pivot point constant.
            
        """
        if not self.xmotor or not self.ymotor:  #ensures that x & y motors will not be called if they are not there.
            fixedxy = False        
        
        new_tilt = tilt * math.pi/180.0
        old_tilt = oldtilt * math.pi/180.0
        rotation_rad = self.zflip * ( rotation*self.rflip*self.xflip*self.yflip*self.tiltflip + self.base_rotation ) * math.pi/180.0
        cos_rotation = self.yflip * math.cos(rotation_rad)#*(-1)
        sin_rotation = self.xflip * math.sin(rotation_rad)#*(-1)
        delta_tilt_tan = math.tan(new_tilt + old_tilt) - math.tan(old_tilt)
        moveamount1 = -(self.zmotor1_position[0]*cos_rotation + self.zmotor1_position[1]*sin_rotation)*delta_tilt_tan
        moveamount2 = -(self.zmotor2_position[0]*cos_rotation + self.zmotor2_position[1]*sin_rotation)*delta_tilt_tan
        moveamount3 = -(self.zmotor3_position[0]*cos_rotation + self.zmotor3_position[1]*sin_rotation)*delta_tilt_tan
        
        if fixedxy:
            delta_tilt_sin = math.sin(new_tilt + old_tilt) - math.sin(old_tilt)
            xmotormotion = self.stack_height * delta_tilt_sin * self.xflip * math.cos(rotation_rad)
            ymotormotion = self.stack_height * delta_tilt_sin * self.yflip * math.sin(rotation_rad)
            xymove = self.xmotor.check_position(xmotormotion,"mm") & self.ymotor.check_position(ymotormotion,"mm")
        else:
            xymove = True
        
        if check:
            if fixedxy:
                return [moveamount1, moveamount2, moveamount3, xmotormotion, ymotormotion], [self.zmotor1, self.zmotor2, self.zmotor3, self.xmotor, self.ymotor]
            else:
                return [moveamount1, moveamount2, moveamount3], [self.zmotor1, self.zmotor2, self.zmotor3]
        
        if self.zmotor1.check_position(moveamount1,"mm") & self.zmotor2.check_position(moveamount2,"mm") & self.zmotor3.check_position(moveamount3,"mm") & xymove:
            #print rotation_rad * 180.0 / math.pi, cos_rotation, sin_rotation
            #print self.zmotor1.label, moveamount1
            #print self.zmotor2.label, moveamount2
            #print self.zmotor3.label, moveamount3
            self.zmotor1.move(moveamount1)
            self.zmotor2.move(moveamount2)
            self.zmotor3.move(moveamount3)
            if fixedxy: #*** Need X, Y motor motion checks.
                self.xmotor.move(xmotormotion)
                self.ymotor.move(ymotormotion)
                self._calculate_current_xy()
            return True
        else:
            return False        

    def tiltx(self, amount, units = 'deg', fixedxy = False, check = False):
        """Tilt a relative amount of degrees in the X direction"""
        a = self._tip_tilt_z_motions(self.position['rotation'], amount*self.angularunitvalues[units], self.position['xtilt'], fixedxy, check)
        if check:
            return a
        if a:
            self.position['xtilt'] = self.position['xtilt'] + amount*self.reportxflip*self.angularunitvalues[units]
            return True
        else:
            return False
            
    def tiltx_abs(self, amount, units = 'deg', fixedxy = False, check = False):
        """Tilt a specified absolute amount of degrees in the X directin"""
        
        amount = amount*self.angularunitvalues[units] - self.position['xtilt']
        return self.tiltx(amount, fixedxy = fixedxy)
        
    def tilty(self, amount, units = 'deg', fixedxy = False, check = False):
        """Tilt a relative amount of degrees in the Y direction"""
        a = self._tip_tilt_z_motions(self.position['rotation'] + 90*self.rflip*self.xflip*self.yflip*self.tiltflip, amount*self.angularunitvalues[units], self.position['ytilt'], fixedxy, check)
        if check:
            return a
        if a:
            self.position['ytilt'] = self.position['ytilt'] + amount*self.angularunitvalues[units]
            return True
        else:
            return False
            
    def tilty_abs(self, amount, units = 'deg', fixedxy = False, check = False):
        """Tilt a specified absolute amount of degrees in the Y directin"""
        
        amount = amount*self.angularunitvalues[units] - self.position['ytilt']
        return self.tilty(amount, fixedxy = fixedxy)  
        
    def z_position_sensors_status(self, report = None, use = None):
        """Create a use z position sensor attributes only if at least 1 z axis has a position sensor.
        Four attributes created denoting if the sensors are used for position readout, motor motion,
        and if all of the motors in the z group have the same setting.
        Note:  position and use values will only be true if true for all motors.
        
        Inputs: report True / False -- update whether all z motors use position sensor reporting.
                use    True / False -- update whether all z motors use position sensor motion.
                
        If no inputs are provided this function will still update the position sensor attributes.
        """   
        
        checkreport = []
        checkuse = []
        for i in [self.zmotor1, self.zmotor2, self.zmotor3]:
            if hasattr(i, 'report_position_sensor'):
                if report != None:
                    i.report_position_sensor = report
                checkreport.append(i.report_position_sensor)
            if hasattr(i, 'use_position_sensor_feedback'):
                if use != None:
                    i.use_position_sensor_feedback = use            
                checkuse.append(i.use_position_sensor_feedback)              
        
        if len(checkreport) > 0:
            self.report_z_position_sensor = checkreport[0]
            self.report_z_position_sensor_partial = False
            for i in checkreport[1:]:
                if i != self.report_z_position_sensor:
                    self.report_z_position_sensor = False
                    self.report_z_position_sensor_partial = True
                    break
        
        if len(checkuse) > 0:
            self.use_z_position_sensor = checkuse[0]
            self.use_z_position_sensor_partial = False
            for i in checkuse[1:]:
                if i != self.use_z_position_sensor:
                    self.use_z_position_sensor = False
                    self.use_z_position_sensor_partial = True 
                    break
        #Note order of returns is used by wrapper function.
        return self.report_z_position_sensor,self.report_z_position_sensor_partial,self.use_z_position_sensor,self.use_z_position_sensor_partial

    def xy_position_sensors_status(self, report = None, use = None):
        """Create a use z position sensor attributes only if at least 1 z axis has a position sensor.
        Four attributes created denoting if the sensors are used for position readout, motor motion,
        and if all of the motors in the z group have the same setting.
        Note:  position and use values will only be true if true for all motors.
        
        Inputs: report True / False -- update whether all z motors use position sensor reporting.
                use    True / False -- update whether all z motors use position sensor motion.
                
        If no inputs are provided this function will still update the position sensor attributes.
        """   
        
        checkreport = []
        checkuse = []
        for i in [self.xmotor,self.ymotor]:
            if hasattr(i, 'report_position_sensor'):
                if report != None:
                    i.report_position_sensor = report
                checkreport.append(i.report_position_sensor)
            if hasattr(i, 'use_position_sensor_feedback'):
                if use != None:
                    i.use_position_sensor_feedback = use            
                checkuse.append(i.use_position_sensor_feedback)              
        
        if len(checkreport) > 0:
            self.report_z_position_sensor = checkreport[0]
            self.report_z_position_sensor_partial = False
            for i in checkreport[1:]:
                if i != self.report_z_position_sensor:
                    self.report_z_position_sensor = False
                    self.report_z_position_sensor_partial = True
                    break
        
        if len(checkuse) > 0:
            self.use_z_position_sensor = checkuse[0]
            self.use_z_position_sensor_partial = False
            for i in checkuse[1:]:
                if i != self.use_z_position_sensor:
                    self.use_z_position_sensor = False
                    self.use_z_position_sensor_partial = True 
                    break
        #Note order of returns is used by wrapper function.
        return self.report_z_position_sensor,self.report_z_position_sensor_partial,self.use_z_position_sensor,self.use_z_position_sensor_partial


class GroupWrapper(object):
    """Creates object shells for each axis in the group movement.
    this is to make each axis have the same structure as an individual motor
    for purposes of other programs using the functions."""
    
    def __init__(self, group_move_object, group_label):
        
        
        #axis names for position: xpos, ypos, zpos, xtilt, ytilt, rotation, upper_rotation, goniometer
        
        self.group_move_object = group_move_object
        if hasattr(group_move_object, 'ishomed'):
            ishomed = group_move_object.ishomed
        else:
            ishomed = None
        
        if hasattr(group_move_object, 'zpositionsensors') and group_move_object.zpositionsensors:
            zsensor = group_move_object.z_position_sensors_status
        else:
            zsensor = None        
        
        if hasattr(group_move_object, 'xypositionsensors') and group_move_object.xypositionsensors:
            xysensor = group_move_object.xy_position_sensors_status
        else:
            xysensor = None
            
        self.movex= self.MoveAxis(group_move_object, group_move_object.movex, group_move_object.movex_abs, group_label+' X Axis', 'xpos', 'mm', ishomed, xysensor)
        self.movey= self.MoveAxis(group_move_object, group_move_object.movey, group_move_object.movey_abs, group_label+' Y Axis', 'ypos', 'mm', ishomed, xysensor)
        self.movez= self.MoveAxis(group_move_object, group_move_object.movez, group_move_object.movez_abs, group_label+' Z Axis', 'zpos', 'mm', ishomed, zsensor)
        self.tiltx= self.MoveAxis(group_move_object, group_move_object.tiltx, group_move_object.tiltx_abs, group_label+' X Tilt', 'xtilt', 'deg', ishomed, zsensor)
        self.tilty= self.MoveAxis(group_move_object, group_move_object.tilty, group_move_object.tilty_abs, group_label+' Y Tilt', 'ytilt', 'deg', ishomed, zsensor)
        if group_move_object.rotate:
            self.rotate= self.MoveAxis(group_move_object, group_move_object.rotate, group_move_object.rotate_abs, group_label+' Rotation', 'rotation', 'deg', ishomed)
    
    class MoveAxis(object):
        """Basic object template used for every axis"""
        def __init__(self, group_move_object, move, move_abs, label, position_name, units, ishomed, has_pos_sensor = None):
            """
            Inputs:
                group_move_object -- initialized instance of group movement object
                move -- function to call for move commands
                move_abs -- function to call for move_abs commands
                label -- text label to be used by a gui
                position_name -- name of the axis within the group movement object
                units -- default units used by the axis
                ishomed -- T/F flag for if an axis is homed
                has_pos_sensor -- function to call for updating axis position sensor information
            """
            
            if ishomed != None:
                self.ishomed = ishomed
            self.move = move
            self.move_abs = move_abs
            self.label = label
            self.internal_units = units
            self.position_name = position_name
            self.group_move_object = group_move_object
            self.position_sensor = has_pos_sensor
            if self.position_sensor:
                self.check_position_sensor_use()

        def update_position(self):
            """Get and return the position of a specific axis"""
            return self.get_position()
            
        def get_position(self):
            """Get and return the position of a specific axis"""
            return self.group_move_object.get_position(self.position_name)
        
        def origin(self):
            """Origins all motor objects in the group"""
            self.group_move_object.origin(False)
            self.ishomed = self.group_move_object.ishomed
        
        def checkhome(self):
            """A function that checks the base object to update home status"""
            self.ishomed = self.group_move_object.ishomed
            
        def use_position_sensors(self, use = False):
            """Update whether the position sensors are used for motion via an input function"""
            a = self.position_sensor(use = use)
            if len(a) == 2:
                self.use_position_sensor_feedback = a[1]
            elif len(a) == 4:
                self.use_position_sensor_feedback = a[2]
                self.use_position_sensor_feedback_partial = a[3]
                
        def report_position_sensors(self,report = True):
            """Update whether the position sensors are used for reporting via an input function"""
            a = self.position_sensor(report = report)
            if len(a) == 2:
                self.report_position_sensor = a[0]
            elif len(a) == 4:
                self.report_position_sensor = a[0]
                self.report_position_sensor_partial = a[1]
                
        def check_position_sensor_use(self):
            """Read whether the position sensors are used for via an input function"""
            a = self.position_sensor()
            if len(a) == 2:
                self.report_position_sensor = a[0]
                self.use_position_sensor_feedback = a[1]
            elif len(a) == 4:
                self.report_position_sensor = a[0]
                self.report_position_sensor_partial = a[1]
                self.use_position_sensor_feedback = a[2]
                self.use_position_sensor_feedback_partial = a[3]    
            
    
        