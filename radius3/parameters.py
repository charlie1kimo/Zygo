"""
parameters.py
	This file contains classes for setting up input parameters.
	
Author: Charlie Chen
"""

from radius3.utilities import OutputBuffer
import radius3.utilities as utilities

# class Parameters
#	Abstract class for all parameters
class Parameters(object):
	_fields_ = []
	
	def __init__(self, printBuffer=OutputBuffer()):
		self.printBuffer = printBuffer
	
	# return a list of ALL variable names
	def getVarNames(self):
		nameList = []
		for p in self._fields_:
			name = p[0]
			typeP = p[1]
			if typeP != str and typeP != bool and \
				typeP != int and typeP != float:
				l = eval("self."+name+".getVarNames()")
				for i in l:
					nameList.append(name+"."+i)
			else:
				nameList.append(name)
		return nameList
	
	def printParameters(self):
		for n in self.getVarNames():
			self.printBuffer.write(n + " = " + str(eval("self."+n)))


# class PartInfo
class PartInfo(Parameters):
	_fields_ = [("omase_path", str),
				("name", str), 
				("book_title", str),
				("surface", str), 
				("id", str),
				("user", str),
				("glass_type", str),
				("cte", float),
				("target_temp", float),
				("part_radius", float),
				("ts_radius", float),
				("initialized", bool)]

	def __init__(self, printBuffer=OutputBuffer()):
		self.omase_path = ""	# part stored omase path (String)
		self.name = ""			# part identification (String)
		self.book_title = ""		# part "book name" (String)
		self.surface = 	""		# which side is being measured (String)
		self.id = ""			# part serial number (String)
		self.user = ""			# name of Operator (String)
		self.glass_type = ""	# Name of the glass selected (String)
		self.cte = 0.0			# Coefficient of Thermal Expansion (double)
		self.target_temp = 22.0	# target temp (deg C) for CTE calculation (double)
		self.part_radius = 0.0	# Test Optic Radius (double)
		self.ts_radius = 0.0	# Transmission Sphere Radius (double)
		self.initialized = False	# data has been pre initialized (int)
		super(PartInfo, self).__init__(printBuffer)

# class ComInfo
class ComInfo(Parameters):
	_fields_ = [("use_rs232", bool),
				("com_port", str),
				("baud_rate", int),
				("data_bits", str),
				("parity", str),
				("stop_bits", str),
				("timeout", int),
				("handshake", str),
				("buffer_size", int),
				("tcp_host", str),
				("tcp_port", int),
				("trace", bool)]

	def __init__(self, COM="COM1", timeout=5, bufferSize=80, useRs232=True, printBuffer=OutputBuffer()):
		self.use_rs232 = useRs232
		self.com_port = COM										# from the xc.h's ComPort enum
		self.baud_rate = 9600									# from the xc.h's BaudRate enum
		self.data_bits = "EIGHTBITS"							# from the xc.h's DataBits enum
		self.parity = "PARITY_NONE"								# from the xc.h's Parity enum
		self.stop_bits = "STOPBITS_TWO"							# from the xc.h's StopBits enum
		self.timeout = timeout									# seconds (in python)
		self.handshake = "NO_HANDSHAKE"							# from the xc.h's FlowControl enum
		self.buffer_size = bufferSize
		self.tcp_host = "localhost"
		self.tcp_port = 0
		self.trace = False
		super(ComInfo, self).__init__(printBuffer)

# class DmiInfo
class DmiInfo(Parameters):
	_fields_ = [("com_info", ComInfo),
				("dmi_type", str),
				("dmi_sense", float),
				("num_dmi_channels", int)]
	
	def __init__(self, printBuffer=OutputBuffer()):
		self.com_info = ComInfo("COM3", printBuffer=printBuffer)
		self.dmi_type = "ZMI1000"
		self.dmi_sense = 1.0
		self.num_dmi_channels = 1
		super(DmiInfo, self).__init__(printBuffer)
		
# class PhaseInfo
class PhaseInfo(Parameters):
	_fields_ = [("com_info", ComInfo),
				("phase_type", str),
				("connection_type", str),
				("ip", str),
				("port", str)]
				
	def __init__(self, printBuffer=OutputBuffer()):
		self.com_info = ComInfo("COM4", 10, 9*1024, printBuffer=printBuffer)
		self.phase_type = "OpticodePCS"
		self.connection_type = "ncacn_ip_tcp"
		self.ip = ""
		self.port = ""
		super(PhaseInfo, self).__init__(printBuffer)
		
# class WsInfo
class WsInfo(Parameters):
	_fields_ = [("com_info", ComInfo),
				("ws_type", str),
				("part_temp_probe", str),
				("temp_probe", str),
				("press_probe", str),
				("humid_probe", str),
				("temp_override", bool),
				("press_override", bool),
				("humid_override", bool),
				("temp_comp", float),
				("press_comp", float),
				("humid_comp", float)]
				
	def __init__(self, printBuffer=OutputBuffer()):
		self.com_info = ComInfo("COM6", useRs232=False, printBuffer=printBuffer)
		self.ws_type = "Wex"
		self.part_temp_probe = 'T.newporttr3'
		self.temp_probe = 'T.newporttr3'
		self.press_probe = 'P.newporttr3'
		self.humid_probe = 'H.newporttr3'
		self.temp_override = False		# False -> No asking for override; True -> Asks for new temperature
		self.press_override = False
		self.humid_override = False
		self.temp_comp = 0.0			# compensation for weather station */
		self.press_comp = 0.0			# Pressure offset from Standard barometer - units mmHg
		self.humid_comp = 0.0			# Humidity offset from weather station - units %
		super(WsInfo, self).__init__(printBuffer)
		
# class CmdParameters
class CmdParameters(Parameters):
	_fields_ = [("test_bench", str),
				("wave_shift", bool),
				("debug", bool),
				("demo", bool),
				("printer_name", str),
				("part_info", PartInfo),
				("dmi_info", DmiInfo),
				("phase_info", PhaseInfo),
				("ws_info", WsInfo)]

	def __init__(self, printBuffer=OutputBuffer()):
		self.test_bench = ""		# test bench name/number
		self.wave_shift = False		# False = normal phase station, True = Wave Shift
		self.debug = False			# True = debugging - extra stuff printed to screen
		self.demo = False 				# turn on if no hardware attached
		self.printer_name = "PRN:"
		self.part_info = PartInfo(printBuffer=printBuffer)
		self.dmi_info = DmiInfo(printBuffer=printBuffer)
		self.phase_info = PhaseInfo(printBuffer=printBuffer)
		self.ws_info = WsInfo(printBuffer=printBuffer)
		super(CmdParameters, self).__init__(printBuffer)
		
	def saveParameters(self, file):
		helpStr = utilities.CONFIG_HELP
		f = open(file, 'w+')
		f.write(helpStr)
		# saving the sections
		f.write("[%s]\n" % utilities.DEFAULT_SECTION)
		curr_section = utilities.DEFAULT_SECTION
		for i in self.getVarNames():
			name = i
			val = eval("self."+i)
			if type(val) != str and type(val) != unicode:
					val = repr(val)
			elif type(val) == str and type(val) == unicode and len(val) == 0:
				continue
					
			if len(i.split('.')) > 1:
				name = '.'.join(i.split('.')[1:])
				if curr_section != i.split('.')[0]:
					curr_section = i.split('.')[0]
					f.write("\n[%s]\n" % curr_section)
					
			f.write(name+" = "+val+"\n")
		
		f.close()

