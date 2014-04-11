#! !/usr/bin/env python
# file: omMeas/wexLib/nio.py

"""
this file contains the classes needed by the WS for use with newtwork
IO
"""

# author: glc

#======================================================================#

import socket
import errno

class SocketClosed(socket.error):
    """
    SocketClosed is an exception class that is generated when I/O fails
    because the socket is closed.
    """
    def __init__(self):
        socket.error.__init__(self, 0, "Socket closed")

#======================================================================#

def shutdownSocket(aSocket):
    """
    shutdownSocket rudely closes a socket
    """
    try:
        aSocket.shutdown (socket.SHUT_RDWR)
        aSocket.close()
    except socket.error, x:
        err,errstr = x.args
            # is it already closed?
            # catch "Bad file descriptor"
            #       (WSAEBADF/EBADF)
        if (err not in [errno.WSAEBADF, errno.EBADF]):
            raise

#======================================================================#

def sendPacket(aSocket, packet):
    """
    sendPacket sends a packet over a socket.  It can throw the exception
    SocketClosed
    """
    try:
        buff = aSocket.sendall (str (packet))
    except socket.error, x:
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
            raise SocketClosed
        else:
            raise

#======================================================================#

class SocketReader:
    """
    SocketReader reads lines of text from a socket. It can throw the
    exception SocketClosed.
    """
    def __init__(self, socket):
        self.socket = socket
        self.lines = None
        self.index = 0

    def readLine(self):
        """
        readLine & returns the next line of input.
        """
        if (not self.lines) or self.index >= len(self.lines):
            self.getLines()
        elif (self.index == len(self.lines) -1 and
                    self.lines [-1][-1] != '\n'):
            s = self.lines [-1]
            self.getLines()
            s += self.lines [0]
            self.index = 1
            return s
        s = self.lines [self.index]
        self.index += 1
        return s

    def getLines(self):
        """
        getLines gets the next batch of input.  It should not be
        called outside of SocketReader.
        """
        try:
            buff = self.socket.recv (1024)
        except socket.error, x:
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
                print "Caught socket error", err, ':', errstr
                raise SocketClosed
            else:
                raise

        if not buff:
            print "Nothing read, SocketReader::getLines throwing SocketClosed"
            raise SocketClosed
        self.lines = buff.splitlines (True)
        self.index = 0

#======================================================================#

class Packet:
    """
    class Packet
    this class is an abstract class that (hopfully) all packets
    sent/receved via the network will inheirit from
    """
    def getPacketType(self):
        assert 0, "getPacketType not defined"
    def getPacketClass(self):
        assert 0, "getPacketClass not defined"

#======================================================================#

class ParseError(Exception):
    pass

#======================================================================#

class PacketFactory:
    """
    class PacketFactory
    This class is an abstract factory class used to create packets from
    an input source.  It is initilized using calls to its register
    routine and the createPacket routine is used to build the packets.
    """
    def register(cls, packetType, builder):
        """
        register(packetType, builder) --> none
        Register a builder with a unique packetType.
        """
        cls.builders [packetType] = builder
    register = classmethod(register)

    def createPacket(cls, inputSource):
        """
        createPacket(inputSource) -> packet | None
        It will create a packet based on the input source
        """
        raise ParseError ("PacketFactory is an abstract class; it must "
                          "be inheirted before it can be used")
    createPacket = classmethod(createPacket)
