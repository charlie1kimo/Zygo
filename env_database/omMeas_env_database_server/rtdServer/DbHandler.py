#! !/usr/bin/env python
# file: omMeas/rtdServer/DbHandler.py

"""
This file handles output to the database.
"""

# author: glc

import logging
import pyodbc
import time

db = None

#======================================================================#

def getTimeStr (timeTuple = None):
    dbTimestampFormat = "%Y/%m/%d %H:%M:%S"     #mySQL timestamp format
    #dbTimestampFormat = "%d/%b/%Y %H:%M:%S"    #ms access timestamp format
    if timeTuple == None:
        return time.strftime (dbTimestampFormat)
    else:
        return time.strftime (dbTimestampFormat, timeTuple)

#======================================================================#

def insertValues(listOfParams):
##    print ("DbHandler.insertValues (%s)" % str (listOfParams))
##    return

    global db
    if db == None:
        try:
            db = pyodbc.connect("DSN=OmMeas")
        except pyodbc.Error,err:
            print "NIBOX database save failed: %s" % str(err)
            logging.warning("NIBOX database save failed: %s" %
                                                    str(err))
            return

    mycursor = None
    try:
        mycursor = db.cursor()
    except pyodbc.Error, err:
        print "NIBOX database save failed: %s" % str(err)
        logging.warning("NIBOX database save failed: %s" % str(err))
        try:
            db.close()
        except pyodbc.Error:
            pass
        db = None
        return
    
    errorFlag = False
    for entry in listOfParams:          # split the executemany SQL statement because we need to check value == 0
        try:
            probeName = entry[0]
            probeNameIsNotInDB = len(mycursor.execute("SELECT s.Id FROM SensorIds s WHERE s.Id = '%s';" % probeName).fetchall()) == 0
            if probeNameIsNotInDB:
                probeType = probeName[0].lower()
                if probeType == 't':
                    mycursor.execute("INSERT INTO SensorIds VALUES (%s, %s, %s, 20, 25);" % (probeName, 'temperature', 'C'))
                    db.commit()
                    mycursor.execute("INSERT INTO Sensoraliases VALUES (%s, %s);" % (probeName, probeName))
                    db.commit()
                    ungroupedID = mycursor.execute("SELECT s.Id FROM Station s WHERE s.Name = 'Temperature ungrouped';").fetchall()[0][0]
                    mycursor.execute("INSERT INTO StationSensors VALUES (%s, %s);" % (str(ungroupedID), probeName))
                    db.commit()
                elif probeType == 'p':
                    mycursor.execute("INSERT INTO SensorIds VALUES (%s, %s, %s, 100, 10000);" % (probeName, 'pressure', 'mmHg'))
                    db.commit()
                    mycursor.execute("INSERT INTO Sensoraliases VALUES (%s, %s);" % (probeName, probeName))
                    db.commit()
                    ungroupedID = mycursor.execute("SELECT s.Id FROM Station s WHERE s.Name = 'Pressure ungrouped';").fetchall()[0][0]
                    mycursor.execute("INSERT INTO StationSensors VALUES (%s, %s);" % (str(ungroupedID), probeName))
                    db.commit()
                elif probeType == 'h':
                    mycursor.execute("INSERT INTO SensorIds VALUES (%s, %s, %s, 0, 100);" % (probeName, 'humidity', 'percent'))
                    db.commit()
                    mycursor.execute("INSERT INTO Sensoraliases VALUES (%s, %s);" % (probeName, probeName))
                    db.commit()
                    ungroupedID = mycursor.execute("SELECT s.Id FROM Station s WHERE s.Name = 'Humidity ungrouped';").fetchall()[0][0]
                    mycursor.execute("INSERT INTO StationSensors VALUES (%s, %s);" % (str(ungroupedID), probeName))
                    db.commit()
                else:
                    print "WARNING: Unknown type of probe: %s, skipping insert to database." % probeName
                    logging.warning("WARNING: Unknown type of probe: %s, skipping insert to database." % probeName)
                    continue
            # Inserting data VALUES into db
            if entry[2] > 0:            # sanity check for NOT inserting 0 values!
                sqlStmt = "INSERT INTO SensorValues VALUES (?,?,?)"
                mycursor.execute(sqlStmt, entry)
                db.commit()

                # sanity check to throw an warning in logs
                value = entry[2]
                mycursor.execute("SELECT minimum FROM SensorIds WHERE Id = '%s';" % probeName)
                minimum = float(mycursor.fetchall()[0][0])
                mycursor.execute("SELECT maximum FROM SensorIds WHERE Id = '%s';" % probeName)
                maximum = float(mycursor.fetchall()[0][0])
                if float(value) < minimum or float(value) > maximum:
                    print "WARNING: Probe %s has a possible INVALID value: %s" % (probeName, value)
                    logging.warning("Probe %s has a possible INVALID value: %s" % (probeName, value))


        except pyodbc.Error, err:
            print "NIBOX database save on '%s' failed: %s" % (entry[0], str(err))
            logging.warning("NIBOX database save on '%s' failed: %s" % (entry[0], str(err)))
            errorFlag = True
    if errorFlag:
        try:
            db.close()
        except pyodbc.Error:
            pass
            db = None
    try:
        mycursor.close()
    except pyodbc.Error:
        pass
