#!/usr/bin/env python
"""
radius_measure_main.py
	This file sets up the command line options for starting the radius program.
	The command line interface is NOT implemented, yet.
Author: Charlie Chen
"""
__version__ = '3.1.0'
__owner__ = 'cchen'
'''
History:
3/4/2013	cchen	first documentation
'''

import optparse

from ompy import omsys
from radius3.parameters import CmdParameters
from radius3.gui.radius_app import *
from radius3.utilities import OutputBuffer
import radius3.utilities as utilities

# Main Section:
# command line options
usage = "Usage: %prog [options] [finddir_seg]"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-c", "--temperature", dest="temperature",
				help="Temperature Compensation Value (deg c); -0.04 for example\
					Compensation = (Temperature Standard) - (Weather Station)",
				metavar="TEMPERATURE")
parser.add_option("-l", "--direction", dest="direction",
				help="Direction Sense of DMI Counter; -1 Reverse Direction Sense",
				metavar="DIRECTION")
parser.add_option("-s", "--waveShift", dest="waveShift",
				action="store_true", default=False,
				help="Set to True if it's Wave Shifting station; normal station by default")
parser.add_option("-t", "--name", dest="name",
				help="Set Test Bench Name",
				metavar="BENCHNAME")
parser.add_option("-o", "--pressure", dest="pressure",
				help="Pressure Compensation Value (mmHg) \
						Compensation = (Pressure Standard) - (Weather Station)",
				metavar="PRESSURE")
parser.add_option("-H", "--humidity", dest="humidity",
				help="Humidity Compensation Value (%) \
						Compensation = (Humidity Standard) - (Weather Station)",
				metavar="HUMIDITY")
parser.add_option("-r", "--override", dest="override",
				action="store_true", default=False,
				help="Ask for temperature override value during radius measurement")
parser.add_option("-d", "--dmi", dest="dmi",
				help="Set DMI com port to COM \"PORT\". Default is COM3",
				metavar="PORT")
parser.add_option("-p", "--opticode", dest="opticode",
				help="Set Opticode COM port to COM \"PORT\". Default is COM4",
				metavar="PORT")
parser.add_option("-w", "--weather", dest="weather",
				help="Set Weather station COM port to COM \"PORT\". Default is COM6",
				metavar="PORT")
parser.add_option("-e", "--demo", dest="demo",
				action="store_true", default=False,
				help="Demo mode (no hardware)")
parser.add_option("-f", "--file", dest="file",
				default="C:\\omase\\Machinfo\\radius3.cfg",					# CHANGE HERE FOR ACTUAL PATH!
				#default="C:\\svn\\src\\omMeas\\trunk\\ORM\\Orm6\\python\\radius.cfg",
				help="Config file path",
				metavar="CONFIGFILE")
parser.add_option("-v", "--verbose", dest="verbose",
				action="store_true", default=False,
				help="verbose mode (debugging)")
parser.add_option("-D", "--ddmi", dest="ddmi",
				action="store_true", default=False,
				help="Debug DMI")
parser.add_option("-P", "--dopticode", dest="dopticode",
				action="store_true", default=False,
				help="Debug Opticode")
parser.add_option("-W", "--dweather", dest="dweather",
				action="store_true", default=False,
				help="Debug Weather Station")
(options, args) = parser.parse_args()

# print buffer
printBuffer = OutputBuffer()
# cmd parameters
cmdParameters = CmdParameters(printBuffer)

# read the config file if there is one.
if options.file:
	utilities.parseConfig(options.file, cmdParameters, printBuffer, options.verbose)

# proceed to command line settings
# (overrides the default config file!)
if options.temperature:
	cmdParameters.ws_info.temp_comp = float(options.temperature)
if options.direction:
	cmdParameters.dmi_info.dmi_sense = float(options.direction)
if options.waveShift:
	cmdParameters.wave_shift = options.waveShift
if options.name:
	cmdParameters.test_bench = options.name
if options.pressure:
	cmdParameters.ws_info.press_comp = float(options.pressure)
if options.humidity:
	cmdParameters.ws_info.humid_comp = float(options.humidity)
if options.override:
	cmdParameters.ws_info.temp_override = options.override
if options.dmi:
	cmdParameters.dmi_info.com_info.com_port = options.dmi
if options.opticode:
	cmdParameters.phase_info.com_info.com_port = options.opticode
if options.weather:
	cmdParameters.ws_info.com_info.com_port = options.weather
if options.demo:
	cmdParameters.demo = options.demo
if options.ddmi:
	cmdParameters.dmi_info.com_info.trace = options.ddmi
if options.dopticode:
	cmdParameters.phase_info.com_info.trace = options.dopticode
if options.dweather:
	cmdParameters.ws_info.com_info.trace = options.dweather

# proceed to command line arguments settings
if len(args) > 0:
	finddir_seg = " ".join(args)
	omase_path = omsys.finddir(finddir_seg)
	# setup the finddir part info.
	if omase_path != None:
		cmdParameters.part_info.omase_path = omase_path
		cmdParameters.part_info.book_title = omsys.getbooktitle()
		(partName, surface) = utilities.getPartNameAndSurface(omase_path)
		cmdParameters.part_info.name = partName
		cmdParameters.part_info.surface = surface
		masterCFG = utilities.readPartMasterCfg(omase_path)
		if masterCFG != None:
			materialDict = utilities.getMaterialCTE()
			cmdParameters.part_info.glass_type = masterCFG['SubMatl']
			cmdParameters.part_info.cte = float(materialDict[cmdParameters.part_info.glass_type]['CTE'])
			cmdParameters.part_info.part_radius = float(masterCFG['part_radius'])

# start main gui:
app = AppRadius(cmdParameters, printBuffer, options.verbose)
app.MainLoop()
