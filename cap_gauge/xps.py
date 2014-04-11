import socket

class Xps(object):
    """
    The XPS class defines all the functionality for using all the Newport actuators that can be used by an XPS controller.
    Those actuators are defined by their separate classes below.
    Additionally this class defines the methods for estabishing an Ethernet socket connection from a PC to an XPS
    controller.  For a complete definition of these methods see Newport's XPS Programmer's Manual.
    
    Authored by Dennis Hancock
    Apr-Jul 2012
    """

    # Defines
    MAX_NB_SOCKETS = 32

    # Global variables
    sockets = {}
    nbSockets = 0

    # Initialization Function
    def __init__ (self,ip_address,port,name="Newport Xps Controller",timeout=20):
        self.ip_address = ip_address
        self.port = port
        self.controller_name = name
        self.timeout = timeout
        self.TCP_ConnectToServer()
    
    # Send command and get return
    def sendAndReceive (self,command):
        if(self.socketId == -1):
            return[-1,'You do not have a valid socket connection']
        try:
            self.sockets[self.socketId].send(command)
            ret = self.sockets[self.socketId].recv(1024)
            while (ret.find(',EndOfAPI') == -1):
                ret += self.sockets[self.socketId].recv(1024)
        except socket.timeout:
            return [-2, '']
        except socket.error (errNb, errString):            # errNb is currently undefined
            print 'Socket error : ' + errString
            return [-2, '']

        for i in range(len(ret)):
            if (ret[i] == ','):
                return [int(ret[0:i]), ret[i+1:-9]]

    # TCP_ConnectToServer
    def TCP_ConnectToServer (self):
        
        if (Xps.nbSockets >= self.MAX_NB_SOCKETS):
            return -1
        self.socketId = Xps.nbSockets
        Xps.nbSockets += 1
        
        try:
            Xps.sockets[self.socketId] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Xps.sockets[self.socketId].connect((self.ip_address, self.port))
            Xps.sockets[self.socketId].settimeout(self.timeout)
            Xps.sockets[self.socketId].setblocking(1)
        except socket.error:
            return -1
        
    # TCP_SetTimeout
    def TCP_SetTimeout (self,timeOut):
        if (self.socketId > -1):
            Xps.sockets[self.socketId].settimeout(timeOut)

    # TCP_CloseSocket
    def TCP_CloseSocket (self):
        if (self.socketId >= 0 and self.socketId < self.MAX_NB_SOCKETS):
            try:
                Xps.sockets[self.socketId].close()
                Xps.nbSockets -= 1
                Xps.socketId = -1
            except socket.error:
                pass
    # Display error function : simplify error print out and closes socket 
    def displayErrorAndClose (socketId, errorCode, APIName):
       if (errorCode != -2) and (errorCode != -108):
           [errorCode2, errorString] = myxps.ErrorStringGet(socketId, errorCode)
           if (errorCode2 != 0):
               print APIName + ' : ERROR ' + str(errorCode)
           else:
               print APIName + ' : ' + errorString
       else:
           if (errorCode == -2):
               print APIName + ' : TCP timeout'
           if (errorCode == -108):
               print APIName + ' : The TCP/IP connection was closed by an administrator'
       myxps.TCP_CloseSocket(socketId)
       return

    # PositionerMaximumVelocityAndAccelerationGet :  Return maximum velocity and acceleration of the positioner
    def PositionerMaximumVelocityAndAccelerationGet (self, PositionerName):
        command = 'PositionerMaximumVelocityAndAccelerationGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GetLibraryVersion
    def GetLibraryVersion (self):
        return ['MET-5 M1 Drivers v1.0 24Apr12 DMH']

    # ControllerMotionKernelTimeLoadGet :  Get controller motion kernel time load
    def ControllerMotionKernelTimeLoadGet (self):
        command = 'ControllerMotionKernelTimeLoadGet(double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # ObjectsListGet:  undocumented command; gets names of groups and actuators from XPS
    def ObjectsListGet(self):
        command = 'ObjectsListGet(char *)'
        [error,returnedString] = self.sendAndReceive(command);
        return [error,returnedString]
    
    # ControllerStatusGet :  Read controller current status
    def ControllerStatusGet (self):
        command = 'ControllerStatusGet(int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # ControllerStatusStringGet :  Return the controller status string corresponding to the controller status code
    def ControllerStatusStringGet (self,ControllerStatusCode):
        command = 'ControllerStatusStringGet(' + str(ControllerStatusCode) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ElapsedTimeGet :  Return elapsed time from controller power on
    def ElapsedTimeGet (self):
        command = 'ElapsedTimeGet(double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # ErrorStringGet :  Return the error string corresponding to the error code
    def ErrorStringGet (self, ErrorCode):
        command = 'ErrorStringGet(' + str(ErrorCode) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # FirmwareVersionGet :  Return firmware version
    def FirmwareVersionGet (self):
        command = 'FirmwareVersionGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TCLScriptExecute :  Execute a TCL script from a TCL file
    def TCLScriptExecute (self, TCLFileName, TaskName, ParametersList):
        command = 'TCLScriptExecute(' + TCLFileName + ',' + TaskName + ',' + ParametersList + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TCLScriptExecuteAndWait :  Execute a TCL script from a TCL file and wait the end of execution to return
    def TCLScriptExecuteAndWait (self,TCLFileName, TaskName, InputParametersList):
        command = 'TCLScriptExecuteAndWait(' + TCLFileName + ',' + TaskName + ',' + InputParametersList + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TCLScriptExecuteWithPriority :  Execute a TCL script with defined priority
    def TCLScriptExecuteWithPriority (self, TCLFileName, TaskName, TaskPriorityLevel, ParametersList):
        command = 'TCLScriptExecuteWithPriority(' + TCLFileName + ',' + TaskName + ',' + TaskPriorityLevel + ',' + ParametersList + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TCLScriptKill :  Kill TCL Task
    def TCLScriptKill (self, TaskName):
        command = 'TCLScriptKill(' + TaskName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TimerGet :  Get a timer
    def TimerGet (self,TimerName):
        command = 'TimerGet(' + TimerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # TimerSet :  Set a timer
    def TimerSet (self, TimerName, FrequencyTicks):
        command = 'TimerSet(' + TimerName + ',' + str(FrequencyTicks) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # Reboot :  Reboot the controller
    def Reboot (self):
        command = 'Reboot()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # Login :  Log in
    def Login (self, Name, Password):
        command = 'Login(' + Name + ',' + Password + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # CloseAllOtherSockets :  Close all socket beside the one used to send this command
    def CloseAllOtherSockets (self):
        command = 'CloseAllOtherSockets()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # HardwareDateAndTimeGet :  Return hardware date and time
    def HardwareDateAndTimeGet (self):
        command = 'HardwareDateAndTimeGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # HardwareDateAndTimeSet :  Set hardware date and time
    def HardwareDateAndTimeSet (self, DateAndTime):
        command = 'HardwareDateAndTimeSet(' + DateAndTime + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventAdd :  ** OBSOLETE ** Add an event
    def EventAdd (self, PositionerName, EventName, EventParameter, ActionName, ActionParameter1, ActionParameter2, ActionParameter3):
        command = 'EventAdd(' + PositionerName + ',' + EventName + ',' + EventParameter + ',' + ActionName + ',' + ActionParameter1 + ',' + ActionParameter2 + ',' + ActionParameter3 + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventGet :  ** OBSOLETE ** Read events and actions list
    def EventGet (self, PositionerName):
        command = 'EventGet(' + PositionerName + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventRemove :  ** OBSOLETE ** Delete an event
    def EventRemove (self,PositionerName, EventName, EventParameter):
        command = 'EventRemove(' + PositionerName + ',' + EventName + ',' + EventParameter + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventWait :  ** OBSOLETE ** Wait an event
    def EventWait (self, PositionerName, EventName, EventParameter):
        command = 'EventWait(' + PositionerName + ',' + EventName + ',' + EventParameter + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedConfigurationTriggerSet :  Configure one or several events
    def EventExtendedConfigurationTriggerSet (self, ExtendedEventName, EventParameter1, EventParameter2, EventParameter3, EventParameter4):
        command = 'EventExtendedConfigurationTriggerSet('
        for i in range(len(ExtendedEventName)):
            if (i > 0):
                command += ','
            command += ExtendedEventName[i] + ',' + EventParameter1[i] + ',' + EventParameter2[i] + ',' + EventParameter3[i] + ',' + EventParameter4[i]
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedConfigurationTriggerGet :  Read the event configuration
    def EventExtendedConfigurationTriggerGet (self):
        command = 'EventExtendedConfigurationTriggerGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedConfigurationActionSet :  Configure one or several actions
    def EventExtendedConfigurationActionSet (self,ExtendedActionName, ActionParameter1, ActionParameter2, ActionParameter3, ActionParameter4):
        command = 'EventExtendedConfigurationActionSet('
        for i in range(len(ExtendedActionName)):
            if (i > 0):
                command += ','
            command += ExtendedActionName[i] + ',' + ActionParameter1[i] + ',' + ActionParameter2[i] + ',' + ActionParameter3[i] + ',' + ActionParameter4[i]
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedConfigurationActionGet :  Read the action configuration
    def EventExtendedConfigurationActionGet (self):
        command = 'EventExtendedConfigurationActionGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedStart :  Launch the last event and action configuration and return an ID
    def EventExtendedStart (self):
        command = 'EventExtendedStart(int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # EventExtendedAllGet :  Read all event and action configurations
    def EventExtendedAllGet (self):
        command = 'EventExtendedAllGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedGet :  Read the event and action configuration defined by ID
    def EventExtendedGet (self,  ID):
        command = 'EventExtendedGet(' + str(ID) + ',char *,char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedRemove :  Remove the event and action configuration defined by ID
    def EventExtendedRemove (self, ID):
        command = 'EventExtendedRemove(' + str(ID) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventExtendedWait :  Wait events from the last event configuration
    def EventExtendedWait (self):
        command = 'EventExtendedWait()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringConfigurationGet : Read different mnemonique type
    def GatheringConfigurationGet (self):
        command = 'GatheringConfigurationGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringConfigurationSet :  Configuration acquisition
    def GatheringConfigurationSet (self,Type):
        command = 'GatheringConfigurationSet('
        for i in range(len(Type)):
            if (i > 0):
                command += ','
            command += Type[i]
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringCurrentNumberGet :  Maximum number of samples and current number during acquisition
    def GatheringCurrentNumberGet (self):
        command = 'GatheringCurrentNumberGet(int *,int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GatheringStopAndSave :  Stop acquisition and save data
    def GatheringStopAndSave (self):
        command = 'GatheringStopAndSave()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringDataAcquire :  Acquire a configured data
    def GatheringDataAcquire (self):
        command = 'GatheringDataAcquire()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]


    # GatheringDataGet :  Get a data line from gathering buffer
    def GatheringDataGet (self, IndexPoint):
        command = 'GatheringDataGet(' + str(IndexPoint) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringDataMultipleLinesGet :  Get multiple data lines from gathering buffer
    def GatheringDataMultipleLinesGet (self, IndexPoint, NumberOfLines):
        command = 'GatheringDataMultipleLinesGet(' + str(IndexPoint) + ',' + str(NumberOfLines) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringReset :  Empty the gathered data in memory to start new gathering from scratch
    def GatheringReset (self):
        command = 'GatheringReset()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringRun :  Start a new gathering
    def GatheringRun (self, DataNumber, Divisor):
        command = 'GatheringRun(' + str(DataNumber) + ',' + str(Divisor) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringRunAppend :  Re-start the stopped gathering to add new data
    def GatheringRunAppend (self):
        command = 'GatheringRunAppend()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringStop :  Stop the data gathering (without saving to file)
    def GatheringStop (self):
        command = 'GatheringStop()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExternalConfigurationSet :  Configuration acquisition
    def GatheringExternalConfigurationSet (self,Type):
        command = 'GatheringExternalConfigurationSet('
        for i in range(len(Type)):
            if (i > 0):
                command += ','
            command += Type[i]
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExternalConfigurationGet :  Read different mnemonique type
    def GatheringExternalConfigurationGet (self):
        command = 'GatheringExternalConfigurationGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExternalCurrentNumberGet :  Maximum number of samples and current number during acquisition
    def GatheringExternalCurrentNumberGet (self):
        command = 'GatheringExternalCurrentNumberGet(int *,int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GatheringExternalDataGet :  Get a data line from external gathering buffer
    def GatheringExternalDataGet (self, IndexPoint):
        command = 'GatheringExternalDataGet(' + str(IndexPoint) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExternalStopAndSave :  Stop acquisition and save data
    def GatheringExternalStopAndSave (self):
        command = 'GatheringExternalStopAndSave()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GlobalArrayGet :  Get global array value
    def GlobalArrayGet (self,  Number):
        command = 'GlobalArrayGet(' + str(Number) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GlobalArraySet :  Set global array value
    def GlobalArraySet (self, Number, ValueString):
        command = 'GlobalArraySet(' + str(Number) + ',' + ValueString + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # DoubleGlobalArrayGet :  Get double global array value
    def DoubleGlobalArrayGet (self, Number):
        command = 'DoubleGlobalArrayGet(' + str(Number) + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # DoubleGlobalArraySet :  Set double global array value
    def DoubleGlobalArraySet (self, Number, DoubleValue):
        command = 'DoubleGlobalArraySet(' + str(Number) + ',' + str(DoubleValue) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GPIOAnalogGet :  Read analog input or analog output for one or few input
    def GPIOAnalogGet (self, GPIOName):
#        command = 'GPIOAnalogGet('
#        for i in range(len(GPIOName)):
#            if (i > 0):
#                command += ','
#            command += GPIOName[i] + ',' + 'double *'
#        command += ')'
        command = 'GPIOAnalogGet(' + GPIOName + ',' + 'double *)'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

#        i, j, retList = 0, 0, [error]
#        for paramNb in range(len(GPIOName)):
#            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
#                j += 1
#            retList.append(eval(returnedString[i:i+j]))
#            i, j = i+j+1, 0

        return [error,float(returnedString)]

    # GPIOAnalogSet :  Set analog output for one or few output
    def GPIOAnalogSet (self, GPIOName, AnalogOutputValue):
        command = 'GPIOAnalogSet(' + GPIOName + ',' + str(AnalogOutputValue) + ')'
#        for i in range(len(GPIOName)):
#            if (i > 0):
#                command += ','
#            command += GPIOName[i] + ',' + str(AnalogOutputValue[i])
#        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GPIOAnalogGainGet :  Read analog input gain (1, 2, 4 or 8) for one or few input
    def GPIOAnalogGainGet (self, GPIOName):
        command = 'GPIOAnalogGainGet('
        for i in range(len(GPIOName)):
            if (i > 0):
                command += ','
            command += GPIOName[i] + ',' + 'int *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(len(GPIOName)):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GPIOAnalogGainSet :  Set analog input gain (1, 2, 4 or 8) for one or few input
    def GPIOAnalogGainSet (self, GPIOName, AnalogInputGainValue):
        command = 'GPIOAnalogGainSet('
        for i in range(len(GPIOName)):
            if (i > 0):
                command += ','
            command += GPIOName[i] + ',' + str(AnalogInputGainValue[i])
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GPIODigitalGet :  Read digital output or digital input 
    def GPIODigitalGet (self, GPIOName):
        command = 'GPIODigitalGet(' + GPIOName + ',unsigned short *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # GPIODigitalSet :  Set Digital Output for one or few output TTL
    def GPIODigitalSet (self, GPIOName, Mask, DigitalOutputValue):
        command = 'GPIODigitalSet(' + GPIOName + ',' + str(Mask) + ',' + str(DigitalOutputValue) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupAccelerationSetpointGet :  Return setpoint accelerations
    def GroupAccelerationSetpointGet (self, nbElement):
        command = 'GroupAccelerationSetpointGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupAnalogTrackingModeEnable :  Enable Analog Tracking mode on selected group
    def GroupAnalogTrackingModeEnable (self, Type):
        command = 'GroupAnalogTrackingModeEnable(' + self.groupname + ',' + Type + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupAnalogTrackingModeDisable :  Disable Analog Tracking mode on selected group
    def GroupAnalogTrackingModeDisable (self):
        command = 'GroupAnalogTrackingModeDisable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupCorrectorOutputGet :  Return corrector outputs
    def GroupCorrectorOutputGet (self, nbElement):
        command = 'GroupCorrectorOutputGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupCurrentFollowingErrorGet :  Return current following errors
    def GroupCurrentFollowingErrorGet (self,nbElement):
        command = 'GroupCurrentFollowingErrorGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupHomeSearch :  Start home search sequence
    def GroupHomeSearch (self,groupname):
        command = 'GroupHomeSearch(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupHomeSearchAndRelativeMove :  Start home search sequence and execute a displacement
    def GroupHomeSearchAndRelativeMove (self, TargetDisplacement):
        command = 'GroupHomeSearchAndRelativeMove(' + self.groupname + ','
        for i in range(len(TargetDisplacement)):
            if (i > 0):
                command += ','
            command += str(TargetDisplacement[i])
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupInitialize :  Start the initialization
    def GroupInitialize (self,groupname):
        command = 'GroupInitialize(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupInitializeWithEncoderCalibration :  Start the initialization with encoder calibration
    def GroupInitializeWithEncoderCalibration (self):
        command = 'GroupInitializeWithEncoderCalibration(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupJogParametersSet :  Modify Jog parameters on selected group and activate the continuous move
    def GroupJogParametersSet (self, socketId, Velocity, Acceleration):
        command = 'GroupJogParametersSet(' + self.groupname + ','
        for i in range(len(Velocity)):
            if (i > 0):
                command += ','
            command += str(Velocity[i]) + ',' + str(Acceleration[i])
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupJogParametersGet :  Get Jog parameters on selected group
    def GroupJogParametersGet (self, nbElement):
        command = 'GroupJogParametersGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *' + ',' + 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement*2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupJogCurrentGet :  Get Jog current on selected group
    def GroupJogCurrentGet (self, nbElement):
        command = 'GroupJogCurrentGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *' + ',' + 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement*2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupJogModeEnable :  Enable Jog mode on selected group
    def GroupJogModeEnable (self):
        command = 'GroupJogModeEnable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupJogModeDisable :  Disable Jog mode on selected group
    def GroupJogModeDisable (self):
        command = 'GroupJogModeDisable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupKill :  Kill the group
    def GroupKill (self,name):
        command = 'GroupKill(' + name + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupMoveAbort :  Abort a move
    def GroupMoveAbort (self, groupname):
        command = 'GroupMoveAbort(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupMoveAbsolute :  Do an absolute move; name can be group (e.g, XYZ) or indexed actuator (e.g. XYZ.X)
    def GroupMoveAbsolute (self,name,AbsolutePosition):
        command = 'GroupMoveAbsolute(' + name + ','
        for i in range(len(AbsolutePosition)):
            if (i > 0):
                command += ','
            command += str(AbsolutePosition[i])
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupMoveRelative :  Do a relative move; name can be group (e.g, XYZ) or indexed actuator (e.g. XYZ.X)
    def GroupMoveRelative (self,name,RelativeDisplacement):
        command = 'GroupMoveRelative(' + name + ','
        for i in range(len(RelativeDisplacement)):
            if (i > 0):
                command += ','
            command += str(RelativeDisplacement[i])
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupMotionDisable :  Set Motion disable on selected group
    def GroupMotionDisable (self,groupname):
        command = 'GroupMotionDisable(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupMotionEnable :  Set Motion enable on selected group
    def GroupMotionEnable (self,groupname):
        command = 'GroupMotionEnable(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupPositionCorrectedProfilerGet :  Return corrected profiler positions
    def GroupPositionCorrectedProfilerGet (self, PositionX, PositionY):
        command = 'GroupPositionCorrectedProfilerGet(' + self.groupname + ',' + str(PositionX) + ',' + str(PositionY) + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupPositionCurrentGet :  Return current positions
    def GroupPositionCurrentGet (self, groupname, nbElement):
        command = 'GroupPositionCurrentGet(' + groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupPositionPCORawEncoderGet :  Return PCO raw encoder positions
    def GroupPositionPCORawEncoderGet (self,PositionX, PositionY):
        command = 'GroupPositionPCORawEncoderGet(' + self.groupname + ',' + str(PositionX) + ',' + str(PositionY) + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupPositionSetpointGet :  Return setpoint positions
    def GroupPositionSetpointGet (self, nbElement):
        command = 'GroupPositionSetpointGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupPositionTargetGet :  Return target positions
    def GroupPositionTargetGet (self,nbElement):
        command = 'GroupPositionTargetGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupReferencingActionExecute :  Execute an action in referencing mode
    def GroupReferencingActionExecute (self, PositionerName, ReferencingAction, ReferencingSensor, ReferencingParameter):
        command = 'GroupReferencingActionExecute(' + PositionerName + ',' + ReferencingAction + ',' + ReferencingSensor + ',' + str(ReferencingParameter) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupReferencingStart :  Enter referencing mode
    def GroupReferencingStart (self, groupname):
        command = 'GroupReferencingStart(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupReferencingStop :  Exit referencing mode
    def GroupReferencingStop (self, groupname):
        command = 'GroupReferencingStop(' + groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupStatusGet :  Return group status
    def GroupStatusGet (self,groupname):
        command = 'GroupStatusGet(' + groupname + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # GroupStatusStringGet :  Return the group status string corresponding to the group status code
    def GroupStatusStringGet (self,  GroupStatusCode):
        command = 'GroupStatusStringGet(' + str(GroupStatusCode) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupVelocityCurrentGet :  Return current velocities
    def GroupVelocityCurrentGet (self,nbElement):
        command = 'GroupVelocityCurrentGet(' + self.groupname + ','
        for i in range(nbElement):
            if (i > 0):
                command += ','
            command += 'double *'
        command += ')'

        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(nbElement):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # KillAll :  Put all groups in 'Not initialized' state
    def KillAll (self):
        command = 'KillAll()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerAnalogTrackingPositionParametersGet :  Read dynamic parameters for one axe of a group for a future analog tracking position
    def PositionerAnalogTrackingPositionParametersGet (self, PositionerName):
        command = 'PositionerAnalogTrackingPositionParametersGet(' + PositionerName + ',char *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerAnalogTrackingPositionParametersSet :  Update dynamic parameters for one axe of a group for a future analog tracking position
    def PositionerAnalogTrackingPositionParametersSet (self, PositionerName, GPIOName, Offset, Scale, Velocity, Acceleration):
        command = 'PositionerAnalogTrackingPositionParametersSet(' + PositionerName + ',' + GPIOName + ',' + str(Offset) + ',' + str(Scale) + ',' + str(Velocity) + ',' + str(Acceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerAnalogTrackingVelocityParametersGet :  Read dynamic parameters for one axe of a group for a future analog tracking velocity
    def PositionerAnalogTrackingVelocityParametersGet (self, PositionerName):
        command = 'PositionerAnalogTrackingVelocityParametersGet(' + PositionerName + ',char *,double *,double *,double *,int *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(6):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerAnalogTrackingVelocityParametersSet :  Update dynamic parameters for one axe of a group for a future analog tracking velocity
    def PositionerAnalogTrackingVelocityParametersSet (self, PositionerName, GPIOName, Offset, Scale, DeadBandThreshold, Order, Velocity, Acceleration):
        command = 'PositionerAnalogTrackingVelocityParametersSet(' + PositionerName + ',' + GPIOName + ',' + str(Offset) + ',' + str(Scale) + ',' + str(DeadBandThreshold) + ',' + str(Order) + ',' + str(Velocity) + ',' + str(Acceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerBacklashGet :  Read backlash value and status
    def PositionerBacklashGet (self, PositionerName):
        command = 'PositionerBacklashGet(' + PositionerName + ',double *,char *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerBacklashSet :  Set backlash value
    def PositionerBacklashSet (self, PositionerName, BacklashValue):
        command = 'PositionerBacklashSet(' + PositionerName + ',' + str(BacklashValue) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerBacklashEnable :  Enable the backlash
    def PositionerBacklashEnable (self, PositionerName):
        command = 'PositionerBacklashEnable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]


    # PositionerBacklashDisable :  Disable the backlash
    def PositionerBacklashDisable (self, PositionerName):
        command = 'PositionerBacklashDisable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorNotchFiltersSet :  Update filters parameters 
    def PositionerCorrectorNotchFiltersSet (self, PositionerName, NotchFrequency1, NotchBandwith1, NotchGain1, NotchFrequency2, NotchBandwith2, NotchGain2):
        command = 'PositionerCorrectorNotchFiltersSet(' + PositionerName + ',' + str(NotchFrequency1) + ',' + str(NotchBandwith1) + ',' + str(NotchGain1) + ',' + str(NotchFrequency2) + ',' + str(NotchBandwith2) + ',' + str(NotchGain2) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorNotchFiltersGet :  Read filters parameters 
    def PositionerCorrectorNotchFiltersGet (self, PositionerName):
        command = 'PositionerCorrectorNotchFiltersGet(' + PositionerName + ',double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(6):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCorrectorPIDFFAccelerationSet :  Update corrector parameters
    def PositionerCorrectorPIDFFAccelerationSet (self,  PositionerName, ClosedLoopStatus, KP, KI, KD, KS, IntegrationTime, DerivativeFilterCutOffFrequency, GKP, GKI, GKD, KForm, FeedForwardGainAcceleration):
        command = 'PositionerCorrectorPIDFFAccelerationSet(' + PositionerName + ',' + str(ClosedLoopStatus) + ',' + str(KP) + ',' + str(KI) + ',' + str(KD) + ',' + str(KS) + ',' + str(IntegrationTime) + ',' + str(DerivativeFilterCutOffFrequency) + ',' + str(GKP) + ',' + str(GKI) + ',' + str(GKD) + ',' + str(KForm) + ',' + str(FeedForwardGainAcceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorPIDFFAccelerationGet :  Read corrector parameters
    def PositionerCorrectorPIDFFAccelerationGet (self, PositionerName):
        command = 'PositionerCorrectorPIDFFAccelerationGet(' + PositionerName + ',bool *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(12):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCorrectorPIDFFVelocitySet :  Update corrector parameters
    def PositionerCorrectorPIDFFVelocitySet (self, PositionerName, ClosedLoopStatus, KP, KI, KD, KS, IntegrationTime, DerivativeFilterCutOffFrequency, GKP, GKI, GKD, KForm, FeedForwardGainVelocity):
        command = 'PositionerCorrectorPIDFFVelocitySet(' + PositionerName + ',' + str(ClosedLoopStatus) + ',' + str(KP) + ',' + str(KI) + ',' + str(KD) + ',' + str(KS) + ',' + str(IntegrationTime) + ',' + str(DerivativeFilterCutOffFrequency) + ',' + str(GKP) + ',' + str(GKI) + ',' + str(GKD) + ',' + str(KForm) + ',' + str(FeedForwardGainVelocity) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorPIDFFVelocityGet :  Read corrector parameters
    def PositionerCorrectorPIDFFVelocityGet (self, PositionerName):
        command = 'PositionerCorrectorPIDFFVelocityGet(' + PositionerName + ',bool *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(12):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCorrectorPIDDualFFVoltageSet :  Update corrector parameters
    def PositionerCorrectorPIDDualFFVoltageSet (self,  PositionerName, ClosedLoopStatus, KP, KI, KD, KS, IntegrationTime, DerivativeFilterCutOffFrequency, GKP, GKI, GKD, KForm, FeedForwardGainVelocity, FeedForwardGainAcceleration, Friction):

        command = 'PositionerCorrectorPIDDualFFVoltageSet(' + PositionerName + ',' + str(ClosedLoopStatus) + ',' + str(KP) + ',' + str(KI) + ',' + str(KD) + ',' + str(KS) + ',' + str(IntegrationTime) + ',' + str(DerivativeFilterCutOffFrequency) + ',' + str(GKP) + ',' + str(GKI) + ',' + str(GKD) + ',' + str(KForm) + ',' + str(FeedForwardGainVelocity) + ',' + str(FeedForwardGainAcceleration) + ',' + str(Friction) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorPIDDualFFVoltageGet :  Read corrector parameters
    def PositionerCorrectorPIDDualFFVoltageGet (self, PositionerName):
        command = 'PositionerCorrectorPIDDualFFVoltageGet(' + PositionerName + ',bool *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(14):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCorrectorPIPositionSet :  Update corrector parameters
    def PositionerCorrectorPIPositionSet (self, PositionerName, ClosedLoopStatus, KP, KI, IntegrationTime):
        command = 'PositionerCorrectorPIPositionSet(' + PositionerName + ',' + str(ClosedLoopStatus) + ',' + str(KP) + ',' + str(KI) + ',' + str(IntegrationTime) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorPIPositionGet :  Read corrector parameters
    def PositionerCorrectorPIPositionGet (self, PositionerName):
        command = 'PositionerCorrectorPIPositionGet(' + PositionerName + ',bool *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCorrectorTypeGet :  Read corrector type
    def PositionerCorrectorTypeGet (self, PositionerName):
        command = 'PositionerCorrectorTypeGet(' + PositionerName + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCurrentVelocityAccelerationFiltersGet :  Get current velocity and acceleration cutoff frequencies
    def PositionerCurrentVelocityAccelerationFiltersGet (self, PositionerName):
        command = 'PositionerCurrentVelocityAccelerationFiltersGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerCurrentVelocityAccelerationFiltersSet :  Set current velocity and acceleration cutoff frequencies
    def PositionerCurrentVelocityAccelerationFiltersSet (self,PositionerName, CurrentVelocityCutOffFrequency, CurrentAccelerationCutOffFrequency):
        command = 'PositionerCurrentVelocityAccelerationFiltersSet(' + PositionerName + ',' + str(CurrentVelocityCutOffFrequency) + ',' + str(CurrentAccelerationCutOffFrequency) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerDriverFiltersGet :  Get driver filters parameters
    def PositionerDriverFiltersGet (self, PositionerName):
        command = 'PositionerDriverFiltersGet(' + PositionerName + ',double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(5):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerDriverFiltersSet :  Set driver filters parameters
    def PositionerDriverFiltersSet (self, PositionerName, KI, NotchFrequency, NotchBandwidth, NotchGain, LowpassFrequency):
        command = 'PositionerDriverFiltersSet(' + PositionerName + ',' + str(KI) + ',' + str(NotchFrequency) + ',' + str(NotchBandwidth) + ',' + str(NotchGain) + ',' + str(LowpassFrequency) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerDriverPositionOffsetsGet :  Get driver stage and gage position offset
    def PositionerDriverPositionOffsetsGet (self, PositionerName):
        command = 'PositionerDriverPositionOffsetsGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerDriverStatusGet :  Read positioner driver status
    def PositionerDriverStatusGet (self, PositionerName):
        command = 'PositionerDriverStatusGet(' + PositionerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerDriverStatusStringGet :  Return the positioner driver status string corresponding to the positioner error code
    def PositionerDriverStatusStringGet (self, PositionerDriverStatus):
        command = 'PositionerDriverStatusStringGet(' + str(PositionerDriverStatus) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerEncoderAmplitudeValuesGet :  Read analog interpolated encoder amplitude values
    def PositionerEncoderAmplitudeValuesGet (self, PositionerName):
        command = 'PositionerEncoderAmplitudeValuesGet(' + PositionerName + ',double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerEncoderCalibrationParametersGet :  Read analog interpolated encoder calibration parameters
    def PositionerEncoderCalibrationParametersGet (self, PositionerName):
        command = 'PositionerEncoderCalibrationParametersGet(' + PositionerName + ',double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerErrorGet :  Read and clear positioner error code
    def PositionerErrorGet (self, PositionerName):
        command = 'PositionerErrorGet(' + PositionerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerErrorRead :  Read only positioner error code without clear it
    def PositionerErrorRead (self, PositionerName):
        command = 'PositionerErrorRead(' + PositionerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerErrorStringGet :  Return the positioner status string corresponding to the positioner error code
    def PositionerErrorStringGet (self, PositionerErrorCode):
        command = 'PositionerErrorStringGet(' + str(PositionerErrorCode) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerExcitationSignalGet :  Read disturbing signal parameters
    def PositionerExcitationSignalGet (self, PositionerName):
        command = 'PositionerExcitationSignalGet(' + PositionerName + ',int *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerExcitationSignalSet :  Update disturbing signal parameters
    def PositionerExcitationSignalSet (self, PositionerName, Mode, Frequency, Amplitude, Time):
        command = 'PositionerExcitationSignalSet(' + PositionerName + ',' + str(Mode) + ',' + str(Frequency) + ',' + str(Amplitude) + ',' + str(Time) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerExternalLatchPositionGet :  Read external latch position
    def PositionerExternalLatchPositionGet (self, PositionerName):
        command = 'PositionerExternalLatchPositionGet(' + PositionerName + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerHardwareStatusGet :  Read positioner hardware status
    def PositionerHardwareStatusGet (self, PositionerName):
        command = 'PositionerHardwareStatusGet(' + PositionerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerHardwareStatusStringGet :  Return the positioner hardware status string corresponding to the positioner error code
    def PositionerHardwareStatusStringGet (self, PositionerHardwareStatus):
        command = 'PositionerHardwareStatusStringGet(' + str(PositionerHardwareStatus) + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerHardInterpolatorFactorGet :  Get hard interpolator parameters
    def PositionerHardInterpolatorFactorGet (self, PositionerName):
        command = 'PositionerHardInterpolatorFactorGet(' + PositionerName + ',int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerHardInterpolatorFactorSet :  Set hard interpolator parameters
    def PositionerHardInterpolatorFactorSet (self, PositionerName, InterpolationFactor):
        command = 'PositionerHardInterpolatorFactorSet(' + PositionerName + ',' + str(InterpolationFactor) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]


    # PositionerMotionDoneGet :  Read motion done parameters
    def PositionerMotionDoneGet (self, PositionerName):
        command = 'PositionerMotionDoneGet(' + PositionerName + ',double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(5):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerMotionDoneSet :  Update motion done parameters
    def PositionerMotionDoneSet (self,  PositionerName, PositionWindow, VelocityWindow, CheckingTime, MeanPeriod, TimeOut):
        command = 'PositionerMotionDoneSet(' + PositionerName + ',' + str(PositionWindow) + ',' + str(VelocityWindow) + ',' + str(CheckingTime) + ',' + str(MeanPeriod) + ',' + str(TimeOut) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionCompareAquadBAlwaysEnable :  Enable AquadB signal in always mode
    def PositionerPositionCompareAquadBAlwaysEnable (self, PositionerName):
        command = 'PositionerPositionCompareAquadBAlwaysEnable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionCompareAquadBWindowedGet :  Read position compare AquadB windowed parameters
    def PositionerPositionCompareAquadBWindowedGet (self, PositionerName):
        command = 'PositionerPositionCompareAquadBWindowedGet(' + PositionerName + ',double *,double *,bool *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerPositionCompareAquadBWindowedSet :  Set position compare AquadB windowed parameters
    def PositionerPositionCompareAquadBWindowedSet (self, PositionerName, MinimumPosition, MaximumPosition):
        command = 'PositionerPositionCompareAquadBWindowedSet(' + PositionerName + ',' + str(MinimumPosition) + ',' + str(MaximumPosition) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionCompareGet :  Read position compare parameters
    def PositionerPositionCompareGet (self, PositionerName):
        command = 'PositionerPositionCompareGet(' + PositionerName + ',double *,double *,double *,bool *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerPositionCompareSet :  Set position compare parameters
    def PositionerPositionCompareSet (self, PositionerName, MinimumPosition, MaximumPosition, PositionStep):
        command = 'PositionerPositionCompareSet(' + PositionerName + ',' + str(MinimumPosition) + ',' + str(MaximumPosition) + ',' + str(PositionStep) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionCompareEnable :  Enable position compare
    def PositionerPositionCompareEnable (self, PositionerName):
        command = 'PositionerPositionCompareEnable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionCompareDisable :  Disable position compare
    def PositionerPositionCompareDisable (self, PositionerName):
        command = 'PositionerPositionCompareDisable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerPositionComparePulseParametersGet :  Get position compare PCO pulse parameters
    def PositionerPositionComparePulseParametersGet (self, PositionerName):
        command = 'PositionerPositionComparePulseParametersGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerPositionComparePulseParametersSet :  Set position compare PCO pulse parameters
    def PositionerPositionComparePulseParametersSet (self,PositionerName, PCOPulseWidth, EncoderSettlingTime):
        command = 'PositionerPositionComparePulseParametersSet(' + PositionerName + ',' + str(PCOPulseWidth) + ',' + str(EncoderSettlingTime) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerRawEncoderPositionGet :  Get the raw encoder position
    def PositionerRawEncoderPositionGet (self,PositionerName, UserEncoderPosition):
        command = 'PositionerRawEncoderPositionGet(' + PositionerName + ',' + str(UserEncoderPosition) + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionersEncoderIndexDifferenceGet :  Return the difference between index of primary axis and secondary axis (only after homesearch)
    def PositionersEncoderIndexDifferenceGet (self, PositionerName):
        command = 'PositionersEncoderIndexDifferenceGet(' + PositionerName + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerSGammaExactVelocityAjustedDisplacementGet :  Return adjusted displacement to get exact velocity
    def PositionerSGammaExactVelocityAjustedDisplacementGet (self, PositionerName, DesiredDisplacement):
        command = 'PositionerSGammaExactVelocityAjustedDisplacementGet(' + PositionerName + ',' + str(DesiredDisplacement) + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # PositionerSGammaParametersGet :  Read dynamic parameters for one axe of a group for a future displacement 
    def PositionerSGammaParametersGet (self, PositionerName):
        command = 'PositionerSGammaParametersGet(' + PositionerName + ',double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerSGammaParametersSet :  Update dynamic parameters for one axe of a group for a future displacement
    def PositionerSGammaParametersSet (self, PositionerName, Velocity, Acceleration, MinimumTjerkTime, MaximumTjerkTime):
        command = 'PositionerSGammaParametersSet(' + PositionerName + ',' + str(Velocity) + ',' + str(Acceleration) + ',' + str(MinimumTjerkTime) + ',' + str(MaximumTjerkTime) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerSGammaPreviousMotionTimesGet :  Read SettingTime and SettlingTime
    def PositionerSGammaPreviousMotionTimesGet (self, PositionerName):
        command = 'PositionerSGammaPreviousMotionTimesGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerStageParameterGet :  Return the stage parameter
    def PositionerStageParameterGet (self, PositionerName, ParameterName):
        command = 'PositionerStageParameterGet(' + PositionerName + ',' + ParameterName + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerStageParameterSet :  Save the stage parameter
    def PositionerStageParameterSet (self, PositionerName, ParameterName, ParameterValue):
        command = 'PositionerStageParameterSet(' + PositionerName + ',' + ParameterName + ',' + ParameterValue + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerTimeFlasherGet :  Read time flasher parameters
    def PositionerTimeFlasherGet (self, PositionerName):
        command = 'PositionerTimeFlasherGet(' + PositionerName + ',double *,double *,double *,bool *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerTimeFlasherSet :  Set time flasher parameters
    def PositionerTimeFlasherSet (self, PositionerName, MinimumPosition, MaximumPosition, TimeInterval):
        command = 'PositionerTimeFlasherSet(' + PositionerName + ',' + str(MinimumPosition) + ',' + str(MaximumPosition) + ',' + str(TimeInterval) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerTimeFlasherEnable :  Enable time flasher
    def PositionerTimeFlasherEnable (self, PositionerName):
        command = 'PositionerTimeFlasherEnable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerTimeFlasherDisable :  Disable time flasher
    def PositionerTimeFlasherDisable (self, PositionerName):
        command = 'PositionerTimeFlasherDisable(' + PositionerName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerUserTravelLimitsGet :  Read UserMinimumTarget and UserMaximumTarget
    def PositionerUserTravelLimitsGet (self, PositionerName):
        command = 'PositionerUserTravelLimitsGet(' + PositionerName + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerUserTravelLimitsSet :  Update UserMinimumTarget and UserMaximumTarget
    def PositionerUserTravelLimitsSet (self, PositionerName, UserMinimumTarget, UserMaximumTarget):
        command = 'PositionerUserTravelLimitsSet(' + PositionerName + ',' + str(UserMinimumTarget) + ',' + str(UserMaximumTarget) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerDACOffsetGet :  Get DAC offsets
    def PositionerDACOffsetGet (self, PositionerName):
        command = 'PositionerDACOffsetGet(' + PositionerName + ',short *,short *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerDACOffsetSet :  Set DAC offsets
    def PositionerDACOffsetSet (self,PositionerName, DACOffset1, DACOffset2):
        command = 'PositionerDACOffsetSet(' + PositionerName + ',' + str(DACOffset1) + ',' + str(DACOffset2) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerDACOffsetDualGet :  Get dual DAC offsets
    def PositionerDACOffsetDualGet (self, PositionerName):
        command = 'PositionerDACOffsetDualGet(' + PositionerName + ',short *,short *,short *,short *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerDACOffsetDualSet :  Set dual DAC offsets
    def PositionerDACOffsetDualSet (self,  PositionerName, PrimaryDACOffset1, PrimaryDACOffset2, SecondaryDACOffset1, SecondaryDACOffset2):
        command = 'PositionerDACOffsetDualSet(' + PositionerName + ',' + str(PrimaryDACOffset1) + ',' + str(PrimaryDACOffset2) + ',' + str(SecondaryDACOffset1) + ',' + str(SecondaryDACOffset2) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerCorrectorAutoTuning :  Astrom&Hagglund based auto-tuning
    def PositionerCorrectorAutoTuning (self,PositionerName, TuningMode):
        command = 'PositionerCorrectorAutoTuning(' + PositionerName + ',' + str(TuningMode) + ',double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # PositionerAccelerationAutoScaling :  Astrom&Hagglund based auto-scaling
    def PositionerAccelerationAutoScaling (self, PositionerName):
        command = 'PositionerAccelerationAutoScaling(' + PositionerName + ',double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # MultipleAxesPVTVerification :  Multiple axes PVT trajectory verification
    def MultipleAxesPVTVerification (self, TrajectoryFileName):
        command = 'MultipleAxesPVTVerification(' + self.groupname + ',' + TrajectoryFileName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # MultipleAxesPVTVerificationResultGet :  Multiple axes PVT trajectory verification result get
    def MultipleAxesPVTVerificationResultGet (self, PositionerName):
        command = 'MultipleAxesPVTVerificationResultGet(' + PositionerName + ',char *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # MultipleAxesPVTExecution :  Multiple axes PVT trajectory execution
    def MultipleAxesPVTExecution (self, TrajectoryFileName, ExecutionNumber):
        command = 'MultipleAxesPVTExecution(' + self.groupname + ',' + TrajectoryFileName + ',' + str(ExecutionNumber) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # MultipleAxesPVTParametersGet :  Multiple axes PVT trajectory get parameters
    def MultipleAxesPVTParametersGet (self):
        command = 'MultipleAxesPVTParametersGet(' + self.groupname + ',char *,int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # MultipleAxesPVTPulseOutputSet :  Configure pulse output on trajectory
    def MultipleAxesPVTPulseOutputSet (self, StartElement, EndElement, TimeInterval):
        command = 'MultipleAxesPVTPulseOutputSet(' + self.groupname + ',' + str(StartElement) + ',' + str(EndElement) + ',' + str(TimeInterval) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # MultipleAxesPVTPulseOutputGet :  Get pulse output on trajectory configuration
    def MultipleAxesPVTPulseOutputGet (self):
        command = 'MultipleAxesPVTPulseOutputGet(' + self.groupname + ',int *,int *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # SingleAxisSlaveModeEnable :  Enable the slave mode
    def SingleAxisSlaveModeEnable (self):
        command = 'SingleAxisSlaveModeEnable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SingleAxisSlaveModeDisable :  Disable the slave mode
    def SingleAxisSlaveModeDisable (self):
        command = 'SingleAxisSlaveModeDisable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SingleAxisSlaveParametersSet :  Set slave parameters
    def SingleAxisSlaveParametersSet (self, PositionerName, Ratio):
        command = 'SingleAxisSlaveParametersSet(' + self.groupname + ',' + PositionerName + ',' + str(Ratio) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SingleAxisSlaveParametersGet :  Get slave parameters
    def SingleAxisSlaveParametersGet (self):
        command = 'SingleAxisSlaveParametersGet(' + self.groupname + ',char *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # SpindleSlaveModeEnable :  Enable the slave mode
    def SpindleSlaveModeEnable (self):
        command = 'SpindleSlaveModeEnable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SpindleSlaveModeDisable :  Disable the slave mode
    def SpindleSlaveModeDisable (self):
        command = 'SpindleSlaveModeDisable(' + self.groupname + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SpindleSlaveParametersSet :  Set slave parameters
    def SpindleSlaveParametersSet (self, PositionerName, Ratio):
        command = 'SpindleSlaveParametersSet(' + self.groupname + ',' + PositionerName + ',' + str(Ratio) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SpindleSlaveParametersGet :  Get slave parameters
    def SpindleSlaveParametersGet (self):
        command = 'SpindleSlaveParametersGet(' + self.groupname + ',char *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))

        return retList

    # GroupSpinParametersSet :  Modify Spin parameters on selected group and activate the continuous move
    def GroupSpinParametersSet (self, Velocity, Acceleration):
        command = 'GroupSpinParametersSet(' + self.groupname + ',' + str(Velocity) + ',' + str(Acceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupSpinParametersGet :  Get Spin parameters on selected group
    def GroupSpinParametersGet (self):
        command = 'GroupSpinParametersGet(' + self.groupname + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupSpinCurrentGet :  Get Spin current on selected group
    def GroupSpinCurrentGet (self):
        command = 'GroupSpinCurrentGet(' + self.groupname + ',double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # GroupSpinModeStop :  Stop Spin mode on selected group with specified acceleration
    def GroupSpinModeStop (self, Acceleration):
        command = 'GroupSpinModeStop(' + self.groupname + ',' + str(Acceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYLineArcVerification :  XY trajectory verification
    def XYLineArcVerification (self, TrajectoryFileName):
        command = 'XYLineArcVerification(' + self.groupname + ',' + TrajectoryFileName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYLineArcVerificationResultGet :  XY trajectory verification result get
    def XYLineArcVerificationResultGet (self, PositionerName):
        command = 'XYLineArcVerificationResultGet(' + PositionerName + ',char *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # XYLineArcExecution :  XY trajectory execution
    def XYLineArcExecution (self, socketId, TrajectoryFileName, Velocity, Acceleration, ExecutionNumber):
        command = 'XYLineArcExecution(' + GroupName + ',' + TrajectoryFileName + ',' + str(Velocity) + ',' + str(Acceleration) + ',' + str(ExecutionNumber) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYLineArcParametersGet :  XY trajectory get parameters
    def XYLineArcParametersGet (self):
        command = 'XYLineArcParametersGet(' + self.groupname + ',char *,double *,double *,int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # XYLineArcPulseOutputSet :  Configure pulse output on trajectory
    def XYLineArcPulseOutputSet (self, StartLength, EndLength, PathLengthInterval):
        command = 'XYLineArcPulseOutputSet(' + self.groupname + ',' + str(StartLength) + ',' + str(EndLength) + ',' + str(PathLengthInterval) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYLineArcPulseOutputGet :  Get pulse output on trajectory configuration
    def XYLineArcPulseOutputGet (self):
        command = 'XYLineArcPulseOutputGet(' + self.groupname + ',double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # XYZGroupPositionCorrectedProfilerGet :  Return corrected profiler positions
    def XYZGroupPositionCorrectedProfilerGet (self, PositionX, PositionY, PositionZ):
        command = 'XYZGroupPositionCorrectedProfilerGet(' + self.groupname + ',' + str(PositionX) + ',' + str(PositionY) + ',' + str(PositionZ) + ',double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # XYZSplineVerification :  XYZ trajectory verifivation
    def XYZSplineVerification (self, TrajectoryFileName):
        command = 'XYZSplineVerification(' + self.groupname + ',' + TrajectoryFileName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYZSplineVerificationResultGet :  XYZ trajectory verification result get
    def XYZSplineVerificationResultGet (self, PositionerName):
        command = 'XYZSplineVerificationResultGet(' + PositionerName + ',char *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # XYZSplineExecution :  XYZ trajectory execution
    def XYZSplineExecution (self,TrajectoryFileName, Velocity, Acceleration):
        command = 'XYZSplineExecution(' + self.groupname + ',' + TrajectoryFileName + ',' + str(Velocity) + ',' + str(Acceleration) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # XYZSplineParametersGet :  XYZ trajectory get parameters
    def XYZSplineParametersGet (self):
        command = 'XYZSplineParametersGet(' + self.groupname + ',char *,double *,double *,int *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(3):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # OptionalModuleExecute :  Execute an optional module
    def OptionalModuleExecute (self, ModuleFileName, TaskName):
        command = 'OptionalModuleExecute(' + ModuleFileName + ',' + TaskName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # OptionalModuleKill :  Kill an optional module
    def OptionalModuleKill (self,  TaskName):
        command = 'OptionalModuleKill(' + TaskName + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EEPROMCIESet :  Set CIE EEPROM reference string
    def EEPROMCIESet (self, CardNumber, ReferenceString):
        command = 'EEPROMCIESet(' + str(CardNumber) + ',' + ReferenceString + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EEPROMDACOffsetCIESet :  Set CIE DAC offsets
    def EEPROMDACOffsetCIESet (self, PlugNumber, DAC1Offset, DAC2Offset):
        command = 'EEPROMDACOffsetCIESet(' + str(PlugNumber) + ',' + str(DAC1Offset) + ',' + str(DAC2Offset) + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EEPROMDriverSet :  Set Driver EEPROM reference string
    def EEPROMDriverSet (self, PlugNumber, ReferenceString):
        command = 'EEPROMDriverSet(' + str(PlugNumber) + ',' + ReferenceString + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EEPROMINTSet :  Set INT EEPROM reference string
    def EEPROMINTSet (self, CardNumber, ReferenceString):
        command = 'EEPROMINTSet(' + str(CardNumber) + ',' + ReferenceString + ')'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # CPUCoreAndBoardSupplyVoltagesGet :  Get power informations
    def CPUCoreAndBoardSupplyVoltagesGet (self):
        command = 'CPUCoreAndBoardSupplyVoltagesGet(double *,double *,double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(8):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # CPUTemperatureAndFanSpeedGet :  Get CPU temperature and fan speed
    def CPUTemperatureAndFanSpeedGet (self):
        command = 'CPUTemperatureAndFanSpeedGet(double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # ActionListGet :  Action list
    def ActionListGet (self):
        command = 'ActionListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ActionExtendedListGet :  Action extended list
    def ActionExtendedListGet (self):
        command = 'ActionExtendedListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # APIExtendedListGet :  API method list
    def APIExtendedListGet (self):
        command = 'APIExtendedListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # APIListGet :  API method list without extended API
    def APIListGet (self):
        command = 'APIListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ControllerStatusListGet :  Controller status list
    def ControllerStatusListGet (self):
        command = 'ControllerStatusListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ErrorListGet :  Error list
    def ErrorListGet (self):
        command = 'ErrorListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # EventListGet :  General event list
    def EventListGet (self):
        command = 'EventListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringListGet :  Gathering type list
    def GatheringListGet (self):
        command = 'GatheringListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExtendedListGet :  Gathering type extended list
    def GatheringExtendedListGet (self):
        command = 'GatheringExtendedListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringExternalListGet :  External Gathering type list
    def GatheringExternalListGet (self):
        command = 'GatheringExternalListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GroupStatusListGet :  Group status list
    def GroupStatusListGet (self):
        command = 'GroupStatusListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # HardwareInternalListGet :  Internal hardware list
    def HardwareInternalListGet (self):
        command = 'HardwareInternalListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # HardwareDriverAndStageGet :  Smart hardware
    def HardwareDriverAndStageGet (self, PlugNumber):
        command = 'HardwareDriverAndStageGet(' + str(PlugNumber) + ',char *,char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ObjectsListGet :  Group name and positioner name
    def ObjectsListGet (self):
        command = 'ObjectsListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerErrorListGet :  Positioner error list
    def PositionerErrorListGet (self):
        command = 'PositionerErrorListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerHardwareStatusListGet :  Positioner hardware status list
    def PositionerHardwareStatusListGet (self):
        command = 'PositionerHardwareStatusListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # PositionerDriverStatusListGet :  Positioner driver status list
    def PositionerDriverStatusListGet (self):
        command = 'PositionerDriverStatusListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ReferencingActionListGet :  Get referencing action list
    def ReferencingActionListGet (self):
        command = 'ReferencingActionListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # ReferencingSensorListGet :  Get referencing sensor list
    def ReferencingSensorListGet (self):
        command = 'ReferencingSensorListGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # GatheringUserDatasGet :  Return user data values
    def GatheringUserDatasGet (self):
        command = 'GatheringUserDatasGet(double *,double *,double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(8):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # ControllerMotionKernelPeriodMinMaxGet :  Get controller motion kernel min/max periods
    def ControllerMotionKernelPeriodMinMaxGet (self):
        command = 'ControllerMotionKernelPeriodMinMaxGet(double *,double *,double *,double *,double *,double *)'
        [error, returnedString] = self.sendAndReceive(command)
        if (error != 0):
            return [error, returnedString]

        i, j, retList = 0, 0, [error]
        for paramNb in range(6):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0

        return retList

    # ControllerMotionKernelPeriodMinMaxReset :  Reset controller motion kernel min/max periods
    def ControllerMotionKernelPeriodMinMaxReset (self):
        command = 'ControllerMotionKernelPeriodMinMaxReset()'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # SocketsStatusGet :  Get sockets current status
    def SocketsStatusGet (self, socketId):
        command = 'SocketsStatusGet(char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

    # TestTCP :  Test TCP/IP transfert
    def TestTCP (self, socketId, InputString):
        command = 'TestTCP(' + InputString + ',char *)'
        [error, returnedString] = self.sendAndReceive(command)
        return [error, returnedString]

        
    
