"""
weather_station.py
	This file implements the weather station to read and retreive
	the environment variables (namely temperature, pressure, and
	humidity) from the environment probes
Author: Charlie Chen
"""
import numpy

from env_database.envdb import EnvDB
from radius3.utilities import OutputBuffer
from radius3.rs232 import *


#######################################################################
# class WeatherProbingException
#	This class throws exception for probing non-existent weather probe
#######################################################################
class WeatherProbingException(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	def __str__(self):
		return "ERROR: WeatherProbingException; expression = %s; %s\n" % (repr(self.expr), self.msg)


###########################################################
# class WeatherStation
# 	This class interfaces with weather station
###########################################################
class WeatherStation(RS232):

	def __init__(self, params, cts_in, printBuffer=OutputBuffer(), debug=False):
		######### CONSTANTS ##########
		self.index_of_air = 1.0			# index of air
		self.temperatureConst = 22.0			# default temperature in degree C
		self.pressureConst = 760.0			# default pressure in mmHg
		self.humidityConst = 50.0			# default relative humidity in %
		self.partTemperature = 22.0		# default part temperature in degree C
		self.sAtm_IC = None				# default standard atm correction
		self.tempRange = (18, 26)		# default allowed temperature range
		self.pressRange = (715, 805)	# default allowed pressure range
		self.humidRange = (0, 100)		# default allowed humidity range
		##############################
		self.cts_in = cts_in			# DMI counts/inch in vacuum
		self.isConnected = True			# status variable for connected or not.
		self.part_temp_override = False	# forcing a part temperature or not.
	
		super(WeatherStation, self).__init__(params, printBuffer, debug)
		if self.debug:
			self.printBuffer.write("INFO: Initializing WeatherStation...")
		# setup the compensations
		self.temperature = self.temperatureConst + self.params.temp_comp
		self.pressure = self.pressureConst + self.params.press_comp
		self.humidity = self.humidityConst + self.params.humid_comp
		self.temperatureStation = self.params.temp_probe
		self.pressureStation = self.params.press_probe
		self.humidityStation = self.params.humid_probe
		self.partTemperatureStation = self.params.part_temp_probe
		
		if self.params.com_info.use_rs232:		# use RS232 conneciton
			self.initConnection()
			##### OBSOLETE HERE #####
	
	# updateWeather (throws exception)
	# @Purpose:
	#	This funciton updates the weather constants
	#	handles thrown exception in upper level
	def updateWeather(self):
		if not self.params.com_info.use_rs232:			# using ethernet
			### checked with rtdserver code verify that it was using only the latest values from socket / database ###
			### therefore we just probe the database for latest values...(update interval = 5 mins)

			# create a db connection
			try:
				db = EnvDB()
				db_temp = db.getLatestProbeValue(self.temperatureStation)
				db_press = db.getLatestProbeValue(self.pressureStation)
				db_humid = db.getLatestProbeValue(self.humidityStation)
				if db_temp >= self.tempRange[0] and db_temp <= self.tempRange[1] and (not self.params.temp_override):
					self.temperature = db.getLatestProbeValue(self.temperatureStation) + self.params.temp_comp
				elif (not self.params.temp_override):
					self.temperature = self.temperatureConst + self.params.temp_comp

				if db_press >= self.pressRange[0] and db_press <= self.pressRange[1] and (not self.params.press_override):
					self.pressure = db.getLatestProbeValue(self.pressureStation) + self.params.press_comp
				elif (not self.params.press_override):
					self.pressure = self.pressureConst + self.params.press_comp

				if db_humid >= self.humidRange[0] and db_humid <= self.humidRange[1] and (not self.params.humid_override):
					self.humidity = db.getLatestProbeValue(self.humidityStation) + self.params.humid_comp
				elif (not self.params.humid_override):
					self.humidity = self.humidityConst + self.params.humid_comp

				self.isConnected = True
			except Exception, e:
				self.isConnected = False
				self.temperature = self.temperatureConst + self.params.temp_comp
				self.pressure = self.pressureConst + self.params.press_comp
				self.humidity = self.humidityConst + self.params.humid_comp
				# remember to do atmosphereCorrect
				self.atmosphereCorrect()
				raise WeatherProbingException('db.EnvDB()', 'cannot connect to database.')
			
			# probe part temperature probe
			try:
				if not self.part_temp_override:
					self.partTemperature = db.getLatestProbeValue(self.partTemperatureStation)
			except Exception, e:
				raise WeatherProbingException("db.getLatestProbeValue(%s)" % self.partTemperatureStation,
											"cannot find probe name: %s" % self.partTemperatureStation)

			# remember to do atmosphereCorrect
			self.atmosphereCorrect()
	
	# atmosphereCorrect:
	# @Purpose:
	#	This function calculates the index of air (n) based on 
	#	Barometric Pressure (mm Hg), Temperature (deg C) and 
	#	Relative Humidity (Percentage).
	#	Then it gets DMI couts/in. in vacuum to set the 
	#	DMI's IC number for the current atmspheric conditions
	#
	#	Calculation refer to Zygo ZMI-1000 manual for calculation documentation
	def atmosphereCorrect(self):
		f_term1 = 4.07859739
		f_term2 = 0.44301857
		f_term3 = 0.00232093
		f_term4 = 0.00045785
		
		f = (self.humidity / 100.0) * \
			(f_term1 + \
			f_term2 * self.temperature + \
			f_term3 * (self.temperature)**2 + \
			f_term4 * (self.temperature)**3)
		n = 1 + self.pressure * (0.817 - (0.0133 * self.temperature)) * 0.000001
		n /= (1 + 0.003661 * self.temperature)
		n = n * (0.00000038369 * self.pressure) + 1
		n -= (0.00000005607943 * f)
		self.index_of_air = n
		
		self.sAtm_IC = self.index_of_air * self.cts_in

	# setTemperature
	# @Purpose:
	#	set the temperature (override the current value)
	# @Inputs:
	#	value = override temperature value
	def setTemperature(self, value):
		self.temperature = value

	# setPressure
	# @Purpose:
	#	set the pressure (override)
	# @Inputs:
	#	value = override pressure value
	def setPressure(self, value):
		self.pressure = value

	# setHumidity
	# @Purpose:
	#	set the humidity (override)
	# @Inputs:
	#	value = override humidity value
	def setHumidity(self, value):
		self.humidity = value
	
	# setTemperatureOverride:
	# @Purpose:
	#	set the temperature override flag to be True or False
	# @Inputs:
	#	value = True / False
	def setTemperatureOverride(self, value):
		self.params.temp_override = value
	
	# setPressureOverride:
	# @Purpose:
	#	set the pressure override flag to be True or False
	# @Inputs:
	#	value = True / False
	def setPressureOverride(self, value):
		self.params.press_override = value
	
	# setHumidityOverride:
	# @Purpose:
	#	set the humidity override flag to be True or False
	# @Inputs:
	#	value = True / False
	def setHumidityOverride(self, value):
		self.params.humid_override = value
		
	# setPartTemperatureStation
	# @Purpose:
	#	set the part temperature station name to be "station"
	# @Inputs:
	#	station = (String) name of the probe
	def setPartTemperatureStation(self, station):
		self.partTemperatureStation = station

	# setPartTemperatureOverride
	# @Purpose:
	#	set the part temperature to override state or not
	# @Inputs:
	#	value = True if overriding, False otherwise.
	def setPartTemperatureOverride(self, value):
		self.part_temp_override = value
	
		
