import env_database.envdb as envdb
from pprint import pprint

def add(groups, debug=False):
    """
    add:
    @Purpose:
        add / setup probes name, types, groups and aliases.
    @Inputs:
        groups = 
        example groups, aliases, and probes setup:
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
        debug = True to turn on debug (no execution)
                False = default, to execute query.
    """
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
                
    if debug:
        print 'Probes to add:'
        pprint(listProbesToAdd)
        print '\n'
        print 'Probe Aliases to add:'
        pprint(listProbesAliasesToAdd)
        print '\n'
        print 'Probes Groups to add:'
        pprint(listProbesStationsToAdd)
        print '\n'
    else:
        if len(listProbesToAdd) > 0:
            db.addProbes(listProbesToAdd)
        if len(listProbesAliasesToAdd) > 0:
            db.addProbeAliases(listProbesAliasesToAdd)
        if len(listProbesStationsToAdd) > 0:
            db.addSensorsInStations(listProbesStationsToAdd)
