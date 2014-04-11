#! !/usr/bin/env python
# file: omMeas/wexLib/Device.py

"""
This file implements the Generic device RS232/TCP routines.

Differences between Devices and Probes.
A Device is a physical object (i.e. "something you can kick"); a Probe
is something that returns a measurment.  Some devices, like the Newport
iBTHX support multiple Probes since they can measure different values.
Probes usually have an associated device (but not always--the Default
Device doesn't have an associated device).
"""

# author: glc

#=====================================================================#

import socket
import errno
import threading
# serial module isn't standard Python so only import it if it is used
#import serial

TRACE = __name__ == "__main__"
#TRACE = True

#=====================================================================#

def trace(s):
    if TRACE:
        print s

#=====================================================================#

class DeviceError(EnvironmentError):
    """
    This exception class is used when any of the device classes need to
    throw an exception.
    """
    def __init__(self, why):
        trace ("DeviceError.__ini__(%s)" % why)
        if not why:
            why = "Device error"
        EnvironmentError.__init__(self, 0, why)

#=====================================================================#

class Device:
    """
    The device class is an abstract class that all devices that need
    RS232 and/or TCP connections. Other connections (UDP? USP?, SSL?)
    can be added later.
    """

#---------------------------------------------------------------------#
    
    def setRS232Defaults(self, comNum = None, baud = None,
                                    databits = None, parity = None,
                                    stopbits = None, timeout = None):
        """Sets/changes the RS232 defaults"""
        trace ("Device.setRS232Defaults()")
        if self.interfaceType == "RS232":
            if comNum != None and self.comNum == None:
                self.comNum = comNum
            if baud != None and self.baud == None:
                self.baud = baud
            if databits != None and self.databits == None:
                self.databits = databits
            if parity != None and self.parity == None:
                self.parity = parity
            if stopbits != None and self.stopbits == None:
                self.stopbits = stopbits
                #generic defaults
            if timeout != None and self.timeout == 1:
                self.timeout = timeout

#---------------------------------------------------------------------#
    
    def setTcpDefaults(self, host = None, port = None, timeout = None):
        """Sets/changes the TCP defaults"""
        trace ("Device.setTcpDefaults()")
        if self.interfaceType == "TCP":
            if host != None and self.host == None:
                self.host = host
            if port != None and self.port == None:
                self.port = port
                #generic defaults
            if timeout != None and self.timeout == 1:
                self.timeout = timeout

#---------------------------------------------------------------------#

    def __init__(self, address):
        trace ("Device.__init__(%s)" % address)
        self.deviceIsOpen = False
        self.interfaceType = None
        self.timeout = 1
        tokens = address.split()
        if tokens[0].upper() == "RS232":
            self.interfaceType = "RS232"
            self.comNum = self.baud = self.databits = None
            self.parity = self.stopbits = None
            if len(tokens) > 1:
                self.comNum = int (tokens [1])
            if len(tokens) > 2:
                self.baud = int (tokens [2])
            if len(tokens) > 3:
                self.databits = int (tokens [3][0])
                self.parity = tokens[3][1]
                self.stopbits = int (tokens [3][2])
        elif tokens[0].upper() == "TCP":
            self.interfaceType = "TCP"
            addressPort = tokens[1].split(":")
            self.host = addressPort[0]
            self.port = int(addressPort[1])
        else:
            raise DeviceError("unknown address (%s) in "
                        "Device.__init__(): %s" % (tokens[0], address))
        self.myMutex = threading.Condition()

#---------------------------------------------------------------------#

    def openDevice(self):
        trace ("Device.openDevice()")
        if self.interfaceType == "RS232":
            import serial
            trace ("calling serial.Serial(%i)" %(self.comNum -1))
            try:
                self.serial = serial.Serial (self.comNum -1,
                                                timeout=self.timeout)
            except serial.SerialException, x:
                raise DeviceError("Unable to connect to device: %s " %
                                                        str(x.message))
            if self.baud != None:
                trace ("  setting baud rate: %s" % str(self.baud))
                self.serial.setBaudrate (self.baud)
            if self.databits != None:
                trace ("  setting data bits: %s" % str(self.databits))
                self.serial.setByteSize (self.databits)
            if self.parity != None:
                trace ("  setting parity: %s" % str(self.parity))
                self.serial.setParity (self.parity.upper())
            if self.stopbits != None:
                trace ("  setting stop bits: %s" % str(self.stopbits))
                self.serial.setStopbits (self.stopbits)
            self.deviceIsOpen = True
        elif self.interfaceType == "TCP":
            try:
                self.socket = socket.socket (socket.AF_INET,
                                                socket.SOCK_STREAM)
                trace ("calling mySocket.connect (%s, %d)" %
                                                (self.host,self.port))
                self.socket.connect ((self.host, self.port))
                self.socket.settimeout (self.timeout)
            except socket.error, x:
                raise DeviceError("Unable to connect to device: %s " %
                                                        str(x.message))
            self.deviceIsOpen = True
        else:
            raise DeviceError("unknown interface (%s) in "
                    "Device.openDevice()" % str (self.interfaceType))
        trace ("leaving openDevice()")

#---------------------------------------------------------------------#

    def close(self):
        """
        close() --> None
        This routine closes the connection to a device.
        """
        trace ("Device.close()")
        if not self.isOpen():
            return
        self.deviceIsOpen = False
        if self.interfaceType == "RS232":
            import serial
            try:
                self.serial.close()
            except:
                pass
            self.serial = None
        elif self.interfaceType == "TCP":
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        else:
            raise ("unknown interface (%s) in Device.close()" %
                                            str (self.interfaceType))

#---------------------------------------------------------------------#

    def isOpen(self):
        """
        isOpen() --> Boolean
        This routine returns true if the connection to the device is
        open.
        """
        trace ("Device.isOpen(): %s" % str(self.deviceIsOpen))
        return self.deviceIsOpen

#---------------------------------------------------------------------#

    def writeString (self, s):
        trace ("Device.writeStr(%s)" % s)
        if not self.isOpen():
            raise DeviceError("Device %s not open" % str(self.name))
        if self.interfaceType == "RS232":
            import serial
            self.serial.write (s)
        elif self.interfaceType == "TCP":
            self.socket.sendall(s)
        else:
            raise DeviceError("unknown interface (%s) in "
                "Device.writeString(%s)" % (str(self.interfaceType),s))

#---------------------------------------------------------------------#

    def readString(self):
        trace ("Device.readResponse()")
        if not self.isOpen():
            raise DeviceError("Device %s not open" % str(self.name))
        if self.interfaceType == "RS232":
            import serial
            s = self.serial.readline ()
            if s is None or len(s) == 0:
                print "self.serial.readline() returns nothing"
                raise DeviceError("Connection timeout")
            trace (s)
            return s
        elif self.interfaceType == "TCP":
            try:
                return self.socket.recv(1024).strip()
            except socket.timeout:
                print ("Device.sendCmdAndRecvResponse() throws "
                                                    "socket.timeout")
                raise DeviceError("Connection timeout")
        else:
            raise DeviceError("unknown interface (%s) in "
                    "Device.readString()" % str (self.interfaceType))

#---------------------------------------------------------------------#

    def sendCmdAndRecvResponse (self, s, getResponse = True):
        trace ("Device.sendCmdAndRecvResponse(%s, %s)" %
                                            (s, str (getResponse)))
        try:
            self.writeString (s)
            if getResponse:
                return self.readString()
            else:
                return
        except socket.timeout:
            print "Device.sendCmdAndRecvResponse() throws socket.timeout"
        except socket.error, x:
            trace ("have socket.error: %s" % str (x))
            err,errstr = x.args
                # catch "Software caused connection abort"
                #       (WSAECONNABORTED/ECONNABORTED) and
                # "Connection reset by peer"
                #       (WSAECONNRESET/ECONNRESET) and
                # "Bad file descriptor" (WSAEBADF/EBADF) and
                # maybe "Cannot send after Socket shutdown"
                #       (WSAESHUTDOWN/ESHUTDOWN) and
                # maybe "Network dropped connection on reset"
                #       (WSAENETRESET/ENETRESET) and
                # maybe "Network is down" (WSAENETDOWN/ENETDOWN)

            if (err in [errno.WSAECONNABORTED, errno.ECONNABORTED,
                          errno.WSAECONNRESET, errno.ECONNRESET,
                          errno.WSAEBADF, errno.EBADF,
                          errno.WSAESHUTDOWN, errno.ESHUTDOWN,
                          errno.WSAENETRESET, errno.ENETRESET,
                          errno.WSAENETDOWN, errno.ENETDOWN]):
                try:
                    self.close()
                    self.openDevice()
                    self.writeString (s)
                    if getResponse:
                        return self.readString()
                    else:
                        return
                except socket.error:
                    pass
            print "sendCmdAndRecvResponse() throws socket.error: %s"%str(x)
            raise DeviceError ("Cannot connect to " +(self.name))

#---------------------------------------------------------------------#

    def lockDevice(self):
        """
        lockDevice() --> None
        This routine will lock a mutex since several stations can share
        a device.
        """
        self.myMutex.acquire()

#---------------------------------------------------------------------#

    def unlockDevice(self):
        """
        unlockDevice() --> None
        This routine will unlock a mutex since several stations can
        share a device.
        """
        self.myMutex.release()

#=====================================================================#
