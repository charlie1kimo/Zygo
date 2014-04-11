import xps
import capgauge
import pzc200
import xpsactuators
import os

class TSzMotorDummy(capgauge.MotorDummy):
    """Modified motor dummy class for unique POB TS Z sensor unmodified position readout
    sensor is the TS Z motor in this case."""
    def __init__(self, sensor, label = None, name = None):
        capgauge.MotorDummy.__init__(self, sensor, label , name )
    def update_position(self,units=None):
        """
        Return unmodified (no TS Z offset position)
        """
        self.sensor.update_position()
        self.position = self.sensor.read_position


NI_config_file_path = os.path.dirname(os.path.abspath(__file__)) + '/National Instruments 9205 Config POB.txt'

print 'Initializing Controllers'
pza_controller = pzc200.Pzc200('172.18.106.120', 2000)
xps_controller1 = xps.Xps( '172.18.106.128',5001)
xps_controller2 = xps.Xps( '172.18.106.127',5001)


print 'Initializing Part Motors'
Amotor = xpsactuators.Pob_partxy(xps_controller1,"AAxis.Positioner",speed=0.5, label = 'Part A Motor')
Bmotor = xpsactuators.Pob_partxy(xps_controller1,"BAxis.Positioner",speed=0.5, label = 'Part B Motor')
zmotor1 = xpsactuators.UZS80PP(xps_controller1,"ZAxis.Z1", label = 'Part Z1 Motor')
zmotor2 = xpsactuators.UZS80PP(xps_controller1,"ZAxis.Z2", label = 'Part Z2 Motor')
zmotor3 = xpsactuators.UZS80PP(xps_controller1,"ZAxis.Z3", label = 'Part Z3 Motor')
lrmotor = xpsactuators.PobPartRotation(xps_controller1,"RAxis.Positioner",speed=5, label = 'Part Rotation')

part = pzc200.GroupMovements(Amotor, Bmotor, zmotor1, zmotor2, zmotor3, (-101.6, 175.9712), (203.2, 0), (-101.6, -175.9712), lrmotor, base_rotation = 0, rflip = True, xflip = False, reportxflip = True, reportyflip = True, reportrflipxy = True)


print 'Initializing Cal Sphere Motors'
##ccalz1 = capgauge.Capgauge(7,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CalZ1 NanoPZ PZA12")  # the first parameter is the NI channel number
##ccalz2 = capgauge.Capgauge(5,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CalZ2 NanoPZ PZA12")
##ccalz3 = capgauge.Capgauge(6,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CalZ3 NanoPZ PZA12")
##ccalA = capgauge.Capgauge(5, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CalA NanoPZ PZA12")
##ccalB = capgauge.Capgauge(6, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CalB NanoPZ PZA12")

calAmotor = pzc200.Pza12(pza_controller,1,2,position_sensor=None,name="CalA",  label = 'Cal Sphere A Axis', correction = None, correction_minus = None)
calBmotor = pzc200.Pza12(pza_controller,2,2,position_sensor=None,name="CalB",  label = 'Cal Sphere B Axis', correction = None, correction_minus = None)
calzmotor1 = pzc200.Pza12(pza_controller,1,4,position_sensor=None,name="CalZ1", label = 'Cal Sphere Z1 Axis', correction = None, correction_minus = None)
calzmotor2 = pzc200.Pza12(pza_controller,2,4,position_sensor=None,name="CalZ2", label = 'Cal Sphere Z2 Axis', correction = None, correction_minus = None)
calzmotor3 = pzc200.Pza12(pza_controller,3,4,position_sensor=None,name="CalZ3", label = 'Cal Sphere Z3 Axis', correction = None, correction_minus = None)

calsphere = pzc200.GroupMovements(calAmotor, calBmotor, calzmotor1, calzmotor2, calzmotor3, (-127, 0), (50.8, 116.84), (50.8, -116.84), base_rotation = 180, yflip = True, zflip = False)
##calspheregongpio = xpsactuators.Gpio(xps_controller2, input_analog_channel="GPIO2.ADC1",output_analog_channel="GPIO2.DAC1",output_digital_channel = "GPIO1.DO", digital_channel = 1)
##calspheregoniometer = xpsactuators.M2Goniometer(calspheregongpio, label = 'Cal Sphere Goniometer')
calspheregonbreak = xpsactuators.Gpio(xps_controller2,output_digital_channel = "GPIO1.DO", digital_channel = 5)
calspheregoniometer = xpsactuators.PobCalGoniometer(xps_controller2,"CalGon.Pos",calspheregonbreak, speed=1.0, label = 'Cal Sphere Gon.')
calspherermotor = xpsactuators.M2CalRotation(xps_controller2,"CalRot.Pos",speed=20, label = 'Cal Sphere Rotation',xpsdirectionflip = True)


print 'Initializing Retro Sphere Motors'
cretz1 = capgauge.Capgauge(0,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For RetZ1 NanoPZ PZA12")  # the first parameter is the NI channel number
cretz2 = capgauge.Capgauge(1,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For RetZ2 NanoPZ PZA12")
cretz3 = capgauge.Capgauge(2,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For RetZ3 NanoPZ PZA12")
cretA = capgauge.Capgauge(3, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For RetA NanoPZ PZA12")
cretB = capgauge.Capgauge(4, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For RetB NanoPZ PZA12")

retAmotor = pzc200.Pza12(pza_controller,1,1,position_sensor=cretA,name="RetroA",  label = 'Retro Sphere A Axis', correction = None, correction_minus = None)
retBmotor = pzc200.Pza12(pza_controller,2,1,position_sensor=cretB,name="RetroB",  label = 'Retro Sphere B Axis', correction = None, correction_minus = None)
retzmotor1 = pzc200.Pza12(pza_controller,1,3,position_sensor=cretz1,name="RetroZ1", label = 'Retro Sphere Z1 Axis', correction = None, correction_minus = None)
retzmotor2 = pzc200.Pza12(pza_controller,2,3,position_sensor=cretz2,name="RetroZ2", label = 'Retro Sphere Z2 Axis', correction = None, correction_minus = None)
retzmotor3 = pzc200.Pza12(pza_controller,3,3,position_sensor=cretz3,name="RetroZ3", label = 'Retro Sphere Z3 Axis', correction = None, correction_minus = None)


retsphere = pzc200.GroupMovements(retAmotor, retBmotor, retzmotor1, retzmotor2, retzmotor3, (126.06, 99.1616), (22.86, -158.75), (-148.9202, 59.5884), base_rotation = 0, yflip = True, zflip = False)

retspheregonbreak = xpsactuators.Gpio(xps_controller2,output_digital_channel = "GPIO1.DO", digital_channel = 4)
retgonsafety = xpsactuators.SafetySwitch(xps_controller2, input_digital_connector = 'GPIO1.DI', digital_channel = 2)
retspheregoniometer = xpsactuators.PobRetGoniometer(xps_controller2,"RetGon.Pos",retspheregonbreak, retgonsafety, speed=1.0, label = 'Retro Sphere Gon.')
retspherermotor = xpsactuators.PobRetRotation(xps_controller2,"RetRot.Pos",speed=40, label = 'Retro Sphere Rotation',xpsdirectionflip = True)
##retsphere.goniometer = retspheregoniometer
##retsphere.rmotor = retspherermotor


print 'Initializing Loader Motor'
partloadmotor = xpsactuators.POBPartLoader(xps_controller1,"Loader.Pos",speed=7.12, label = 'Loader',xpsdirectionflip = True)



print 'Initializing Transmission Sphere Motors'
tsz1 = capgauge.Capgauge(5,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For TSZ1 NanoPZ PZA12")
tsz2 = capgauge.Capgauge(6,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For TSZ2 NanoPZ PZA12")
tsz3 = capgauge.Capgauge(7,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For TSZ3 NanoPZ PZA12")

tszpos1 = capgauge.MotorDummy(tsz1, label = 'TS Z Pos 1')
tszpos2 = capgauge.MotorDummy(tsz2, label = 'TS Z Pos 2')
tszpos3 = capgauge.MotorDummy(tsz3, label = 'TS Z Pos 3')
tsavgzpos = capgauge.AvgSensor([tsz1,tsz2,tsz3])
tszposavg = capgauge.MotorDummy(tsavgzpos, label = '   TS Z CG')
tsxmotor = xpsactuators.Pob_ts(xps_controller2,"TSX.Pos", label = 'TS X Axis')
tsymotor = xpsactuators.Pob_ts(xps_controller2,"TSY.Pos", label = 'TS Y Axis',xpsdirectionflip = True)
tszmotor = xpsactuators.Pob_ts_z(xps_controller2,"TSZ.Pos", label = 'TS Z Axis',xpsdirectionflip = True)
tszencpos = TSzMotorDummy(tszmotor, label = '   TS Z Encoder')

print 'Initializing Conjugate Transfer'
#cctz1 = capgauge.Capgauge(7,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CTZ1 NanoPZ PZA12")  # the first parameter is the NI channel number
#cctz2 = capgauge.Capgauge(5,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CTZ2 NanoPZ PZA12")
#cctz3 = capgauge.Capgauge(6,serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CTZ3 NanoPZ PZA12")
#cctA = capgauge.Capgauge(5, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CTA NanoPZ PZA12")
#cctB = capgauge.Capgauge(6, serial_number="", ni_config_file = NI_config_file_path ,name="Cap Sensor For CTB NanoPZ PZA12")

#ctAmotor = pzc200.Pza12(pza_controller,1,1,position_sensor=cctA,name="CTA",  label = 'CT A Axis', correction = None, correction_minus = None)
#ctBmotor = pzc200.Pza12(pza_controller,2,1,position_sensor=cctB,name="CTB",  label = 'CT B Axis', correction = None, correction_minus = None)
#ctzmotor1 = pzc200.Pza12(pza_controller,1,3,position_sensor=cctz1,name="CTZ1", label = 'CT Z1 Axis', correction = None, correction_minus = None)
#ctzmotor2 = pzc200.Pza12(pza_controller,2,3,position_sensor=cctz2,name="CTZ2", label = 'CT Z2 Axis', correction = None, correction_minus = None)
#ctzmotor3 = pzc200.Pza12(pza_controller,3,3,position_sensor=cctz3,name="CTZ3", label = 'CT Z3 Axis', correction = None, correction_minus = None)

# Initializing power reset function.
pzaresetgpio = xpsactuators.Gpio(xps_controller2,output_digital_channel = "GPIO1.DO", digital_channel = 1)
pzapower = xpsactuators.PZAPower(pzaresetgpio)



# Objects to be used via a gui
motorlist = [retsphere.xmotor,
             retsphere.ymotor,
             retsphere.zmotor1,
             retsphere.zmotor2,
             retsphere.zmotor3,
             retspherermotor,
             retspheregoniometer,
             calsphere.xmotor,
             calsphere.ymotor,
             calsphere.zmotor1,
             calsphere.zmotor2,
             calsphere.zmotor3,
             calspherermotor,
             calspheregoniometer,
             tsxmotor,
             tsymotor,
             tszmotor,
             tszpos1,
             tszpos2,
             tszpos3,
             Amotor,
             Bmotor,
             zmotor1,
             zmotor2,
             zmotor3,
             lrmotor,
             partloadmotor]

partobjects = pzc200.GroupWrapper(part, 'Part')
calobjects = pzc200.GroupWrapper(calsphere, 'Cal')
retobjects = pzc200.GroupWrapper(retsphere, 'Ret')

retobjects.movex.use_position_sensors(True)
retobjects.movey.use_position_sensors(True)
retobjects.movez.use_position_sensors(True)
retobjects.tiltx.use_position_sensors(True)
retobjects.tilty.use_position_sensors(True)

paxislist = [partobjects.movex,
            partobjects.movey,
            partobjects.movez,
            partobjects.tiltx,
            partobjects.tilty,
            partobjects.rotate]

motorgroups = [part, retsphere]

axislist = [retobjects.movex,
            retobjects.movey,
            retobjects.movez,
            retobjects.tiltx,
            retobjects.tilty,
            retspheregoniometer,
            retspherermotor,
            tsxmotor,
            tsymotor,
            tszmotor,
            partobjects.movex,
            partobjects.movey,
            partobjects.movez,
            partobjects.tiltx,
            partobjects.tilty,
            partobjects.rotate]

calaxislist = [calobjects.movex,
               calobjects.movey,
               calobjects.movez,
               calobjects.tiltx,
               calobjects.tilty,
               calspheregoniometer,
               calspherermotor]

retaxislist = [retobjects.movex,
               retobjects.movey,
               retobjects.movez,
               retobjects.tiltx,
               retobjects.tilty,
               retspheregoniometer,
               retspherermotor]

tsaxislist = [tsxmotor,
              tsymotor,
              tszmotor,
              tszposavg,
              tszencpos,
              tszpos1,
              tszpos2,
              tszpos3]

"""
motorlist = [calsphere.xmotor,
             calsphere.ymotor,
             calsphere.zmotor1,
             calsphere.zmotor2,
             calsphere.zmotor3,
             calspheregoniometer,
             calspherermotor,
             retsphere.xmotor,
             retsphere.ymotor,
             retsphere.zmotor1,
             retsphere.zmotor2,
             retsphere.zmotor3,
             retspheregoniometer,
             retspherermotor,
             part.xmotor,
             part.ymotor,
             part.zmotor1,
             part.zmotor2,
             part.zmotor3,
             part.rmotor,
             tsxmotor,
             tsymotor,
             tszmotor,
             partloadmotor]

motorgroups = [part, calsphere, retsphere, ts]

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
"""

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
#__all__ = ['cgh','part','reference','pzapower', 'saveoffset','loadoffset']



