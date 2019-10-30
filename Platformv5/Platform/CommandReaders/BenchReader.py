from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.BenchMessageGenerator import BenchMessageGenerator
from Utilities.Const import *

class SendBenchReader(TCPReader):
    def GetResponse(self):
        dbgprint("SendBenchReader")
        return BenchMessageGenerator(self.context)

class ReceiveBenchReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecieveBenchReader")
        vals = data.split(",")
        nodeid = vals[1]
        nodebench = vals[2]
        self.context.SetNeighborBench(nodeid, nodebench)
        
