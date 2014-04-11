#!/usr/bin/env python

import sys
import time
import usb_temperature

vendor = 0x09db
product = 0x008d

a = usb_temperature.USB_TEMP(vendor, product)

print 'test blinking LED...'
a.blinkLED()
print 'Done.'
time.sleep(3)

print 'getting the status...'
print "Status: %s " % a.getStatus()
print 'Done.'
time.sleep(3)

print "getting the serial number..."
print "Serial Number: %s " % a.getSerialNumber()
print "Done."
time.sleep(3)

print 'testing calibration...'
a.calibrate()
print 'Done.'
#time.sleep(3)

print "testing RTD temperature measurement 10 times, channel 0, FOUR_WIRE..."
for i in range(10):
	print a.measureRTD(0, 'FOUR_WIRE')
	time.sleep(2)
print "Done."
time.sleep(2)

"""
print "testing measuring thermocopule channel 0, TYPE_J temperature..."
print a.measureThermocoupleTemperature(0, 'TYPE_J')
print "Done."
time.sleep(2)

print "10 values measurement of channel 1, TYPE_J thermocopule temperature:"
for i in range(10):
	print a.measureThermocoupleTemperature(1, 'TYPE_J')
	#time.sleep(2)
"""
print "reset the device."
a.reset()
