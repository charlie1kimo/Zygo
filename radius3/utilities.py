"""
utilities.py
	This file includes the utilities constants, classes, and funcitons for
	supporting basic operations (such as console output, config parsing, and debugging
	
Author: Charlie Chen
"""
import ConfigParser
import os
import platform
import re
import sys
import traceback

from ompy.omsys import compinfo
import ompy.equ
import tagfile

######### CONSTANTS ##########
GLASS_TYPES = {"BAL35Y": 57e-7,
			"BK7": 7.1e-6,
			"Calcium_Fluoride": 1.67e-5,
			"F2": 8.7e-6,
			"FK5": 9.2e-6,
			"Fused_Silica": 5.2e-7,
			"LF5": 9.1e-6,
			"PBL25Y": 8.7e-6,
			"S-FSL5Y": 8.9e-6,
			"ULE": 0.0,
			"Zerodur": 0.0}			# from C:\WRK\CTE_INFO.DAT
DEFAULT_SECTION = 'cmd'
PART_SECTION = 'part_info'
CONFIG_HELP = \
"""#########################################################################################
# sample config files format:
# with possible options separated by ","
#
# [cmd]			# general options
#	test_bench = NAME (default = "")
#	wave_shift = True: wave_shift; False: Normal
#	debug = True: debug on; False: debug off
#	demo = True: demo on; False: demo off
#	printer_name: NAME (default = "PRN:"
#
# [part_info]	# part information setup
#	omase_path = PATH (default = "")
#	name = NAME (default = "")
#	book_title = NAME (default = "")
#	surface = SURFACE (default = "")
#	id = PART_SERIAL_NUMBER (default = "")
#	user = NAME (default = "")
#	glass_type = TYPE (default = "")
#	cte = (float) coefficient of thermal expansion
#	target_temp = (float) target temp (deg C) for CTE calculation
#	part_radius = (float) Test Optic Radius
#	ts_radius = (float) Transmission Sphere Radius
#
# [dmi_info]	# DMI setup
#	*Have @sub-parts "com_info"
#	dmi_type = ZMI1000, AXIOM, ZMI2000
#	dmi_sense = (float)
#	num_dmi_channels = (int)
#
# [phase_info]	# phaser setup
#	*Have @sub-parts "com_info"
#	phase_type = OpticodePCS / MetroPro
#	connection_type = 'ncacn_ip_tcp' (if it's MetroPro)
#	ip =  IP
#	port = port
#
# [ws_info]		# weather station setup
#	*Have @sub-parts "com_info"
#	ws_type = PerceptionII, Wex
#	part_temp_probe = 'T.newporttr3' (default the same with temp_probe)
#	temp_probe = 'T.newporttr3' (by default, can be changed)
#	press_probe = 'P.newporttr3' (by default, can be changed)
#	humid_probe = 'H.newporttr3' (by default, can be changed)
#	temp_override = True: override temperature;
#	press_override = True: override pressure;
#	humid_override = True: override humidity;
#	temp_comp = (float) temperature compensation (degree C) (default = 0.0)
#	press_comp = (float) pressure compensation (mmHg) (default = 0.0)
#	humid_comp = (float) humidity compensation (%) (default = 0.0)
#
# @sub-parts
# com_info:
#	com_info.use_rs232 = True; False
# 	com_info.com_port = COM#
# 	com_info.baud_rate = (int)
# 	com_info.data_bits = FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
# 	com_info.parity = PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
# 	com_info.stop_bits = STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
# 	com_info.timeout = (int) seconds
#	com_info.handshake = NO_HANDSHAKE, BOTH, RTS_CTS, DSR_DTR
#	com_info.buffer_size = (int)
# 	com_info.tcp_host = HOSTNAME
# 	com_info.tcp_port = (int)
#	com_info.trace = True; False
#########################################################################################

"""
PROG_DESCRIPTION = \
"""
This Unified Radius Measurement Program integrates Distance Measuring Interferometer (DMI), weather station, and 
phase station to gather different data in order to perform the radius measurement for a given glass. The previous 
two versions (1.0 and 2.0) are developed in C programming language, and the current version (3.0) rewrites everything 
in Python for easier maintainence and enhancement. The program has the follwoing basic functionality:
    1. communicating to DMI machine and gets the position measured.
    2. communicating to environment database and gather the environment variables for focus correction measurements.
    3. performing the normal uncorrected radius measurements, focus corrected measurements, and gap measurements.
This program designs a user-friendly graphical user interface that allows the operator to navigate the menu more easily 
to perform the radius measurements.
"""
LICENSE = \
"""
(C) 2013 Zygo Corporation, all right reserved
"""
###########################

##### classes #####
###################################
# OutputBuffer:
#	The wrapper class for printing to Console and target text area within a wx.Frame
###################################
class OutputBuffer(object):
	# __init__
	# @Purpose:
	#	class constructor
	# @Inputs:
	#	frame = (wx.Frame) the output frame flushing out to.
	def __init__(self, frame=None):
		self.buffer = ""
		self.frame = frame
		
	def setFrame(self, frame):
		self.frame = frame
	
	def write(self, msg):
		msg += "\n"
		self.buffer += msg
		sys.stdout.write(msg)
	
	def printOut(self):
		if self.frame != None:
			prevBuffer = self.frame.out_buffer.GetValue()
			self.frame.out_buffer.SetValue(prevBuffer+self.buffer)
			self.frame.out_buffer.SetInsertionPointEnd()			# move cursor to end
		
	def flush(self):
		self.buffer = ""
	
	def printOutAndFlush(self):
		self.printOut()
		self.flush()
	
	def writePrintOutFlush(self, msg):
		self.write(msg)
		self.printOutAndFlush()

		
##### functions #####
########################################
# parseConfig:
#	parse the given config file
########################################
def parseConfig(file, cmdParameters, printBuffer=OutputBuffer(), debug=False):
	config = ConfigParser.RawConfigParser()
	config.read(file)

	if debug:
		printBuffer.write("Reading config files from: "+file)
		printBuffer.write("...")
		
	partParameters = cmdParameters.part_info
	
	# read the config file:
	for sect in config.sections():
		for opt in config.options(sect):
			if sect == PART_SECTION:
				partParameters.initialized = True
				varName = 'partParameters.'+opt
			elif sect == DEFAULT_SECTION:
				varName = 'cmdParameters.'+opt
			else:
				varName = 'cmdParameters.'+sect+'.'+opt
				
			typeCompare = eval("type("+varName+")")			# determine the type of variable name
			value = config.get(sect, opt)
			optBase = opt.split('.')[-1]					# split to get the latest basename
			if typeCompare == unicode or typeCompare == str:
				value = "\"" + value + "\""
				
			exec(varName + "=" + value)					# execute the assignment
			
	# print all parameters for debug
	if debug:
		printBuffer.write("Command Parameters:")
		cmdParameters.printParameters()
		printBuffer.write("")


#################################################################################################
# getMaterialCTE
# @Purpose:
#	get the materials' CTE
# @Outputs:
#	return a dictionary of all materials and CTE values.
def getMaterialCTE():
	materialsCFG = compinfo['omasepath'] + '/AuxFiles/MastrCfg/MaterialProperties.cfg'
	return tagfile.CfgRead(materialsCFG)['#blocks#']			# weirdo config file with section '#block'...


#################################################################################################
# getPartNameAndSurface
# @Purpose:
#	get the part name and surface from omase path
# @Inputs:
#	path = omase path
# @Outputs:
#	returns part name
def getPartNameAndSurface(path):
	path = os.path.splitdrive(path)[1]
	if re.search('Windows', platform.architecture()[1]):
		delimiter = '\\'
	else:
		delimiter = '/'
	partNameList = path.split(delimiter)[2:]
	surface = partNameList.pop().upper()
	partName = "/".join(partNameList)
	return (partName, surface)


#################################################################################################
# readPartMasterCfg:
# @Purpose:
#	read the part master config file...
# @Inputs:
#	path = part master config file path
# @Outputs:
#	a dictionary of master cfg with: keys = variable / blocks, values = values / sub-blocks
#	e.g. { 'a': '1', 'b': {'c': '2'} }
#	None if there's ERROR
#################################################################################################
def readPartMasterCfg(path, wxWindow=None):
	(partName, surface) = getPartNameAndSurface(path)
	# read the part master config
	masterCFGPath = compinfo['surdirspath']+'/'+partName+'/RGEN/SETUP/MASTER.cfg'
	try:
		# opening the master config:
		f = open(masterCFGPath, 'r')
		masterCFG = {}
		blockList = []							# stack-like list
		for line in f:
			line = line.lstrip()
			if re.match('^[#!]', line):			# omit the comments
				continue
			elif len(line) == 0:
				continue

			line = line.split('#')[0].rstrip()	# omit the trailing comments
			var = line.split('=')[0].rstrip()
			value = line.split('=')[1].lstrip()
			if var == 'Begin_Block':		# starting of a block
				tempDict = masterCFG
				for block in blockList:		# recursive search the nested blocks
					tempDict = tempDict[block]
				tempDict[value] = {}		# finally create the new dictionary
				tempDict = tempDict[value]
				blockList.append(value)
			elif var == 'End_Block':		# ending of a block
				if value != blockList[-1]:	# unclosed block
					errTitle = 'ERROR: Malformed Master Config'
					errMsg = 'ERROR: Malformed master config in %s!!!\n Some block does not close!!!\n Please manually setup this part information.' % path
					if wxWindow != None:
						wxWindow.popErrorBox(errTitle, errMsg)
					else:
						print errTitle + '\n\n' + errMsg
					return None
				else:						# closed block
					blockList.pop()
			else:							# var = value line
				tempDict = masterCFG
				if len(blockList) > 0:		# in the nested block, figure out current dictionary
					for block in blockList:		# recursive
						tempDict = tempDict[block]

				# just assign var = value
				tempDict[var] = value
		f.close()

		# setup part radius...
		try:
			equObj = ompy.equ.Equ('master')
			masterCFG['part_radius'] = equObj.get_bfr()
		except Exception, e:						# we don't have a part radius...
			masterCFG['part_radius'] = 0.0

		return masterCFG

	except Exception, e:
		errTitle = 'ERROR'
		errMsg = 'ERROR: Reading master config: %s error!!!\n Please manually setup the part info.' % path
		if wxWindow != None:
			wxWindow.popErrorBox(errTitle, errMsg)
		else:
			print errTitle + '\n\n' + errMsg

		print traceback.format_exc()
		return None
