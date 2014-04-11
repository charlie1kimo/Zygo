"""
find_ni_chassis.py:
	test the nisyscfg C API functions
"""

from ctypes import *
import nisyscfg_wrapper as ni

dll = windll.LoadLibrary('nisyscfg.dll')

cfgHandle = c_void_p()
sHandle = c_void_p()
enumHardware = c_void_p()
hHardware = c_void_p()
hardwareName = create_string_buffer(255)
hostName = create_string_buffer(255)
serial_num = create_string_buffer(255)
ip_address = create_string_buffer(255)

"""
# example C codes (from http://forums.ni.com/t5/LabWindows-CVI/Device-list/td-p/2133268/highlight/true)

#include "nisyscfg.h"
#include <ansi_c.h>
static NISysCfgEnumExpertHandle cfgHandle;
static char hardwareName[255];
static NISysCfgResourceHandle hHardware;
static NISysCfgEnumResourceHandle enumHardware;
static NISysCfgSessionHandle sHandle;

void main (void)
{
	NISysCfgInitializeSession ("localhost", NULL, NULL, NISysCfgLocaleDefault, NISysCfgBoolTrue, 10000, &cfgHandle, &sHandle);
	NISysCfgFindHardware (sHandle, NISysCfgFilterModeMatchValuesAll, NULL, NULL, &enumHardware);
	NISysCfgNextResource (sHandle, enumHardware, &hHardware);
	NISysCfgGetResourceProperty (hHardware, NISysCfgResourcePropertyProductName, &hardwareName);
	printf ("name: %s", hardwareName);
	getchar();
}
"""

dll.NISysCfgInitializeSession("localhost", None, None, ni.NISysCfgLocale['Default'], ni.NISysCfgBool['True'], 10000, byref(cfgHandle), byref(sHandle))
dll.NISysCfgFindHardware(sHandle, ni.NISysCfgFilterMode['All'], None, None, byref(enumHardware))
dll.NISysCfgNextResource(sHandle, enumHardware, byref(hHardware))
dll.NISysCfgGetResourceProperty(hHardware, ni.NISysCfgResourceProperty['ProductName'], byref(hardwareName))
dll.NISysCfgGetResourceProperty(hHardware, ni.NISysCfgResourceProperty['TcpHostName'], byref(hostName))
dll.NISysCfgGetResourceProperty(hHardware, ni.NISysCfgResourceProperty['SerialNumber'], byref(serial_num))
dll.NISysCfgGetResourceProperty(hHardware, ni.NISysCfgResourceProperty['TcpIpAddress'], byref(ip_address))
dll.NISysCfgCloseHandle(hHardware)
dll.NISysCfgCloseHandle(enumHardware)
dll.NISysCfgCloseHandle(sHandle)
dll.NISysCfgCloseHandle(cfgHandle)

print "Found: %s: SN: %s; hostName: %s; ip: %s" % (hardwareName.value, serial_num.value, hostName.value, ip_address.value)