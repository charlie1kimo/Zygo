"""
dmi.py
	This file implements the Distance Measuring Interferometer (DMI)
	class to interface with the DMI machine
Author: Charlie Chen
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/4/2013	cchen	first documented
'''

import time
import traceback

from radius3.utilities import OutputBuffer
from radius3.rs232 import *


####################################################################
# class DMIPollingException
#	This class throws exception if DMI Poll returns "NOT READY"
####################################################################
class DMIPollingException(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "WARNING: DMIPollingException; expression = %s; %s\n" % (repr(self.expr), self.msg)


################################################################
# Decorator samplingIndicator:
#	contains (and process) wxWidget for indicating sampling DMI
################################################################
def samplingIndicator(funct, *args):
	def wrapper(self, *args):
		frame = self.printBuffer.frame
	
		if frame != None:
			frame.setDMIStatus('READING')
		try:
			ret = funct(self, *args)
		except DMIPollingException, e:
			if frame != None:
				frame.setDMIStatus('WARNING')
			raise e
		except Exception, e:
			if frame != None:
				frame.setDMIStatus('ERROR')
			raise e
		if frame != None:
			frame.setDMIStatus('A-OK')
			
		return ret
			
	return wrapper
		
#######################################################
# class DMI:
#	This class interfaces with DMI station
#######################################################
class DMI(RS232):
	# __init__: (raises Exceptions)
	# @Purpose:
	# 	constructor method:
	# @Arguments:
	#	params = (DmiInfo) DmiInfo parameters
	#	dmiType = (String) dmi type
	#	buffer_size = (int) size of the buffer
	#	debug = (boolean) turn debug on/off
	def __init__(self, params, printBuffer=OutputBuffer(), debug=False):
		# dmi control codes (from C file dmiLink.c)
		# only supporting ZMI1000 now...
		self.CONTROL_CODES = {"ZMI1000":{"ZERO": "*RST\n",
											"INITIALIZE": "RESTART\n",
											"CLEAR": "*CLS\n",
											"AVG": "AV?\n",
											"POLL": "*STB?\n",
											"SAMPLE": "SAM %d,%d,%c\n",
											"READ": "R? 1,G\n"}}
		self.CTS_IN = {"ZMI1000": 10272491.56, 
						"AXIOM": 10192237.72}
		
		super(DMI, self).__init__(params, printBuffer, debug)
		if self.debug:
			self.printBuffer.write("INFO: Initializing DMI...")
		self.cts_in = self.CTS_IN[self.params.dmi_type]
		self.retries = 5				# times to retry
		self.STDEV_LIM = 0.0002			# sampling DMI standard deviation limits
		
		self.initConnection()
		self.control_type = self.params.dmi_type
		# DMI specific initialization
		if not self.send(self.CONTROL_CODES[self.control_type]["INITIALIZE"]):
			raise RS232Exception('self.send(self.CONTROL_CODES[self.params.dmi_type]["Initialize"])',
								"ERROR: Cannot initialize DMI system.")
		if not self.send(self.CONTROL_CODES[self.control_type]["CLEAR"]):
			raise RS232Exception('self.send(self.CONTROL_CODES[self.params.dmi_type]["Clear"])',
								"ERROR: Cannot Clear DMI system.")
	
	# sampleDMI: (raises Exception)
	# @Purpose:
	#	This function uses the sample command to capture position data.
	#	The average and standard deviation of the measurement is returned with the AV?
	#	command.
	# @Inputs:
	#	sameples = (int) # of samples to take (usually 100)
	#	rate = (char) sample rate (usually 'M')
	#	beamline = (int) 3 = want null lens position; 1 = Asphere Mount position returned.
	#					If 1, only reads Channel 1. (usually 1)
	# 	smpdsp = False = sampling for measurement; True = sampling for display.
	#	ws = WeatherStation object for calculate atmosphere correction.
	# @Outputs:
	#	a tuple of DMI positions list and std list
	#	( [pos1, pos2, ...], [std1, std2, ...] ); all pos and std are flows
	#	return None if ERROR happens
	@samplingIndicator
	def sampleDMI(self, samples, rate, beamline, smpdsp, ws):
		retries = 0
		done_flag = False
		while (not done_flag) and retries < self.retries:
			avg = []
			stdev = []
		
			# sending sampling command
			for i in range(beamline):		# loop through boards
				self.flushInput()
				sampleCMD = self.CONTROL_CODES[self.control_type]["SAMPLE"] % (i+1, samples, rate)
				try:
				# handling success sending sampleCMD
					if self.send(sampleCMD):
						time.sleep(0.0001)
						pollCMD = self.CONTROL_CODES[self.control_type]["POLL"]
						if self.send(pollCMD):
							# timeout for waiting response
							if self.responseTimeout():
								self.printBuffer.writePrintOutFlush('ERROR: DMI sampling timeout!')
								raise RS232Exception('self.inWaiting()',
													'ERROR: DMI timeout in waiting for response!')
						
							buffer = self.recv(self.inWaiting())
							if buffer != "2\n":			# POLL return "2\n" if no error; otherwise error (POLL-ing DMI too fast)
								self.printBuffer.writePrintOutFlush('WARNING: DMI cannot react to Polling! Try to Poll DMI too fast?')
								raise DMIPollingException("buffer != \"2\\n\"",
													"WARNING: DMI cannot react to Polling!")
						else:
							raise RS232Exception('self.send(pollCMD)',
												'ERROR: DMI Communication Problem on POLL!')												
						# poll DMI for average and stdev
						avgCMD = self.CONTROL_CODES[self.control_type]["AVG"]
						if self.send(avgCMD):
							# timeout for waiting response
							if self.responseTimeout():
								self.printBuffer.writePrintOutFlush('ERROR: DMI sampling timeout!')
								raise RS232Exception('self.inWaiting()',
													'ERROR: DMI timeout in waiting for response!')
													
							buffer = ""									# reset the buffer
							done_reading_avg = False
							while not done_reading_avg:					# AVG command ALWAYS returning 2 NUMBERS, ALWAYS checking for 2 numbers.
								buffer += self.recv(self.inWaiting())
								bufferList = buffer.split("\n")
								if len(bufferList) > 2:
									done_reading_avg = True

							avg.append(float(bufferList[0]))
							stdev.append(float(bufferList[1]))
							if self.debug:
								self.printBuffer.writePrintOutFlush('INFO: DMI detected average position = %0.6f' % avg[i])
								self.printBuffer.writePrintOutFlush('INFO: DMI detected position standard deviation = %0.6f' % stdev[i])
							avg[i] = self.params.dmi_sense * avg[i] / ws.sAtm_IC * 25.4		# correction from C code
							stdev[i] = self.params.dmi_sense * stdev[i] / ws.sAtm_IC * 25.4 	# correction from C code
						
							if not smpdsp:
								if stdev[i] > self.STDEV_LIM:
									if self.debug:
										self.printBuffer.write("WARNING: DMI measurement not in tolerance! Retrying...")
									time.sleep(0.002)
									self.flushInput()
									break					# break out of for loop
								else:
									done_flag = True
							else:
								done_flag = True
						else:
							raise RS232Exception('self.send(avgCMD)',
												'ERROR: DMI Communication Problem on AVG!')
				except Exception, e:
					self.printBuffer.writePrintOutFlush("ERROR: in DMI exception caught.")
					self.printBuffer.writePrintOutFlush(traceback.format_exc())
					raise e
				
			retries += 1
					
		if retries == self.retries:
			raise RS232Exception('retries == self.retries',
								'ERROR: Unstable Environment. No Measurement Taken!!!')
		else:
			if self.debug:
				for i in range(beamline):
					self.printBuffer.writePrintOutFlush('INFO: DMI Board #%d Position = %.6f mm; Stdev = %.6f mm' % \
							(i+1, avg[i], stdev[i]))
		#ret_code = avg[0]		# something about beamline value here... weird C code...
		return (avg, stdev)
		
	# clearDMI
	# @Purpose:
	#	This function clears control board and measurement board errors
	def clearDMI(self):
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: DMI: clearing DMI")
		self.send(self.CONTROL_CODES[self.control_type]["CLEAR"])
		time.sleep(0.001)
		self.zeroDMI()
		
	# zeroDMI
	# @Purpose:
	#	This function zeros DMI
	def zeroDMI(self):		
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: DMI: zeroing DMI")
		self.send(self.CONTROL_CODES[self.control_type]["ZERO"])
		time.sleep(0.001)
		self.flushInput()
		
	# chk_stat_reg2(count):
	# @Purpose:
	#	This function checks the Error Register and deciphers any error codes.
	# @Output:
	#	True if there is ERROR, False otherwise
	def chk_stat_reg2(self):
		DMI_ERROR = True
		retries = 0
		ret_code = True
		
		while DMI_ERROR and retries < 2:
			self.flushInput()
			DMI_ERROR = False
			if not self.send(self.CONTROL_CODES[self.control_type]["READ"]):
				self.printBuffer.writePrintOutFlush("ERROR: DMI, chk_stat_reg2: detect DMI send Error")
				DMI_ERROR = True
				retries += 1
				ret_code = False
				continue
				
			# read the recv buffer
			if self.responseTimeout():
				self.printBuffer.writePrintOutFlush("ERROR: DMI, chk_stat_reg2: received NO RESPONSE from DMI")
				DMI_ERROR = True
				retries += 1
			else:
				buffer = self.recv(self.inWaiting())
				if long(buffer) & long(32) != 0:			# error mask = 0x20 = 32.	need them cancel for no error
					self.printBuffer.writePrintOutFlush("ERROR: DMI, chk_stat_reg2: detect DMI Error; status = %x" % long(buffer))
					DMI_ERROR = True
					retries += 1

		return DMI_ERROR