"""
monitor.py:
	This module monitor the health of env_database.
"""

import ConfigParser
import datetime
import os
import time
import traceback
from env_database.envdb import EnvDB
from notify import Notify

class MonitorDaemon(object):
	"""
	MonitorDaemon:
		this class create a MonitorDaemon object to monitor the health of env_database
	"""
	def __init__(self, monitorCfg, notifyList, monitorInterVal=15):
		"""
		@Purpose:
			Constructor
		@Inputs:
			(str) monitorCfg = probes configuration files to parse the monitoring probes attributes
			(list) notifyList = list of ppl's email to notify.
			(int) monitorInterVal = monitoring time interval in minutes
		"""
		############################################## CONSTANTS #############################################
		self.__PROBE_THRESHOLD__ = 0.5
		self.__DATABASE_DOWN_SUBJECT__ = "MonitorDaemon: Environment Database is DOWN!"
		self.__DATABASE_DOWN_MSG__ = \
"""
Automatic generated message from %s:
Environment Database is DOWN! Contact environment system administrator!

-------------
MonitorDaemon
-------------
"""
		self.__PROBE_OUT_OF_RANGE_SUBJECT__ = "MonitorDaemon: %s value is OUT OF EXPECTED RANGE!"
		self.__PROBE_OUT_OF_RANGE_MSG__ = \
"""
Automatic generated message from %s:
%s value is OUT OF EXPECTED RANGE: %0.2f!
Please check if the probe is behaving.

-------------
MonitorDaemon
-------------
"""
		self.__PROBE_COME_BACK_WITH_IN_RANGE_SUBJECT__ = "MonitorDaemon: %s value COMES BACK EXPECTED RANGE"
		self.__PROBE_COME_BACK_WITH_IN_RANGE_MSG__ = \
"""
Automatic generated message from %s:
%s value is NOW in EXPECTED RANGE: %0.2f.

-------------
MonitorDaemon
-------------
"""
		############################################## CONSTANTS #############################################
		self.__parseProbeConfig__(monitorCfg)
		self.notifyList = notifyList
		self.monitorInterVal = monitorInterVal
		self.isEnvDBAlive = True
		self.sentDownMsg = False
		self.monitorValidMap = {}
		for probe in self.monitorList:
			self.monitorValidMap[probe] = True

	def __parseProbeConfig__(self, monitorCfg):
		"""
		@Purpose:
			private function for parsing the probes configuration file.
		@Inputs:
			(str) monitorCfg = probe configuration file name
		"""
		config = ConfigParser.RawConfigParser()
		config.read(monitorCfg)
		self.monitorList = config.sections()
		self.__PROBE_RANGE__ = {}
		for probe in self.monitorList:
			min_range = config.getfloat(probe, 'min')
			max_range = config.getfloat(probe, 'max')
			self.__PROBE_RANGE__[probe] = (min_range, max_range)

	def __getTimeString__(self):
		return "MonitorDaemon @ "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	def monitor(self):
		"""
		@Purpose:
			Main monitoring routine.
		"""
		while True:
			##### Checking envdb availability #####
			try:
				envdb = EnvDB()
				self.isEnvDBAlive = True
			except Exception, e:
				if self.isEnvDBAlive:
					self.isEnvDBAlive = False
				else:
					if not self.sentDownMsg:
						################ EMAIL DOWN MSG ###############
						print self.__DATABASE_DOWN_SUBJECT__
						print self.__DATABASE_DOWN_MSG__ % self.__getTimeString__()
						notifyObj = Notify(notifyList, subject=self.__DATABASE_DOWN_SUBJECT__)
						notifyObj.send(self.__DATABASE_DOWN_MSG__ % self.__getTimeString__())
						###############################################
						self.sentDownMsg = True
			######
			try:
				for probe in self.monitorList:
					latestValue = envdb.getLatestProbeValue(probe)
					probeRange = self.__PROBE_RANGE__[probe]
					if self.monitorValidMap[probe] and (latestValue > probeRange[1] or latestValue < probeRange[0]):
						self.monitorValidMap[probe] = False
						############### EMAIL PROBE OUT OF RANGE MSG ############
						print self.__PROBE_OUT_OF_RANGE_SUBJECT__ % probe
						print self.__PROBE_OUT_OF_RANGE_MSG__ % (self.__getTimeString__(), probe, latestValue)
						notifyObj = Notify(notifyList, subject=self.__PROBE_OUT_OF_RANGE_SUBJECT__ % probe)
						notifyObj.send(self.__PROBE_OUT_OF_RANGE_MSG__ % (self.__getTimeString__(), probe, latestValue))
						#########################################################
					elif (not self.monitorValidMap[probe]) and \
						(latestValue >= probeRange[0]-self.__PROBE_THRESHOLD__ and latestValue <= probeRange[1]-self.__PROBE_THRESHOLD__):
						self.monitorValidMap[probe] = True
						############### EMAIL PROBE WITHIN RANGE MSG ############
						print self.__PROBE_COME_BACK_WITH_IN_RANGE_SUBJECT__ % probe
						print self.__PROBE_COME_BACK_WITH_IN_RANGE_MSG__ % (self.__getTimeString__(), probe, latestValue)
						notifyObj = Notify(notifyList, subject=self.__PROBE_COME_BACK_WITH_IN_RANGE_SUBJECT__ % probe)
						notifyObj.send(self.__PROBE_COME_BACK_WITH_IN_RANGE_MSG__ % (self.__getTimeString__(), probe, latestValue))
						#########################################################
			except Exception, e:
				print traceback.print_exc()


			###### DEBUG #####
			#print self.__getTimeString__()
			###### check time interval ######			
			time.sleep(self.monitorInterVal * 60)



##################### MAIN #######################
if __name__ == "__main__":
	cwd = os.path.dirname(os.path.abspath(__file__)) + "/"
	probeCheckListCfg = "probes.cfg"
	emailingListFile = "email_list.txt"
	emailingList = []
	fE = open(cwd+emailingListFile, "r")
	for email in fE:
		email = email.strip()
		if len(email) > 0:
			emailingList.append(email)
	fE.close()
	m = MonitorDaemon(probeCheckListCfg, emailingList)
	m.monitor()
##################################################

