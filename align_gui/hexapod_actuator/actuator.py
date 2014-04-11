"""
hexapod.py
"""

import ConfigParser
import os.path
import numpy
import time
import wx

from capgauge import CompositeCapgauge
from capgauge import CapgaugeException
from picomotor import PicomotorWeb
from picomotor import PicomotorWebException
from actuator_wx import HexapodActuatorWxScrolledPanel, ActuatorDoneEvent

class MotorLeg(object):
	"""
	@Purpose:
		create a MotorLeg class
	"""
	def __init__(self, capgauge_params, picomotor_params):
		"""
		@Purpose:
			Constructor
		@Inputs:
			(dict) capgauge_params:
				{'obj': CompositeCapgauge object,
				'slope': Capgauge voltage to distance slope,
				'piston': Capgauge voltage to distance offset,
				'index': CompositeCapgauge index for this leg
				}
			(dict) picomotor_params:
				{'obj': PicomotorWeb object,
				'axis': Picomotor motor axis
				}
		"""
		self.__DEFAULT_RETRY__ = 5
		self._calibrate_steps = 100
		self.capgauge = capgauge_params
		self.picomotor = picomotor_params
		self.slope = {'up': 1.0, 'down': 1.0}
		self.offset = self.getPosition()
		self.capgauge_pos = self.offset

		self.picomotor['obj'].setHomePosition(self.picomotor['axis'], 0)

	def setCapgaugeObj(self, capgaugeObj):
		self.capgauge['obj'] = capgaugeObj

	def setPicomotorWebObj(self, picomotorWebObj):
		self.picomotor['obj'] = picomotorWebObj

	def calibratePositive(self):
		"""
		@Purpose:
			calibrate this motor leg in + direction of motor steps.
		"""
		# calibrate the upward relationship of slope and offset (assume linear relationship)
		b4_cap = self.getPosition()
		self.moveMotorRelatively(self._calibrate_steps)
		steps_cap = self.getPosition()
		pos_changes = steps_cap - b4_cap

		# steps_cap = slope * calibrate_steps + curr_pos
		# cap_original_pos = slope * 0 + offset
		if pos_changes > 0:
			self.slope['up'] = pos_changes / self._calibrate_steps
		else:
			self.slope['down'] = pos_changes / self._calibrate_steps

		self.capgauge_pos = self.getPosition()

	def calibrateNegative(self):
		"""
		@Purpose:
			calibrate this motor leg in - direction of motor steps.
		"""
		# move the motor back to home position (zero position), and calibrate downward relationship.
		b4_cap = self.getPosition()
		self.moveMotorRelatively(-1*self._calibrate_steps)
		steps_cap = self.getPosition()
		pos_changes = steps_cap - b4_cap
		if pos_changes > 0:
			self.slope['up'] = pos_changes / self._calibrate_steps
		else:
			self.slope['down'] = pos_changes / self._calibrate_steps

		self.capgauge_pos = self.getPosition()

	def getPosition(self):
		"""
		@Purpose:
			Get the Capgauge's current position
		@Output:
			(float) position
		"""
		retries = 0
		try:
			return self.capgauge['obj'].readPositions(self.capgauge['slope'], self.capgauge['piston'])[self.capgauge['index']]
		except CapgaugeException, e:
			if retries > self.__DEFAULT_RETRY__:
				raise HexaPodActuatorException(e.expr, e.msg)
			else:
				retries += 1

	def getMotorPosition(self):
		"""
		@Purpose:
			Get the Motor step position
		@Outpus:
			(int) position
		"""
		retries = 0
		try:
			return self.picomotor['obj'].getActualPosition(self.picomotor['axis'])
		except PicomotorWebException, e:
			if retries > self.__DEFAULT_RETRY__:
				raise HexaPodActuatorException(e.expr, e.msg)
			else:
				retries += 1


	def moveMotorRelatively(self, change):
		"""
		@Purpose:
			move the motor relatively
		@Inputs:
			(int) change = relative change amount in motor steps. 
		"""
		retries = 0
		try:
			self.picomotor['obj'].moveRelativePosition(self.picomotor['axis'], change)
			while not self.picomotor['obj'].isMotionDone(self.picomotor['axis']):
				pass
		except PicomotorWebException, e:
			if retries > self.__DEFAULT_RETRY__:
				raise HexaPodActuatorException(e.expr, e.msg)
			else:
				retries += 1

		self.capgauge_pos = self.getPosition()

	def moveMotorAbsoultely(self, target):
		"""
		@Purpose:
			move the motor to a target position
		@Inputs:
			(int) target = target motor step to move to.
		"""
		retries = 0
		try:
			self.picomotor['obj'].moveTargetPosition(self.picomotor['axis'], target)
			while not self.picomotor['obj'].isMotionDone(self.picomotor['axis']):
				pass
		except PicomotorWebException, e:
			if retries > self.__DEFAULT_RETRY__:
				raise HexaPodActuatorException(e.expr, e.msg)
			else:
				retries += 1

		self.capgauge_pos = self.getPosition()

	def change(self, delta, isReversed=True):
		"""
		@Purpose:
			change the motor and makes the capgauge change the given amount.
				-> Updates:
					now the slope fits the latest movement, a feedback calibration technique.
		@Inputs:
			(float) delta = the amount to change in position.
		"""
		# special case, delta = 0, don't move the motor.
		if delta == 0:
			return

		if isReversed:
			delta = delta * -1
		old_pos = self.capgauge_pos
		############## iterative steps ##############
		target_pos = old_pos + delta
		#############################################

		if delta > 0:
			motor_steps = int(delta/self.slope['up'])
			self.moveMotorRelatively(motor_steps)
		else:
			motor_steps = int(delta/self.slope['down'])
			self.moveMotorRelatively(motor_steps)

		"""
		if (not self.is_position_motor_direction_reverse and delta > 0) or \
			(self.is_position_motor_direction_reverse and delta < 0):
			if delta > 0:
				motor_steps = int((target_pos - self.capgauge_pos) / self.slope['up'])
				self.moveMotorRelatively(motor_steps)
				#self.slope['up'] = (self.capgauge_pos - old_pos) / motor_steps
			else:
				motor_steps = int((self.capgauge_pos - target_pos) / self.slope['down'])
				self.moveMotorRelatively(motor_steps)
				#self.slope['down'] = (self.capgauge_pos - old_pos) / motor_steps
		else:
			if delta > 0:
				motor_steps = int((self.capgauge_pos - target_pos) / self.slope['down'])
				self.moveMotorRelatively(motor_steps)
				#self.slope['down'] = (self.capgauge_pos - old_pos) / motor_steps
			else:
				motor_steps = int((target_pos - self.capgauge_pos) / self.slope['up'])
				self.moveMotorRelatively(motor_steps)
				#self.slope['up'] = (self.capgauge_pos - old_pos) / motor_steps
		"""

		#print "leg#%d moves: %d, with motor_steps:%d" % (self.capgauge['index'], delta, motor_steps)

	def stop(self):
		"""
		@Purpose:
			STOP this leg movement immediately
		"""
		try:
			### try to stop the specific motor first ###
			self.picomotor['obj'].stopMotion(self.picomotor['axis'])
		except Exception, e:
			### Fail safe mode, stop controller's action ###
			retries = 0
			while retries < self.__DEFAULT_RETRY__:
				self.picomotor['obj'].abortMotion()
				retries += 1
			raise HexaPodActuatorException(e.expr, e.msg)


class HexaPodActuatorException(Exception):
	"""
	@Purpose:
		customized HexaPodActuatorException
	"""
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: HexaPodActuatorException.\n expression = %s.\n %s\n" % (repr(self.expr), self.msg)	


############# Decorator for HexapodActuator #############
def handlesRetryOnCapgaugeHexapodActuator(funct, *args, **kwargs):
	def wrapper(self, *args, **kwargs):
		while True:
			try:
				return funct(self, *args, **kwargs)
				break
			except HexaPodActuatorException, e:
				if self.moveWidget != None:		### GUI Retry box ask if users wants to retry
					title = "ERROR in Capgauge Reading, Retrying?"
					msg = \
"""
ERROR encountered in reading capgauge. Do you want to retry? 
Please restart capgauge if possible before retry, and also make sure you have good ethernet communication to capgauges.
"""
					wantRetry = self.moveWidget.popRetryBoxAndReturnBool(title, msg)
					if wantRetry:
						self.__createCapgaugeObjForMotorLeg__()
					else:
						raise e
				else:
					raise e
	return wrapper
#########################################################

class HexaPodActuator(object):
	"""
	@Purpose:
		create a HexPod class that can controll the all the sensors and motors on a HexPod machine
	"""
	def __init__(self, capgauge_config, picomotor_controllers, calibrate_config='hexapod_calibrate.cfg', move_widget=None):
		"""
		@Purpose:
			Constructor
		@Inputs:
			(str) capgauge_config = path to NI capgauge controller config file.
			(list) picomotor_controllers = list of picomotor hostnames or ip addresses.
			(str) calibrate_config = saved hexapod calibration configuration file
			(wx_extensions.dialogs.DialogProgress) logGUIWidget = wxPython extended dialog to show details of movements.
		"""
		if move_widget != None:
			assert isinstance(move_widget, HexapodActuatorWxScrolledPanel), "move_widget is %s, but it's required to be HexapodActuatorWxScrolledPanel" % repr(type(move_widget))
		self.moveWidget = move_widget
		######### STOP FLAG: Interrupt legChange or capChange ########
		self.__stop__ = False
		##############################################################
		######### IsCompositeCapgauge FLAG: determine if we are using the CompositeCapgauge ########
		self.__isCompositeCapgauge__ = True
		############################################################################################
		######### RETRY NUMBERS ######################################
		self.__DEFAULT_RETRY__ = 5
		##############################################################
		self.capgauge_config = capgauge_config
		self.picomotor_controllers = picomotor_controllers
		picomotor1 = PicomotorWeb(picomotor_controllers[0])
		picomotor2 = PicomotorWeb(picomotor_controllers[1])
		self.picomotors = [picomotor1, picomotor2]

		"""
		cap0 = Capgauge(0, ni_config_file=capgauge_config, name='leg0')
		cap1 = Capgauge(1, ni_config_file=capgauge_config, name='leg1')
		cap2 = Capgauge(2, ni_config_file=capgauge_config, name='leg2')
		cap3 = Capgauge(3, ni_config_file=capgauge_config, name='leg3')
		cap4 = Capgauge(4, ni_config_file=capgauge_config, name='leg4')
		cap5 = Capgauge(5, ni_config_file=capgauge_config, name='leg5')
		"""
		cap = CompositeCapgauge(range(6), capgauge_config)

		cap_dict_0 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 0
				}
		cap_dict_1 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 1
				}
		cap_dict_2 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 2
				}
		cap_dict_3 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 3
				}
		cap_dict_4 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 4
				}
		cap_dict_5 = {'obj': cap,
				'slope': 25,
				'piston': 0,
				'index': 5
				}
		pico_dict_0 = {'obj': picomotor1,
				'axis': 1,
		}
		pico_dict_1 = {'obj': picomotor1,
				'axis': 2,
		}
		pico_dict_2 = {'obj': picomotor1,
				'axis': 3,
		}
		pico_dict_3 = {'obj': picomotor1,
				'axis': 4,
		}
		pico_dict_4 = {'obj': picomotor2,
				'axis': 1,
		}
		pico_dict_5 = {'obj': picomotor2,
				'axis': 2,
		}

		#### CREATION of LEGS ###
		self.legs = [MotorLeg(cap_dict_0, pico_dict_0),
				MotorLeg(cap_dict_1, pico_dict_1),
				MotorLeg(cap_dict_2, pico_dict_2),
				MotorLeg(cap_dict_3, pico_dict_3),
				MotorLeg(cap_dict_4, pico_dict_4),
				MotorLeg(cap_dict_5, pico_dict_5),
		]
		#### Save the config file name
		self.calibrate_config = os.path.dirname(os.path.realpath(__file__)) + '/' + calibrate_config

		if os.path.exists(self.calibrate_config):		# read the config...
			config = ConfigParser.RawConfigParser()
			config.read(self.calibrate_config)
			for index in range(len(self.legs)):
				leg = 'leg%d' % index
				self.legs[index].slope['up'] = config.getfloat(leg, 'slope.up')
				self.legs[index].slope['down'] = config.getfloat(leg, 'slope.down')
		else:
			self.calibrate()

	def __createCapgaugeObjForMotorLeg__(self):
		"""
		@Purpose:
			private function to recreate capgauge obj when it hangs
		"""
		if self.__isCompositeCapgauge__:
			cap = CompositeCapgauge(range(6), self.capgauge_config)
			for leg in self.legs:
				leg.setCapgaugeObj(cap)
		else:
			cap0 = Capgauge(0, ni_config_file=self.capgauge_config, name='leg0')
			cap1 = Capgauge(1, ni_config_file=self.capgauge_config, name='leg1')
			cap2 = Capgauge(2, ni_config_file=self.capgauge_config, name='leg2')
			cap3 = Capgauge(3, ni_config_file=self.capgauge_config, name='leg3')
			cap4 = Capgauge(4, ni_config_file=self.capgauge_config, name='leg4')
			cap5 = Capgauge(5, ni_config_file=self.capgauge_config, name='leg5')
			for legInd in range(len(self.legs)):
				self.legs[legInd].setCapgaugeObj(eval("cap"+str(legInd)))

	def setMoveWidget(self, widget):
		"""
		@Purpose:
			Set a wx.Panel widget to attach to this actuator (for customized displaying).
		@Inputs:
			(wx.Panel) widget = input attaching widget.
		"""
		if widget != None:
			assert isinstance(widget, HexapodActuatorWxScrolledPanel), "widget is %s, but it's required to be HexapodActuatorWxScrolledPanel" % repr(type(widget))
		self.moveWidget = widget

	def calibrate(self):
		"""
		@Purpose:
			Calibrate the 6 motor legs. Figuring out the correlation between motor steps and capgauge position.
		"""
		# calibrate directional slopes
		for index in range(len(self.legs)):
			self.legs[index].calibratePositive()
			self.legs[index].calibrateNegative()

		# write the calibration to a config.
		config = ConfigParser.RawConfigParser()
		for index in range(len(self.legs)):
			leg = 'leg%d' % index
			config.add_section(leg)
			config.set(leg, 'slope.up', self.legs[index].slope['up'])
			config.set(leg, 'slope.down', self.legs[index].slope['down'])

		config_f = open(self.calibrate_config, 'w')
		config.write(config_f)
		config_f.close()

	def capgaugeChangeQuick(self, target_capgauge, min_amounts=[0.005, 0.005, 0.005, 0.005, 0.005, 0.005], max_iter=3, debug=False):
		"""
		@Purpose:
			new way to move motors and read the capgauge sensors:
				1. read 6 capgauge sensors positions
				2. move 6 motors
				3. update graph, and update amounts to go.
		@Inputs:
			(numpy.array) target_capgauge = [leg0_pos, leg1_pos, leg2_pos, leg3_pos, leg4_pos, leg5_pos]
			(list) min_amounts = minimum amount lists
			(int) max_iter = maximum iterations to perform
		"""
		################################## Error handling #######################################
		if len(min_amounts) != 6:
			raise HexaPodActuatorException("len(min_amounts) != 6",
				"ERROR: min_amounts definitions must be length of 6.")

		for i in range(len(min_amounts)):
			if type(min_amounts[i]) != int and type(min_amounts[i]) != float and \
					type(amounts[i]) != numpy.float64 and type(amounts[i]) != numpy.float32:
				raise HexaPodExcept('min_amounts[%d] != int and min_amounts[%d] != float' % (i, i),
					"ERROR: min_amounts must defined as INT or FLOAT.")
		###########################################################################################

		if debug:
			debug_start_time = time.time()
			print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: Reading Starting Positions."
		cur_positions = self.getPositions()

		if debug:
			debug_end_time = time.time()
			print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: Reading Starting Positions. DONE. Take: %f (s)" % (debug_end_time - debug_start_time)

		delta_positions = target_capgauge - cur_positions
		for i in range(max_iter):
			# update the movePanel plots, to re-scale every iterations
			if self.moveWidget != None:
				self.moveWidget.setAutoPlotCapYLim()
				self.moveWidget.plotCapChange()

			for index in range(len(self.legs)):
				if abs(delta_positions[index]) < min_amounts[index]:
					continue
				else:
					###### INTERRUPT FLAG #######
					if self.__stop__:
						self.__stop__ = False				# reset it, and exit
						return
					#############################
					if debug:
						debug_start_time = time.time()
						print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: MOVING leg# %d, iter %d" % (index, i)
					self.changeLeg(index, delta_positions[index])
					if debug:
						debug_end_time = time.time()
						print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: MOVING leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

			if debug:
				debug_start_time = time.time()
				print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: Reading AFTER position."
			cur_positions = self.getPositions()
			if debug:
				debug_end_time = time.time()
				print "DEBUG: actuator.HexaPodActuator.capgaugeChangeQuick: Reading AFTER position. DONE. Take: %f (s)" % (debug_end_time - debug_start_time)
			delta_positions = target_capgauge - cur_positions
			# update movePanel plots... if it's given. (AFTER THE MOTOR MOVEMENTS)
			if self.moveWidget != None:
				self.moveWidget.cap_change_amounts = delta_positions
				self.moveWidget.cap_change_labels = ['Leg1,i:%d'%(i+1), 'Leg2,i:%d'%(i+1), 'Leg3,i:%d'%(i+1), 'Leg4,i:%d'%(i+1), 'Leg5,i:%d'%(i+1), 'Leg6,i:%d'%(i+1)]
				self.moveWidget.plotCapChange()

		### finishing... stop the statusBar pulse ###
		if self.moveWidget != None:
			wx.PostEvent(self.moveWidget, ActuatorDoneEvent(fromFunction='capgaugeChange'))

	def capgaugeChange(self, target_capgauge, min_amounts=[0.005, 0.005, 0.005, 0.005, 0.005, 0.005], max_iter=3, debug=False):
		"""
		@Purpose:
			Change the hex_pod six legs by amounts (in list)
			This method changes them in 6-legs sequence per iterations to achieve the goal change amounts.
				use the given starting positions to calculate the target positions
				leg1_iter1
				leg2_iter1
				...
				leg1_iter2
				leg2_iter2
				...
		@Inputs:
			(numpy.array) target_capgauge = [leg0_pos, leg1_pos, leg2_pos, leg3_pos, leg4_pos, leg5_pos]
			(list) min_amounts = minimum amount lists
			(int) max_iter = maximum iterations to perform
		"""
		# update movePanel plots... if it's given.
		"""
		if self.moveWidget != None:
			try:
				self.moveWidget.getTopLevelWindow().statusBarMain.PulseStart()
			except AttributeError, e:
				pass
		"""

		################################## Error handling #######################################
		if len(min_amounts) != 6:
			raise HexaPodActuatorException("len(min_amounts) != 6",
				"ERROR: min_amounts definitions must be length of 6.")

		for i in range(len(min_amounts)):
			if type(min_amounts[i]) != int and type(min_amounts[i]) != float and \
					type(amounts[i]) != numpy.float64 and type(amounts[i]) != numpy.float32:
				raise HexaPodExcept('min_amounts[%d] != int and min_amounts[%d] != float' % (i, i),
					"ERROR: min_amounts must defined as INT or FLOAT.")
		###########################################################################################

		for i in range(max_iter):
			# update the movePanel plots, to re-scale every iterations
			if self.moveWidget != None:
				self.moveWidget.setAutoPlotCapYLim()
				self.moveWidget.plotCapChange()

			for index in range(len(self.legs)):

				if debug:
					debug_start_time = time.time()
					print "DEBUG: actuator.HexaPodActuator.capgaugeChange: Reading position BEFORE move on leg# %d, iter %d" % (index, i)
				curr_pos = self.getLegPosition(index)
				if debug:
					debug_end_time = time.time()
					print "DEBUG: actuator.HexaPodActuator.capgaugeChange: Reading position BEFORE move on leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

				delta_pos = target_capgauge[index] - curr_pos
				if abs(delta_pos) < min_amounts[index]:
					continue
				else:
					###### INTERRUPT FLAG #######
					if self.__stop__:
						self.__stop__ = False				# reset it, and exit
						return
					#############################

					if debug:
						debug_start_time = time.time()
						print "DEBUG: actuator.HexaPodActuator.capgaugeChange: MOVING on leg# %d, iter %d" % (index, i)
					self.changeLeg(index, delta_pos)
					if debug:
						debug_end_time = time.time()
						print "DEBUG: actuator.HexaPodActuator.capgaugeChange: MOVING on leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

					# update movePanel plots... if it's given.
					if self.moveWidget != None:
						if debug:
							debug_start_time = time.time()
							print "DEBUG: actuator.HexaPodActuator.capgaugeChange: Reading position AFTER move on leg# %d, iter %d" % (index, i)
						after_pos = self.getLegPosition(index)
						if debug:
							debug_end_time = time.time()
							print "DEBUG: actuator.HexaPodActuator.capgaugeChange: Reading position AFTER move on leg# %d, iter %d. DONE. Take %f (s)" % (index, i, (debug_end_time - debug_start_time))
						amounts_to_go = target_capgauge[index] - after_pos
						self.moveWidget.cap_change_amounts[index] = amounts_to_go
						curr_label = self.moveWidget.cap_change_labels[index].split(':')[0]
						self.moveWidget.cap_change_labels[index] = curr_label+':%d' % (i+1)
						self.moveWidget.plotCapChange()

		### finishing... stop the statusBar pulse ###
		if self.moveWidget != None:
			wx.PostEvent(self.moveWidget, ActuatorDoneEvent(fromFunction='capgaugeChange'))

	def legChange(self, amounts, min_amounts=[0.005, 0.005, 0.005, 0.005, 0.005, 0.005], max_iter=3, debug=False):
		"""
		@Purpose:
			Change ths hex_pod six legs by amounts (in list)
			This method changes the leg ONE BY ONE:
				leg1_change_iter1
				leg1_change_iter2
				leg2_change_iter1
				leg2_change_iter2
				...
		@Inputs:
			(list) amounts = [leg0, leg1, leg2, leg3, leg4, leg5]
			(list) min_amounts = minimum amount lists
			(int) max_iter = maximum iterations to perform
		"""
		# update movePanel plots... if it's given.
		"""
		if self.moveWidget != None:
			try:
				self.moveWidget.getTopLevelWindow().statusBarMain.PulseStart()
			except AttributeError, e:
						pass
		"""

		dummy_delta = 999999

		################################## Error handling #######################################
		if len(amounts) != 6:
			raise HexaPodActuatorException("len(legs) != 6",
				"ERROR: Input legs changes requires 6 amounts.")
		if len(min_amounts) != 6:
			raise HexaPodActuatorException("len(min_amounts) != 6",
				"ERROR: min_amounts definitions must be length of 6.")

		for i in range(len(amounts)):
			if type(amounts[i]) != int and type(amounts[i]) != float and \
					type(amounts[i]) != numpy.float64 and type(amounts[i]) != numpy.float32:
				raise HexaPodActuatorException('type(amounts[%d]) == %s' % (i, str(type(amounts[i]))),
					"ERROR: Input legs positions must be INT or FLOAT.")

		for i in range(len(min_amounts)):
			if type(min_amounts[i]) != int and type(min_amounts[i]) != float and \
					type(amounts[i]) != numpy.float64 and type(amounts[i]) != numpy.float32:
				raise HexaPodExcept('min_amounts[%d] != int and min_amounts[%d] != float' % (i, i),
					"ERROR: min_amounts must defined as INT or FLOAT.")
		############################################################################################

		delta = [dummy_delta, dummy_delta, dummy_delta, dummy_delta, dummy_delta, dummy_delta]
		for index in range(len(self.legs)):
			for i in range(max_iter):
				if delta[index] < min_amounts[index]:
					continue

				if debug:
					debug_start_time = time.time()
					print "DEBUG: actuator.HexaPodActuator.legChange: Reading position BEFORE move on leg# %d, iter %d" % (index, i)
				prev_pos = self.getLegPosition(index)
				if debug:
					debug_end_time = time.time()
					print "DEBUG: actuator.HexaPodActuator.legChange: Reading position BEFORE move on leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

				### INTERRUPT FLAG ###
				if self.__stop__:
					self.__stop__ = False				# reset
					return
				######################

				if debug:
					debug_start_time = time.time()
					print "DEBUG: DEBUG: actuator.HexaPodActuator.legChange: Moving leg# %d, iter %d, by %f" % (index, i, amounts[index])
				self.changeLeg(index, amounts[index])
				if debug:
					debug_end_time = time.time()
					print "DEBUG: DEBUG: actuator.HexaPodActuator.legChange: Moving leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

				if debug:
					debug_start_time = time.time()
					print "DEBUG: actuator.HexaPodActuator.legChange: Reading position AFTER move on leg# %d, iter %d" % (index, i)
				curr_pos = self.getLegPosition(index)
				if debug:
					debug_end_time = time.time()
					print "DEBUG: DEBUG: actuator.HexaPodActuator.legChange: Reading position AFTER MOVE on leg# %d, iter %d. DONE. Take: %f (s)" % (index, i, (debug_end_time - debug_start_time))

				delta[index] = abs(curr_pos - prev_pos)
				if amounts[index] > 0:
					amounts[index] -= delta[index]
				else:
					amounts[index] += delta[index]
				
				# update movePanel plots... if it's given.
				if self.moveWidget != None:
					self.moveWidget.leg_change_amounts[index] = amounts[index]
					curr_label = self.moveWidget.leg_change_labels[index].split(':')[0]
					self.moveWidget.leg_change_labels[index] = curr_label+':%d' % (i+1)
					self.moveWidget.plotLegChange()
					self.moveWidget.plotCapChange()

		### finishing... stop the statusBar pulse ###
		if self.moveWidget != None:
			wx.PostEvent(self.moveWidget, ActuatorDoneEvent(fromFunction='legChange'))

	def change(self, cap_change_amounts, leg_change_amounts):
		"""
		@Purpose: (DEPRECATED)
			General change function that perform the leg changes.
		@Inputs:
			(list) change_amounts = amounts to change
		"""
		starting_capgauge = self.getPositions()
		self.legChange(leg_change_amounts)
		self.capgaugeChange(starting_capgauge, cap_change_amounts)

	def stop(self):
		"""
		@Purpose:
			STOP 'legChange' function call or 'capChange' function call by setting private flag that's checked in the functions
		"""
		for motor in self.picomotors:
			motor.abortMotion()
		self.__stop__ = True

	def changeLeg(self, legInd, amounts):
		"""
		@Purpose:
			change the position of a specific leg by amounts
		@Inputs:
			(int) legInd = leg index number
			(float) amounts = change amounts
		"""
		self.legs[legInd].change(amounts)

	@handlesRetryOnCapgaugeHexapodActuator
	def getLegPosition(self, legInd):
		"""
		@Purpose:
			get the position for a specific leg
		@Input:
			(int) legInd: leg index number
		@Output:
			(float) position
		"""
		return self.legs[legInd].getPosition()

	@handlesRetryOnCapgaugeHexapodActuator
	def getPositions(self):
		"""
		@Purpose:
			get positions for six legs
		@Output:
			(numpy.array) [leg0, leg1, leg2, leg3, leg4, leg5]
		"""
		if not self.__isCompositeCapgauge__:
			retlist = []
			for index in range(len(self.legs)):
				retlist.append(self.getLegPosition(index))

			return numpy.array(retlist)
		else:
			slope = self.legs[0].capgauge['slope']
			piston = self.legs[0].capgauge['piston']
			cap = self.legs[0].capgauge['obj']

			retries = 0
			try:
				return numpy.array(cap.readPositions(slope, piston))
			except CapgaugeException, e:
				if retries > self.__DEFAULT_RETRY__:
					raise HexaPodActuatorException(e.expr, e.msg)
				else:
					retries += 1

