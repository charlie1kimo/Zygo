import os
import xps
import capgauge
import pzc200
import xpsactuators

print 'Initializing Controllers'
xps_controller1 = xps.Xps( '172.18.106.125',5001)
xps_controller2 = xps.Xps( '172.18.106.68',5001)
pza_controller = pzc200.Pzc200('172.18.106.121', 2000)

print 'Initializing CGH Motors'
cuz1 = capgauge.Capgauge(0,serial_number="120639-??", ni_config_file = 'National Instruments 9205 Config M2.txt',name="Cap Sensor For UX NanoPZ PZA12")  # the first parameter is the NI channel number
cuz2 = capgauge.Capgauge(1,serial_number="120639-??", ni_config_file = 'National Instruments 9205 Config M2.txt',name="Cap Sensor For UY NanoPZ PZA12")
cuz3 = capgauge.Capgauge(2,serial_number="120639-??", ni_config_file = 'National Instruments 9205 Config M2.txt',name="Cap Sensor For UZ1 NanoPZ PZA12")
cuz4 = capgauge.Capgauge(3,serial_number="120639-??", ni_config_file = 'National Instruments 9205 Config M2.txt',name="Cap Sensor For UZ2 NanoPZ PZA12")
cuz5 = capgauge.Capgauge(4,serial_number="120639-??", ni_config_file = 'National Instruments 9205 Config M2.txt',name="Cap Sensor For UZ3 NanoPZ PZA12")

cghxmotor = pzc200.Pza12(pza_controller,1,1,position_sensor=cuz1,name="UX", label = 'CGH X Axis', correction = 0.8, correction_minus = None)        #correction = 1.25, cor
cghymotor = pzc200.Pza12(pza_controller,1,2,position_sensor=cuz2,name="UY", label = 'CGH Y Axis', correction = 0.749, correction_minus = None)      # correction = 1.335, co
cghzmotor1 = pzc200.Pza12(pza_controller,1,3,position_sensor=cuz3,name="UZ1", label = 'CGH Z1 Axis', correction = 0.629, correction_minus = None)   # ', correction = 1.589,
cghzmotor2 = pzc200.Pza12(pza_controller,2,0,position_sensor=cuz4,name="UZ2", label = 'CGH Z2 Axis', correction = 0.568, correction_minus = 0.552)  # ', correction = 1.76, 
cghzmotor3 = pzc200.Pza12(pza_controller,3,0,position_sensor=cuz5,name="UZ3", label = 'CGH Z3 Axis', correction = 0.698, correction_minus = None)   # ', correction = 1.432,
#cghzmotor1 = pzc200.Pza12(pza_controller,1,3,name="UZ1", label = 'CGH Z1 Axis', correction = None, correction_minus = None)
#cghzmotor2 = pzc200.Pza12(pza_controller,2,0,name="UZ2", label = 'CGH Z2 Axis', correction = None, correction_minus = None)
#cghzmotor3 = pzc200.Pza12(pza_controller,3,0,name="UZ3", label = 'CGH Z3 Axis', correction = None, correction_minus = None)

cgh = pzc200.GroupMovements(cghxmotor, cghymotor, cghzmotor1, cghzmotor2, cghzmotor3, (0, 102.87), (82.55, -47.66), (-82.55, -47.66), zflip = True, reportxflip = True)  
#cgh = pzc200.GroupMovements(cghxmotor, cghymotor, cghzmotor1, cghzmotor2, cghzmotor3, (0, -102.87), (82.55, 47.66), (-82.55, 47.66), zflip = True) 

print 'Initializing Part Motors'    
#xmotor = xpsactuators.Ltahl(xps_controller1,"XAxis.Positioner",speed=0.5, label = 'Part X Motor')
#ymotor = xpsactuators.Ltahl(xps_controller1,"YAxis.Positioner",speed=0.5, label = 'Part Y Motor')
# LG 5/9/13 swap x/y motors and change labels from Y, X to A, B
xmotor = xpsactuators.Ltahl(xps_controller1,"YAxis.Positioner",speed=0.5, label = 'Part A Motor')
ymotor = xpsactuators.Ltahl(xps_controller1,"XAxis.Positioner",speed=0.5, label = 'Part B Motor')
zmotor1 = xpsactuators.Mvp5za(xps_controller1,"ZAxis.Z1",position_sensor=None, label = 'Part Z1 Motor')
zmotor2 = xpsactuators.Mvp5za(xps_controller1,"ZAxis.Z2",position_sensor=None, label = 'Part Z2 Motor')
zmotor3 = xpsactuators.Mvp5za(xps_controller1,"ZAxis.Z3",position_sensor=None, label = 'Part Z3 Motor')
lrmotor = xpsactuators.M2LowerRotation(xps_controller1,"Rotation.Positioner",speed=5, label = 'Part Rotation') 

#"Temporary' acceleration change for the air bearing (lrmotor)
_current = lrmotor.controller.PositionerSGammaParametersGet(lrmotor.actuatorname)
print _current
_lrmotorspeed = 5
_lrmotoracceleration = 24
[_error,returnString] = lrmotor.controller.PositionerSGammaParametersSet(lrmotor.actuatorname,_lrmotorspeed,_lrmotoracceleration,_current[3],_current[4]) #Convert to controller units for command.
if (_error != 0):
    raise RuntimeError, "Error "+str(_error)+" executing PositionerSGammaParametersGet for " + lrmotor.label        
_current = lrmotor.controller.PositionerSGammaParametersGet(lrmotor.actuatorname)
print _current

#part = pzc200.GroupMovements(ymotor, xmotor, zmotor1, zmotor2, zmotor3, (182.302, -233.085), (-293.009, -41.336), (110.706, 274.421), lrmotor, base_rotation = 254.03, zflip = True, tiltflip = True)
part = pzc200.GroupMovements(ymotor, xmotor, zmotor1, zmotor2, zmotor3, (156.5455, -251.11), (-295.74, -10.0174), (139.195, 261.1274), lrmotor, base_rotation = 254.03, zflip = True, tiltflip = True)  #45.97+ 15.97

#part = pzc200.GroupMovements(xmotor, ymotor, zmotor1, zmotor2, zmotor3, (-295.91, 0.0), (147.955, -256.266), (147.955, 256.266), lrmotor, base_rotation = -15.97, xflip = False, yflip = True, zflip = True)


print 'Initializing Reference Motors'
zcalmotor1 = xpsactuators.Mvp5za(xps_controller2,"ZCal.Z1",position_sensor=None, label = 'Cal Z1 Axis')
zcalmotor2 = xpsactuators.Mvp5za(xps_controller2,"ZCal.Z2",position_sensor=None, label = 'Cal Z2 Axis')
zcalmotor3 = xpsactuators.Mvp5za(xps_controller2,"ZCal.Z3",position_sensor=None, label = 'Cal Z3 Axis')
calgongpio = xpsactuators.Gpio(xps_controller2, input_analog_channel="GPIO2.ADC1",output_analog_channel="GPIO2.DAC1",output_digital_channel = "GPIO1.DO", digital_channel = 1)
calgoniometer = xpsactuators.M2Goniometer(calgongpio, label = 'Cal Goniometer')
rcalmotor = xpsactuators.M2CalRotation(xps_controller2,"CalRot.Positioner",speed=20, label = 'Cal Rotation')

#reference = pzc200.GroupMovements(None, None, zcalmotor1, zcalmotor2, zcalmotor3, (39.386, -280.246), (-262.393, 106.0137), (223.007, 174.232), base_rotation = 0, zflip = False)  #*** positions and base rotation are wrong.
reference = pzc200.GroupMovements(None, None, zcalmotor1, zcalmotor2, zcalmotor3, (-43.4777, 309.3597), (289.6522, -117.027), (-246.175, -192.333), base_rotation = 180, zflip = True)  #*** positions and base rotation are wrong.


"""
class Reference(object):
        
    def __init__(self, xps_controller, part_object):
        
        self.xmotor  = part_object.xmotor 
        self.ymotor  = part_object.ymotor 
        self.zmotor1 = part_object.zmotor1
        self.zmotor2 = part_object.zmotor2
        self.zmotor3 = part_object.zmotor3
        
        self.lrmotor = part_object.lrmotor
        
        self.urmotor = xpsactuators.Sr50pp(xps_controller,"GROUP2.POSITIONER", label = 'CS Rotation')
        gongpio = xpsactuators.Gpio(xps_controller, input_analog_channel="GPIO2.ADC1",output_analog_channel="GPIO2.DAC1",output_digital_channel = "GPIO1.DO", digital_channel = 1)
        self.goniometer = xpsactuators.Goniometer(gongpio, deg_per_volt  = -1/0.6591, sensor_voltage_offset = 6.2083, label = 'CS Goniometer') #SH changed from deg_per_volt=-3.5/2.86 and sensor_voltage_offset = 8.0769   

reference = Reference(xps_controller, part)
"""

print 'Initializing Loader and Tool Changer Motors'
toolchangemotor = xpsactuators.M2ToolChanger(xps_controller2,"ToolChange.Positioner",speed=2.6458, label = 'Tool Changer')
partloadmotor = xpsactuators.M2PartLoader(xps_controller2,"PartLoad.Positioner",speed=7.12, label = 'Loader')

# Initializing power reset function.
pzaresetgpio = xpsactuators.Gpio(xps_controller2,output_digital_channel = "GPIO1.DO", digital_channel = 2)
pzapower = xpsactuators.PZAPower(pzaresetgpio)
#pzapower.on()

# Objects to be used via a gui
motorlist = [cgh.xmotor,    
             cgh.ymotor,
             cgh.zmotor1,
             cgh.zmotor2,
             cgh.zmotor3,
             part.ymotor, 
             part.xmotor, 
             part.zmotor1,
             part.zmotor2,
             part.zmotor3,
             part.rmotor,
             zcalmotor1, 
             zcalmotor2, 
             zcalmotor3, 
             calgoniometer,
             rcalmotor,
             toolchangemotor,
             partloadmotor]


motorgroups = [part, cgh, reference]


partobjects = pzc200.GroupWrapper(part, 'Part')
cghobjects = pzc200.GroupWrapper(cgh, 'CGH')
referenceobjects = pzc200.GroupWrapper(reference, 'Cal')

#Warning, Part motors and reference motors should not not be moved at the same time.
axislist = [cghobjects.movex,
           cghobjects.movey,
           cghobjects.movez,
           cghobjects.tiltx,
           cghobjects.tilty,
           partobjects.movex,
           partobjects.movey,
           partobjects.movez,
           partobjects.tiltx,
           partobjects.tilty,
           partobjects.rotate,
           referenceobjects.movez,
           referenceobjects.tiltx,  
           referenceobjects.tilty,  
           calgoniometer,  
           rcalmotor]     
             
             

paxislist = [cghobjects.movex,
            cghobjects.movey,
            cghobjects.movez,
            cghobjects.tiltx,
            cghobjects.tilty,
            partobjects.movex,
            partobjects.movey,
            partobjects.movez,
            partobjects.tiltx,
            partobjects.tilty,
            partobjects.rotate]
          

calaxislist = [cghobjects.movex,
              cghobjects.movey,
              cghobjects.movez,
              cghobjects.tiltx,
              cghobjects.tilty,
              referenceobjects.movez,
              referenceobjects.tiltx,
              referenceobjects.tilty,
              calgoniometer,
              rcalmotor]   



# Checking for Referencing State
if os.path.isfile('RefMotor.cfg'):
    f = open('RefMotor.cfg', 'r')
    lines = f.readlines()
    f.close()
    print 'Warning, the following motors are in a referencing state:'
    for i in lines:
        line = i.strip()
        if line != '':
            for j in motorlist:
                if hasattr(j, 'actuatorname') and line == j.actuatorname:
                    print '\t',j.label
    raw_input('Press Enter to Continue. ')

    
def saveoffset(filename, motors):
    """Save the _current position of the specified motors to a file
    
    Inputs:
        filename -- string input of the file to create.  Will overwrite existing files.
        axes -- a list of the axes to save.  Will use axis objects or labels.
    """
    motornames = {}
    for i in motorlist:
        motornames[i.label] = i
    
    f = open(filename, 'w')
    for i in motors:
        if type(i) == str:
            a = motornames[i]
        else:
            a = i
        f.write(a.label + ' = ' + str(a.get_position()) +'\n')
    f.close()
    
def loadoffset(filename, motors = [], move = True):
    """Load saved positions for motors and move to those positions.  Moves will
    be executed in order of motors provided, or in order saved if a motor list 
    is omitted.
    
    Inputs:
            filename -- string input of the file to create.  Will overwrite existing files.
            axes -- a list of the axes to save.  Will use axis objects or labels.
            move -- will execute the moves.  else, returns a dictionary of saved positions.
    """
    
    motornames = {}
    for i in motorlist:
        motornames[i.label.upper()] = i 
    
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    
    order = []
    positions = {}
    for line in lines:
        a = line.split('=')
        if len(a) == 2:
            order.append(a[0].strip())
            positions[a[0].strip()] = float(a[1].strip())
    
    if move:
        if motors:
            order = motors

        for i in order:
            if type(i) == str:
                a = motornames[i]
                b = i
            else:
                a = i
                b = i.label
            a.move_abs(positions[i])
    else:
        return positions

# Objects to be called from interactive command line
__all__ = ['cgh','part','reference','pzapower', 'saveoffset','loadoffset']

             

