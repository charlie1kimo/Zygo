"""
Provides python interface tags for XPS motors.

All Motor objects must have the following attributes defined in the init function:



All motor objects must have the following functions defined:
    set_velocity(self, speed)   Sets the motor speed, acceleration, and jerk.

"""
import os
import socket
import sys
import time    #SH added for sleep (see line 1730)


class CommonXPSFunctions(object):
    """The functions in this super class are used by multiple XPS motor types.
    This function assumes a single positioner group.  Or a single axis in a 
    multi-axis group.  It has partial support for Multi-axis positioner groups, 
    but will need to overwrite some functions.
    
    The following functions are currently restricted to a single axis:
        move
        move_abs
        check_position
        load_position
        save_position
        get_position
        update_position
        reference_to_position*
        get_motion_control_parameters
        get_max_velocity_and_acceleration
        reset_position
        set_position
        
    The following functions will function correctly with multiple axes:
        _open_save_file
        motor_on*
        motor_off*
        stop*
        Origin*
    
    *  These functions will affect an entire group when executed for any motor in the group.
    """
    def __init__(self,xps_controller,actuatorname,speed, name="", label = ''):
        """
        This method creates an instance of a M_VP_5ZA actuator and also initializes the actuators to their home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the full actuatorname the Newport setup software gives to the M_VP_5ZA actuator instantiated with this class
                            which has format GROUPNAME.POSTIONERNAME
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        #Define motorunits, if not already defined by subclass
        if not hasattr(self, 'motorunits'):
            self.motorunits = 1.0 #Motor units are the conversion factor for xps motors in which the default software units do not match the internal motor units.
                                  #They are applied to all position / speed calls to the xps controller for that motor. * on send, / on recieve
        
        #Copy input variables to object variables
        self.label = label
        self.controller = xps_controller
        self.groupname = actuatorname.split('.')[0]                                                 
        self.actuatorname = actuatorname
        self.name = name
        [error,returnString,vel] = self.set_velocity(speed)
        self.speed = vel

        #Determine the xps group size
        self.groupsize = 0
        self.groupnames = []
        xpsobjects = self.controller.ObjectsListGet()[1].split(';')
        for xpsobject in xpsobjects:
            if xpsobject.find(self.groupname + '.') != -1:
                self.groupsize += 1
                self.groupnames.append(str(xpsobject))
        
        #Set Internal movement variable
        self.offset = 0.0
        
        #Detect if the motor is already homed, and get current position if it is.
        self.ishomed = False
        motor_status = self.controller.GroupStatusGet(self.groupname)
        if motor_status[0] == 0:
            motor_status_string = self.controller.GroupStatusStringGet(motor_status[1])[1].upper()
            if motor_status_string.find('READY STATE') != -1 or motor_status[1] == 20:
                self.ishomed = True
                self.position = self.controller.GroupPositionCurrentGet(self.actuatorname,1)[1]/self.motorunits
            if motor_status_string.find('READY STATE') != -1:
                self.motor_off()        


    def move(self,relative_displacement,units=None):
        """
        Move this actuator in the relative mode.  Before the motion is commanded, it is checked to see if 
        the final position is within the range of the actuator's travel limits.
        Inputs:
            relative_displacement:  the amount of displacement requested from current position.
            units:  an optionally provided unit that qualifies relative_displacement.  Default is deg.
        Outputs:
            TRUE if the commanded motion was performed.
            FALSE if the commanded motion was not performed.
        """
        if not units:
            units = self.internal_units        
        amount = self.unitvalues[units]*relative_displacement
        if self.check_position(amount):
            self.motor_on()   # ????
            [error, returnString] = self.controller.GroupMoveRelative(self.actuatorname,[amount*self.motorunits])
            motor_status = 44
            while motor_status == 44:
                time.sleep(0.5)
                motor_status = self.controller.GroupStatusGet(self.groupname)[1]
                #print motor_status
            self.motor_off()
            if (error != 0):
                print 'Movement Error, ', self.label
                return False
              
            if hasattr(self, 'position_sensor') and self.position_sensor and self.report_position_sensor:   #Any function that has position_sensor should also have report_position_sensor and use_position_sensor_feedback, and self.loop_count = 1    
                current_position = self.position_sensor.read_position(1)
                delta = (self.position + amount) - current_position  # difference between desired position and current position as read from cap gauge
                self.position = current_position
                if self.use_position_sensor_feedback:
                    if np.abs(delta) > self.CAP_SENSOR_FEEDBACK_POSITION_TOLERANCE:
                        self.loop_convergence_result = False
                        if self.loop_count < self.CAP_SENSOR_FEEDBACK_CONVERGENCE_TRIES: 
                            self.loop_count += 1
                            self.move(delta,"mm")                        
                    else:
                        self.loop_convergence_result = True
                else:
                    self.loop_convergence_result = True
                
                self.loop_count = 1     #This must come after the secondary movement call, but before the return
                self.save_position()
                return self.loop_convergence_result
            else:
                self.update_position()              # self.position stored in internal units
                time.sleep(0.1)  #Initial reading was not maching controller.  Stabilization time after move of read wait read was needed for matching values.
                self.update_position() 
                self.save_position()
                return True            
        else:
            return False

    def move_abs(self,absolute_position,units=None):
        """
        Move this actuator in the absolute mode.  Before the motion is commanded, it is checked to see if 
        the final position is within the range of the actuator's travel limits.
        Inputs:
            absolute_displacement:  the position desired for the actuator.
            units:  an optionally provided unit that qualifies absolute_position.  Default is deg.
        Outputs:
            TRUE if the commanded motion was performed.
            FALSE if the commanded motion was not performed.
        """            
        if not units:
            units = self.internal_units
        amount = absolute_position*self.unitvalues[units] - self.position
        return self.move(amount,units=units)            

         
    def check_position(self,amount, units = None):
        """
        This method checks to see if the resulting motion will be within the range of the  actuator and the
        position ensor if present.  All limit values are relative to the positioners home position, and 
        given in the positioners internal units.
        Inputs:
             amount: value of proposed relative motion in internal units.
        Output:
             TRUE if commanded move will be within travel range.
             FALSE if commanded move will exceed the range of the 5ZA.
        """
        checkamount = self.position + amount
        
        if not self.ishomed:
            return False
        if hasattr(self, 'position_sensor') and self.position_sensor:    #Actuator is connected to a position sensor.
            if( (checkamount>self.MAX_SENSOR_DISPLACEMENT) | (checkamount<self.MIN_SENSOR_DISPLACEMENT) ):   # movement will exceed sensor position range.
                return False
        if ( (checkamount>self.MAX_POSITION) | (checkamount<self.MIN_POSITION) ):
            return False    # commanded motion will exceed positioner travel range
        
        return True    # commanded motion is valid

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

    def motor_on(self):
        """
        Turns ON the motor and restarts the corrector servo loop for the URS150BPP actuator.
        Input:  None
        Output:  None
        """
        [error, returnString] = self.controller.GroupMotionEnable(self.groupname)
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing GroupMotionEnable for " + self.label

    def motor_off(self):
        """
        Turns OFF the motor, stops the corrector servo loop and disables the position compare mode if it's active
           of the URS150BPP rotary actuator.
        Input:  None
        Output:  None
        """
        [error, returnString] = self.controller.GroupMotionDisable(self.groupname)
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing GroupMotionDisable for " + self.label

    def get_position(self,units=None):
        """
        Return current position of the actuator in user requested units.
        Input:  optionally provided units.  Default is in mm or deg depending on the stage type.
        Output: the group position in user specified units.
        """
        if not units:
            units = self.internal_units
        return (self.position + self.offset)/self.unitvalues[units]  


    def update_position(self,units=None):
        """
        Return current position of this URS150BPP actuator in user requested units.
        Input:  optionally provided units.  Default is in mm or deg depending on the stage type.
        Output: the group position in user specified units.
        """
        if not units:
            units = self.internal_units        
        
        if hasattr(self, 'position_sensor') and self.position_sensor and self.report_position_sensor:
            self.position = self.position_sensor.read_position(3)
        else:
            self.position = self.controller.GroupPositionCurrentGet(self.actuatorname,1)[1]/self.motorunits
        
        return (self.position + self.offset)/self.unitvalues[units]         

    def reference_to_position(self, position = None, warning = True, reset = False):
        """Reference motor to the current position.  Will also initialize if in state 0 (power failure).
        If no position is provided it will reference 0.0 to the motor's current position.
        If a position is provided, the positions must be provided for all axes in a group in alphabetical
        order of actuator names. (case sensitive)"""
        def check_allowed_pos(value):
            if ( (value>self.MAX_POSITION) | (value<self.MIN_POSITION) ) :
                raise ValueError, 'New position outside of allowed travel limits:  '+str(self.MIN_POSITION)+' to '+str(self.MAX_POSITION)
        
        
        if reset:
            [error, returnString] = self.controller.GroupKill(self.groupname)
            if (error != 0):
                raise RuntimeError, "Error "+str(error)+" executing GroupKill for " + self.label
        
        motor_status = self.controller.GroupStatusGet(self.groupname)
        if motor_status[1] in [0,2, 7]:    #Power failure 0, emergency stop 2, group kill command 7
            self.controller.GroupInitialize(self.groupname)
            motor_status = self.controller.GroupStatusGet(self.groupname)
        if motor_status[1] == 42:
            self.controller.GroupReferencingStart(self.groupname)
            if position:
                if not warning:
                    check_allowed_pos(float(position))
                    self.controller.GroupReferencingActionExecute(self.actuatorname, "SetPosition", "None", float(position)*self.motorunits)
                    self.add_referenced_axis(self.actuatorname)
                elif self.groupsize == 1 and type(position) in [str, int, float]:
                    check_allowed_pos(float(position))
                    self.controller.GroupReferencingActionExecute(self.actuatorname, "SetPosition", "None", float(position)*self.motorunits)
                    self.add_referenced_axis(self.actuatorname)
                elif type(position) in [list, tuple] and self.groupsize == len(position):
                    for i in zip(self.groupnames, position):
                        check_allowed_pos(float(i[1]))
                        self.controller.GroupReferencingActionExecute(i[0], "SetPosition", "None", float(i[1])*self.motorunits)
                        self.add_referenced_axis(i[0])
                else:
                    raise Warning, "The number of items in the position input does not match the groupsize."
            self.controller.GroupReferencingStop(self.groupname)
            self.ishomed = True
            self.motor_off()
            self.update_position()
        else:
            raise RuntimeError, "Motor not ready to be referenced"

    def add_referenced_axis(self, axis):
        """ Used with the referencing function to track what axes have been referenced.
        Adds an axis to the trcking file"""
        if os.path.isfile('RefMotor.cfg'):
            f = open('RefMotor.cfg', 'r')
            lines = f.readlines()
            f.close()
            lines.append(axis)                          #Add new axis
        else:
            lines = [axis]
        slines = []
        for i in lines:
            si = i.strip()
            if (not si+'\n' in slines) and si != '':      #Eliminates Duplicates and blank lines.
                slines.append(si+'\n')
        f = open('RefMotor.cfg', 'w')
        for i in slines:
            f.write(i)
        f.close()
    
    def remove_referenced_axis(self, axis):
        """ Used with the referencing function to track what axes have been referenced.
        Removes an axis to the trcking file"""
        if os.path.isfile('RefMotor.cfg'):
            f = open('RefMotor.cfg', 'r')
            lines = f.readlines()
            f.close()
            axis = axis.strip()
            slines = []
            for i in lines:
                si = i.strip()
                if (not si+'\n' in slines) and si != ''and si != axis:        #Eliminates Duplicates, blank lines, and the specified axis
                    slines.append(si+'\n')
            if slines != []:
                f = open('RefMotor.cfg', 'w')
                for i in slines:
                    f.write(i)
                f.close()
            else:
                os.remove('RefMotor.cfg')

    
    def get_motion_control_parameters(self):
        """
        Obtain the maximum velocity, maximum acceleration, minimum jerktime, and maximum jerktime of this
        actuator.
        Inputs:  None
        Output:
           error: returned error code.  error is '0' for no error.
           velocity:  maximum velocity that the actuator can attain.
           acceleration:  maximum acceleration that the actuator can attain.
           minjerktime:  minimum time when derivative of acceleration goes to zero during commanded motion.
           maxjerktime:  maximu time when derivative of acceleration goes to zero during commanded motion.
        """
        [error,velocity,acceleration,minjerktime,maxjerktime] = self.controller.PositionerSGammaParametersGet(self.actuatorname)
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing PositionerSGammaParametersGet for " + self.label
        return [error,velocity/self.motorunits,acceleration/self.motorunits,minjerktime/self.motorunits,maxjerktime/self.motorunits]

    def get_max_velocity_and_acceleration(self):
        """
        Obtain the maximum velocity and acceleration this actuator can attain.
        Inputs: None
        Output:
             error: returned error code.  error is '0' for no error.
             maxvelocity:  maximum velocity an LTA-HL actuator can attain.
             maxacceleration:  maximum acceleration an LTA-HL actuator can attain.
        """
        [error,maxvelocity,maxacceleration] = self.controller.PositionerMaximumVelocityAndAccelerationGet(self.actuatorname)
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing PositionerMaximumVelocityAndAccelerationGet for " + self.label
        return [error,maxvelocity/self.motorunits,maxacceleration/self.motorunits]

    def stop(self):
        """
        terminates motion of actively moving group of actuators
        """
        self.controller.GroupMoveAbort(self.groupname)

    def reset_position(self):
        """
        Resets self.offset to zero so that reported position from using self.get_position reflects the "true" mechanical position of the URS150BPP.
        Inputs:
            None
        Ouputs:
            None
        """
        self.offset = 0.0

    def set_position(self,requested_position,units=None):
        """
        Set the URS150BPP actuator's self.position instance in deg, overriding specified units value. The actuator is 
        not moved.  Instead the instance's internal self.position value is updated.
        Inputs:  
             requested_position:  the absolute value requested to set the instance's internal position amount.
             units:  an optionally provided user amount chosen from the canonical Zygo unitvalues array.  Default is deg.
        Output:
             actuator's self.position in user requested units (deg is default.)
        """
        if not units:
            units = self.internal_units   
            
        self.offset = self.unitvalues[units]*requested_position - self.position
     
    def set_velocity(self,vel, units = None):
        """
        Set the maximum velocity this LTA-HL can attain.  The units are defined in the stages.ini file used
        by the Newport XPS software.  Default is mm/sec.
        The requested velocity is bounds checked against the min/max values of the actuator.  And only the
        velocity is allowed to be set.  The acceleration, and min/max jerktimes are not allowed to be set.
        Inputs:
           velocity:  requested velocity in system defined units/sec.
        Outputs:
           error:  returned error code from XPS controller.  A '0' value means no error
           returnString: XPS returned string that defines operation.  A an empty string ("") is returned upon no error.
           vel:  the velocity value actually set by this method.
        """
        if not units:
            units = self.internal_units           
        
        if vel > self.MAX_VELOCITY:
            vel = self.MAX_VELOCITY
        if vel < 0.001: #smaller values will create an error.
            raise ValueError, str(vel) + " is less than the minimum velocity"
        current = self.controller.PositionerSGammaParametersGet(self.actuatorname)
        [error,returnString] = self.controller.PositionerSGammaParametersSet(self.actuatorname,self.motorunits*vel,current[2],current[3],current[4]) #Convert to controller units for command.
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing PositionerSGammaParametersGet for " + self.label
        self.speed = vel
        return [error,returnString,vel]     
     
    def origin(self):
        """
        This method 1) stops all current motion of the  actuator 2) initializes internal command
        structures in the XPS control software for this instance, and 3) sets the actuator to its home position. 
        Newport states this sequence of commands must be first applied before any other motions can be commanded of the
        actuator.
        Inputs: None
        Output: None
        """
        #Stop all current motions, and kill group
        [error, returnString] = self.controller.GroupKill(self.groupname)
        if (error != 0):
            raise RuntimeError, "Error "+str(error)+" executing GroupKill for " + self.label
        else:
            # Initialize the group
            [error, returnString] = self.controller.GroupInitialize(self.groupname)
            if (error != 0):
                raise RuntimeError, "Error "+str(error)+" executing GroupInitialize for " + self.label
            else:
                # Home search
                [error, returnString] = self.controller.GroupHomeSearch(self.groupname)
                if (error != 0):
                    raise RuntimeError, "Error "+str(error)+" executing GroupHomeSearch for " + self.label
                else:
                    #self.position = 0.0
                    self.update_position()
                    self.ishomed = True
                    self.motor_off() 
                    for i in self.groupnames:
                        self.remove_referenced_axis(i)

#####################################################################################################
class Mvp5za(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport M_VP_5ZA linear actuator.
    
    The methods in this class are:
        __init__()
        use_position_sensors(bool)
        report_position_sensors(bool)
        set_velocity(float)
    """
        
    MAX_VELOCITY = 5.0       # maximum velocity in mm/sec for an M VP 5ZA
    MAX_POSITION = 2.4       # in mm
    MIN_POSITION = -2.4      # in mm
    MAX_SENSOR_DISPLACEMENT = 2.250  # maximum value of displacement for Lion cap gauge sensor in 'Lo' sensitivity mode; in mm
    MIN_SENSOR_DISPLACEMENT = 0.250  # minimum value of displacement for Lion cap gauge sensor in 'Lo" sensitivity mode; in mm
    CAP_SENSOR_FEEDBACK_POSITION_TOLERANCE  = 0.000050   # 50 nm
    CAP_SENSOR_FEEDBACK_CONVERGENCE_TRIES = 10           # maximum number of attempts to reach position convergence using cap gauge sensor feedback
    unitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    
    def __init__(self,xps_controller,actuatorname,position_sensor = None,speed=MAX_VELOCITY,
                 name="M_VP_5ZA actuator attached to XPS controller", label = '',report_position_sensor = True):
        """
        This method creates an instance of a M_VP_5ZA actuator and also initializes the actuators to their home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the full actuatorname the Newport setup software gives to the M_VP_5ZA actuator instantiated with this class
                            which has format GROUPNAME.POSTIONERNAME
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """

        self.internal_units = "mm"  
        
        #Set position sensor use
        self.position_sensor = position_sensor
        self.loop_count = 1   # used to terminate loop control of reading cap gauges when self. use_position_sensor_feedback is True
        self.loop_convergence_result = True    # used to properly report state of loop convergence when self.use_position_sensor_feedback is True
        self.use_position_sensors(False)     # internally sets self.use_position_sensor_feedback to FALSE (default;) call this line before setting self.position below
        if position_sensor and report_position_sensor:
            self.report_position_sensor = True
        else:
            self.report_position_sensor = False
            
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)


                
    def use_position_sensors(self,proposition = False):
        """
        Determines if the position sensor is used for iterative movement feedback.
        Both use_position_sensors and report_position_sensors must be TRUE for the sensor to
        be used for iterative feedback.
        
        Input:
             proposition:  TRUE / FALSE enable / disable iterative movement using the sensor.
        Output:
             None
        """
        self.use_position_sensor_feedback = proposition
                
    def report_position_sensors(self,proposition = True):
        """
        Determines if the position sensor is used to update the position.

        Input:
             proposition:  TRUE / FALSE use / don't use the sensor to measure actuator position.
        Output:
             None
        """
        self.report_position_sensor = proposition
    

     
########################################################################################
class Urs150bpp(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport URS150BPP rotary stage.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 40.0      # maximum angular velocity of URS150BPP; verify this number
    MAX_POSITION = 179       # in degress; verify this number
    MIN_POSITION = -179      # in degrees; verify this number
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed Urs150bpp rotary staged attached to an XPS controller", label = ''):
        """
        This method creates an instance of the Newport URS150BPP rotary actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the name the Newport setup software gives to the URS150BPP actuator instantiated with this class.
             units:  optionally input value for units that are chosen from units list appropriate for angular units.
                     Default value is degrees.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)

########################################################################################
class M2LowerRotation(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport URS150BPP rotary stage.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 40.0      # maximum angular velocity of URS150BPP; verify this number
    MAX_POSITION = 226.56       # in degress; verify this number
    MIN_POSITION = -131.62      # in degrees; verify this number
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed rotary staged attached to an XPS controller", label = ''):
        """
        This method creates an instance of the Newport URS150BPP rotary actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the name the Newport setup software gives to the URS150BPP actuator instantiated with this class.
             units:  optionally input value for units that are chosen from units list appropriate for angular units.
                     Default value is degrees.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)
            
########################################################################################
class Sr50pp(CommonXPSFunctions):
    """
    This class makes an instance of a single SR50PP linear actuator.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 4.0       # maximum angular velocity in deg/sec for an SR50PP; verify this number
    MAX_POSITION = 179       # in degrees; verify this number
    MIN_POSITION = -179      # in degrees; verify this number
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed SR50PP rotary actuator attached to an XPS controller", label = ''):
        """
        This method creates an instance of an SR50PP rotary actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the name the Newport setup software gives to the M_VP_5ZA actuator instantiated with this class.
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
      
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)
    
########################################################################################
class M2CalRotation(CommonXPSFunctions):
    """
    This class makes an instance of a single SR50PP linear actuator.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 30.0       # maximum angular velocity in deg/sec for an SR50PP; verify this number
    MAX_POSITION = 1080.001      # in degrees; verify this number (Not used for this motor, many rotations allowed)
    MIN_POSITION = -1080.001    # in degrees; verify this number
    #unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed SR50PP rotary actuator attached to an XPS controller", label = ''):
        """
        This method creates an instance of an SR50PP rotary actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the name the Newport setup software gives to the M_VP_5ZA actuator instantiated with this class.
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
      
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)

             
########################################################################################
class Ltahl(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport LTA-HL linear actuator.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 1.0     # maximum velocity in mm/sec for an LTA-HL linear actuator
    MAX_POSITION = 25.4    # in mm
    MIN_POSITION = 0.0     # in mm
    unitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed LTA-HL linear actuator attached to an XPS controller", label = ''):
        """
        This method creates an instance of a Newport LTA-HL linear actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the full actuatorname the Newport setup software gives to the LTA-HL actuator instantiated with this class
                            which has format GROUPNAME.POSTIONERNAME
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        self.internal_units = "mm"   # this just asserts self.position is stored internally in mm units; and it is the default unit if no unit is specified.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)
    
########################################################################################
class M2ToolChanger(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport LTA-HL linear actuator.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 1000.*25.4 /9600.0    # maximum velocity in mm/sec for actuator
    MAX_POSITION = 55200.*25.4 /9600.0     # in mm
    MIN_POSITION = 0.0     # in mm
    unitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed LTA-HL linear actuator attached to an XPS controller", label = ''):
        """
        This method creates an instance of a Newport LTA-HL linear actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the full actuatorname the Newport setup software gives to the LTA-HL actuator instantiated with this class
                            which has format GROUPNAME.POSTIONERNAME
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        self.internal_units = "mm"   # this just asserts self.position is stored internally in mm units; and it is the default unit if no unit is specified.
        self.motorunits  = 9600.0/25.4  #Conversion factor from software internal units to motor drive units.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)
    
########################################################################################
class M2PartLoader(CommonXPSFunctions):
    """
    This class makes an instance of a single Newport LTA-HL linear actuator.
    
    The methods in this class are:
        __init__()
        set_velocity()
    """
        
    MAX_VELOCITY = 1200. *25.4 /2000.0   # maximum velocity in mm/sec for an LTA-HL linear actuator
    MAX_POSITION = 1080200. *25.4 /2000.0    # in mm
    MIN_POSITION = 0.0     # in mm
    unitvalues={'mm':1.,'m':1000.,'cm':10.,'nm':1.0e-6,'um':.001,'aa':1.0e-7,\
           'in':25.4,'uin':.0000254,'wv':.000633,'wv632.8':.0006328,\
           'wv633':.000633,'wv193':.000193,'wv13':.000013}
    
    def __init__(self,xps_controller,actuatorname,speed=MAX_VELOCITY,
                 name="An UnNamed LTA-HL linear actuator attached to an XPS controller", label = ''):
        """
        This method creates an instance of a Newport LTA-HL linear actuator and also initializes the actuator to its home position.
        
        Inputs:
             xps_controller:  an instance of the XPS class which contains the socket used for PC to XPS controller communications.
             actuatorname:  the full actuatorname the Newport setup software gives to the LTA-HL actuator instantiated with this class
                            which has format GROUPNAME.POSTIONERNAME
             units:  optionally input value for units that are chosen from the canonical Zygo list in the included unitvalues array.
                     Default value is mm.
             speed: optionally input speed value in XPS units defined in the stages.ini file.  Valid values are from 0 to self.MAX_VELOCITY.
             name:  an optionally provided user string that defines this actuator instance.
             label: an optional label that will be used for Gui display of the motor
        """
        self.internal_units = "mm"   # this just asserts self.position is stored internally in mm units; and it is the default unit if no unit is specified.
        self.motorunits  = 2000.0/25.4  #Conversion factor from software internal units to motor drive units.
        CommonXPSFunctions.__init__(self, xps_controller,actuatorname,speed, name, label)
    

        
########################################################################################
class Goniometer(object):

    """
    Instantiates the General Purpose I/O functionality for the Newport XPS controller. I/O
    functionality refers to digital input/output and analog input/output capabilities.
    
    The methods for this class are:
    
        __init__()
        move()
        move_abs()
        check_position()
        set_speed()
        get_analog()
        set_analog()
        get_digital()
        set_digital()
        
    Output angular range for the M1 goniometer is -3.05 to +3.05 deg (SH changed from 0 to 3 deg to make motion symmetrical)
    """
        
    MAX_POSITION =  3.0500000001  # in degrees;      add an epsilon of 0.0000000001 to handle round-off errors
    MIN_POSITION = -3.0500000001  # in degrees; subtract an epsilon of 0.0000000001 to handle round-off errors
    MAX_SPEED = 8.9     # in volts (SH changed from 6.6 to reflect new range of motion) 
    MIN_SPEED = 4.3     # in volts (SH changed from 3.74 to reflect new range of motion)
    MOTOR_OFF = 0.0      # in volts
    SENSOR_VOLTAGE_OFFSET = 6.2083  # SH updated from 8.0769
                                  # SH Updated Measurement travel from -2.8 to 2.8 degrees with 8.9 to 4.3V; 0 degrees at 6.6V
                                  # SH updated formula to Postion=DegPerV*(V-Volt_Offset) from Position = DegPerV * V  + Volt_Offset
    
                                  # OLD: The position sensor outputs approximately 0.9 to 8.0 volts.  To make the center position
                                  # OLD: read 0.0 deg, you need to subtract this voltage value from the sensor voltage reading and convert to deg
    DEG_PER_VOLT  = -1/0.6591      # SH changed from -3.5/2.86.  A "first order" conversion coefficient for the M1 goniometer setup
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,GPIO_instance,deg_per_volt, sensor_voltage_offset, speed = 3.5, label = ''): #SH change speed value from 4 to send different voltage to motor
        """
        Instantiates a GPIO class.  Initializes self.output_analog_channel to 0.0 volts; initializes 
        self.output_digital_channel to #00.
        Inputs:
             xps_controller: the XPS controller that's providing the GPIO capability for this GPIO class
             input_analog_channel: name of GPIO analog input channel hardwired for M1 setup
             output_analog_channel: name of GPIO analog output channel hardwired for M1 setup
             input_digital_channel: name of GPIO digital input channel hardwired for M1 setup
             output_digital_channel: name of GPIO digital output channel hardwired for M1 setup
             label: an optional label that will be used for Gui display of the motor
        Output:
             a GPIO instance
        """
        self.controller = GPIO_instance.controller
        self.get_analog = GPIO_instance.get_analog
        self.set_analog = GPIO_instance.set_analog
        self.input_analog_channel = GPIO_instance.input_analog_channel
        self.output_analog_channel = GPIO_instance.output_analog_channel 
        self.set_digital = GPIO_instance.set_digital
        self.output_digital_channel = GPIO_instance.output_digital_channel
        self.digital_channel = GPIO_instance.digital_channel
        
        self.label = label
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        self.SENSOR_VOLTAGE_OFFSET = sensor_voltage_offset
        self.DEG_PER_VOLT = deg_per_volt

        self.set_analog(self.MOTOR_OFF)

        self.position = self.DEG_PER_VOLT*(self.get_analog() - self.SENSOR_VOLTAGE_OFFSET)   # SH updated formula to Postion=DegPerV*(V-Volt_Offset) from Position = DegPerV * V  + Volt_Offset
        self.speed = speed
        self.offset = 0.0
        if self.DEG_PER_VOLT < 0.0:
            self.direction = 1
        else:
            self.direction = -1

    def get_position(self, units = "deg"):
        """Reads the analog voltage, and calculates the current position"""
        return (self.position + self.offset) / self.unitvalues[units]
 
    def update_position(self, units = "deg"):
        """Reads the analog voltage, and calculates the current position"""
        self.position = self.DEG_PER_VOLT*(self.get_analog() - self.SENSOR_VOLTAGE_OFFSET)   # SH updated formula to Postion=DegPerV*(V-Volt_Offset) from Position = DegPerV * V  + Volt_Offset
        return (self.position + self.offset) / self.unitvalues[units] 
 
    def move(self,amount, units = "deg"):
        """
        Moves goniometer in a relative sense and updates new rotation position.  Range of motion is +/- 2.8 degrees.
        If the resulting position exceeds the mechanical extent of the Firgelli actuator, no motion occurs.
        Input:
           amount:  the amount of requested relative angular motion in deg
        Output:
           None
        """
        amount = amount * self.unitvalues[units]             #Convert to degrees for performing the move.
        if self.check_position(amount):
            self.motor_on()
            #target_voltage = ((self.position + amount)/self.DEG_PER_VOLT) + self.SENSOR_VOLTAGE_OFFSET   # SH updated formula from V = ( P - Volt_Offset ) / DegPerV.  
            position_voltage = self.get_analog()        # where you are now in volts
            #amount = amount * self.direction    
            if amount >= 0.0:
                target_voltage = ((self.position + amount)/self.DEG_PER_VOLT) + self.SENSOR_VOLTAGE_OFFSET 
                #raw_input(str(('+',self.speed * self.direction, position_voltage,target_voltage,position_voltage > target_voltage)))
                self.set_analog(self.speed )             # turn motor on with proper polarity
                while position_voltage * self.direction> target_voltage * self.direction:
                    #print self.get_analog()
                    position_voltage = self.get_analog()
            else:
                target_voltage = ((self.position + amount)/self.DEG_PER_VOLT) + self.SENSOR_VOLTAGE_OFFSET 
                #raw_input(str(('-',-self.speed * self.direction, position_voltage,target_voltage,position_voltage < target_voltage)))
                self.set_analog(-self.speed )    # turn motor on with proper polarity
                while position_voltage * self.direction < target_voltage * self.direction:
                    #print self.get_analog()
                    position_voltage = self.get_analog()

            self.set_analog(self.MOTOR_OFF)     # turn motor off
            time.sleep(0.5)     #SH added to wait for motor to stop before updating position
            self.update_position()
            self.motor_off()
            return True
        
        else:
            return False
            
    def move_abs(self,amount, units = "deg"):
        """
        Moves goniometer in an absolute sense and updates new rotation position.  Range of position is +/- 2.8 degrees.
        If the resulting position exceeds the mechanical extent of the Firgelli actuator, no motion occurs.
        Input:
           amount:  the requested absolute angular position in deg
        Output:
           None
        """
        return self.move( amount*self.unitvalues[units] - self.position )
 
    def check_position(self,displacement):
        """
        Before a relative or absolute move is performed, this method is called to see that the desired position is
        within bounds of Firgelli motor.  The input units are in degrees and is the relative amount of displacement
        reuired.  This displacement value is presented whether the move() or move_abs() methods are called.
        Input:
            displacement: amount of relative angular rotation in deg
        Ouput:
            True if this requested motion will be within the physical bounds of the Firgelli motor
            False if this requested motion will not be within the physical bounds of the Firgelli motor
        """
        if ( bool((self.position + displacement)<= self.MAX_POSITION) & (bool((self.position + displacement)>= self.MIN_POSITION)) ):
            return True
        else:
            return False
    
    def set_velocity(self,amount):
        """
        Sets the motor voltage to the Firgelli motor.  A larger voltage gives a larger angular rate of change.
        A minimum voltage of 2.75 seems to be needed to overcome the string restoration force when moving with a
        negative motor voltage.
        """
        if amount > self.MAX_SPEED:
            amount = self.MAX_SPEED
        if amount < self.MIN_SPEED:
            amount = self.MIN_SPEED
        self.speed = amount
        

    def motor_on(self):
        """Set relay switch to on"""
        self.set_digital(255)
        
    def motor_off(self):
        """Set relay switch to off"""
        self.set_digital(0)

#######################################################################################
class M2Goniometer(Goniometer):
    MAX_POSITION =  11.8 
    MIN_POSITION = -11.4 
    MAX_SPEED = 2.01     
    MIN_SPEED = 0.24     
    MOTOR_OFF = 0.0      # in volts
    SENSOR_VOLTAGE_OFFSET = 3.046  # SH updated from 8.0769
                                  # SH Updated Measurement travel from -2.8 to 2.8 degrees with 8.9 to 4.3V; 0 degrees at 6.6V
                                  # SH updated formula to Postion=DegPerV*(V-Volt_Offset) from Position = DegPerV * V  + Volt_Offset
    
                                  # OLD: The position sensor outputs approximately 0.9 to 8.0 volts.  To make the center position
                                  # OLD: read 0.0 deg, you need to subtract this voltage value from the sensor voltage reading and convert to deg
    DEG_PER_VOLT  = 1.0/0.187      # SH changed from -3.5/2.86.  A "first order" conversion coefficient for the M1 goniometer setup
    unitvalues={'deg':1.,'rad':57.29577951308,'urad':0.00005729577951308}
    
    def __init__(self,GPIO_instance, speed = 2, label = ''): #SH change speed value from 4 to send different voltage to motor
        self.controller = GPIO_instance.controller
        self.get_analog = GPIO_instance.get_analog
        self.set_analog = GPIO_instance.set_analog
        self.input_analog_channel = GPIO_instance.input_analog_channel
        self.output_analog_channel = GPIO_instance.output_analog_channel 
        self.set_digital = GPIO_instance.set_digital
        self.output_digital_channel = GPIO_instance.output_digital_channel
        self.digital_channel = GPIO_instance.digital_channel
        
        self.label = label
        self.internal_units = "deg"   # this just asserts self.position is stored internally in deg units; and it is the default unit if no unit is specified.
        #self.SENSOR_VOLTAGE_OFFSET = sensor_voltage_offset
        #self.DEG_PER_VOLT = deg_per_volt

        self.set_analog(self.MOTOR_OFF)

        self.position = self.DEG_PER_VOLT*(self.get_analog() - self.SENSOR_VOLTAGE_OFFSET)   # SH updated formula to Postion=DegPerV*(V-Volt_Offset) from Position = DegPerV * V  + Volt_Offset
        self.speed = speed
        self.offset = 0.0
        if self.DEG_PER_VOLT < 0.0:
            self.direction = 1
        else:
            self.direction = -1

#######################################################################################
class PZAPower(object):
    """
    Use a GPIO relay to reset the power to the PZA switches.
    
    Methods:
        on()
        off()
    """
    def __init__(self, GPIO_instance):
        self.controller = GPIO_instance.controller
        self.set_digital = GPIO_instance.set_digital
    
    def on(self):
        """Set relay switch to on"""
        self.set_digital(255)
        
    def off(self):
        """Set relay switch to off"""
        self.set_digital(0)
        
        
########################################################################################
class Gpio(object):
    """
    Instantiates the General Purpose I/O functionality for the Newport XPS controller. I/O
    functionality refers to digital input/output and analog input/output capabilities.
    
    The methods for this class are:
    
        __init__()
        get_analog()
        set_analog()
        get_digital()
        set_digital()
        
    Only methods with IO channels on initialization will be available.
    """
    
    MAX_GPIO_DAC_OUTPUT_VOLTAGE = 10.0   # might not need these
    MIN_GPIO_DAC_OUTPUT_VOLTAGE = - 10.0
    
    def __init__(self,xps_controller,input_analog_channel=None,output_analog_channel=None,
                 input_digital_channel = None,output_digital_channel = None, digital_channel = None):
        """
        Instantiates a GPIO class.  Initializes self.output_analog_channel to 0.0 volts; initializes 
        self.output_digital_channel to #00.
        Inputs:
             xps_controller: the XPS controller that's providing the GPIO capability for this GPIO class
             input_analog_channel: name of GPIO analog input channel hardwired for M1 setup
             output_analog_channel: name of GPIO analog output channel hardwired for M1 setup
             input_digital_channel: name of GPIO digital input channel connector hardwired for M1 setup
             output_digital_channel: name of GPIO digital output channel connector hardwired for M1 setup
             digital_channel: digital output pin, specify DO channel number 1-8, use a list for multiple channels
        Output:
             a GPIO instance
        """
        self.controller = xps_controller
        if input_analog_channel:
            self.input_analog_channel = input_analog_channel
        
        
        if output_analog_channel:
            self.output_analog_channel = output_analog_channel
        

        print digital_channel
        if output_digital_channel and digital_channel:
            self.output_digital_channel = output_digital_channel
            if type(digital_channel) in [float, int, str]:
                self.digital_channel = 2**(int(digital_channel) - 1)
            elif type(digital_channel) in [list, tuple]:
                dc = 0
                for i in digital_channel:
                    dc += 2**(int(i) - 1)
                self.digital_channel = dc
        elif output_digital_channel or digital_channel:
            raise ValueError, 'must specify both output_digital_channel and digital_channel'
        print self.digital_channel
        
        if input_digital_channel:
            self.input_digital_channel = input_digital_channel 
        else:
            self.input_digital_channel = output_digital_channel
                    
            
    def get_analog(self):
        """
        Reads the analog value from the GPIO analog input channel self.input_analog_channel
        Input:
           None
        Output:
           voltage_reading of self.input_analog_channel in volts
        """
        [error,voltage_reading] = self.controller.GPIOAnalogGet(self.input_analog_channel)
        return voltage_reading
        
    def set_analog(self,voltage):
        """
        Sets the analog voltage for self.output_analog_channel in volts.  Also checks the
        output voltage for bounds checking of the DAC.
        Input:
            voltage:  desired voltage value in volts
        Output
            None
        """
        if voltage > self.MAX_GPIO_DAC_OUTPUT_VOLTAGE:
            voltage = self.MAX_GPIO_DAC_OUTPUT_VOLTAGE
        if voltage < self.MIN_GPIO_DAC_OUTPUT_VOLTAGE:
            voltage = self.MIN_GPIO_DAC_OUTPUT_VOLTAGE
        [error, returnString] = self.controller.GPIOAnalogSet(self.output_analog_channel,voltage)
        
    def get_digital(self):
        """
        Reads the 8 bits of self.input_digital_channel
        Input:  None
        Output: digital_value.  Displayed as 1 to 255.
        """
        [error,digital_value] = self.controller.GPIODigitalGet(self.input_digital_channel)
        return digital_value
    
    def set_digital(self,value):
        """
        Sets any combination of the 8 bits of self.output_digital_channel active.
        
        set mask = Sum{int(2^n)} where 0<=n<=7; e.g. 128 for channel 7
        value = int(255)
        
        Input:
            mask:  which of the 8 channels to set
            value:  int(255)
        Output:
            error:  error code from XPS to this command; value is '0' if no error.
        """
        [error,returnString] = self.controller.GPIODigitalSet(self.output_digital_channel,self.digital_channel,value)
        self.digital_value = value
        return error
                                 
        
        
            
    