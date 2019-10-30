from CommandReaders.TCPReader import TCPReader
from Utilities.Const import *
from CommandMessageGenerators.ConnRespMGen import ConnRespMGen

class ConnTestReader(TCPReader):
    def __init__(self):
        self.finished = False
        
    def HandleLine(self, line):
        dbgprint("ConnTest")
        vals = line.split(COMMA)
        if(int(vals[2]) == 0):
            self.finished = True

    def IsFinished(self):
        return self.finished


    def GetResponse(self):
        dbgprint("CTR_GR")
        return ConnRespMGen(self.context)

class ConnRespReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(",")
        self.context.ReportConnTestFinished(vals[1])
