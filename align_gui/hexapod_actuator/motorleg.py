"""
motorleg.py
	DEPRECATED Module
"""
import numpy

class MotorLegException(Exception):
	"""
	@Purpose:
		customized MotorLegActuatorException
	"""
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: MotorLegException.\n expression = %s.\n %s\n" % (repr(self.expr), self.msg)


class CompositeMotorLegs(object):
	"""
	@Purpose:
		create a CompositeMotorLeg class
	"""
	def __init__(self, capgauge_params, list_picomotor_params, legs=6):
		"""
		@Purpose:
			Constructor of the class
		@Inputs:
			(dict) capgauge_params:
				{'obj': CompositeCapgauge object,
				'slope': Capgauge voltage to distance slope,
				'piston': Capgauge voltage to distance offset
				}
			(list) list_picomotor_params:
				[
					{'obj': PicomotorWeb object,
					'axis': Picomotor motor axis
					}, 
					{'obj': PicomotorWeb object,
					'axis': Picomotor motor axis
					}, ...
				]
				list index reflects to the channel sequence (leg sequence) that CompositeCapgauge is setup.
		"""
		# error checking.
		if len(list_picomotor_params) != legs:
			raise MotorlegException("CompositeMotorLegs.__init__",
				"ERROR: Given list_picomotor_params has size inconsistent with defines legs number!")

		self._calibrate_steps = 100
		self.__threadMap__ = [None for i in range(legs)]
		self.capgauge = capgauge_params
		self.picomotors = list_picomotor_params
		self.positions = self.getPositions()
		self.calibrations = []
		for leg in xrange(len(self.picomotors)):
			leg_calibrations = {'slope.up': 1.0, 'slope.down': 1.0, 'offset': self.positions[leg], 'direction_reversed': False}
			self.calibrations.append(leg_calibrations)
			picomotor = self.picomotors[leg]
			picomotr['obj'].setHomePosition(picomotor['axis'], 0)

	def calibrate(self):
		"""
		@Purpose:
			calibrate all motor legs in both:
				+ direction of motor steps.
				- direction of motor steps.
		"""
		for leg in xrange(len(self.positions)):
			# calibrate the upward relationship of slope and offset (assume linear relationship)
			# + direction
			b4_cap = self.positions[leg]
			self.moveMotorRelatively(self._calibrate_steps, leg)
			steps_cap = self.positions[leg]

			# steps_cap = slope * calibrate_steps + curr_pos
			# cap_original_pos = slope * 0 + offset
			leg_calibration = self.calibrations[leg]
			leg_calibration['slope.up'] = (steps_cap - b4_cap) / self._calibrate_steps

			if steps_cap < leg_calibration['offset']:
				leg_calibration['direction_reversed'] = True

			# - direction
			b4_cap = self.positions[leg]
			self.moveMotorRelatively(-1*self._calibrate_steps, leg)
			steps_cap = self.positions[leg]

			leg_calibration = self.calibrations[leg]
			leg_calibration['slope.down'] = (steps_cap - b4_cap) / self._calibrate_steps

	def getPositions(self):
		"""
		@Purpose:
			Get the CompositeCapgauge's current positions
		@Output:
			(numpy.array) [pos1, pos2, pos3, ...]
		"""
		return numpy.array(self.capgauge['obj'].readPositions(self.capgauge['slope'], self.capgauge['piston']))

	def getMotorPosition(self, leg):
		"""
		@Purpose:
			Get the Motor step position
		@Inputs:
			(int) leg = leg index.
		@Outpus:
			(int) position
		"""
		picomotor = self.picomotors[leg]
		return picomotor['obj'].getActualPosition(picomotor['axis'])

	def moveMotorRelatively(self, leg, change):
		"""
		@Purpose:
			move the motor relatively
		@Inputs:
			(int) leg = leg index.
			(int) change = relative change amount in motor steps. 
		"""
		picomotor = self.picomotors[leg]
		picomotor['obj'].moveRelativePosition(picomotor['axis'], change)
		while not picomotor['obj'].isMotionDone(picomotor['axis']):
			pass
		self.positions = self.getPositions()

	def moveMotorAbsoultely(self, leg, target):
		"""
		@Purpose:
			move the motor to a target position
		@Inputs:
			(int) leg = leg index.
			(int) target = target motor step to move to.
		"""
		picomotor = self.picomotors[leg]
		picomotor['obj'].moveTargetPosition(picomotor['axis'], target)
		while not picomotor['obj'].isMotionDone(picomotor['axis']):
			pass
		self.capgauge_pos = self.getPosition()

	def change(self, leg, delta):
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

		leg_calibration = self.calibrations[leg]
		if leg_calibration['direction_reversed']:
			delta *= -1

		if delta > 0:
			motor_steps = int(delta / leg_calibration['slope.up'])
			self.moveMotorRelatively(motor_steps)
		else:
			motor_steps = int(delta / leg_calibration['slope.down'])
			self.moveMotorRelatively(motor_steps)

	def stop(self):
		"""
		@Purpose:
			STOP all movement immediately
		"""
		for leg in xrange(len(self.picomotors)):
			picomotor = self.picomotors[leg]
			try:
				### try to stop the specific motor first ###
				picomotor['obj'].stopMotion(picomotor['axis'])
			except Exception, e:
				### Fail safe mode, stop controller's action ###
				picomotor['obj'].abortMotion()



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
		self._calibrate_steps = 100
		self.capgauge = capgauge_params
		self.picomotor = picomotor_params
		self.slope = {'up': 1.0, 'down': 1.0}
		self.offset = self.getPosition()
		self.is_position_motor_direction_reverse = False
		self.capgauge_pos = self.offset

		self.picomotor['obj'].setHomePosition(self.picomotor['axis'], 0)

	def calibratePositive(self):
		"""
		@Purpose:
			calibrate this motor leg in + direction of motor steps.
		"""
		# calibrate the upward relationship of slope and offset (assume linear relationship)
		b4_cap = self.getPosition()
		self.moveMotorRelatively(self._calibrate_steps)
		steps_cap = self.getPosition()

		# steps_cap = slope * calibrate_steps + curr_pos
		# cap_original_pos = slope * 0 + offset
		self.slope['up'] = (steps_cap - b4_cap) / self._calibrate_steps

		if steps_cap < self.offset:
			self.is_position_motor_direction_reverse = True

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
		self.slope['down'] = (steps_cap - b4_cap) / self._calibrate_steps

		self.capgauge_pos = self.getPosition()

	def getPosition(self):
		"""
		@Purpose:
			Get the Capgauge's current position
		@Output:
			(float) position
		"""
		return self.capgauge['obj'].readPositions(self.capgauge['slope'], self.capgauge['piston'])[self.capgauge['index']]

	def getMotorPosition(self):
		"""
		@Purpose:
			Get the Motor step position
		@Outpus:
			(int) position
		"""
		return self.picomotor['obj'].getActualPosition(self.picomotor['axis'])

	def moveMotorRelatively(self, change):
		"""
		@Purpose:
			move the motor relatively
		@Inputs:
			(int) change = relative change amount in motor steps. 
		"""
		self.picomotor['obj'].moveRelativePosition(self.picomotor['axis'], change)
		while not self.picomotor['obj'].isMotionDone(self.picomotor['axis']):
			pass
		self.capgauge_pos = self.getPosition()

	def moveMotorAbsoultely(self, target):
		"""
		@Purpose:
			move the motor to a target position
		@Inputs:
			(int) target = target motor step to move to.
		"""
		self.picomotor['obj'].moveTargetPosition(self.picomotor['axis'], target)
		while not self.picomotor['obj'].isMotionDone(self.picomotor['axis']):
			pass
		self.capgauge_pos = self.getPosition()

	def change(self, delta):
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

		old_pos = self.capgauge_pos
		############## iterative steps ##############
		target_pos = old_pos + delta
		#############################################

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
			self.picomotor['obj'].abortMotion()

