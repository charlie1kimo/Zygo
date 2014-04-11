#! !/usr/bin/env python
# file: omMeas/wexLib/wsp.py
# author: glc

# this file contains the classes needed by the WS to communicate with
#   the WM

#TODO: should we enforce the valid chars in the various strings?

#import omMeas.wexLib.nio as nio
import nio
import string

    # wavemeter request packet command names
MEASURE_WAVELENGTH  = "MeasureWavelength"
READ_WAVELENGTH     = "ReadWavelength"
MEASURE_WEATHER     = "MeasureWeather"
READ_WEATHER        = "ReadWeather"
IDENTIFY            = "Identify"
ABORT               = "Abort"

    # Rtd server request packet command names
READ_TEMPERATURE = "ReadTemperature"

    # response packet response types
COMPLETE = "COMPLETE"
ERROR    = "ERROR"
PENDING  = "PENDING"

#======================================================================#

class ParameterLine:
    """
    class ParameterLine
    this class is the object storing parameter data for either the
    ReqPacket or the RspPacket
    """
    def __init__(self, line, value = None):
        """
        create a ParameterLine.
          line:   String: Either the whole Parameter line as a string
                          (if value is none) or just the parameter name
          value:  String: The parameter value
        """
        if value == None:
            if line[0] not in string.whitespace:
                raise nio.ParseError("illegal Parameter line")

            line = line.strip()        #strip leading/trailing ws
            if (line [0] == '='):
                raise nio.ParseError("illegal Parameter name")

                #split the param name off (& toss any trailing ws)
            cols = line.split('=', 1)
            if len(cols) != 2:
                raise nio.ParseError("illegal Parameter line")
            self.paramName = cols [0].rstrip()
            for c in self.paramName:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.' or c == '-'):
                    raise nio.ParseError("illegal Parameter name")
                #now save the param value (& toss any leading ws)
            self.paramValue = cols [1].lstrip()
        else:
            self.paramName = line.strip()
            for c in self.paramName:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.' or c == '-'):
                    raise nio.ParseError("illegal Parameter name")
            self.paramValue= value.strip()

    def getName(self):  return self.paramName
    def getValue(self): return self.paramValue
    def __str__(self):
        return self.paramName +" = " +self.paramValue

    def dump(self):
        print "  Param name:",  self.getName()
        print "  Param value:", self.getValue()
        print "  Param str:",   str(self)

    def test():
        param = ParameterLine(" frog=crunchy");
        param.dump()
        param = ParameterLine("spring", "surprise");
        param.dump()

        strings = [ " goodParamLine=", " badParmLine",
            " spam eggs= no space allowed in parm name",
            "badParmLine=no leading space",
            " !@#$%^Parm= Bad chars", " GoodParm = !@#$%^",
            " Who,me. = No commas allowed!", " Periods.are.Ok = ",
            "    AWholeLotOfSpaces      =      are          fine   ",
            " Dashes-in-name = is Cool " ]
        for s in strings:
            try:
                param = ParameterLine(s);
                param.dump()
            except nio.ParseError, x:
                print s, "generated ParseError:", x

    test = staticmethod(test)

#======================================================================#

class Packet(nio.Packet):
    """
    class om.ws.wm.Packet
    this class is an abstract class that (hopfully) all packets
    sent/receved the WS server and the clients will inheirit from.

    TODO: This class will need a factory added to it that can convert
    text from a socket into the correct packet.
    """
    def __init__(self, ctag):
        self.ctag = ctag
        self.params = []
        
    def getPacketClass(self):
        return "WM"

    def getPacketType(self):
        return self.type

    def getCtag(self):          return self.ctag
    def setCtag(self, ctag):    self.ctag = ctag

    def addParam(self, param):
        if isinstance(param, ParameterLine):
            self.params.append(param)
        elif type(param) == type("Cheese Shop"):
            if len (param):
                self.params.append(ParameterLine(param))
        else:
            raise TypeError("unknown type in om.ws.wmPacket.addParam()")

    def getParamByName(self, paramName):
        """
        Return all parameters of packet whose name is paramName.
        Currently no wildcarding is supported, but that could be added.
        Also could define a regex variant
        """
        pnl = paramName.lower()
        return [p for p in self.params if p.getName().lower()==pnl]

    def getErrorParameters(self):
        """
        Return all parameters of packet whose name starts with ErrorDesc.
        """
        return [p for p in self.params
                    if p.getName().lower().startswith("errordesc")]

    def getOneParamByName(self, paramName):
        pl = self.getParamByName(paramName)
        # XXX: fix exception type
        if len(pl) == 0:
            raise RuntimeError, "Missing parameter: %s" % paramName
        if len(pl) > 1:
            raise RuntimeError, "Too many parameters: %s" % paramName
        return pl[0]


    def getParams(self):    return self.params

    def getMagicPacketType(cps):
        return cps.magicKey
    getMagicPacketType = classmethod(getMagicPacketType)

    def dump(self):
        """
        dump() is used only in debugging/testing.  It outputs all the
        packet's data.
        """
        print "Packet class:", self.getPacketClass()
        print "Packet type:",  self.getPacketType()
        print "Packet ctag:",  self.getCtag()
        for param in self.getParams():
            print "Packet param:"
            param.dump()
        print "Packet str:"
        print str(self)

#======================================================================#

class ReqPacket(Packet):
    """
    class ReqPacket
    this class is the class for sending a request from the IAS PC to the
    WS.
    """
    magicKey = "REQ" 

    def __init__(self, s1, cmdName = None, params = []):
        """
        create a ReqPacket.
          s1:         String:         Either the whole packet as a
                                      string (if cmdName is none) or
                                      just the ctag value
          cmdName:    String:         command name for the packet
          params:     ParameterLine[]:Array of Parameter lines (ignored
                                      if cmdName is null).
        """
        if s1 == None or len(s1) == 0:
            raise nio.ParseError("illegal REQ packet: no data")
        self.type = "REQ"
        if cmdName==None:
            lines = s1.strip().splitlines()
            if len(lines) < 2:
                for i in range (len(lines)):
                    print "line %d: %s" % (i, lines [i])
                raise nio.ParseError("illegal REQ packet: "
                                                "not enough lines")
            colls = lines[0].split()
            if colls == None:
                raise nio.ParseError("illegal REQ packet: %s" % s1)
            if len(colls) != 3:
                print "number of tokens in 1st line: %d" % len(colls)
                for i in range (len(colls)):
                    print "token %d: %s" % (i, colls [i])
                raise nio.ParseError("illegal REQ packet: %s" % s1)
            if colls [0] != "REQ":
                raise nio.ParseError("illegal REQ packet: %s" % s1)
            for c in colls[1]:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal REQ ctag value: %s" %
                                                            colls[1])
            for c in colls[2]:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal REQ cmd-name value: %s " %
                                                            colls[2])
            if lines [-1] != '.':
                raise nio.ParseError("illegal REQ packet: "
                                                    "no trailing dot")
            Packet.__init__(self, colls[1])
            self.cmdName = colls [2]
            for param in lines[1:-1]:
                self.addParam(param)
        else:
            for c in s1:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal REQ ctag value: %s" %
                                                                s1)
            for c in cmdName:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal REQ cmd-name value: %s" %
                                                                cmdName)
            Packet.__init__(self, s1)
            self.cmdName = cmdName
            if isinstance(params, list):
                for param in params:
                    self.addParam(param)
            else:
                self.addParam(params)
  
    def getCmdName(self):
        return self.cmdName

    def __str__(self):
        buff = "%s %s %s\n" % (self.type, str(self.getCtag()),
        				self.cmdName)
        for param in self.getParams():
            buff += " %s\n" % str(param)
        return buff +".\n"

    def init():
        PacketFactory.register ("REQ", ReqPacket.builder)
    init = staticmethod(init)

    def builder(s):
        return ReqPacket(s)
    builder = staticmethod(builder)

    def test():
        packet=ReqPacket("\nREQ 42 WhoAreYou\n jobTitle=lumberjack\n.\n")
        packet.dump()

        params = [ParameterLine (" Nationality = Norwegian")]
        params.append (ParameterLine ("color", "blue"))
        packet = ReqPacket ("Nuge", "GetStatus", params)
        packet.addParam (ParameterLine ("ErrorDesc.1", "'E's dead"))
        packet.addParam (ParameterLine ("plumage", "Beautiful"))
        packet.addParam (ParameterLine ("location",
                "gone to meet 'is maker"))
        packet.addParam (ParameterLine ("ErrorDesc.2",
                "It's stone dead"))
        packet.addParam (ParameterLine ("StatusDesc",
                "tired and shagged out following a prolonged squawk"))
        packet.addParam (ParameterLine ("ErrorDesc.3",
                "'E's bleedin' demised"))
        packet.addParam (ParameterLine ("ErrorDesc.4",
                "'E's off the twig"))
        packet.addParam (ParameterLine ("ErrorDesc.5",
                "pushing up the daisies"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "'E's kicked the bucket,"))
        packet.addParam (ParameterLine ("ErrorDesc", "'E's passed on"))
        packet.addParam (ParameterLine ("ErrorDesc", "ceased to be"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "'e rests in peace"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "shuffled off 'is mortal coil"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "run down the curtain"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "joined the bleedin' choir invisibile"))
        packet.addParam (ParameterLine ("ErrorDesc",
                "'E f'in snuffed it"))
        packet.dump()
        strings = ["color", "colour", "plumage", "ErrorDesc"]
        for string in strings:
            print "calling Packet.getParamByName %s" % string
            try:
                params = packet.getParamByName (string)
                for param in params:
                    param.dump()
            except RuntimeError, x:
                print "RuntimeError:", x

            print "calling Packet.getOneParamByName %s" % string
            try:
                param = packet.getOneParamByName (string)
                param.dump()
            except RuntimeError, x:
                print "RuntimeError:", x
        print "*** Error descriptions:"
        for param in packet.getErrorParameters():
            print param.getValue()

    test = staticmethod(test)

#======================================================================#

class RspPacket(Packet):
    """
    class RspPacket
    this class is the class for sending a response from the WS to the
    IAS PCs
    """
    magicKey = "RSP" 

    def __init__(self, s1, respKind = None, params = []):
        """
        create a RspPacket.
          s1:         String:         Either the whole packet as a
                                      string (if respKind is none) or
                                      just the ctag value
          respKind:   String:         response kind of the packet
          params:     ParameterLine[]:Array of Parameter lines (ignored
                                      if respKind is null).
        """
        if s1 == None or len(s1) == 0:
            raise nio.ParseError("illegal RSP packet: no data")
        self.type = "RSP"
        if respKind==None:
            lines = s1.strip().splitlines()
            if len(lines) < 2:
                for i in range (len(lines)):
                    print "line %d: %s" % (i, lines [i])
                raise nio.ParseError("illegal RSP packet: "
                                                "not enough lines")
            colls = lines[0].split()
            if colls == None:
                raise nio.ParseError("illegal RSP packet: %s" % s1)
            if len(colls) != 3:
                print "number of tokens in 1st line: %d" % len(colls)
                for i in range (len(colls)):
                    print "token %d: %s" % (i, colls [i])
                raise nio.ParseError("illegal RSP packet: %s" % s1)
            if colls [0] != "RSP":
                raise nio.ParseError("illegal RSP packet: %s" % s1)
            for c in colls[1]:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal RSP ctag value: %s" %
                                                            colls[1])
            for c in colls[2]:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal RSP resp-Kind value: %s" %
                                                            colls[2])
            if lines [-1] != '.':
                raise nio.ParseError("illegal RSP packet: "
                                                    "no trailing dot")
            Packet.__init__(self, colls[1])
            self.respKind = colls [2]
            for param in lines[1:-1]:
                self.addParam(param)
        else:
            for c in s1:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal RSP ctag value: %s" %
                                                                s1)
            for c in respKind:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal RSP resp-Kind value: %s" %
                                                                cmdName)
            Packet.__init__(self, s1)
            self.respKind = respKind
            if isinstance(params, list):
                for param in params:
                    self.addParam(param)
            else:
                self.addParam(params)
        
    def getRespKind(self):
        return self.respKind

    def __str__(self):
        buff = "%s %s %s\n" % (self.type, str(self.getCtag()),
        				self.respKind)
        for param in self.getParams():
            buff += " %s\n" % str(param)
        return buff +".\n"

    def init():
        PacketFactory.register ("RSP", RspPacket.builder)
    init = staticmethod(init)

    def builder(s):
        return RspPacket(s)
    builder = staticmethod(builder)

    def test():
        packet = RspPacket("RSP 42 ERROR\n\n Gender=confused\n\n.\n\n")
        packet.dump()

        param = ParameterLine (" parrot=dead");   params = [param]
        packet = RspPacket("Nuge", "ERROR", params)
        packet.dump()
    test = staticmethod(test)

#======================================================================#

class DiePacket(Packet):
    """
    class DiePacket
    this class is the class for sending a response from the WS to the
    IAS PCs
    """
    magicKey = "DIE" 

    def __init__(self, s1, dieName = None, params = []):
        """
        create a DiePacket.
          s1:         String:         Either the whole packet as a
                                      string (if respKind is none) or
                                      just the ctag value
          respKind:   String:         response kind of the packet
          params:     ParameterLine[]:Array of Parameter lines (ignored
                                      if respKind is null).
        """
        if s1 == None or len(s1) == 0:
            raise nio.ParseError("illegal DIE packet: no data")
        self.type = "DIE"
        if dieName==None:
            lines = s1.strip().splitlines()
            if len(lines) < 2:
                for i in range (len(lines)):
                    print "line %d: %s" % (i, lines [i])
                raise nio.ParseError("illegal DIE packet: "
                                                "not enough lines")
            colls = lines[0].split()
            if colls == None:
                raise nio.ParseError("illegal DIE packet: %s" % s1)
            if len(colls) != 3:
                print "number of tokens in 1st line: %d" % len(colls)
                for i in range (len(colls)):
                    print "token %d: %s" % (i, colls [i])
                raise nio.ParseError("illegal DIE packet: %s" % s1)
            if colls [0] != "DIE":
                raise nio.ParseError("illegal DIE packet: %s" % s1)
            for c in colls[1]:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal DIE ctag value: %s" %
                                                            colls[1])
            for c in colls[2]:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal DIE die-name value: %s" %
                                                            colls[2])
            if lines [-1] != '.':
                raise nio.ParseError("illegal DIE packet: "
                                                    "no trailing dot")
            Packet.__init__(self, colls[1])
            self.dieName = colls [2]
            for param in lines[1:-1]:
                self.addParam(param)
        else:
            for c in s1:
                if not( c in string.letters or c in string.digits or
                        c == '_' or c == '.'):
                    raise nio.ParseError("illegal DIE ctag value: %s" %
                                                            s1)
            for c in dieName:
                if not( c in string.letters or c in string.digits):
                    raise nio.ParseError("illegal DIE die-name value: %s" %
                                                            dieName)
            Packet.__init__(self, s1)
            self.dieName = dieName
            if isinstance(params, list):
                for param in params:
                    self.addParam(param)
            else:
                self.addParam(params)
        
    def getDieName(self):
        return self.dieName

    def __str__(self):
        buff = "%s %s %s\n" % (self.type, str(self.getCtag()),
        				self.dieName)
        for param in self.getParams():
            buff += " %s\n" % str(param)
        return buff +".\n"

    def init():
        PacketFactory.register ("DIE", DiePacket.builder)
    init = staticmethod(init)

    def builder(s):
        return DiePacket(s)
    builder = staticmethod(builder)

    def test():
        packet = DiePacket("DIE 0 SESSION\n\n DieDesc=because\n\n.\n\n")
        packet.dump()

        params = [ParameterLine ("DieDesc", "We're doomed")]
        packet = DiePacket("0", "DieDesc", params)
        packet.dump()
    test = staticmethod(test)

#======================================================================#

class PacketFactory(nio.PacketFactory):
    """
    class PacketFactory
    This class is a factory class used to create packets from an
    input source.  It is initilized using calls to its parent's register
    routine and the createPacket routine is used to build the packets.
    """
    builders = dict()

    def createPacket(cls, inputSource):
        """
        createPacket(inputSource) -> packet | None;
        can throw nio.ParseError
        This routine will create a wsp packet based on the input source
        """
        if isinstance(inputSource, nio.SocketReader):
            s = ""
            while True:
                s1 = inputSource.readLine()
                s += s1
                if s1[0] == '.':
                    break
        elif type(inputSource) == type("DeadParrot"):
            s = inputSource
        else:
            raise nio.ParseError("unknown data source")
        s = s.strip()
        builder = cls.builders.get (s[0:3])
        if builder:
            return builder (s)
        else:
            raise nio.ParseError("unknown packet type: %s" % s)
    createPacket = classmethod(createPacket)

    def test():
        strings = ["\n\nRSP 1 spam\n goodPacket=\n.\n\n",
               "Bad 2 eggs\n.",
               "RSP 3 cheese Shop\n  badPacket = 4 tokens in 1st line\n.",
               "REQ good.ctag request\n.",
               "REQ bad-ctag request\n.",
               "RSP 4 bad.request\n." ]

        for s in strings:
            try:
                packet = PacketFactory.createPacket(s)
                packet.dump()
            except nio.ParseError, x:
                print "ParseError:", x, "from ", s
    test = staticmethod(test)

#======================================================================#

ReqPacket.init()
RspPacket.init()
DiePacket.init()

#======================================================================#

if __name__ == "__main__":
    ParameterLine.test()

    print "\n**********************\n"

    ReqPacket.test()

    print "\n**********************\n"

    RspPacket.test()

    print "\n**********************\n"

    DiePacket.test()

    print "\n**********************\n"

    PacketFactory.test()
