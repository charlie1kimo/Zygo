"""picomotor.py"""

import httplib
import re
import socket

"""
Decorators
"""
def doRetry(funct, *args):
	"""
	doRetry:
		@Purpose:
			wrapper function to perform retry when encounter TCP Connection Reset by Peer Error.
			didn't perform error handling rather spits out exceptions when encounter other exceptions.
	"""
	def wrapper(self, *args):
		while self.retry < self.retryLimit:
			try:
				retval = funct(self, *args)
				self.retry = 0
				return retval
			except socket.error, e:
				if e.args[0] == 10054:				# connection reset by peer error, retrying
					self.server.close()
					self.server.connect()
					self.retry += 1
				else:
					raise e
			except Exception, e:
				raise e
	return wrapper


class PicomotorWebException(Exception):
	"""
	@Purpose:
		customized PicomotorWebException
	"""
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: PicomotorWebException; expression = %s; %s\n" % (repr(self.expr), self.msg)	


class PicomotorWeb(object):
	"""
	@Purpose:

	"""
	def __init__(self, host, retryLimit=3):
		self.server = httplib.HTTPConnection(host, 80)
		self.server.connect()
		self.cgi_cmd = '/cmd_send.cgi?cmd=%s&submit=Send'
		self.retryLimit = retryLimit
		self.retry = 0

	def __del__(self):
		self.server.close()

	@doRetry
	def __cmd__(self, cmd):
		"""
		@Purpose:
			private function that runs the cmd to the http server, and return a response in string.
			@doRetry will do the retry when encounter TCP Connection reset by peer Error.
		@Inputs:
			cmd = (str) command to run
		@Outputs:
			(str) cmd's response
		"""
		cmd = re.sub('\?', '%3F', cmd)
		self.server.request('GET', self.cgi_cmd % cmd)
		response = self.server.getresponse()
		if response.status != httplib.OK:
			raise PicomotorWebException('response = self.server.getresponse', 
					'ERROR: Run command %s returned FAILED response. Is the web server on?' % cmd)
		
		resp = response.read()
		return self.__parse_response__(resp)

	def __parse_response__(self, response):
		"""
		@Purpose:
			private function parse the http response
		@Inputs:
			(str) response = http response
		@Outputs:
			(str) the response to the command
		"""
		resp_str = '\t<td align="left"><!--#response-->'
		response_list = response.split('\n')
		for line in response_list:
			if re.search(resp_str, line):
				result = re.sub(resp_str, '', line)
				result.rstrip()
				break
		return result

	def getIdentification(self):
		"""
		@Purpose:
			get the device identification string.
		@Inputs:
			None
		@Outputs:
			(str) identification.
		"""
		return self.__cmd__('*IDN?')

	def restoreSettings(self, settingNum):
		"""
		@Purpose:
			restore the device setting
		@Inputs:
			settingNum: 
				0 (restore to factory default settings)
				1 (restore last saved settings)
		"""
		self.__cmd__('*RCL'+str(settingNum))

	def reset(self):
		"""
		@Purpose:
			soft reset the controller
		"""
		self.__cmd__('*RST')

	def abortMotion(self):
		"""
		@Purpose:
			instantaneously stop any motion in progress.
		"""
		self.__cmd__('AB')

	def setAcceleration(self, axis, acc):
		"""
		@Purpose:
			set the acceleration to given axis motor
		@Inputs:
			axis = (int) axis number
			acc = (int) acceleration
		"""
		self.__cmd__(str(axis)+'AC'+str(acc))

	def getAcceleration(self, axis):
		"""
		@Purpose:
			get the acceleration from give axis motor
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) acceleration
		"""
		return int(self.__cmd__(str(axis)+'AC?'))

	def setHomePosition(self, axis, home):
		"""
		@Purpose:
			set the home position of a motor
		@Inputs:
			axis = (int) axis number
			home = (int) home position
		"""
		self.__cmd__(str(axis)+'DH'+str(home))

	def getHomePosition(self, axis):
		"""
		@Purpose:
			get the home position for a motor
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) the home position
		"""
		return int(self.__cmd__(str(axis)+'DH?'))

	def motorCheck(self):
		"""
		@Purpose:
			motor check
		"""
		self.__cmd__('MC')

	def isMotionDone(self, axis):
		"""
		@Purpose:
			check if the motion is done.
		@Inputs:
			axis = (int) motor axis
		@Outputs:
			(bool) True if motion is done, False otherwise
		"""
		return bool(int(self.__cmd__(str(axis)+'MD?')))

	def moveIndefinitely(self, axis, direction):
		"""
		@Purpose:
			move the motor in specific direction indefinitely
		@Inputs:
			axis = (int) axis number
			direction = (str) '+': positive, '-': negative direction
		"""
		self.__cmd__(str(axis)+'MV'+direction)

	def moveTargetPosition(self, axis, target):
		"""
		@Purpose:
			move the motor to target position
		@Inputs:
			axis = (int) axis number
			target (int) target position
		"""
		self.__cmd__(str(axis)+'PA'+str(target))

	def getTargetPosition(self, axis):
		"""
		@Purpose:
			get the motor's target position
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) position
		"""
		return int(self.__cmd__(str(axis)+'PA?'))

	def moveRelativePosition(self, axis, relative):
		"""
		@Purpose:
			move the motor relatively.
		@Inputs:
			axis = (int) axis number
			relative = (int) relative steps
		"""
		self.__cmd__(str(axis)+'PR'+str(relative))

	def setMotorType(self, axis, mType):
		"""
		@Purpose:
			set the motor type
		@Inputs:
			axis = (int) axis number
			mType = (int) motor type:
				[0: 'None',
				1: 'Unknown',
				2: 'Tiny',
				3: 'Standard']
		"""
		self.__cmd__(str(axis)+'QM'+str(mType))

	def getMotorType(self, axis):
		"""
		@Purpose:
			get the motor type
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) mType:
				[0: 'None',
				1: 'Unknown',
				2: 'Tiny',
				3: 'Standard']
		"""
		return int(self.__cmd__(str(axis)+'QM?'))

	def setAddress(self, addr):
		"""
		@Purpose:
			set the controller address (for RS-485)
		@Inputs:
			addr = (int) address
		"""
		self.__cmd__('SA'+str(addr))

	def getAddress(self):
		"""
		@Purpose:
			get the controller address (for RS-485)
		@Outputs:
			(int) address
		"""
		return int(self.__cmd__('SA?'))

	def saveSettings(self):
		"""
		@Purpose:
			save the settings to device
		"""
		self.__cmd__('SM')

	def stopMotion(self, axis):
		"""
		@Purpose:
			stop a motor in motion
		@Inputs:
			axis = (int) axis number
		"""
		self.__cmd__(str(axis)+'ST')

	def getErrorMessage(self):
		"""
		@Purpose:
			get the error message for previous command, if there is any.
		@Outputs:
			(str) error message
		"""
		return self.__cmd__('TB?')

	def getErrorCode(self):
		"""
		@Purpose:
			get the error code for previous command, if there is any.
		@Outputs:
			(int) error code
		"""
		return int(self.__cmd__('TE?'))

	def getActualPosition(self, axis):
		"""
		@Purpose:
			get the actual position for give motor
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) actual position
		"""
		return int(self.__cmd__(str(axis)+'TP?'))

	def setVelocity(self, axis, velocity):
		"""
		@Purpose:
			set the velocity
		@Inputs:
			axis = (int) axis number
			velocity = (int) velocity
		"""
		self.__cmd__(str(axis)+'VA'+str(velocity))

	def getVelocity(self, axis):
		"""
		@Purpose:
			get the velocity
		@Inputs:
			axis = (int) axis number
		@Outputs:
			(int) velocity
		"""
		return int(self.__cmd__(str(axis)+'VA?'))

