All codes are on N drive under N:\Shared\Users\cchen

Packages:
Every package has a __init__.py, and it has summary / documentation within the file.
__init__ usually contains:
__doc__: a summary strings of what this package does
__version__: version number string
__owner__: who maintains this package
__history__: the change log for this package
__bugs__: known bugs and issues (usually not existed)

1.	align_gui:
	The align_gui program we used for performing aligning / moving on the MET5 POB hexapod system.
	This package contains mostly wxPython GUI codes. I separated them by tabs, so different tabs’ codes are in different files.
	It also contains your “align” and “met5hexapod” module for backend computation.
	a.	hexapod_actuator:
		The low level modules for communicating to capgauge, picomotor controller, and wrapper actuator objects…etc
		It also contains the utility module such as “read_cap_data” so you can gather capgauge readings in a set time period and set time interval.
	b.	pob_measure_gui:
		The pob measurement automation package. It contains the wxPython GUI codes for pob measurement automation.
			i.	pob_measure:
			Low level module for performing actual pob measurements. It has module such as “autonul” (from Bill) to control the autonul functionalities.
	c.	check_wizard:
		This module is the check list GUI for POB operation procedures by Luc’s request. I thought it’s related to MET5/POB so I put it under here.

2.	aligning:
	This package contains the general aligning python modules requested by John and Steve. It has control ability to control a NewFocus 8081 stage platform.
	It has mostly low level (backend) modules.
	a.	gui:
		GUI package containing the wxPython GUI code for general aligning program.

3.	cap_change_tool:
	This package is the small test GUI for change a single MET5 POB hexapod motor leg given an amount, iteration, and tolerance. The functionality is replaced by the “Hexapod Positions” tab in align_gui

4.	cap_gauge:
	capgauge, picomotor, actuator backup modules save place.

5.	cap_gauge_coordinate_display:
	GUI display reading capgauge position for Mark. This was helpful for Mark to perform manual alignment and read the capgauge position from the hexapod.

6.	env_database:
	a.	env_database:
		environment database module. envdb is the python wrapper API for fast and convenient access of the MySQL database backend. Basically let you access database without writing SQL queries.
		i.	env_plots2:
			environmental plots 2 module. Displaying the temperature, pressure, and humidity for given groups and probes.
		ii.	monitoring:
			environmental database monitoring daemon program. It can setup probes to monitor and send out notification email is probes is out of range or envdb is down.
	b.	omMeas_env_database_server:
		This is the RtdServer which gathers the NIBox probes reading and saves them to database. Gary wrote most of the codes.
		i.	rtdServer:
			The rtdServer modules that setups the configurations of probes, handles database accessing, periodically checking probes reading etc.
		ii.	wexLib:
			most useful module is asyncSched. (i.e just read this module if need to modify anything). asyncSched creates asynchronized sockets act as Network server that accept connections from NIBox or other temperature reading devices.
	c.	scripts:
		handy scripts / shortcuts for launching env_plots2.

7.	latex:
	PDF report generator for GNT object. It’s deprecated I think.

8.	metro_pro_client:
	The python wrapper to talk to MetroPro. I put them in the omase system. However, if you want to install it, you need to copy all DLLs to C:/Windows/SystemWOW64 or C:/Windows/System32 (depending on 32 bits or 64 bits OS).

9.	miscellaneous:
	Miscellaneous functions I implemented for omsys and ompy.

10.	MySQL:
	a.	Installer: contains MySQL installer
	b.	Mysql_connector: Installer for MySQL ODBC client driver. Follow the README.txt to install on any client computers.

11.	radius3:
	rewrote radius measure program in Python. Read the modules’ comments for different sub-modules.
	a.	gui:
		Contains all wxPython GUI codes.
	b.	serial:
		python module for serial connection. 3rd party module.
	c.	metro_pro:
		Deprecated. Should just use omase’s metro_pro_client module.

12.	sc_testalignpy:
	Some wxPython GUI for performing aligning in MET5 M2?

13.	usb_temp:
	Project with Jim Kennon. usb temperature reading device python wrapper. See test.py for example usage. This module is intended for Linux environment, so it might not work under windows.

14.	wave_meter_wrapper:
	A ctypes Python wrapper for controlling Bristol wavelength meter. 

15.	wx_extensions:
	My core wxPython API package. This is really intended to use in ALL wxPython GUI developed. I used this API for almost all wxPython GUI I developed. I considered it important enough so I put it in omase system. It contains all handy and utilities class / methods that help developing wxPython GUI faster. For example, __startThread__() starts another thread for calculation, so it won’t “freeze” the GUI. refreshWidget() re-layout the GUI after any components updates so the display won’t look awkward. Read up on the package summary for more information. I strongly recommend the future programmer using this API for developing wxPython GUI (it would save him a lot of troubles I’ve been through), and a programmer should maintain this API as well.
