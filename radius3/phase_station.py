"""
phase_station.py
	This file implements the class to interface with different
	phase station to take the focus measurements.
	It currently only supports Opticode
Author: Charlie Chen
"""
__version__ = '1.0'
__owner__ = '1.0'
'''
History:
3/4/2013	cchen	first created documentation
'''

import os
import re
import time

import radius3
from radius3.utilities import OutputBuffer
from radius3.rs232 import *

####################################################################
# class DMIPollingException
#	This class throws exception if DMI Poll returns "NOT READY"
####################################################################
class PhaseStationException(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: PhaseStationException; expression = %s; %s\n" % (repr(self.expr), self.msg)

#############################################################
# class PhaseStation
#	This class interface with the phase measurement
#
#	Notes on OpticodePCS:
#		1. old notes from C files
#			When taking multiple measurements for averaging, Opticode returns a
#			DN" or "ER" after the first measurement depending on whether it
#       	worked ok.   After all the measurements are taken, Opticode will
#       	return an "ER" if there was an error, else it will upload the report,
#       	ending with a "CTRL-D" character and then send a "RE".
#		2. Nomral Responses:
#			It returns a String of response; it seems like the recognized
#			response will be concatenated together. (ex. "FADN") Parsing
#			the response requires 2 bytes at a time. A report is inserted
#			between the recognized commands and separated by white space.
#		3. Error Responses(ER):
#			It seems like it comes with a colon, then an error code of 2 - 4 
#			digits number presented in String format. (ex. ER:120)
#############################################################
class PhaseStation(RS232):

	# __init__:
	# @Purpose:
	#	constructor; initialize the PhaseStation and its connection
	# @Inputs:
	#	params = parameters; CmdParameters.phase_info
	#	debug = True for debug on
	def __init__(self, params, printBuffer=OutputBuffer(), debug=False):
		self.CONTROL_CODES = {"OpticodePCS":{"GO": "GO",
											"FAULT": "FT",
											"GETFILE": "GF,%s\n",
											"LOADFILE": "CF,%s,%s\n",
											"CALIBRATE": "GC",
											"LOADCONFIG": "CL,%s\n",
											"TAGLINE": "TL %s %s\n",
											"SAVECONFIG": "CS,%s\n"}}
											
		self.RESPONSE_CODES = {"OpticodePCS":{"RE": "Ready for next command",
											"EX": "Operator Exited Remote Mode",
											"MA": "Operator Makes Manual Measurement",
											"DN": "Done Acquiring",
											"PA": "Measurement Passed Specifications",
											"FA": "Measurement Failed Specifications",
											"ER": "Error with Error Code"}}
		
		self.ERROR_CODES = {"OpticodePCS": \
				{10:"Out of memory",
				20:"Out of disk space",
				30:"Calibration check failed.",
				40:"Insufficient number of valid points measured",
				50:"Error loading config file",
				60:"Timed out waiting for environment to settle",
				70:"Acquisition failed due to an improper system setup",
				71:"Acquisition failed due to user aborting measurement",
				72:"Acquisition failed due to low fringe contrast, excessive vibration or poor phase shift",
				80:"No valid data points",
				90:"Could not load specified MAP file",
				100:"Error reading or saving MAPs during averaging",
				110:"Digitizer board failed to initialize",
				111:"Out of memory",
				112:"PCI bus-master mode error",
				113:"No valid data",
				114:"User aborted acquisition",
				117:"PZT is not calibrated",
				118:"Acquiring data is too noisy - PZT might not be calibrated",
				119:"The measuring system is not stable",
				122:"Least-square fitting error. Data is bad",
				123:"Error locking region to memory",
				124:"Error reading region",
				125:"Error unlocking region",
				126:"Null buffer error",
				127:"Error acquiring frame",
				128:"Error locking region",
				129:"Timed out waiting for environment to settle",
				200:"WARNING: Acquired data had poor phase shift (Map still calculated)"
				}}
		
		self.interested_terms = {"OpticodePCS":
							["Focus(wv)",		# focus
							"Z1(wv)",			# tip zernike (R*cos(theta))
							"Z2(wv)",			# tilt zernike (R*sin(theta))
							"Length(nu)",		# length of aperture
							"Width(nu)"]		# length of aperture
							}
	
		super(PhaseStation, self).__init__(params, printBuffer, debug)
		if self.debug:
			self.printBuffer.write("INFO: Initializing PhaseStation...")
		self.control_type = self.params.phase_type
		self.report = None
		self.isSync = False						# sync variable for extern prompts.
		self.cateye_cfg = "ce_cfg.cfg"
		self.centerofcurvature_cfg = "cc_cfg.cfg"
		### FOR GUI ###
		self.mainFrame = None					# default to None for NO GUI

		### Opticode (RS232) ###
		if self.params.phase_type == "OpticodePCS":
			self.initConnection()
		### METRO PRO TCP/IP CONNECTION HANDLE ###
		elif self.params.phase_type == "MetroPro":
			import radius3.metro_pro.mrc3_client as mrc3_client_module
			self.mrc3_client_module = mrc3_client_module
			try:
				self.mrc3Handle = self.mrc3_client_module.mrc3_new_interface()
				self.mrc3_client_module.mrc3_set_interface_params(self.mrc3Handle, self.params.connection_type, self.params.ip, self.params.port)
			except RuntimeError, e:
				errStr = "ERROR: creating phase station handle @ %s:%s with connection type: %s FAILED.\n" % \
						(self.params.ip, self.params.port, self.params.connection_type)
				errStr += "RuntimeError: " + e.message + "\n"
				raise PhaseStationException("self.mrc3Handle = self.mrc3_client_module.mrc3_new_interface()", errStr)
		##########################################

	# __del__:
	# @Purpose:
	#	Destructor. Clean up remaining connections
	def __del__(self):
		if self.params.phase_type == "OpticodePCS":
			self.close()
		elif self.params.phase_type == "MetroPro":
			self.mrc3_client_module.mrc3_free_interface(self.mrc3Handle)

	# run:
	# @Purpose:
	#	This function is a wrapper for all the possible commands that can run
	#	on the PhaseStation
	# @Inputs:
	#	cmd = (String) command to run on PhaseStation
	#	args = [list of arguments for the commands]
	#	tagline = tag line config string ("\n" terminated)
	def run(self, cmd, args=[], tagline=""):
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: PhaseStation running: cmd=%s, args=%s" % (cmd, repr(args)))
		self.flushInput()
		self.flushOutput()
	
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: Phasing - Please Wait...\n")
	
		# start communicating with phase computer
		CMD = self.CONTROL_CODES[self.control_type][cmd]
		if len(args) > 0:
			CMD = CMD % tuple(args)
		
		if not self.send(CMD):
			raise RS232Exception('PhaseStation.send(CMD)',
								'ERROR: Sending to Phase Station Error')
		
		# OpticodePCS LOADCONFIG has trailing run commands... (usually TAGLINE)
		if self.control_type == "OpticodePCS" and cmd == "LOADCONFIG":
			return
		# OpticodePCS TAGLINE has trailing config lines
		if self.control_type == "OpticodePCS" and cmd == "TAGLINE":
			self.send(tagline)
			self.send('\x04\x03')			# EOT (end of trasmission) & ETX (end of text)
		# Opticode FAULT need to wait operator to clear fault part on Opticode machine
		if self.control_type == "OpticodePCS" and cmd == "FAULT":
			self.printBuffer.write("**************************************************************")
			self.printBuffer.write("PROMPT: Hit Enter on the Opticode computer after removing the fault part.")
			self.printBuffer.write("**************************************************************")
			self.printBuffer.writePrintOutFlush("")
			if self.mainFrame != None:				# have GUI; WILL HALT HERE
				title = "Attention!"
				msg = "**************************************************************\nPROMPT: Hit Enter on the Opticode computer after removing the fault part.\nHit <OK> When ready.\n**************************************************************"
				self.mainFrame.popInfoOKBox(title, msg)
			else:
				self.printBuffer.writePrintOutFlush("Hit <Enter> on console when ready.")
				raw_input()
		
		# Getting and Parsing the responses:
		time.sleep(0.1)					# wait for 0.1 sec			
		if self.responseTimeout():				# not receiving any bytes; and reach system timeout
			raise RS232Exception('PhaseStation.inWaiting',
								'ERROR: receiving NO RESPONSES from PhaseStation. Check whether it is on remote mode.')
								
		recvBytes = self.inWaiting()
		response = self.recv(recvBytes)
		# parse the response
		(listResponses, listErrors) = self.parseRecognizedResponse(response)
		self.getErrors(listErrors)
		
		# Opticode GO command will have to handle the report parsing
		if self.control_type == "OpticodePCS" and cmd == "GO":
			if self.hasResponse("DN", listResponses):		# find "DN: Done Aquiring", proceed to report
				# gather all the report string / or the error strings
				EOT = '\x04'
				rChar = '\x00'			# default to NULL character first
				reportStr = ""
				while rChar != EOT:
					if re.match("ER:\d\d\d\dRE", reportStr):
						(lr, le) = self.parseRecognizedResponse(reportStr)
						listResponses += lr
						self.getErrors(le)					# throws an Exception about the error
						
					if self.responseTimeout():
						self.printBuffer.writePrintOutFlush("ERROR: phase station timeout when parsing reports!")
						raise RS232Exception("PhaseStation.parseReport",
											"ERROR: receiving NO REPORTS from PhaseStation. Check whether it is on remote mode.")
					while self.inWaiting() > 0:
						rChar = self.recv()
						if rChar == EOT:
							break
						reportStr += rChar
				
				self.parseReport(reportStr)
				
				# one more check for "RE" (READY) after reading report	
				if self.responseTimeout():
					raise RS232Exception('PhaseStation.inWaiting',
									'ERROR: receiving NO RESPONSES from PhaseStation. Check whether it is on remote mode.')
				response = self.recv(self.inWaiting())
				(lr,le) = self.parseRecognizedResponse(response)
				listResponses += lr
				self.getErrors(le)							# throws an Exception if there is an error
		
		# check if PhaseStation is ready:
		if not self.isReady(listResponses):
			self.isSync = False
			self.printBuffer.writePrintOutFlush("ERROR: PhaseStation link is NOT Ready after run(); try to re-sync...")
			self.sync()
		else:
			self.isSync = True
			
		# DEBUG: print out regular responses:
		if self.debug:
			self.getResponses(listResponses)
			# print report and interested terms:	
			if cmd == "GO":
				self.printBuffer.writePrintOutFlush("INFO: Phase Station Report:")
				for t in self.interested_terms[self.control_type]:
					self.printBuffer.writePrintOutFlush("%s: %0.7f" % (t, self.report[t]))
	
	# parseReport:
	# @Purpose:
	#	This function parse the responses from phase station are all reports end with EOT ('\x04')
	#	Reports usually end with EOT (end of transmission) character = '\x04' (for Opticode)
	# @Inputs:
	#	reportStr = (String) report string
	def parseReport(self, reportStr):
		if self.control_type == "OpticodePCS":				
			# parse REPORTS:
			self.report = {}
			terms = [re.sub(' ', '', i) for i in reportStr.split('\n')[0].split(',')]		# trims the white spaces...
			value = []
			for i in reportStr.split('\n')[1].split(','):
				try:
					value.append(float(i))
				except ValueError:			# this are for String entries
					value.append(re.sub(' ', '', i))
			for i in range(len(terms)):
				self.report[terms[i]] = value[i]
				
	# parseRecognizedResponse:
	# @Purpose:
	#	Parsing only the recognized responses.
	# @Inputs:
	#	response = (String) series of response
	# @Outputs:
	#	tuples of (listOfRecognizedResponses, listOfError)
	def parseRecognizedResponse(self, response):
		if self.control_type == "OpticodePCS":
			listResponses = []
			listErrors = []
			while len(response) > 0:
				r = response[:2]				# two characters
				if r == "ER":					# has errors "ER:xxxx" 4 characters code
					e = response[3:7]
					listErrors.append(int(e))
					listResponses.append(r)
					response = response[7:]			# dropped parsed codes
				else:
					listResponses.append(r)
					response = response[2:]			# dropped parsed response
						
			return (listResponses, listErrors)
		elif self.control_type == "MetroPro":
			err = self.mrc3_client_module.mrc3_get_script_error(self.mrc3Handle)
			if err != 0:							# has error. just output script errors
				return ([], ["ERROR: "+self.mrc3_client_module.mrc3_get_error_message(err), \
							response+"\nIs GPI.app the FRONT MOST App?"])
			else:
				return (response.split(), [])
		else:
			pass
	
	# getResponses
	# @Purpose:
	#	Debugging; printing out the recognized responses that phase station returns
	def getResponses(self, listResponses):
		mStr = ""
		for mCode in listResponses:
			mStr += "INFO: Phase Station return, %s: %s\n" % \
				(repr(mCode), self.RESPONSE_CODES[self.control_type][mCode])
		self.printBuffer.writePrintOutFlush(mStr)
		
	# getErrors (throws exceptions)
	# @Purpose:
	#	Get and raise exceptions if there is error.
	def getErrors(self, listErrors):
		if len(listErrors) > 0:			# errors responses
			if self.control_type == "OpticodePCS":
				errStr = ""
				for eCode in listErrors:
					errStr += "ERROR: error with error code %d: %s\n" % \
								(eCode, self.ERROR_CODES[self.control_type][eCode])
				raise RS232Exception('response = self.recv(recvBytes)', errStr)
			elif self.control_type == "MetroPro":
				errStr = ""
				for err in listErrors:
					errStr += err+"\n\n"
				raise PhaseStationException('self.mrc3_client_module.mrc3_get_script_output(self.mrc3Handle)', errStr)
	
	# isReady:
	# @Purpose:
	#	check if the PhaseStation link is ready again.
	# @Input:
	#	listResponses = list of responses
	# @Output:
	#	True if it's ready; False otherwise
	def isReady(self, listResponses):
		if self.control_type == "OpticodePCS":
			return self.hasResponse("RE", listResponses)
		else:
			return self.isSync
			
	# hasResponse:
	# @Purpose:
	#	check if the phase station response contains the given response code
	# @Input:
	#	resp = response code
	#	listResponses = list of responses from phase station
	# @Output: True if it contains response code; False otherwise
	def hasResponse(self, resp, listResponses):
		if self.control_type == "OpticodePCS":
			if resp in listResponses:
				return True
			else:
				return False
		else:
			return False
	
	# sync: (previously sync_comp)
	# @Purpose:
	#	synchronize the PhaseStation link.
	def sync(self):
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: PhaseStation: synchronizing links...")
		if self.control_type == "OpticodePCS":
			self.calibrate()
		elif self.control_type == "MetroPro":
			try:
				self.mrc3_client_module.mrc3_ping_server(self.mrc3Handle)
				self.isSync = True
			except RuntimeError, e:
				errStr = "ERROR: creating phase station handle @ %s:%s with connection type: %s FAILED.\n" % \
						(self.params.ip, self.params.port, self.params.connection_type)
				errStr += "RuntimeError: " + e.message + "\n"
				self.isSync = False
				raise PhaseStationException("self.mrc3_client_module.mrc3_ping_server(self.mrc3Handle)", errStr)
		else:
			raise PhaseStationException("self.sync()", "ERROR: Unsupported Phase Station type")
	
	# go: (previously run_on_host)
	# @Purpose:
	#	Perform the PhaseStation measurement...
	def go(self):
		if self.control_type == "OpticodePCS":
			self.run("GO")
		elif self.control_type == "MetroPro":
			try:
				fScript = open(os.path.dirname(radius3.__file__)+'/metro_pro/EPOgetzrnaperture.scr', 'r')
				script = fScript.read()
				fScript.close()
				self.mrc3_client_module.mrc3_set_script_context(self.mrc3Handle, self.mrc3_client_module.MRC_SCRIPT_CONTEXT_FRONTMOST_APP)
				self.mrc3_client_module.mrc3_set_script_text(self.mrc3Handle, script)
				self.mrc3_client_module.mrc3_run_script(self.mrc3Handle, True)
				responses = self.mrc3_client_module.mrc3_get_script_output(self.mrc3Handle).rstrip(os.linesep)
				(lr, le) = self.parseRecognizedResponse(responses)
				self.getErrors(le)

				# setup reports as the same format.
				(tip, tilt, focus, length, width) = lr
				self.report = {}
				self.report['Tip'] = float(tip)
				self.report['Tilt'] = float(tilt)
				self.report['Focus'] = float(focus)
				self.report['Length'] = float(length)
				self.report['Width'] = float(width)
			except IOError, e:
				raise PhaseStationException("fScript = open('"+os.path.dirname(radius3.__file__)+"/metro_pro/EPOgetzrnaperture.scr', 'r')",
											"ERROR: MetroPro measurement script EPOgetzrnaperture.scr NOT FOUND.")
			except RuntimeError, e:
				raise PhaseStationException("self.mrc3_client_module.mrc_run_script(self.mrc3Handle, True)", 
											"ERROR: MetroPro FAILS to run target script. Is MetroPro server OFFLINE?")

			
	# writeConfig:
	# @ Purpose:
	#	writes a configuration file to "file"
	# @Inputs:
	#	file = (String) file path.
	def writeConfig(self, file):
		if self.control_type == "OpticodePCS":
			self.run("SAVECONFIG", [file])
			
	# loadConfig:
	def loadConfig(self, file):
		if self.control_type == "OpticodePCS":
			self.run("LOADFILE", [file, "F"])
			
	# calibrate:
	def calibrate(self):
		if self.control_type == "OpticodePCS":
			self.run("CALIBRATE")
	
	# ft
	def ft(self):
		if self.control_type == "OpticodePCS":
			self.run("FAULT")
			
	# tagline
	# @Purpose:
	#	Setup config file loading and send a config tag line.
	# @Inputs:
	#	tagline = (String) of tag lines feed
	def tagline(self, tagline):
		if self.control_type == "OpticodePCS":
			self.run("LOADCONFIG", ["F"])
			self.run("TAGLINE", [4530,1], tagline)
			
	# setCavitiyLength
	# @Purpose:
	# 	This function is passed the test position, and the radii of the transmission sphere and the test
	#	optic.  The proper cavity length is computed and the function then
	#	automatically sets Opticode to this value.  It is up to Opticode to re-calibrate for the new
	#	cavity length.
	# @Inputs:
	#	cateye = (bool) True if cateye, False if center of curvature
	#	tsRadius = (float) transmission sphere radius (mm)
	#	partRadius = (float) part radius (mm)
	def setCavityLength(self, cateye, tsRadius, partRadius):
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: PhaseStation setting cavity length with parameters: ")
			self.printBuffer.writePrintOutFlush("\t cateye: %s, tsRadius = %f, partRadius = %f" % (repr(cateye), tsRadius, partRadius))
		
		if cateye:
			cavity_length = tsRadius * 1000.0
		else:
			cavity_length = (tsRadius + partRadius) * 1000.0
		
		# setting cavity length to PhaseStation
		self.flushInput()
		self.flushOutput()
		
		if self.control_type == "OpticodePCS":
			tagline = repr(cavity_length)+"\n"
			self.tagline(tagline)
	
	# setWaveShift:
	# @Purpose:
	#	 This function sets up the wave shifting phase station
	# @Inputs:
	#	cateye = (bool) True if cateye, False if center of curvature
	#	tsRadius = (float) transmission sphere radius (mm)
	#	partRadius = (float) part radius (mm)
	def setWaveShift(self, cateye, tsRadius, partRadius):
		if self.debug:
			self.printBuffer.writePrintOutFlush("INFO: PhaseStation is setting wave shift...")
		
		self.setCavityLength(cateye, tsRadius, partRadius)
		self.flushInput()
		time.sleep(0.001)
		
		self.calibrate()
		time.sleep(0.001)
		self.flushInput()
		
		if cateye:
			self.writeConfig(self.cateye_cfg)
		else:
			self.writeConfig(self.centerofcurvature_cfg)
	
	# getFocus
	# @Purpose:
	#	return the focus measured from phase station
	# @Output:
	#	(float) focus value (in wv)
	def getFocus(self):
		if self.report == None:
				raise PhaseStationException("self.getFocus()",
									"ERROR: phase station report is EMPTY. Error syncing with phase station?")
		if self.control_type == "OpticodePCS":
			return self.report["Focus(wv)"]
		elif self.control_type == "MetroPro":
			return self.report["Focus"]
		else:
			# FOR OTHER PHASE STATION, IMPLEMENT HERE
			return None
			
	# getTipZernike
	# @Purpose:
	#	return the tip zernike measured from phase station
	# @Output:
	#	(float) tip zernike (Z1) value (in wv)
	def getTipZernike(self):
		if self.report == None:
			raise PhaseStationException("self.getTipZernike()",
								"ERROR: phase station report is EMPTY. Error syncing with phase station?")
		if self.control_type == "OpticodePCS":
			return self.report["Z1(wv)"]
		elif self.control_type == "MetroPro":
			return self.report["Tip"]
		else:
			# FOR OTHER PHASE STATION, IMPLEMENT HERE
			return None
		
	# getTiltZernike
	# @Purpose:
	#	return the tilt zernike measured from phase station
	# @Output:
	#	(float) tilt zernike (Z2) value (in wv)
	def getTiltZernike(self):
		if self.report == None:
			raise PhaseStationException("self.getTiltZernike()",
								"ERROR: phase station report is EMPTY. Error syncing with phase station?")
		if self.control_type == "OpticodePCS":
			return self.report["Z2(wv)"]
		elif self.control_type == "MetroPro":
			return self.report["Tilt"]
		else:
			# FOR OTHER PHASE STATION, IMPLEMENT HERE
			return None
			
	# getLength
	# @Purpose:
	#	return the length of aperture measured from phase station
	# @Output:
	#	(float) length value (in nu)
	def getLength(self):
		if self.report == None:
			raise PhaseStationException("self.getLength()",
									"ERROR: phase station report is EMPTY. Error syncing with phase station?")
		if self.control_type == "OpticodePCS":
			return self.report["Length(nu)"]
		elif self.control_type == "MetroPro":
			return self.report["Length"]
		else:
			# FOR OTHER PHASE STATION, IMPLEMENT HERE
			return None
	
	# getWidth
	# @Purpose:
	#	return the width of aperture measured from phase station
	# @Output:
	#	(float) width value (in nu)
	def getWidth(self):
		if self.report == None:
			raise PhaseStationException("self.getWidth()",
									"ERROR: phase station report is EMPTY. Error syncing with phase station?")
		if self.control_type == "OpticodePCS":
			return self.report["Width(nu)"]
		elif self.control_type == "MetroPro":
			return self.report["Width"]
		else:
			# FOR OTHER PHASE STATION, IMPLEMENT HERE
			return None
			