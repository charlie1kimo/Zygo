__doc__ = \
"""
package env_database:
	This env_database package contains the utility modules and sub-packages regarding to 
	the environment env_database.

	modules:
		1. envdb:
			- contains the EnvDB class for connectung to a MySQL database.
		2. setup:
			- contains convenient functions for settng up probes.
	sub-packages:
		1. env_plots2:
			- the environment plot program that monitors temperature, pressure, and humidity
			  for different probes.
		2. monitoring:
			- the monitoring daemon program for monitoring environmental database's health and probes temperature
			  out of control email notification.
"""
__version__ = '1.3.0'
__owner__ = 'cchen'
__history__ = \
'''
History:
4/7/2014	1.3.0	cchen	add sub-packages monitoring for monitoring env_database's and probes' health.
5/15/2013	1.2.0	cchen	add Linux support for EnvDB
5/3/2013	1.1.1	cchen	re-add function addSensorsInStations in envdb for setup moudles to use.
5/3/2013	1.1.0	cchen	add setup_probes modules.
4/5/2013	1.0.0	cchen	first created version number and documentation
'''