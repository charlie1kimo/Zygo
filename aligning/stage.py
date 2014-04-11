"""
stage.py
	This module contains classes to control different type of stages.
"""
import numpy
from picomotor import PicomotorWeb

class StageExceptions(Exception):
	"""
	@Purpose:
		custom Exception class for Stage
	"""
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: StageException; expression = %s; %s\n" % (repr(self.expr), self.msg)	

class Stage(object):
	"""
	@Purpose:
		General class for the Stage
	"""
	def __init__(self, controllers):
		"""
		@Purpose:
			constructor
		@Inputs:
			(list) controllers = list of controllers' hostnames.
		"""
		self.controllers = []
		for hostname in controllers:
			self.controllers.append(PicomotorWeb(hostname))

class NewFocus8081Stage(Stage):
	"""
	@Purpose:
		Stage class for model NewFocus 8081.
		=====================================
		Please connect the motors as:
			controller1 = [px1, px2, py]
			controller2 = [pz1, pz2]
		=====================================

		transfer matrix:
		| xtran |     | K  K  0  0  0  |     | px1 |
		| ytran |     | 0  0  K  0  0  |     | px2 |
		| ztran |  =  | 0  0  0  K  K  |  *  | py  |
		| xrot  |     | 0  0  0  R -R  |     | pz1 |
		| zrot  |     | R -R  0  0  0  |     | pz2 |

		motorSteps vs. distance (mm) correlations:	(performed by MANUAL MEASUREMENTS)
		px1: steps = 9373 * dist + 91.905, R^2 = 0.9998
		px2: steps = 8353.9 * dist + 1223.6, R^2 = 0.9925
		py: steps = 12077 * dist + 1233.1, R^2 = 0.9917
		pz1: steps = 10473 * dist - 680.95, R^2 = 0.9977
		pz2: steps = 11304 * dist - 647.62, R^2 = 0.9973
	"""
	def __init__(self, controllers):
		"""
		@Purpose:
			construtor
		@Inputs:
			(list) controllers = list of controllers' hostnames.
		"""
		# DIMENSION specs for this 8081 stage
		self.dimensions = {'length': 1,
							'width': 1,
							'height': 1}
		# correlation maps: (assumming linear relationship)
		#	{'motor': {'pos': positive_step_scale, 'neg': negative_step_scale}}
		self.correlations = {'px1': {'pos': 9373.3, 'neg': 9258.9},
							'px2': {'pos': 9416.8, 'neg': 6335},
							'py': {'pos': 13887, 'neg': 9701.7},
							'pz1': {'pos': 9534.7, 'neg': 10988},
							'pz2': {'pos': 10315, 'neg': 12262}}
		self.pos_xtrans = 0.0
		self.pos_ytrans = 0.0
		self.pos_ztrans = 0.0
		self.pos_xrot = 0.0
		self.pos_zrot = 0.0
		self.motorPositions = [0, 0, 0, 0, 0]
		super(NewFocus8081Stage, self).__init__(controllers)

	def __del__(self):
		# zero the motor steps
		self.moveMotor('px1', -1*self.motorPositions[0])
		self.moveMotor('px2', -1*self.motorPositions[1])
		self.moveMotor('py', -1*self.motorPositions[2])
		self.moveMotor('pz1', -1*self.motorPositions[3])
		self.moveMotor('pz2', -1*self.motorPositions[4])

	def abortAll(self):
		"""
		@Purpose:
			instantly stop all controllers' motion
		"""
		for c in self.controllers:
			c.abortMotion()

	def getPositions(self):
		return [self.pos_xtrans, self.pos_ytrans, self.pos_ztrans, self.pos_xrot, self.pos_zrot]

	def getMotorPositions(self):
		return self.motorPositions

	def updateMotorPositions(self):
		"""
		@Purpose:
			return the 5 motors positions
		"""
		self.motorPositions = [self.controllers[0].getTargetPosition(1),
								self.controllers[0].getTargetPosition(2),
								self.controllers[0].getTargetPosition(3),
								self.controllers[1].getTargetPosition(1),
								self.controllers[1].getTargetPosition(2)]

	def moveMotor(self, which, steps):
		"""
		@Purpose:
			move a specific motor by given motor steps
		@Inputs:
			(str) which = either 'px1', 'px2', 'py', 'pz1', or 'pz2'
			(int) steps = motor steps to move
		"""
		if steps == 0:
			return
		if which == 'px1':
			while not self.controllers[0].isMotionDone(1):
				pass
			self.controllers[0].moveRelativePosition(1, steps)
		elif which == 'px2':
			while not self.controllers[0].isMotionDone(2):
				pass
			self.controllers[0].moveRelativePosition(2, steps)
		elif which == 'py':
			while not self.controllers[0].isMotionDone(3):
				pass
			self.controllers[0].moveRelativePosition(3, steps)
		elif which == 'pz1':
			while not self.controllers[1].isMotionDone(1):
				pass
			self.controllers[1].moveRelativePosition(1, steps)
		elif which == 'pz2':
			while not self.controllers[1].isMotionDone(2):
				pass
			self.controllers[1].moveRelativePosition(2, steps)
		else:
			raise StageException("self.moveMotor(%s, %d)"%(which, steps),
								"NewFocus8081Stage doesn't support motor type: %s."%which)
		self.updateMotorPositions()

	def translateX(self, amounts):
		"""
		@Purpose:
			translate the stage in x-direction
		@Inputs:
			(float) amounts = move amounts in x-direction in (mm)
		"""
		if amounts == 0.0:
			return

		# px1
		while not self.controllers[0].isMotionDone(1):
			pass
		if amounts > 0:
			correlations = self.correlations['px1']['pos']
		else:
			correlations = self.correlations['px1']['neg']
		steps = correlations * amounts
		self.controllers[0].moveRelativePosition(1, steps)

		# px2
		while not self.controllers[0].isMotionDone(2):
			pass
		if amounts > 0:
			correlations = self.correlations['px2']['pos']
		else:
			correlations = self.correlations['px2']['neg']
		steps = correlations * amounts
		self.controllers[0].moveRelativePosition(2, steps)
		self.pos_xtrans += amounts
		self.updateMotorPositions()

	def translateY(self, amounts):
		"""
		@Purpose:
			translate the stage in y-direction
		@Inputs:
			(float) amounts = move amounts in y-direction in (mm)
		"""
		if amounts == 0.0:
			return
		# py
		while not self.controllers[0].isMotionDone(3):
			pass
		if amounts > 0:
			correlations = self.correlations['py']['pos']
		else:
			correlations = self.correlations['py']['neg']
		steps = correlations * amounts
		self.controllers[0].moveRelativePosition(3, steps)
		self.pos_ytrans += amounts
		self.updateMotorPositions()

	def translateZ(self, amounts):
		"""
		@Purpose:
			translate the stage in z-direciton
		@Inputs:
			(float) amounts = move amounts in z-direction in (mm)
		"""
		if amounts == 0.0:
			return

		# pz1
		while not self.controllers[1].isMotionDone(1):
			pass
		if amounts > 0:
			correlations = self.correlations['pz1']['pos']
		else:
			correlations = self.correlations['pz1']['neg']
		steps = correlations * amounts
		self.controllers[1].moveRelativePosition(1, steps)

		# pz2
		while not self.controllers[1].isMotionDone(2):
			pass
		if amounts > 0:
			correlations = self.correlations['pz2']['pos']
		else:
			correlations = self.correlations['pz2']['neg']
		steps = correlations * amounts
		self.controllers[1].moveRelativePosition(2, steps)
		self.pos_ztrans += amounts
		self.updateMotorPositions()

	def rotateX(self, amounts):
		"""
		@Purpose:
			rotate the stage along x-axis
		@Inputs:
			(float) amounts = rotate amounts (radians)
		"""
		if amounts == 0.0:
			return
		# displacements = (length / 2) * sin(rotation)
		displacements = self.specs['length']/2 * numpy.sin(amounts)

		# pz1
		while not self.controllers[1].isMotionDone(1):
			pass
		####### REVERSED DUE TO pz1 REVERSE in ROTATION #######
		if displacements > 0:
			correlations = self.correlations['pz1']['neg']
		else:
			correlations = self.correlations['pz1']['pos']
		steps = correlations * -1*displacements
		self.controllers[1].moveRelativePosition(1, steps)

		# pz2
		while not self.controllers[1].isMotionDone(2):
			pass
		if displacements > 0:
			correlations = self.correlations['pz2']['pos']
		else:
			correlations = self.correlations['pz2']['neg']
		steps = correlations * displacements
		self.controllers[1].moveRelativePosition(2, steps)
		self.pos_xrot += amounts
		self.updateMotorPositions()

	def rotateZ(self, amounts):
		"""
		@Purpose:
			rotate the stage along z-axis
		@Inputs:
			(float) amounts = rotate amounts (radians)
		"""
		if amounts == 0.0:
			return
		# displacements = (length / 2) * sin(rotation)
		displacements = self.specs['length']/2 * numpy.sin(amounts)

		# px1
		while not self.controllers[0].isMotionDone(1):
			pass
		if displacements > 0:
			correlations = self.correlations['px1']['pos']
		else:
			correlations = self.correlations['px1']['neg']
		steps = correlations * displacements
		self.controllers[0].moveRelativePosition(1, steps)

		# px2
		while not self.controllers[0].isMotionDone(2):
			pass
		##### REVERSED DUE TO px2 REVERSE in ROTATION #####
		if displacements > 0:
			correlations = self.correlations['px2']['neg']
		else:
			correlations = self.correlations['px2']['pos']
		steps = correlations * -1*displacements
		self.controllers[0].moveRelativePosition(2, steps)
		self.pos_zrot += amounts
		self.updateMotorPositions()

