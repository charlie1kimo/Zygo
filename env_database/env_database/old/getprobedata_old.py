#! !/usr/bin/env python
# file: env_database/getprobedata.py

"""
This file get probe data/probe names from the database.
    getProbeData(probeName, startTime=None, endTime = None):
        getProbeData returns a list of probe data from the probe
        database.

    getProbeNames(startTime=None, endTime = None):
        getProbeNames returns a list of probe names from the probe
        database.

This file assumes there is an odbc connection to the probe database
accessable using 'server=rotr5ws1;dsn=omMeas'.
"""

# $Date: 2012-12-13 13:54:24 -0800 (Thu, 13 Dec 2012) $
# $Revision: 972 $
# $Id: getprobedata.py 972 2012-12-13 21:54:24Z dpierce $
# $Author: dpierce $
# History:
# 12/13/2012 bk changed server to rotr5ws1
__version__=298
__owner__='cchen'


whatString = "@(#)ASML getprobedata.py 2012-12-13"

import logging
import pyodbc
import time
import sys

dbTimestampFormat = "%Y-%m-%d %H:%M:%S"     #mySQL timestamp format
#dbTimestampFormat = "%d/%b/%Y %H:%M:%S"    #ms access timestamp format
DFLT_START_TIME = "1970-01-01 00:00:00"     # default start time

db_server='rotr5ws1'
db = None
sqlStmt = 'SELECT timestamp,value FROM SensorValues ' \
        'WHERE UCASE(sensorId) = "?" AND ' \
               ' timestamp >= "?" AND timestamp <= "?"'

#======================================================================#

def getTimeStr (timeTuple = None):
    if timeTuple == None:
        return time.strftime (dbTimestampFormat)
    else:
        return time.strftime (dbTimestampFormat, timeTuple)

#======================================================================#

def getProbeData(probeName, startTime=None, endTime = None):
    """
        get probe data returns a list of probe data from the probe
        database.

            probeName: string name of the probe in question
            startTime: string repersentation of the start time; optional
                        (defaults to no start time).
            endTime:   string repersentation of the end time; optional
                        (defaults to now).
            returns a list of tuples in the following format:
                        [(timestamp, value), ...]
                        timestamp is a datetime tuple, value is a
                        floating point number.
            startTime and endTime are strings in the format used by the
                        database and returned by getTimeStr().
                        (currently YYYY-MM-DD HH:MM:SS).
    """
##    print "inside getProbeData ('%s', '%s', '%s')" % (probeName,
##                                                startTime, endTime)
    global db
    if db == None:
        try:
            db = pyodbc.connect("server="+db_server+";dsn=omMeas")
##            print pyodbc.paramstyle
        except pyodbc.Error,err:
            print "Probe database get failed: %s" % str(err)
            logging.warning("Probe database get failed: %s" % str(err))
            return

    mycursor = None
    try:
        mycursor = db.cursor()
    except pyodbc.Error, err:
        print "Probe database get failed: %s" % str(err)
        logging.warning("Probe database get failed: %s" % str(err))
        try:
            db.close()
        except pyodbc.Error:
            pass
        db = None
        return

    if startTime==None:
        startTime = DFLT_START_TIME

    if endTime==None:
        endTime= getTimeStr (time.localtime())

    myList = []
    try:
            # this should work & it doesn't.
##        print "%s ('%s', '%s', '%s')" % (sqlStmt, probeName.upper(),
##                                                    startTime, endTime)
##        mycursor.execute (sqlStmt, (probeName.upper(), startTime,
##                                                            endTime))

            # This is not the recommended approach but if it works and
            #   is 'fast enough'...
        sqlStmt = """
SELECT timestamp,value FROM SensorValues 
    WHERE timestamp >= '%s' AND timestamp <= '%s' AND 
         (UCASE(sensorId) = '%s' OR 
           UCASE(sensorId) = (SELECT UCASE(Id) FROM sensoraliases 
                                 WHERE UCASE(Alias) = '%s'))""" % \
                       (startTime, endTime, probeName.upper(),
                        probeName.upper())
##        print sqlStmt
        mycursor.execute (sqlStmt)

        for row in mycursor:
            myList.append ((row[0], row[1]))
    except pyodbc.Error, err:
        print "Probe database get failed: %s" % str(err)
        logging.warning("Probe database get failed: %s" % str(err))
        try:
            db.close()
        except pyodbc.Error:
            pass
        db = None
        myList = None
    finally:
        try:
            mycursor.close()
        except pyodbc.Error:
            pass
    return myList

#=====================================================================#

def getProbeNames(startTime=None, endTime = None):
    """
        get probe names returns a list of probe names from the probe
        database.

            startTime: string repersentation of the start time; optional
                        (defaults to no start time).
            endTime:   string repersentation of the end time; optional
                        (defaults to now).
            returns a list of probe names producing data in the
                        requested time period.
            startTime and endTime are strings in the format used by the
                        database and returned by getTimeStr().
                        (currently YYYY-MM-DD HH:MM:SS).
    """
##    print "inside getProbeNames ('%s', '%s')" % (startTime, endTime)
    global db
    if db == None:
        try:
            db = pyodbc.connect("server="+db_server+";dsn=omMeas")
##            print pyodbc.paramstyle
        except pyodbc.Error,err:
            print "Probe database get failed: %s" % str(err)
            logging.warning("Probe database get failed: %s" % str(err))
            return

    mycursor = None
    try:
        mycursor = db.cursor()
    except pyodbc.Error, err:
        print "Probe database get failed: %s" % str(err)
        logging.warning("Probe database get failed: %s" % str(err))
        try:
            db.close()
        except pyodbc.Error:
            pass
        db = None
        return

    if startTime==None:
        startTime = DFLT_START_TIME

    if endTime==None:
        endTime= getTimeStr (time.localtime())

    myList = []
    try:
            # This is not the recommended approach but if it works and
            #   is 'fast enough'...
        sqlStmt = "SELECT DISTINCT SensorId FROM SensorValues " \
                "WHERE  timestamp >= '%s' AND timestamp <= '%s'" % \
                       (startTime, endTime)
#        print sqlStmt
        mycursor.execute (sqlStmt)

        for row in mycursor:
            myList.append (row[0])
    except pyodbc.Error, err:
        print "Probe database get failed: %s" % str(err)
        logging.warning("Probe database get failed: %s" % str(err))
        try:
            db.close()
        except pyodbc.Error:
            pass
        db = None
        myList = None
    finally:
        try:
            mycursor.close()
        except pyodbc.Error:
            pass
    return myList

#=====================================================================#

def closeProbeDatabase():
    global db
    try:
        db.close()
    except pyodbc.Error:
        pass
    db = None

#=====================================================================#

def RunApp(argv):
    if len(argv) < 2:
        print ("Usage: %s <probeName> [<startTime> [<endTime>]]" %
                        argv[0])
        return
    elif len(argv) < 3:
        myList = getProbeData(argv[1])
    elif len(argv) < 4:
        myList = getProbeData(argv[1], argv[2])
    elif len(argv) < 5:
        myList = getProbeData(argv[1], argv[2], argv[3])

##    myList = getProbeData ('tr1-2-5', '2008-11-12 9:20:0')
##    myList = getProbeNames('2008-10-08 9:0:0') 

    print "requested probe data:"
    for v in myList:
        print v
    closeProbeDatabase()
##    print ('good by!')

#=====================================================================#

if __name__=='__main__':
    RunApp (sys.argv)
