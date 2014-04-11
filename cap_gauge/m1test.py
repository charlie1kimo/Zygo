import xps
import capgauge
import pzc200
import xpsactuators

print 'Initializing Controllers'
pza_controller = pzc200.Pzc200('172.18.106.89', 2000)
xps_controller = xps.Xps( '172.18.106.63',5001)


print 'Initializing CGH Motors'
cuz1 = capgauge.Capgauge(7,serial_number="120639-08",name="Cap Sensor For UZ1 NanoPZ PZA12")  # the first parameter is the NI channel number
cuz2 = capgauge.Capgauge(5,serial_number="120639-06",name="Cap Sensor For UZ2 NanoPZ PZA12")
cuz3 = capgauge.Capgauge(6,serial_number="120639-07",name="Cap Sensor For UZ3 NanoPZ PZA12")


uxmotor = pzc200.Pza12(pza_controller,2,1,name="UX", label = 'CGH X Axis', correction = None, correction_minus = None)
uymotor = pzc200.Pza12(pza_controller,2,2,name="UY", label = 'CGH Y Axis', correction = None, correction_minus = None)
uzmotor1 = pzc200.Pza12(pza_controller,2,3,position_sensor=cuz1,name="UZ1", label = 'CGH Z1 Axis', correction = {99: [0.0058, 1/1.2389], 0.02: [0.00009, 1/0.9102, 4.3155]}, correction_minus = None)
uzmotor2 = pzc200.Pza12(pza_controller,2,4,position_sensor=cuz2,name="UZ2", label = 'CGH Z2 Axis', correction = {99: [0.0017, 1/1.1664], 0.02: [0.0001, 1/0.8769, 4.8735]}, correction_minus = None)
uzmotor3 = pzc200.Pza12(pza_controller,2,5,position_sensor=cuz3,name="UZ3", label = 'CGH Z3 Axis', correction = {99: [0.0033, 1/1.1334], 0.02: [0.0002, 1/0.8942, 5.1334]}, correction_minus = None)

cgh = pzc200.GroupMovements(uxmotor, uymotor, uzmotor1, uzmotor2, uzmotor3, (-177.800, -9.525), (139.167, 139.167), (139.167, -139.167), base_rotation = 90, yflip = True, zflip = True)

                                                                        

print 'Initializing Part Motors'    
clz1 = capgauge.Capgauge(3,serial_number="120639-04",name="Cap Sensor For LZ1 NanoPZ PZA12")
clz2 = capgauge.Capgauge(4,serial_number="120639-05",name="Cap Sensor For LZ2 NanoPZ PZA12")
clz3 = capgauge.Capgauge(2,serial_number="120639-03",name="Cap Sensor For LZ3 NanoPZ PZA12")

xmotor = pzc200.Pza12(pza_controller,1,1,name="LX", label = 'Part X Axis', correction = None, correction_minus = None)
ymotor = pzc200.Pza12(pza_controller,1,2,name="LY", label = 'Part Y Axis', correction = None, correction_minus = None)
zmotor1 = pzc200.Pza12(pza_controller,1,3,position_sensor=clz1,name="LZ1", label = 'Part Z1 Axis', correction = {99: [-0.0006, 1/1.5647], 0.02: [0.000006, 1/1.1106, 0.9635]}, correction_minus = None)
zmotor2 = pzc200.Pza12(pza_controller,1,4,position_sensor=clz2,name="LZ2", label = 'Part Z2 Axis', correction = {99: [0.0007, 1/0.7567]}, correction_minus = {0: [0.00007, 1/0.4197]})
zmotor3 = pzc200.Pza12(pza_controller,1,5,position_sensor=clz3,name="LZ3", label = 'Part Z3 Axis', correction = {99:  [0.001, 1/1.288]}, correction_minus = {0: [-0.0006, 1/1.2916]})

lrmotor = xpsactuators.Urs150bpp(xps_controller,"GROUP1.POSITIONER",speed=10, label = 'Part Rotation')

part = pzc200.GroupMovements(xmotor, ymotor, zmotor1, zmotor2, zmotor3, (0.000, 139.700), (120.980, -69.850), (-120.980, -69.850), lrmotor, base_rotation = 90, rflip = True)
part.lrmotor = part.rmotor



print 'Initializing Reference Motors'
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


# Initializing power reset function.
pzaresetgpio = xpsactuators.Gpio(xps_controller,output_digital_channel = "GPIO1.DO", digital_channel = 2)
pzapower = xpsactuators.PZAPower(pzaresetgpio)



# Objects to be used via a gui
motorlist = [cgh.xmotor,    
             cgh.ymotor,
             cgh.zmotor1,
             cgh.zmotor2,
             cgh.zmotor3,
             part.xmotor, 
             part.ymotor, 
             part.zmotor1,
             part.zmotor2,
             part.zmotor3,
             part.lrmotor,
             reference.urmotor,
             reference.goniometer]

motorgroups = [part, cgh]

partobjects = pzc200.GroupWrapper(part, 'Part')
cghobjects = pzc200.GroupWrapper(cgh, 'CGH')

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
            reference.urmotor,
            reference.goniometer]  

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
    
def saveoffset(filename, motors):
    """Save the current position of the specified motors to a file
    
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

             

