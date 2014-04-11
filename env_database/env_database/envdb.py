"""
envdb.py
Author: Charlie Chen
"""

import getpass
import platform
import re
import traceback

# architecture specific Python-=ySQL connector
arch = platform.architecture()[1]
if re.search('Windows', arch):			# Windows
	import pyodbc
elif re.search('ELF', arch):			# Linux
	import MySQLdb

###################################################################
## class EnvDB
## @Purpose:
##		class to handle the MySQL database connections
## @Database Schema:
##		SensorAliases: 	Id [VARCHAR(255),(PK, FK SensorIds)], 
##						Alias [VARCHAR(255), (NOT NULL)]
##		SensorIds:		Id [VARCHAR(255), (PK)], 
##						SensorType [VARCHAR(255), (NOT NULL)],
##						Units [VARCHAR(255), (NOT NULL)], 
##						Minimum [float],
##						Maximum [float]
##		SensorValues:	SensorId [VARCHAR(255), (PK, FK SensorIds)], 
##						Timestamp [VARCHAR(255), (PK)]
##						value [float, (NOT NULL)]
##		Station:		Id [int, (PK)]
##						name [VARCHAR(255), (NOT NULL)]
##		StationSensors:	StationId [int, (PK, FK Station)]
##						SensorsId [VARCHAR(255), (PK, FK SensorIds)]
####################################################################
class EnvDB(object):
	def __init__(self, server='rotr5ws1', database='omMeas', timeout=120, user=None, debug=False):
		if re.search('ELF', arch):			# Linux
			self.executemany_symbol = "%s"
			if user == None:		# assume pre-setup connection in ODBC settings
				self.db = MySQLdb.connect(host=server, user='scott', passwd='tiger', db=database, connect_timeout=timeout)
			else:
				password = getpass.getpass()
				self.db = MySQLdb.connect(host=server, user=user, passwd=password, db=database, connect_timeout=timeout)
		else:								# assume Windows
			self.executemany_symbol = "?"
			try:
				if user == None:		# assume pre-setup connection in ODBC settings
					self.db = pyodbc.connect("server="+server+";dsn="+database+";timeout="+str(timeout))
				else:
					password = getpass.getpass()
					self.db = pyodbc.connect("server="+server+";dsn="+database+";timeout="+str(timeout)+";uid="+user+";pwd="+password)
			except pyodbc.Error, e:
				print traceback.print_exc()
				if e.args[0] == 'IM002':		# no driver error
					print \
					"""
==========================================================================================
ERROR: ODBC Driver NOT FOUND. Please Install MySQL ODBC Connector to your local Computer.
==========================================================================================
					"""
				raise e
			
		self.debug = debug
	
	def __del__(self):
		self.db.close()

	# addProbe:
	# @Purpose:
	#	add a probe into database, given the name (id), type, units, and optional min, max values
	# @Inputs:
	#	probeName = probe name (id)
	#	probeType = probe type (temperature, pressure, humidity...)
	#	probeUnits = probe units (degree C, mmHg, percentage)
	#	probeMin = probe minimum allowed value
	#	probeMax = probe maximum allowed value
	def addProbe(self, probeName, probeType, probeUnits, probeMin=None, probeMax=None):
		if probeMin == None:
			probeMin = "NULL"
		if probeMax == None:
			probeMax = "NULL"
		if self.debug:
			print "INFO: addProbe SQL: \"INSERT INTO SensorIds VALUES (%s, %s, %s, %s, %s);\" " % \
				(probeName, probeType, probeUnits, str(probeMin), str(probeMax))

		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorIds VALUES (%s, %s, %s, %s, %s);" % tuple([self.executemany_symbol for i in range(5)])
		cursor = cursor.execute(mysqlCMD,
							probeName, probeType, probeUnits, str(probeMin), str(probeMax))
		self.db.commit()
		
	# addProbes:
	# @Purpose:
	#	add a series of new probes into database
	# @Inputs:
	#	listNewProbes: a list of new probes, with format like the following:
	#		[(probeName1, probeType1, probeUnits1, probeMin1, probeMax1), 
	#		(probeName2, probeType2, probeUnits2, probeMin2, probeMax2), ...]
	def addProbes(self, listNewProbes):
		if self.debug:
			for i in listNewProbes:
				print "INFO: addProbes SQL: \"INSERT INTO SensorIds VALUES (%s, %s, %s, %s, %s);\" " % i
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorIds VALUES (%s, %s, %s, %s, %s);" % tuple([self.executemany_symbol for i in range(5)])
		cursor.executemany(mysqlCMD, listNewProbes)
		self.db.commit()
		
	# addProbeAlias:
	# @Purpose:
	#	associate with a probe with an alias
	# @Inputs:
	#	probeName = probe name (id) (need to have existing entry in TABLE SensorIds)
	#	probeAlias = probe alias
	def addProbeAlias(self, probeName, probeAlias):
		if self.debug:
			print "INFO: addProbeAlias SQL: \"INSERT INTO SensorAliases VALUES (%s, %s);\" " % (probeName, probeAlias)
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorAliases VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor = cursor.execute(mysqlCMD, probeName, probeAlias)
		self.db.commit()
		
	# addProbeAliases:
	# @Purpose:
	#	add a series of new aliases to associated probes
	# @Inputs:
	#	listNewAliases = list of new aliases to add; format:
	#		[(probeName1, probeAlias1), (probeName2, probeAlias2), ...]
	def addProbeAliases(self, listNewAliases):
		if self.debug:
			for i in listNewAliases:
				print "INFO: addProbeAliases SQL: \"INSERT INTO SensorAliases VALUES (%s, %s);\" " % i
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorAliases VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor.executemany(mysqlCMD, listNewAliases)
		self.db.commit()
		
	# addProbeValue:
	# @Purpose:
	#	add a probed value into the database
	# @Inputs:
	#	probeName = probe name (id) (need to be in SensorIds)
	#	probeAlias = probe alias (need to be in SensorAliases)
	#	timestamp = time for this value recorded
	#	value = the probed value
	def addProbeValue(self, probeName, probeAlias, timestamp, value):
		if self.debug:
			print "INFO: addProbeValue SQL: \"INSERT INTO SensorValues VALUES (%s, %s, %s, %s);\" " % (probeName, probeAlias, timestamp, value)
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorValues VALUES (%s, %s, %s, %s);" % tuple([self.executemany_symbol for i in range(4)])
		cursor = cursor.execute(mysqlCMD, probeName, probeAlias, timestamp, value)
		self.db.commit()

	# addProbeValues
	# @Purpose:
	#	add a series of new values associated with probe name (id) and probe aliases to the database
	# @Inputs:
	#	listNewValues = list of new values with following format:
	#		[(probeName1, probeAlias1, timestamp1, value1), (probeName2, probeAlias2, timestamp2, value2), ...]
	def addProbeValues(self, listNewValues):
		if self.debug:
			for i in listNewValues:
				print "INFO: addProbeValues SQL: \"INSERT INTO SensorValues VALUES (%s, %s, %s, %s);\" " % i
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO SensorValues VALUES (%s, %s, %s, %s);" % tuple([self.executemany_symbol for i in range(4)])
		cursor.executemany(mysqlCMD, listNewValues)
		self.db.commit()
		
	# addStation
	# @Purpose:
	#	add a station into the database
	# @Inputs:
	#	stationName = new station's name
	#	stationID = new id number (optional)
	def addStation(self, stationName, stationID=0):
		if self.debug:
			print "INFO: addStation SQL: \"INSERT INTO Station VALUES (%s, %s);\" " % (stationName, stationID)
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO Station VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor = cursor.execute(mysqlCMD, stationName, stationID)
		self.db.commit()
		
	# addStations
	# @Purpose:
	#	add list of stations into the database
	# @Inputs:
	#	listNewStations = [(newName1, 0), (newName2, 0), ...]
	def addStations(self, listNewStations):
		if self.debug:
			for i in listNewStations:
				print "INFO: addStations SQL: \"INSERT INTO Station VALUES (%s, %s);\" " % i
		
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO Station VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor.executemany(mysqlCMD, listNewStations)
		self.db.commit()
		
	# addSensorInStation
	# @Purpose:
	#	add a sensor to a specific station group
	# @Inputs:
	#	station = the specific station name
	#	sensorId = the given sensor
	def addSensorInStation(self, station, sensorId):
		sqlCMD = "SELECT Id FROM Station WHERE Name=\'%s\';" % station
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		stationId = cursor.fetchall()[0][0]

		if self.debug:
			print "INFO: addSensorInStation SQL: \"INSERT INTO StationSensors VALUES (%s, %s);\" " % (stationId, sensorId)
		
		mysqlCMD = "INSERT INTO StationSensors VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor = cursor.execute(mysqlCMD, stationId, sensorId)
		self.db.commit()

	# addSensorsInStations
	# @Purpose:
	#	add a sensor to specific station group (ID)
	#	MAIN PURPOSE for setup.add function
	# @Inputs:
	#	listSS = [(stationId1, sensorId1), (stationId2, sensorId2), ...]
	def addSensorsInStations(self, listSS):
		if self.debug:
			for i in listSS:
				print "INFO: addSensorsInStations SQL: \"INSERT INTO StationSensors VALUES (%s, %s);\"" % i
		cursor = self.db.cursor()
		mysqlCMD = "INSERT INTO Station VALUES (%s, %s);" % tuple([self.executemany_symbol for i in range(2)])
		cursor.executemany(mysqlCMD, listSS)
		self.db.commit()
		
	# deleteProbe:
	# @Purpose:
	#	delete a probe with given probe name
	#	*** WILL DELETE ALL ASSOCIATE DATA WITH 'probe', USE WITH CAUTION!!!***
	# @Inputs:
	#	probe = the probe name to be deleted
	def deleteProbe(self, probe):
		sqlCMD = "DELETE FROM SensorIds WHERE Id=\'%s\';" % probe
		if self.debug:
			print "INFO: deleteProbe SQL: %s" % sqlCMD
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		self.db.commit()

	# deleteProbeAlias:
	# @Purpose:
	#	delete a probe's alias
	# @Inputs:
	#	probe = given probe name
	#	alias = alias to delete
	def deleteProbeAlias(self, probe, alias):
		sqlCMD = "DELETE FROM SensorAliases WHERE Id=\'%s\' AND alias=\'%s\';" % (probe, alias)
		if self.debug:
			print "INFO: deleteProbe SQL: %s" % sqlCMD
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		self.db.commit()

	# deleteStation:
	# @Purpose:
	#	delete a station
	# @Inputs:
	#	station = station to delete
	def deleteStation(self, station):
		sqlCMD = "DELETE FROM Station WHERE Name=\'%s\';" % station
		if self.debug:
			print "INFO: deleteProbe SQL: %s" % sqlCMD
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		self.db.commit()

	# deleteProbeInStation:
	def deleteProbeInStation(self, probe, station):
		sqlCMD = "SELECT Id FROM Station WHERE Name=\'%s\';" % station
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		stationId = cursor.fetchall()[0][0]

		sqlCMD = "DELETE FROM StationSensors WHERE StationId=\'%s\' AND sensorId=\'%s\';" % (stationId, probe)
		if self.debug:
			print "INFO: deleteProbe SQL: %s" % sqlCMD
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		self.db.commit()
		
	# getProbeNames:
	# @Purpose:
	#	return all the probe names (id) given a probe type
	# @Inputs:
	#	probeTypes = list of probe types to return
	# @Outputs:
	#	return [name1, name2, name3, ...]
	def getProbeNames(self, probeTypes=[]):
		if len(probeTypes) == 0:
			sqlCMD = "SELECT Id FROM SensorIds;"
		else:
			sqlCMD = "SELECT Id FROM SensorIds WHERE "
			for i in xrange(len(probeTypes)):
				sqlCMD += "SensorType = \"" + probeTypes[i] + "\""
				if (i + 1) < len(probeTypes):
					sqlCMD += " OR "
				else:
					sqlCMD += ";"
		
		if self.debug:
			print "INFO: getProbeNames SQL: \"" + sqlCMD + "\""
	
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		retlist = cursor.fetchall()
		return [item for sublist in retlist for item in sublist]
		
	# getProbeAliases:
	# @Purpose:
	#	return the tuples of (probeName, alias) specified probe names
	# @Inputs:
	#	probeNames = list of probe names to filter
	# @Outputs:
	#	return [(probeName, probeAlias), ...]
	def getProbeAliases(self, probeNames=[]):
		if len(probeNames) == 0:
			sqlCMD = "SELECT * FROM SensorAliases;"
		else:
			sqlCMD = "SELECT * FROM SensorAliases WHERE "
			for i in xrange(len(probeNames)):
				sqlCMD += "Id = \"" + probeNames[i] + "\""
				if (i + 1) < len(probeNames):
					sqlCMD += " OR "
				else:
					sqlCMD += ";"
		
		if self.debug:
			print "INFO: getProbeAliases SQL: \"" + sqlCMD + "\""
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return list(cursor.fetchall())

	# getAliases:
	# @Purpose:
	#	return the tuples of (probeName, alias) specified probe alias
	# @Inputs:
	#	aliases = given aliases to search
	# @Outputs:
	#	return [(probeName, probeAlias), ...]
	def getAliases(self, aliases=[]):
		if len(aliases) == 0:
			sqlCMD = "SELECT * FROM SensorAliases;"
		else:
			sqlCMD = "SELECT * FROM SensorAliases WHERE "
			for i in xrange(len(aliases)):
				sqlCMD += "Alias = \"" + aliases[i] + "\""
				if (i + 1) < len(aliases):
					sqlCMD += " OR "
				else:
					sqlCMD += ";"
		
		if self.debug:
			print "INFO: getAliases SQL: \"" + sqlCMD + "\""
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return list(cursor.fetchall())
		
	# getProbeValues:
	# @Purpose:
	#	return the probes and their values with different time stamps
	# @Inputs:
	#	namesAliases = [(name, alias), ...], the list of names and aliases filter
	#					name and alias can be "*", denote that it's NOT filtering.
	#					e.g. (*, alias) only filter alias=alias
	#	timeAfter = keep entries after this timestamp
	#	timeBefore = keep entries before this timestamp
	# @Outputs:
	#	return [(probeName, timestamp, value, probeAlias), ...]
	def getProbeValues(self, namesAliases=[], timeAfter=None, timeBefore=None):
		if len(namesAliases) == 0 and timeAfter == None and timeBefore == None:
			print "WARNING: You are retrieving EVERY VALUES in database, possiblely leading to crash!!!"
			print "Press Enter if you are sure to continue; Ctrl+C to stop."
			raw_input()
			sqlCMD = "SELECT * FROM SensorValues;"
		else:
			sqlCMD = "SELECT * FROM SensorValues WHERE "
			if len(namesAliases) > 0:
				for i in xrange(len(namesAliases)):
					name = namesAliases[i][0]
					alias = namesAliases[i][1]
					
					if (name != "*" or alias != "*") and i > 0:
						sqlCMD += " OR "
					
					if name != "*" and alias != "*":
						sqlCMD += "(SensorId = \"%s\" AND Alias = \"%s\") " % (name, alias)
					elif name != "*":
						sqlCMD += "(SensorId = \"%s\") " % name
					elif alias != "*":
						sqlCMD += "(Alias = \"%s\") " % alias
			
			if timeAfter != None:
				if len(namesAliases) > 0:
					sqlCMD += " AND "
				sqlCMD += "Timestamp >= \"%s\" " % timeAfter
				
			if timeBefore != None:
				if len(namesAliases) > 0 or timeAfter != None:
					sqlCMD += " AND "
				sqlCMD += "Timestamp <= \"%s\" " % timeBefore
				
			sqlCMD += " ORDER BY Timestamp ASC;"
		
		if self.debug:
			print "INFO: getProbeValues SQL: \"" + sqlCMD + "\""
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return list(cursor.fetchall())
	
	# getStations:
	# @Purpose:
	#	return the list of station defined.
	# @Output:
	#	return [station1, station2, station3, ...]
	def getStations(self):
		sqlCMD = "SELECT Name FROM Station;"
		
		if self.debug:
			print "INFO: getStations SQL: \"" + sqlCMD + "\""
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		retlist = cursor.fetchall()
		return [item for sublist in retlist for item in sublist]
		
	# getProbesInStation:
	# @Purpose:
	#	return a list of probes given stations filtering
	# @Inputs:
	#	stations = list of stations to keep
	# @Outpus:
	#	return filtered [(station, probe), ...]
	def getProbesInStation(self, stations=[]):
		if len(stations) == 0:
			sqlCMD = "SELECT Station.Name, StationSensors.SensorId FROM Station, StationSensors WHERE Station.Id = StationSensors.StationId;"
		else:
			sqlCMD = "SELECT Station.Name, StationSensors.SensorId FROM Station, StationSensors WHERE "
			for i in xrange(len(stations)):
				sqlCMD += "Station.name = \"" + stations[i] + "\""
				if (i + 1) < len(stations):
					sqlCMD += " OR "
				else:
					sqlCMD += " AND Station.Id = StationSensors.StationId;"

		if self.debug:
			print "INFO: getProbesInStation SQL: \"" + sqlCMD + "\""
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return list(cursor.fetchall())
	
	# getProbeAssociatedStations:
	# @Purpose:
	#	return a list of stations given probes filtering
	# @Inputs:
	#	probes = list of probes to keep
	# @Outpus:
	#	return filtered [(station, probe), ...]
	def getProbeAssociatedStations(self, probes=[]):
		if len(probes) == 0:
			sqlCMD = "SELECT Station.Name, StationSensors.SensorId FROM Station, StationSensors WHERE Station.Id = StationSensors.StationId;"
		else:
			sqlCMD = "SELECT Station.Name, StationSensors.SensorId FROM Station, StationSensors WHERE "
			for i in xrange(len(probes)):
				sqlCMD += "StationSensors.SensorId = \"" + probes[i] + "\""
				if (i + 1) < len(probes):
					sqlCMD += " OR "
				else:
					sqlCMD += " AND Station.Id = StationSensors.StationId;"

		if self.debug:
			print "INFO: getProbeAssociatedStations SQL: \"" + sqlCMD + "\""
				
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return list(cursor.fetchall())
		
	# getProbeWithStationAndAlias:
	# @Purpose:
	#	return a probe with given station and alias
	#	(for progrom env_plot2 to use...)
	# @Outputs:
	#	query results
	def getProbeWithStationAndAlias(self, station, alias):
		sqlCMD = "SELECT StationSenSors.SensorId \
                  FROM SensorAliases, Station, StationSensors \
                  WHERE Station.name = \"%s\" AND SensorAliases.Alias = \"%s\" \
                  AND SensorAliases.Id = StationSensors.SensorId \
                  AND Station.Id = StationSensors.StationId;" % \
				(station, alias)
						
		if self.debug:
			print "INFO: getProbeWithStationAndAlias SQL: %s" % sqlCMD
		
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		retlist = cursor.fetchall()
		return [item for sublist in retlist for item in sublist]

	# getLatestProbeValue:
	# @Purpose:
	#	get the latest probe's value (primary used by radius3)
	# @Inputs:
	#	probe = probe name
	# @Outputs:
	#	a single floating value
	def getLatestProbeValue(self, probe):
		sqlCMD = "SELECT SensorValues.value FROM SensorValues WHERE SensorValues.SensorId=\'%s\' ORDER BY SensorValues.timestamp DESC LIMIT 1;" % probe

		if self.debug:
			print "INFO: getLatestProbeValue SQL: %s" % sqlCMD

		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		return cursor.fetchall()[0][0]

	# moveProbeIntoStation:
	# @Purpose:
	#	move a given probe from one station to another
	# Inputs:
	#	probe = given probe to move
	#	from = from what station (must exist)
	#	to = to what station (muest exist)
	def moveProbeIntoStation(self, probe, fromS, toS):
		# get the 'from' stationId
		sqlCMD = "SELECT Id FROM Station WHERE Name=\'%s\';" % fromS
		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		fromId = cursor.fetchall()[0][0]
		# get the 'to' stationId
		sqlCMD = "SELECT Id FROM Station WHERE Name=\'%s\';" % toS
		cursor.execute(sqlCMD)
		toId = cursor.fetchall()[0][0]

		sqlCMD = "UPDATE StationSensors SET StationId=\'%s\' WHERE sensorId=\'%s\' AND StationId=\'%s\';" % (str(toId), probe, str(fromId))

		if self.debug:
			print "INFO: moveProbeIntoStation: %s" % sqlCMD

		cursor.execute(sqlCMD)
		self.db.commit()
		
	# runSQL:
	# @Purpose:
	#	run the given SQL query on database...
	# @Inputs:
	#	cmd = SQL command
	# @Outputs:
	#	result of SQL commands...
	def runSQL(self, cmd):
		if self.debug:
			print "INFO: runSQL: %s" % cmd
		cursor = self.db.cursor()
		cursor.execute(cmd)
		return list(cursor.fetchall())
	
	# updateProbeAlias:
	# @Purpose:
	# 	update the probe's alias given probe name and new alias name
	# @Inputs:
	# 	probe = probe name to change alias with
	#	oldAlias = the old alias
	#	alias = new alias
	def updateProbeAlias(self, probe, oldAlias, alias):
		sqlCMD = "UPDATE SensorAliases SET Alias=\'%s\' WHERE Id=\'%s\' AND Alias=\'%s\';" % (alias, probe, oldAlias)

		if self.debug:
			print "INFO: updateProbeAlias SQL: %s" % sqlCMD

		cursor = self.db.cursor()
		cursor.execute(sqlCMD)
		self.db.commit()
