"""
reset_anonymous_positions.py
"""

import numpy
from actuator import *

# home positions of motors in (um)
MOTOR_HOME_POSITIONS = numpy.array([2.0225, -16.985, -0.465, -164.7475, -10.015, 16.6775])
# tolerances 
TOLERANCE = 0.005
# NI config file path
NI_config = './NI_composite_capgauge.config'
# picomotor controllers
controllers = ['8742-10140', '8742-10159']
# actuator obj
actuator = HexaPodActuator(NI_config, controllers)

delta = MOTOR_HOME_POSITIONS - actuator.getPositions()
for legInd in range(len(actuator.legs)):
	leg = actuator.legs[legInd]

	while abs(delta[legInd]) > TOLERANCE:
		leg.change(delta[legInd])
		delta = MOTOR_HOME_POSITIONS - actuator.getPositions()

print "Finished:"
print "HOME: ", MOTOR_HOME_POSITIONS
print "CURRENT: ", actuator.getPositions()
