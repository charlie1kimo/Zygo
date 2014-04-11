"""
rs232.py
	This file includes the basic RS232 serial connection class interfaces
	
Author: Charlie Chen
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/4/2013	cchen	first created documenation
'''

from radius3 import serial
from radius3.serial.serialutil import *
import time
import traceback

from radius3.utilities import OutputBuffer

#######################################################
# class RS232Exception
#	This class throws exception for RS232 interface
#######################################################
class RS232Exception(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: RS232Exception; expression = %s; %s\n" % (repr(self.expr), self.msg)


#######################################################
# class RS232:
#	This class is a base class for RS232 interface
#	TRICKY: base class should inherit "object" for children to use super() method.
#######################################################
class RS232(object):
	# __init__:
	# @Purpose:
	# 	constructor method:
	# @Arguments:
	#	params = (Parameters) parameters object
	#	debug = (boolean) turn debug on/off
	def __init__(self, params, printBuffer=OutputBuffer(), debug=False):
		self.timeout = params.com_info.timeout			# timeout in second for waiting rs232 connection to response
		self.params = params
		self.printBuffer = printBuffer
		self.debug = debug
		self.serialCom = None
		
		# parse handshake types; default no hand shake
		self.rtscts = False
		self.dsrdtr = False
		if self.params.com_info.handshake == "RTS_CTS":
			self.rtscts = True
		elif self.params.com_info.handshake == "DSR_DTR":
			self.dsrdtr = True
		elif self.params.com_info.handshake == "BOTH":
			self.rtscts = True
			self.dsrdtr = True
			
	# __del__:
	# @Purpose:
	#	destructor method
	def __del__(self):
		if self.serialCom != None:
			self.serialCom.close()
			
	# initConnection: (raises Exceptions)
	# @Purpose:
	#	initialize the RS232 connection
	def initConnection(self):
		# initialize the connection
		if self.debug:			
			self.printBuffer.writePrintOutFlush("INFO: Initializing serial connection...")
		try:
			self.serialCom = serial.Serial(port=self.params.com_info.com_port,
										baudrate=self.params.com_info.baud_rate,
										bytesize=eval("serial."+self.params.com_info.data_bits),
										parity=eval("serial."+self.params.com_info.parity),
										stopbits=eval("serial."+self.params.com_info.stop_bits),
										timeout=self.params.com_info.timeout,
										xonxoff=False,
										rtscts=self.rtscts,
										writeTimeout=None,
										dsrdtr=self.dsrdtr,
										interCharTimeout=None)
		except SerialException, e:
			self.printBuffer.writePrintOutFlush("ERROR: CANNOT OPEN SERIAL PORT %s!" % repr(self.params.com_info.com_port))
			self.printBuffer.writePrintOutFlush(traceback.format_exc())
			raise e			# possible for sending exception up?
		
		# flush all the input outputs of connection
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: Flushing all serial inputs/outputs...")
		self.flushInput()
		self.flushOutput()
	
	# close:
	# @Purpose:
	#	Close the serial connection
	def close(self):
		if self.serialCom != None:
			self.serialCom.close()
			
	# recv:
	# @Purpose:
	#	receive buffer from RS232 serial connection
	# @Arguments:
	#	b = (int) # of bytes to read
	# @Output:
	#	(String) bytes received
	def recv(self, b=None):
		if b == None:
			received = self.serialCom.read()
		else:
			received = self.serialCom.read(b)
			if self.debug:
				self.printBuffer.writePrintOutFlush('INFO: received buffer: %s' % repr(received))
		return received
		
	# send:
	# @Purpose:
	#	send command to RS232 serial connection
	# @Arguments:
	#	cmd = (String, String, ...) tuple of String of send command
	# @Output:
	#	(boolean) True if success send all bytes, False otherwise
	# @Notes:
	#	1. old version of serial package return NONE after writing; thus return success (True) by default...
	def send(self, cmd):
		if self.debug:
			self.printBuffer.writePrintOutFlush('INFO: sending %s to serial connection' % repr(cmd))
		#if len(cmd) == self.serialCom.write(cmd):
		#	return True
		#else:
		#	return False
		self.serialCom.write(cmd)
		return True
	
	# flushInput:
	# @Purpose:
	#	wrapper method for serial.flushInput()
	def flushInput(self):
		if self.debug:
			self.printBuffer.writePrintOutFlush('INFO: flushing incoming buffer...')
		self.serialCom.flushInput()
		
	# flushOutput:
	# @Purpose:
	#	wrapper method for serial.flushOutput()	
	def flushOutput(self):
		if self.debug:
			self.printBuffer.writePrintOutFlush('INFO: flushing outgoing buffer...')
		self.serialCom.flushOutput()
		
	# inWaiting:
	# @Purpose:
	#	wrapper method for serial.inWaiting()
	def inWaiting(self):
		recvBytes = self.serialCom.inWaiting()
		#if self.debug and recvBytes > 0:
		#	self.printBuffer.writePrintOutFlush('INFO: serial connection receives %d bytes' % recvBytes)
		return recvBytes
	
	# responseTimeout:
	# @Purpose:
	#	check if we time-outed for waiting the response from RS232 connection
	# @Output:
	#	True if time-out; False otherwise
	def responseTimeout(self):
		timewait = time.time()
		while time.time() - timewait < self.timeout:
			if self.inWaiting() > 0:
				return False
		return True

