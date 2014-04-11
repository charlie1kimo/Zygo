README.txt

This document explains the requirements, installation procedures, and usage for usb_temperature python moudule.

1.  Requirements:
	- Python 2.7 (Haven’t tested on omase’s python 2.5 as some package might not be supported)
	- PyUsb 1.0 (installed this through easy_install utility) http://sourceforge.net/apps/trac/pyusb/
	- libusb-win32 http://sourceforge.net/projects/libusb-win32/
	- usb_temperature module (My module)

2. Installation:
	- libusb-win32:
		- Download ths zip. Extract it.
	 	- Attached the USB_TEMP device
		- Navigate to ./bin/inf-wizard.exe
		- Select the USB TEMP device (should automatically found by Windows)
		- Install the driver.
	- PyUSB 1.0:
		- Download the package. Extract it.
		- Navigate to the extract folder.
		- $> python setup.py install

3. Usage:
	- See N:\Shared\Users\cchen\usb_temp\python\test.py for example usage.
