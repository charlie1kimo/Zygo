import env_database.envdb as envdb

"""
groups = {'MET-PO': [('TR5.3.0', 'temperature', 'MET5-PO-1'),
					('TR5.3.1', 'temperature', 'MET5-PO-2'),
					('TR5.3.2', 'temperature', 'MET5-PO-3'),
					('TR5.3.3', 'temperature', 'MET5-PO-4'),
					('TR5.3.4', 'temperature', 'MET5-PO-5'),
					('TR5.3.5', 'temperature', 'MET5-PO-6')],
		'MET-RM': [('TR5.3.6', 'temperature', 'MET5-RM-1'),
					('TR5.3.7', 'temperature', 'MET5-RM-2'),
					('TR5.3.8', 'temperature', 'MET5-RM-3'),
					('TR5.3.9', 'temperature', 'MET5-RM-4'),
					('TR5.3.10', 'temperature', 'MET5-RM-5'),
					('TR5.3.11', 'temperature', 'MET5-RM-6')]
		}
"""

groups = {'Keck Leitz M6': [('TR4.0.0', 'temperature', 'M6_rt_out'),
							('TR4.0.1', 'temperature', 'M6_rt_mid_low'),
							('TR4.0.2', 'temperature', 'M6_rt_mid_hgh'),
							('TR4.0.3', 'temperature', 'M6_rt_bk_low'),
							('TR4.0.4', 'temperature', 'M6_rt_bk_hgh'),
							('TR4.0.5', 'temperature', 'M6_mid_bk_low'),
							('TR4.0.6', 'temperature', 'M6_mid_bk_hgh'),
							('TR4.0.7', 'temperature', 'M6_lft_mid_mid'),
							('TR4.0.8', 'temperature', 'M6_lft_mid_hgh')]
		'Keck Zeiss M8': [('TR4.1.0', 'temperature', 'M8_lft_fr_air_in'),
						  ('TR4.1.1', 'temperature', 'M8_lft_bk_air_in'),
						  ('TR4.1.2', 'temperature', 'M8_rt_fr_air_in'),
						  ('TR4.1.3', 'temperature', 'M8_rt_bk_air_in'),
						  ('TR4.1.4', 'temperature', 'M8_lft_top'),
						  ('TR4.1.5', 'temperature', 'M8_table'),
						  ('TR4.1.6', 'temperature', 'M8_fr_top'),
						  ('TR4.1.7', 'temperature', 'M8_bk_6ft'),
						  ('TR4.1.8', 'temperature', 'M8_rt_6ft'),
						  ('TR4.1.9', 'temperature', 'M8_bk_top'),
						  ('TR4.1.10', 'temperature', 'M8_rt_top'),
						  ('TR4.1.11', 'temperature', 'M8_lft_6ft'),
						  ('TR4.3.0', 'temperature', 'M8_Air_In'),
						  ('TR4.3.1', 'temperature', 'M8_Air_Ret')]
		 }	
		
#db = envdb.EnvDB(database='omMeas_new')
db = envdb.EnvDB()
listProbesToAdd = []
listProbesAliasesToAdd = []
listProbesStationsToAdd = []
for k in groups.keys():
	isGroupExist = bool(db.runSQL("SELECT Id FROM Station s WHERE s.Name = '%s';" % k))
	if not isGroupExist:
		db.addStation(k, 0)

	stationId = db.runSQL("SELECT Id FROM Station s WHERE s.Name = '%s';" % k)
	stationId = stationId[0][0]
	
	for probe in groups[k]:
		isProbeExist = bool(db.runSQL("SELECT Id FROM SensorIds s WHERE s.Id = '%s';" % probe[0]))
		if not isProbeExist:
			if probe[1] == 'temperature':
				listProbesToAdd.append( (probe[0], probe[1], 'C', 20, 25) )
			elif probe[1] == 'pressure':
				listProbesToAdd.append( (probe[0], probe[1], 'mmHg', 0, 10000) )
			elif probe[1] == 'humidity':
				listProbesToAdd.append( (probe[0], probe[1], 'percent', 0, 100) )

		isAliasExist = bool(db.runSQL("SELECT Id FROM SensorAliases s WHERE s.Id = '%s' AND s.Alias = '%s';" % (probe[0], probe[2])))
		if not isAliasExist:
			listProbesAliasesToAdd.append( (probe[0], probe[2]) )

		isProbeInStation = bool(db.runSQL("SELECT StationId FROM StationSensors s WHERE s.StationId = '%s' AND s.sensorId = '%s';" % (stationId, probe[0])))
		if not isProbeInStation:
			listProbesStationsToAdd.append( (stationId, probe[0]) )
			
print listProbesToAdd
db.addProbes(listProbesToAdd)
print listProbesAliasesToAdd
db.addProbeAliases(listProbesAliasesToAdd)
print listProbesStationsToAdd
db.addSensorsInStations(listProbesStationsToAdd)


