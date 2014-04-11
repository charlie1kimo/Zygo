"""
usb_temperature.py
	This module contains the class to access the Measurement Computing Corp. USB temperature measuring device.
"""

import struct
import sys
import time
import usb.core
import usb.util
import traceback

class USB_TEMP(object):
	"""
	USB_TEMP class:
		this class defined the basic accessment for the Measurement Computing Corp. USB TEMP
		measuring device
	"""
	# information from lsusb
	__inAddr = 1
	__outAddr = 0x81
	__interfaceNum = 0
	__delay = 100
	# commands taken from usb-temp.h (C driver files from Measurement Computing Corp.)
	commands = {
				# Digital I/O Commands
				'DCONFIG': chr(0x01),				# Configure digital port
				'DCONFIG_BIT': chr(0x02),			# Configure individual digital port bits
				'DIN': chr(0x03),					# Read digital port
				'DOUT': chr(0x04),					# Write digital port
				'DBIT_IN': chr(0x05),				# Read digital port bit
				'DBIT_OUT': chr(0x06),				# Write digital port bit

				'TIN': chr(0x18),					# Read input channel
				'TIN_SCAN': chr(0x19),				# Read multiple input channels

				# Memory Commands
				'MEM_READ': chr(0x30),				# Read Memory
				'MEM_WRITE': chr(0x31),				# Write Memory

				# Miscellaneous Commands
				'BLINK_LED': chr(0x40),				# Causes LED to blink
				'RESET': chr(0x41),					# Reset USB interface
				'GET_STATUS': chr(0x44),			# Get device status
				'SET_ITEM': chr(0x49),				# Set a configuration item
				'GET_ITEM': chr(0x4A),				# Get a configuration item
				'CALIBRATE': chr(0x4B),				# Perform a channel calibration
				'GET_BURNOUT_STATUS': chr(0x4C),	# Get thermocopule burnout detection status

				# Code Update Commands
				'PREPARE_DOWNLOAD': chr(0x50),		# Prepare for program memory download
				'WRITE_CODE': chr(0x51),			# Write program memory
				'WRITE_SERIAL': chr(0x53),			# Write a new serial number to device
				'READ_CODE': chr(0x55)				# Read program memory
				}
	# channels definitions in the device
	channels = {
				'CH0': chr(0x0),					# Channel 0
				'CH1': chr(0x1),					# Channel 1
				'CH2': chr(0x2),					# Channel 2
				'CH3': chr(0x3),					# Channel 3
				'CH4': chr(0x4),					# Channel 4
				'CH5': chr(0x5),					# Channel 5
				'CH6': chr(0x6),					# Channel 6
				'CH7': chr(0x7),					# Channel 7
				'CJC0': chr(0x80),					# Cold Junction Compensator 0
				'CJC1': chr(0x81)					# Cold Junction Compensator 1
				}
	# device's items constants
	items = {
			# Configuration Items
			'ADC_0': chr(0x0),						# Setting for ADC 0
			'ADC_1': chr(0x1),						# Setting for ADC 1
			'ADC_2': chr(0x2),						# Setting for ADC 2
			'ADC_3': chr(0x3),						# Setting for ADC 3

			# Sub Items
			'SENSOR_TYPE': chr(0x00),				# Sensor type  Read Only
			'CONNECTION_TYPE': chr(0x01),			# Connection type - RTD & Thermistor
			'FILTER_RATE': chr(0x02),				# Filter update rate
			'EXCITATION': chr(0x03),				# Curret excitation
			'VREF': chr(0x04),						# Measured Vref value
			'I_value_0': chr(0x05),					# Measured I value @ 10uA
			'I_value_1': chr(0x06),					# Measured I value @ 210uA
			'I_value_2': chr(0x07),					# Measured I value @ 10uA (3 wire connection)
			'V_value_0': chr(0x08),					# Measured V value @ 10uA
			'V_value_1': chr(0x09),					# Measured V value @ 210uA
			'V_value_2': chr(0x0a),					# Measured V value @ 210uA (3 wire conneciton)
			'CH_0_TC': chr(0x10),					# Thermocouple type for channel 0
			'CH_1_TC': chr(0x11),					# Thermocouple type for channel 1
			'CH_0_GAIN': chr(0x12),					# Channel 0 gain value
			'CH_1_GAIN': chr(0x13),					# Channel 1 gain value
			'CH_0_COEF_0': chr(0x14),				# Coefficient 0
			'CH_1_COEF_0': chr(0x15),				# Coefficient 0
			'CH_0_COEF_1': chr(0x16),				# Coefficient 1
			'CH_1_COEF_1': chr(0x17),				# Coefficient 1
			'CH_0_COEF_2': chr(0x18),				# Coefficient 2
			'CH_1_COEF_2': chr(0x19),				# Coefficient 2
			'CH_0_COEF_3': chr(0x1a),				# Coefficient 3
			'CH_1_COEF_3': chr(0x1b),				# Coefficient 3
			}
	# device's values constants
	values = {
			# Possible Values
			'RTD': chr(0x0),
			'THERMISTOR': chr(0x1),
			'THERMOCOUPLE': chr(0x2),
			'SEMICONDUCTOR': chr(0x3),
			'DISABLED': chr(0x4),

			'TWO_WIRE_ONE_SENSOR': chr(0x0),
			'TWO_WIRE_TWO_SENSOR': chr(0x1),
			'THREE_WIRE': chr(0x2),
			'FOUR_WIRE': chr(0x3),

			# Current excitation values
			'EXCITIATION_OFF': chr(0x0),
			'MU_A_10': chr(0x1),					# 10 micro Amps
			'MU_A_210': chr(0x2),					# 210 micro Amps

			# For connection types Semiconductor
			'SINGLE_ENDED': chr(0x00),
			'DIFFERENTIAL': chr(0x01),

			'FREQ_500_HZ': chr(0x1),
			'FREQ_250_HZ': chr(0x2),
			'FREQ_125_HZ': chr(0x3),
			'FREQ_62_5_HZ': chr(0x4),
			'FREQ_50_HZ': chr(0x5),
			'FREQ_39_2_HZ': chr(0x6),
			'FREQ_33_3_HZ': chr(0x7),
			'FREQ_19_6_HZ': chr(0x8),
			'FREQ_16_7_HZ': chr(0x9),
			#'FREQ_16_7_HZ': chr(0xa),
			'FREQ_12_5_HZ': chr(0xb),
			'FREQ_10_HZ': chr(0xc),
			'FREQ_8_33_HZ': chr(0xd),
			'FREQ_6_25_HZ': chr(0xe),
			'FREQ_4_17_HZ': chr(0xf),

			'TYPE_J': chr(0x0),
			'TYPE_K': chr(0x1),
			'TYPE_T': chr(0x2),
			'TYPE_E': chr(0x3),
			'TYPE_R': chr(0x4),
			'TYPE_S': chr(0x5),
			'TYPE_B': chr(0x6),
			'TYPE_N': chr(0x7),

			'GAIN_1X': chr(0x0),
			'GAIN_2X': chr(0x1),
			'GAIN_4X': chr(0x2),
			'GAIN_8X': chr(0x3),
			'GAIN_16X': chr(0x4),
			'GAIN_32X': chr(0x5),
			'GAIN_64X': chr(0x6),
			'GAIN_128X': chr(0x7)
			}

	def __init__(self, vendorID, productID):
		"""
		@Purpose:
			constructor
		@Inputs:
			vendorID = USB device's vendor ID
			productID = USB device's product ID
		"""
		self.__dev = usb.core.find(idVendor=vendorID, idProduct=productID)
		if self.__dev == None:
			raise usb.core.USBError("Error: Device 0x%x:0x%x NOT FOUND.", errno=-999)
		# try to detach the Human Interactive Device from Linux (automatically grabbed by Linux OS)
		try:
			self.__dev.detach_kernel_driver(0)
		except Exception, e:		# already detached.
			pass

	def __del__(self):
		"""
		destructor
		"""
		# try to attach back to Linux OS after done.
		not_detached = True
		while not_detached:
			try:
				self.__dev.detach_kernel_driver(0)
				not_detached = False
			except Exception, e:
				time.sleep(1)
			finally:
				self.__dev.attach_kernel_driver(0)

	def __send__(self, cmd):
		"""
		private method for wrapping usb device write.
		"""
		sentBytes = self.__dev.write(self.__inAddr, cmd, self.__interfaceNum)
		if sentBytes != len(cmd):
			raise usb.core.USBError("Error: Failed to send commands to USB.", errno=-99)

	def __recv__(self):
		"""
		private method for wrapping usb device read.
		"""
		ret_bytes_len = 256
		return self.__dev.read(self.__outAddr, ret_bytes_len, self.__interfaceNum)

	def __get_item__(self, channel, item):
		"""
		private method for getting set item for device
		"""
		cmd = self.commands['GET_ITEM'] + chr(channel/2) + item
		self.__send__(cmd)
		ret_array = self.__recv__()

		if chr(ret_array[0]) != self.commands['GET_ITEM']:
			self.reset()
			raise RuntimeError('Error: __get_item__() returns wrong commands (0x%x) return values, should be (0x%x).' % \
				(ret_array[0], ord(self.commands['GET_ITEM'])))
		time.sleep(2)

		ret_array.pop(0)
		byteStr = ""
		for i in ret_array:
			byteStr += chr(i)
		return struct.unpack('f', byteStr)[0]

	def __t_in__(self, channel):
		"""
		private method for getting temperature reading from device
		"""
		cmd = self.commands['TIN'] + chr(channel) + chr(0)		# command_TIN + channel + [0: temperature, 1: raw]
		self.__send__(cmd)
		ret_array = self.__recv__()

		if chr(ret_array[0]) != self.commands['TIN']:
			self.reset()
			raise RuntimeError('Error: __t_in__() returns wrong commands (0x%x) return values, should be (0x%x).' % \
				(ret_array[0], ord(self.commands['TIN'])))
		time.sleep(2)

		ret_array.pop(0)
		byteStr = ""
		for i in ret_array:
			byteStr += chr(i)
		return struct.unpack('f', byteStr)[0]

	def blinkLED(self):
		"""
		@Purpose:
			method to make device's LED blink.
		@Inputs:
			N/A
		@Outputs:
			N/A
		"""
		cmd = self.commands['BLINK_LED']
		self.__send__(cmd)
		time.sleep(2)

	def calibrate(self):
		"""
		@Purpose
			method to calibrate the device
		@Inputs:
			N/A
		@Outputs:
			N/A
		"""
		sys.stdout.write("Calibrating.")
		cmd = self.commands['CALIBRATE']
		self.__send__(cmd)
		time.sleep(1)
		while self.getStatus() != 0:
			time.sleep(1)
			sys.stdout.write(".")
		sys.stdout.write("done.")

	def getBurnoutStatus(self):
		"""
		@Purpose:
			method to get burnout status
		@Inputs:
			N/A
		@Outputs:
			(int) burnout status code
		"""
		cmd = self.commands['GET_BURNOUT_STATUS']
		self.__send__(cmd)
		ret_array = self.__recv__()
		if chr(ret_array[0]) != cmd:
			raise RuntimeError('Error: getBurnoutStatus() returns wrong commands (0x%x) return values, should be (0x%x).' % \
				(ret_array[0], ord(cmd)))

		time.sleep(1)			# rest time for device response
		return ret_array[1]

	def getSerialNumber(self):
		"""
		@Purpose:
			method to get serial number
		@Inputs:
			N/A
		@Outputs:
			(str) serialNumber
		"""
		str_len = 256
		return usb.util.get_string(self.__dev, str_len, self.__dev.iSerialNumber)

	def getStatus(self):
		"""
		@Purpose:
			method to return the status code (int) of device.
		@Inputs:
			N/A
		@Outputs:
			(int) status code
		"""
		cmd = self.commands['GET_STATUS']
		self.__send__(cmd)
		ret_array = self.__recv__()
		if chr(ret_array[0]) != cmd:
			raise RuntimeError('Error: getStatus() returns wrong commands (0x%x) return values, should be (0x%x).' % \
				(ret_array[0], ord(cmd)))

		return ret_array[1]

	def measureRTD(self, channel, wireType):
		"""
		@Purpose:
			measure the RTD temperature given channel and wire connection type
		@Inputs:
			channel: (int) [0-7]
			wireType: (str) choice from:
			['TWO_WIRE_ONE_SENSOR',
			'TWO_WIRE_TWO_SENSOR',
			'THREE_WIRE',
			'FOUR_WIRE']
		@Outputs:
			(float) temperature in Celcius.
		"""
		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['SENSOR_TYPE'] + self.values['RTD']
		self.__send__(cmd)
		try:
			wireType = self.values[wireType]
		except Exception, e:
			raise RuntimeError("Error: Please enter the correct wire type, choices from: \
							['TWO_WIRE_ONE_SENSOR','TWO_WIRE_TWO_SENSOR','THREE_WIRE','FOUR_WIRE']")

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CONNECTION_TYPE'] + wireType
		self.__send__(cmd)

		R0 = 100.0					# R0 value
		A = .003908					# Callendar-Van Dusen Coefficient A	
		B = -5.8019E-7				# Callendar-Van Dusen Coefficient B
		C = -4.2735E-12				# Callendar-Van Dusen Coefficient C
		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['EXCITATION'] +  self.values['MU_A_210']
		self.__send__(cmd)

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_%s_GAIN' % (channel%2)] + chr(0x2)						# Set 0 - 0.5V for RTD
		self.__send__(cmd)

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_%s_COEF_0' % (channel%2)] + struct.pack('f', R0)	# R0 value
		self.__send__(cmd)
		#ret_R0 = self.__get_item__(channel, self.items['CH_%s_COEF_0' % (channel%2)])
		#print "R0: %f" % ret_R0

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_%s_COEF_1' % (channel%2)] + struct.pack('f', A)	# Callendar-Van Dusen Coefficient A
		self.__send__(cmd)
		#ret_A = self.__get_item__(channel, self.items['CH_%s_COEF_1' % (channel%2)])
		#print "A: %f" % ret_A

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_%s_COEF_2' % (channel%2)] + struct.pack('f', B)		# Callendar-Van Dusen Coefficient B
		self.__send__(cmd)
		#ret_B = self.__get_item__(channel, self.items['CH_%s_COEF_2' % (channel%2)])
		#print "B: %f" % ret_B

		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_%s_COEF_3' % (channel%2)] + struct.pack('f', C)		# Callendar-Van Dusen Coefficient C
		self.__send__(cmd)
		#ret_C = self.__get_item__(channel, self.items['CH_%s_COEF_3' % (channel%2)])
		#print "C: %f" % ret_C

		time.sleep(1)
		temperature = self.__t_in__(channel)
		return temperature

	def measureThermocoupleTemperature(self, channel, thermocoupleType):
		"""
		@Purpose:
			measure the thermocouple's temperature given channel and thermocouple type
		@Inputs:
			channel: (int) [0-7]
			thermocoupleType: (str) choices from:
				['TYPE_J',
				'TYPE_K',
				'TYPE_T',
				'TYPE_E',
				'TYPE_R',
				'TYPE_S',
				'TYPE_B',
				'TYPE_N']
		@Outputs:
			(float) temperature in Celcius.
		"""
		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['SENSOR_TYPE'] + self.values['THERMOCOUPLE']
		self.__send__(cmd)
		cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['EXCITATION'] + self.values['EXCITIATION_OFF']
		self.__send__(cmd)
		#print "connect to thermocouple to channel %d." % channel

		if channel % 2 == 0:
			cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_0_TC'] + self.values[thermocoupleType]
		else:
			cmd = self.commands['SET_ITEM'] + chr(channel/2) + self.items['CH_1_TC'] + self.values[thermocoupleType]
		self.__send__(cmd)
		#print "%s thermocouple selected." % thermocoupleType

		temperature = self.__t_in__(channel)
		return temperature

	def reset(self):
		"""
		@Purpose:
			method to reset the device.
		@Inputs:
			N/A
		@Outputs:
			N/A
		"""
		cmd = self.commands['RESET']
		self.__send__(cmd)
