"""
picomotor_cmdLib_ironpython.py
"""

import clr
import optparse
import re
import sys
import System
import traceback
import time

functions_list = {"GetFirstDevice": "This method returns the first found device string.\n(stdout: str(dev))",
				"GetDevices": "This method returns the list of devices found.\n(stdout: str(dev1), str(dev2), str(dev3), ...",
				"GetIdentification": "This method gets the identification string from the specified device.\n(args: str(deviceKey))\n(stdout: str(id)",
				"GetHostName": "This method gets the hostname from the specified device.\n(args: str(deviceKey))\n(stdout: str(host))",
				"SetHostName": "This method sets the host name for the specified device.\n(args: str(deviceKey))\n(stdout: None)",
				"GetMotorType": "This method gets the motor type from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(motorType))",
				"SetMotorType": "This method sets the motor type for the specified device.\n(args: str(deviceKey), int(motorNum), str(motorType)); motorType=['NoMotor', 'Undefined', 'Tiny', 'Standard']",
				"GetPosition": "This method gets the current position from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(position))",
				"GetRelativeSteps": "This method gets the relative steps setting from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(relativeSteps))",
				"RelativeMove": "This method performs a relative move on the specified device.\n(args: str(deviceKey), int(motorNum), int(relativeSteps))",
				"GetAbsTargetPos": "This method gets the absolute target position from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(targetPos))",
				"AbsoluteMove": "This method performs an absolute move on the specified device.\n(args: str(deviceKey), int(motorNum), int(targetPos))",
				"JogNegative": "This method performs a jog in the negative direction on the speicified device.\n(args: str(deviceKey), int(motorNum))",
				"JogPositive": "This method performs a job in the positive direction on the specified device.\n(args: str(deviceKey), int(motorNum))",
				"AbortMotion": "This method performs an abort motion on the specified device.\n(args: str(deviceKey))",
				"StopMotion": "This method performs a stop motion on the specified device.\n(args: str(deviceKey), int(motorNum))",
				"SetZeroPosition": "This method sets the zero position (define home) for the specified device.\n(args: str(deviceKey), int(motorNum))",
				"GetMotionDone": "This method gets the motion done status from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(isDone))",
				"GetVelocity": "This method gets the veloctiy from the sepcified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(velocity))",
				"SetVelocity": "This method sets the velocity fro the specified device.\n(args: str(deviceKey), int(motorNum), int(velocity))",
				"GetAccerleration": "This method gets the accerleration from the specified device.\n(args: str(deviceKey), int(motorNum))\n(stdout: str(accerleration))",
				"SetAccerleration": "This method sets the accerleration from the specified device.\n(args: str(deviceKey), int(motorNum), int(accerleration))",
				"RunSeriesCommands": "This OPTION is for running series of functions as arguments.\n(ex. args: function1_arg1_arg2 function2_arg1_arg2 function3_arg1_arg2)"
}

# utility functions
def generateRuntimeError(cmdlib, deviceKey, errStr):
	errorNum = clr.Reference[str]()
	success = cmdlib.GetErrorNum(deviceKey, errorNum)
	if not success:
		errStr += 'ERROR: cmdlib.GetErrorNum(deviceKey, errorNum) FAILED.\n'
	errorMsg = clr.Reference[str]()
	success = cmdlib.GetErrorMsg(deviceKey, errorMsg)
	if not success:
		errStr += 'ERROR: cmdlib.GetErrorMsg(deviceKey, errorMsg) FAILED.\n'
	errStr += 'ERROR #%s: %s\n' % (errorNum.Value, errorMsg.Value)
	raise RuntimeError(errStr)

parser = optparse.OptionParser()
parser.add_option("-c", "--cmdlib", dest="cmdlibpath",
				help="specify the picomotor CmdLib.dll path", metavar="PATH",
				default="C:/Program Files/New Focus/New Focus Picomotor Application/Samples/")
parser.add_option("-D", "--debug", dest="debug", action="store_true",
				help="turn on the debug mode", default=False)
parser.add_option("-d", "--delayDiscovery", dest="delayDiscovery", action="store", type="int",
				help="set the delay for discovering devices in milliseconds. defaut 10 milliseconds.",
				metavar="MILLISECONDS", default=1500)
for f in functions_list:
	parser.add_option("--"+f, dest=f, action="store_true", default=False,
					help=functions_list[f])
(options, args) = parser.parse_args()

sys.path.append(options.cmdlibpath)
clr.AddReferenceToFile('CmdLib.dll')
from NewFocus.Picomotor import *

functions_return_type = {
				"GetFirstDevice": 'str',
				"GetDevices": 'str',
				"GetIdentification": 'str',
				"GetHostName": 'str',
				"SetHostName": None,
				"GetMotorType": 'CmdLib8742.eMotorType',
				"SetMotorType": None,
				"GetPosition": 'int',
				"GetRelativeSteps": 'int',
				"RelativeMove": None,
				"GetAbsTargetPos": 'int',
				"AbsoluteMove": None,
				"JogNegative": None,
				"JogPositive": None,
				"AbortMotion": None,
				"StopMotion": None,
				"SetZeroPosition": None,
				"GetMotionDone": 'bool',
				"GetVelocity": 'int',
				"SetVelocity": None,
				"GetAccerleration": 'int',
				"SetAccerleration": None,
}

# functions list:
if options.GetFirstDevice:
	deviceKey = clr.Reference[str]()
	cmdlib = CmdLib8742(options.debug, options.delayDiscovery, deviceKey)
	cmdlib.Shutdown()
	if deviceKey.Value == None:
		raise RuntimeError('ERROR: No Devices Found.')
	print re.sub(' ', '_', deviceKey.Value)
elif options.GetDevices:
	# default maximum 5 devices
	devicesKey = clr.Reference[System.Array[str]](('','','','',''))
	cmdlib = CmdLib8742(options.debug, options.delayDiscovery, devicesKey)
	cmdlib.Shutdown()
	deviceStr = ""
	if devicesKey.Value == None:
		raise RuntimeError('ERROR: No Devices Found.')
	for device in devicesKey.Value:
		deviceStr += re.sub(' ', '_', device)+","
	deviceStr = deviceStr[:-1]
	print deviceStr
else:
	firstDeviceKey = clr.Reference[str]()
	cmdlib = CmdLib8742(options.debug, options.delayDiscovery, firstDeviceKey)
	deviceKey = re.sub('_', ' ', args[0])
	if firstDeviceKey.Value != deviceKey:
		cmdlib.Close(firstDeviceKey.Value)
		cmdlib.Open(deviceKey)
	success = True
	errStr = ""
	try:
		if options.GetIdentification:
			identification = clr.Reference[str]()
			success = cmdlib.GetIdentification(deviceKey, identification)
			if not success:
				errStr = 'ERROR: cmdlib.GetIdentification(deviceKey, identification) FAILED.\n'
			else:
				print identification
		elif options.GetHostName:
			displayName = clr.Reference[str]()
			success = cmdlib.GetHostName(deviceKey, displayName)
			if not success:
				errStr = 'ERROR: cmdlib.GetHostName(deviceKey, displayName) FAILED.\n'
			else:
				print displayName
		elif options.GetMotorType:
			motorType = clr.Reference[CmdLib8742.eMotorType]()
			motorNum = int(args[1])
			success = cmdlib.GetMotorType(deviceKey, motorNum, motorType)
			if not success:
				errStr = 'ERROR: cmdlib.GetMotorType(deviceKey, motorNum, motorType) FAILED.\n'
			else:
				print motorType.Value.split('.')[-1]
		elif options.SetMotorType:
			motorNum = int(args[1])
			motorType = eval('CmdLib8742.eMotorType.'+args[2])
			success = cmdlib.SetMotorType(deviceKey, motorNum, motorType)
			if not success:
				errStr = 'ERROR: cmdlib.SetMotorType(deviceKey, motorNum, motorType) FAILED.\n'
		elif options.GetPosition:
			position = clr.Reference[int]()
			motorNum = int(args[1])
			success = cmdlib.GetPosition(deviceKey, motorNum, position)
			if not success:
				errStr = 'ERROR: cmdlib.GetPosition(deviceKey, motorNum, position) FAILED.\n'
			else:
				print position.Value
		elif options.GetRelativeSteps:
			relativeSteps = clr.Reference[int]()
			motorNum = int(args[1])
			success = cmdlib.GetRelativeSteps(deviceKey, motorNum, relativeSteps)
			if not success:
				errStr = 'ERROR: cmdlib.GetRelativeSteps(deviceKey, motorNum, relativeSteps) FAILED.\n'
			else:
				print relativeSteps.Value
		elif options.RelativeMove:
			motorNum = int(args[1])
			relativeSteps = int(args[2])
			success = cmdlib.RelativeMove(deviceKey, motorNum, relativeSteps)
			if not success:
				errStr = 'ERROR: cmdlib.RelativeMove(deviceKey, motorNum, relativeSteps) FAILED.\n'
		elif options.GetAbsTargetPos:
			targetPos = clr.Reference[int]()
			deviceKey = re.sub('_', ' ', args[0])
			motorNum = int(args[1])
			success = cmdlib.GetAbsTargetPos(deviceKey, motorNum, targetPos)
			if not success:
				errStr = 'ERROR: cmdlib.GetAbsTargetPos(deviceKey, motorNum, targetPos) FAILED.\n'
		elif options.AbsoluteMove:
			motorNum = int(args[1])
			targetPos = int(args[2])
			success = cmdlib.AbsoluteMove(deviceKey, motorNum, targetPos)
			if not success:
				errStr = 'ERROR: cmdlib.AbsoluteMove(deviceKey, motorNum, targetPos) FAILED.\n'
		elif options.JogNegative:
			motorNum = int(args[1])
			success = cmdlib.JogNegative(deviceKey, motorNum)
			if not success:
				errStr = 'ERROR: cmdlib.JogNegative(deviceKey, motorNum) FAILED.\n'
		elif options.JogPositive:
			motorNum = int(args[1])
			success = cmdlib.JogPositive(deviceKey, motorNum)
			if not success:
				errStr = 'ERROR: cmdlib.JogPositive(deviceKey, motorNum) FAILED.\n'
		elif options.AbortMotion:
			success = cmdlib.AbortMotion(deviceKey)
			if not success:
				errStr = 'ERROR: cmdlib.AbortMotion(deviceKey) FAILED.\n'
		elif options.StopMotion:
			motorNum = int(args[1])
			success = cmdlib.StopMotion(deviceKey, motorNum)
			if not success:
				errStr = 'ERROR: cmdlib.StopMotion(deviceKey, motorNum) FAILED.\n'
		elif options.SetZeroPosition:
			motorNum = int(args[1])
			success = cmdlib.SetZeroPosition(deviceKey, motorNum)
			if not success:
				errStr = 'ERROR: cmdlib.SetZeroPosition(deviceKey, motorNum) FAILED.\n'
		elif options.GetMotionDone:
			isMotionDone = clr.Reference[bool]()
			motorNum = int(args[1])
			success = cmdlib.GetMotionDone(deviceKey, motorNum, isMotionDone)
			if not success:
				errStr = 'ERROR: cmdlib.GetMotionDone(deviceKey, motorNum, isMotionDone) FAILED.\n'
			else:
				print isMotionDone.Value
		elif options.GetVelocity:
			velocity = clr.Reference[int]()
			motorNum = int(args[1])
			success = cmdlib.GetVelocity(deviceKey, motorNum, velocity)
			if not success:
				errStr = 'ERROR: cmdlib.GetVelocity(deviceKey, motorNum, velocity) FAILED.\n'
			else:
				print velocity.Value
		elif options.SetVelocity:
			motorNum = int(args[1])
			velocity = int(args[2])
			success = cmdlib.SetVelocity(deviceKey, motorNum, velocity)
			if not success:
				errStr = 'ERROR: cmdlib.SetVelocity(deviceKey, motorNum, velocity) FAILED.\n'
		elif options.GetAccerleration:
			accerleration = clr.Reference[int]()
			motorNum = int(args[1])
			success = cmdlib.GetAccerleration(deviceKey, motorNum, accerleration)
			if not success:
				errStr = 'ERROR: cmdlib.GetAccerleration(deviceKey, motorNum, accerleration) FAILED.\n'
			else:
				print accerleration.Value
		elif options.SetAccerleration:
			motorNum = int(args[1])
			accerleration = int(args[2])
			success = cmdlib.SetAccerleration(deviceKey, motorNum, accerleration)
			if not success:
				errStr = 'ERROR: cmdlib.SetAccerleration(deviceKey, motorNum, accerleration) FAILED.\n'
		elif options.RunSeriesCommands:
			for arg in args:
				tempList = arg.split('_')
				funct = tempList.pop(0)
				if len(tempList) == 1:
					deviceKey = re.sub('_', ' ', tempList[0])
					funct_type = eval("functions_return_type['"+funct+"']")
					if funct_type != None:
						exec("out = clr.Reference["+funct_type+"]()")
						exec("success = cmdlib."+funct+"(deviceKey, out)")
					else:
						exec("success = cmdlib."+funct+"(deviceKey)")
					if not success:
						errStr += 'ERROR: cmdlib.'+funct+"(deviceKey, out) FAILED.\n"
					elif funct_type != None:
						print out.Value
				elif len(tempList) == 2:
					deviceKey = re.sub('_', ' ', tempList[0])
					motorNum = int(tempList[1])
					funct_type = eval("functions_return_type['"+funct+"']")
					if funct_type != None:
						exec("out = clr.Reference["+funct_type+"]()")
						exec("success = cmdlib."+funct+"(deviceKey, motorNum, out)")
					else:
						exec("success = cmdlib."+funct+"(deviceKey, motorNum)")
					if not success:
						errStr += 'ERROR: cmdlib.'+funct+"(deviceKey, motorNum, out) FAILED.\n"
					elif funct_type != None:
						print out.Value
				elif len(tempList) == 3:
					deviceKey = re.sub('_', ' ', tempList[0])
					motorNum = int(tempList[1])
					if funct == 'SetMotorType':
						arg3 =  eval('CmdLib8742.eMotorType.'+tempList[2])
					else:
						arg3 = int(tempList[2])
					exec("success = cmdlib."+funct+"(deviceKey, motorNum, arg3)")
					if not success:
						errStr += 'ERROR: cmdlib.'+funct+"(deviceKey, motorNum, arg3) FAILED.\n"
		else:
			print 'WARNING: No function option SELECTED. EXTING.'
	except Exception, e:
		print 'ERROR: arguments parsing error!'
		traceback.print_exc()
	finally:
		cmdlib.Shutdown()
		if not success or errStr:
			generateRuntimeError(cmdlib, deviceKey, errStr)
