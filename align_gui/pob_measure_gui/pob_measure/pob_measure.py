"""
pob_measure.py
	This is a low level module for handling the pob measurement automation.
"""

import sys
sys.path.append("C:/motion")

import wx
from align_py.pob_measure_gui.pob_measure import autonul
import metro_pro_client.mrc3_client as mrc3_client
from pob_measure_wx_event import PobMeasureProgressEvent
from pob_measure_wx_event import PobMeasureErrorEvent
from pob_measure_wx_event import PobMeasureUpdateTestLetterEvent
import pobtest

class PobMeasureException(Exception):
	"""
	@Purpose:
		This is a custom exception class for PobMeasure.
	"""
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: PobMeasureException; expression = %s; %s\n" % (repr(self.expr), self.msg)

class PobMeasure(object):
	"""
	@Purpose:
		This class create a PobMeasure object.
	"""
	def __init__(self, metroProIP, wxWidget=None):
		"""
		@Purpose:
			Constructor
		"""
		##### PRIVATE VARIABLE #####
		self.__isMeasuring__ = False
		self.__stop__ = False
		self.__metroProParamFile__ = "\\\\1PBZ3V1/POB_Shared/pob_measure_params.txt"
		self.__metroProSleepParamFile__ = "\\\\1PBZ3V1/POB_Shared/pob_measure_sleep_params.txt"
		### Retro Sphere Current Rotation (deg)
		self.__currRetroRot__ = 0
		############################
		##### filename: a<pobID><testLetter>_<fieldNumber>_<xpos*1000>_<ypos*1000>_<fieldRepeatIter>.dat #####
		self.savedFileNameTemplate = "a%s%s_%d_%d_%d_%d.dat"
		######################################################################################################
		if wxWidget != None:
			assert isinstance(wxWidget, wx.Frame), "ERROR: wxWidget attached to PobMeasure should be an instance of wx.Frame"
		self.wxWidget = wxWidget
		self.metroProIP = metroProIP
		self.pobID = ""
		self.fieldCoordinates = [(0,0),(1,1),(1,-1),(-1,-1),(-1,1)]
		self.tsCenterFieldCoordinates = None
		self.pobRotation = None
		self.numAvgMapPerField = 128
		self.numFieldRepeats = 4
		self.numFullMeasurementRepeats = 1
		self.retroRotation = 0
		self.testLetter = ""
		self.measurementStartDelay = 0		# in seconds
		self.autoNullParameters = {'RS': {'iter': 2, 'type': "RetroSph Trans"},
									'TS': {'iter': 0, 'type': "TransSph Trans"}}

	def postWxProgressEvent(self, msg):
		"""
		@Purpose:
			Post a wxProgressEvent for the wxPython GUI to update the progress.
		@Inputs:
			(str) msg = progress display message
		"""
		if self.wxWidget != None:
			wx.PostEvent(self.wxWidget, PobMeasureProgressEvent(message=msg))

	def postWxErrorEvent(self, msg):
		"""
		@Purpose:
			Post a wxErrorEvent for the wxPython GUI to handle the error message in the measurement.
		@Inputs:
			(str) msg = error display message
		"""
		if self.wxWidget != None:
			wx.PostEvent(self.wxWidget, PobMeasureErrorEvent(message=msg))
		else:
			print "ERROR in pob_measure.PobMeasure.measure: %s" % msg

	def postWxUpdateTestLetterEvent(self, testLetter):
		"""
		@Purpose:
			Post a wxUpdateTestLetterEvent for updating GUI's testLetter parameters as we go.
		@Inputs:
			(str) testLetter = testLetter to be updated.
		"""
		if self.wxWidget != None:
			wx.PostEvent(self.wxWidget, PobMeasureUpdateTestLetterEvent(testLetter=testLetter))

	def autonull(self):
		"""
		@Purpose:
			perform auotnull by preset autonull parameters.
		"""
		# RS
		RSType = self.autoNullParameters['RS']['type']
		for autoIter in range(1, self.autoNullParameters['RS']['iter']+1):
			self.postWxProgressEvent("RS %s Autonulling #%d..." % (RSType, autoIter))
			AUTONULL_PARAMS = autonul.autonulchoices[RSType]
			autonul.moveautonul(AUTONULL_PARAMS)
		# TS
		TSType = self.autoNullParameters['TS']['type']
		for autoIter in range(1, self.autoNullParameters['TS']['iter']+1):
			self.postWxProgressEvent("TS %s Autonulling #%d..." % (TSType, autoIter))
			AUTONULL_PARAMS = autonul.autonulchoices[TSType]
			autonul.moveautonul(AUTONULL_PARAMS)

	def measure(self):
		"""
		@Purpose:
			perform the automated measurements
		"""
		##### START DELAY #####
		if self.measurementStartDelay > 0:
			self.postWxProgressEvent("Delaying %f minutes to start..." % (self.measurementStartDelay/60))
			fSleepParam = open(self.__metroProSleepParamFile__, "w")
			fSleepParam.write("%d" % int(self.measurementStartDelay))
			fSleepParam.close()
			try:
				(outBuffer, errMsg, errNum) = mrc3_client.run_script("EPOsleep.scr", self.metroProIP)
			except mrc3_client.MetroProClientException, exception:
				self.postWxErrorEvent(str(exception))
				self.__isMeasuring__ = False
				raise exception
		############################

		self.__isMeasuring__ = True
		### check the TS against TS Center Field Coordinates
		if self.tsCenterFieldCoordinates != None:
			##### PERFORM CHECKS #####
			tsCenterFieldDifferenceThreshold = 0.005
			self.postWxProgressEvent("Checking the TS against the TS Center Field Coordinates...")
			ts_x_pos = pobtest.tsxmotor.update_position()
			ts_y_pos = pobtest.tsymotor.update_position()
			ts_z_pos = pobtest.tszmotor.update_position()
			if abs(self.tsCenterFieldCoordinates[0] - ts_x_pos) > tsCenterFieldDifferenceThreshold or \
				abs(self.tsCenterFieldCoordinates[1] - ts_y_pos) > tsCenterFieldDifferenceThreshold or \
				abs(self.tsCenterFieldCoordinates[2] - ts_z_pos) > tsCenterFieldDifferenceThreshold:
				self.postWxErrorEvent("TS Coordinates are out of tolerant range! Check if TS Coordinates is centered.")
				self.__isMeasuring__ = False
				return

		##### Initialization for MetroScript Measuring: #####
		self.postWxProgressEvent("Initialize MetroScript parameters...")
		(outBuffer, errMsg, errNum) = mrc3_client.run_script("EPOinit5f.scr", self.metroProIP)
		#####################################################

		for fullMeasIter in range(1, self.numFullMeasurementRepeats+1):
			self.postWxProgressEvent("Performing Full Measurement Iter#%d: with test letter: '%s'" % (fullMeasIter, self.testLetter))

			for (ind,field) in enumerate(self.fieldCoordinates):
				###### RESET Retro Rotation to 0 degree if necessary #####
				if self.__currRetroRot__ != 0:
					self.postWxProgressEvent("Reset Retro Rotation to 0 degree.")
					pobtest.retspherermotor.move(-1*self.__currRetroRot__)
					self.__currRetroRot__ = 0
				##########################################################

				########## MOVE TS & RETRO if necessary ###########
				if ind > 0:
					self.postWxProgressEvent("Moving TS and RETRO from %s to: %s" % (repr(self.fieldCoordinates[ind-1]), repr(field)))
					tsxmove = field[0] - self.fieldCoordinates[ind-1][0]
					tsymove = field[1] - self.fieldCoordinates[ind-1][1]
					pobtest.tsxmotor.move(tsxmove)
					pobtest.tsymotor.move(tsymove)
					pobtest.retsphere.movex(-0.2*tsxmove)
					pobtest.retsphere.movey(-0.2*tsymove)
				###################################################

				for fIter in range(1,self.numFieldRepeats+1):
					###### DISPLAY EVENT #######
					self.postWxProgressEvent("Starting Measurement #%d on: %s, iteration: %d" % (ind, repr(field), fIter))
					############################

					###### CALL AUTONULL #######
					self.autonull()
					############################

					############## STOP PRESSED ############
					if self.__stop__:
						self.__stop__ = False
						self.postWxProgressEvent("Measurement STOPPED.")
						self.postWxProgressEvent("==========================")
						self.__isMeasuring__ = False
						return
					########################################

					savedFileName = self.savedFileNameTemplate % \
						(self.pobID, self.testLetter, ind, field[0]*1000, field[1]*1000, fIter)

					##### CALL METROSCRIPT #####
					self.postWxProgressEvent("Calling MetroPro to measure...")
					fParam = open(self.__metroProParamFile__, 'w')
					fParam.write("%d, %d, %d, %d, %s" % (field[0]*1000, field[1]*1000, self.pobRotation, self.numAvgMapPerField, savedFileName))
					fParam.close()
					try:
						(outBuffer, errMsg, errNum) = mrc3_client.run_script("EPOtakedata5f.scr", self.metroProIP)
					except mrc3_client.MetroProClientException, exception:
						self.postWxErrorEvent(str(exception))
						self.__isMeasuring__ = False
						raise exception
					############################

					############## STOP PRESSED ############
					if self.__stop__:
						self.__stop__ = False
						self.postWxProgressEvent("Measurement STOPPED.")
						self.postWxProgressEvent("==========================")
						self.__isMeasuring__ = False
						return
					########################################

					##### ROTATE RETRO if necessary #####
					if self.retroRotation > 0:
						self.postWxProgressEvent("Request Rotating Retro by %d degree..." % self.retroRotation)
						pobtest.retspherermotor.move(self.retroRotation)
						self.__currRetroRot__ += self.retroRotation
					#####################################

					############## STOP PRESSED ############
					if self.__stop__:
						self.__stop__ = False
						self.postWxProgressEvent("Measurement STOPPED.")
						self.postWxProgressEvent("==========================")
						self.__isMeasuring__ = False
						return
					########################################

					##### DISPLAY EVENT #####
					self.postWxProgressEvent("Measurement #%d on: %s, iteration: %d is DONE." % (ind, repr(field), fIter))
					#########################
			
			##### DISPLAY DONE EVENT; move back to (0,0) #####
			self.postWxProgressEvent("Moving TS and RETRO from %s to: %s" % (repr(self.fieldCoordinates[-1]), repr(self.fieldCoordinates[0])))
			tsxmove = self.fieldCoordinates[0][0] - self.fieldCoordinates[-1][0]
			tsymove = self.fieldCoordinates[0][1] - self.fieldCoordinates[-1][1]
			pobtest.tsxmotor.move(tsxmove)
			pobtest.tsymotor.move(tsymove)
			pobtest.retsphere.movex(-0.2*tsxmove)
			pobtest.retsphere.movey(-0.2*tsymove)
			###### CALL AUTONULL #######
			self.autonull()
			###### Print this full measurement is done. ######
			self.postWxProgressEvent("Full Measurement Iter#%d: with test letter: '%s' is DONE." % (fullMeasIter, self.testLetter))
			###### UPDATE TEST LETTER ######
			self.updateTestLetter()

		############################
		self.postWxProgressEvent("Measurements are ALL DONE.")
		self.udataarc()
		self.postWxProgressEvent("==========================")
		##############################
		self.__isMeasuring__ = False

	def stop(self):
		"""
		@Purpose:
			Stop the next iteration measurement.
		"""
		if self.__isMeasuring__:
			self.__stop__ = True

	def setPobID(self, pobId):
		"""
		@Purpose:
			pobID setter
		@Inputs:
			(String) id
		"""
		self.pobID = pobId

	def setFieldCoordinates(self, inputs):
		"""
		@Purpose:
			field coordinates setter
		@Inputs:
			(list or int) inputs
		"""		
		if type(inputs) == list:
			self.fieldCoordinates = inputs
		elif type(inputs) == int or type(inputs) == float:
			self.fieldCoordinates = [(0,0),(inputs, inputs), (inputs, -1*inputs), (-1*inputs, -1*inputs), (-1*inputs, inputs)]
		else:
			raise PobMeasureException("PobMeasure.setFieldCoordinates(%s)"%str(inputs),
									"ERROR: Input Field Coordinates are not 'LIST', 'FLOAT', nor 'INT'!")

	def setTSCenterFieldCoordinates(self, coords):
		"""
		@Purpose:
			tsCenterFieldCoordinates setter
		@Inputs:
			(list) coords
		"""
		self.tsCenterFieldCoordinates = coords

	def setPobRotation(self, deg):
		"""
		@Purpose:
			pobRotation setter
		@Inputs:
			(int) deg
		"""
		self.pobRotation = deg

	def setNumAvgMapPerField(self, avg):
		"""
		@Purpose:
			numAvgMapPerField setter
		@Inputs:
			(int) avg
		"""
		self.numAvgMapPerField = avg

	def setNumFieldRepeats(self, repeats):
		"""
		@Purpose:
			numFieldRepeats setter
		@Inputs:
			(int) repeats
		"""
		self.numFieldRepeats = repeats

	def setNumFullMeasurementRepeats(self, repeats):
		"""
		@Purpose:
			numFullMeasurementRepeats setter
		@Inputs:
			(int) repeats
		"""
		self.numFullMeasurementRepeats = repeats

	def setRetroRotation(self, deg):
		"""
		@Purpose:
			retroRotation setter
		@Inputs:
			(int) deg = deg
		"""
		self.retroRotation = deg

	def setTestLetter(self, letters):
		"""
		@Purpose:
			testLetter setter
		@Inputs:
			(String) letters
		"""
		self.testLetter = letters

	def setMeasurementStartDelay(self, delayInMin):
		"""
		@Purpose:
			measurementStartDelay setter
		@Inputs:
			(float) delayInMin
		"""
		self.measurementStartDelay = delayInMin * 60

	def setAutoNullParameter(self, RSParams, TSParams):
		"""
		@Purpose:
			autoNullParameters setter
		@Inputs:
			(dict) RSParams: {'iter': (int) iterations, 'type': (str) moveType}
			(dict) TSParams: {'iter': (int) iterations, 'type': (str) moveType}
		"""
		self.autoNullParameters['RS']['iter'] = RSParams['iter']
		self.autoNullParameters['RS']['type'] = RSParams['type']
		self.autoNullParameters['TS']['iter'] = TSParams['iter']
		self.autoNullParameters['TS']['type'] = TSParams['type']

	def updateTestLetter(self):
		"""
		@Purpose:
			update the Test Letter to the next Test Letter sequence
		"""
		if self.testLetter:
			for indTestLetter in range(len(self.testLetter)):
				currCheckInd = len(self.testLetter)-(indTestLetter+1)
				currChar = self.testLetter[currCheckInd]
				if currChar != 'z':
					nextChar = chr(ord(currChar)+1)
					self.testLetter = self.testLetter[:currCheckInd] + nextChar + self.testLetter[currCheckInd+1:]
					break
				else:
					nextChar = 'a'
					self.testLetter = self.testLetter[:currCheckInd] + nextChar + self.testLetter[currCheckInd+1:]

				##### end check, add a new letter to the end #####
				if indTestLetter == (len(self.testLetter) - 1):
					self.testLetter += 'a'

			self.postWxUpdateTestLetterEvent(self.testLetter)

	def udataarc(self):
		"""
		@Purpose:
			upload the measurement data to shared location after measurements.
			Currently calls MetroScript on the remote computer to do the data upload.
		"""
		self.postWxProgressEvent("Uploading data through udataarc...")
		try:
			(outBuffer, errMsg, errNum) = mrc3_client.run_script("epodarc.scr", self.metroProIP)
			return
		except mrc3_client.MetroProClientException, exception:
			self.postWxErrorEvent(str(exception))
			raise exception
