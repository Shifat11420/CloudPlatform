from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.LatencyMessageGenerator import LatencyMessageGenerator
from Utilities.Const import *

class SendLatencyReader(TCPReader):
    def GetResponse(self):
        dbgprint("SendLatencyReader")
        return LatencyMessageGenerator(self.context)

class ReceiveLatencyReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecieveLatencyReader")
        vals = data.split(",".encode('utf-8'))

        i = 0
        nodeid = None
        nodeip = None
        nodeport = 0
        nodelatency = None

        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                nodeip = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == STR_PORT):
                nodeport = int(vals[i+1].decode('utf-8'))
            if(val.decode('utf-8') == STR_ID):
                nodeid = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == AVGLATENCY):
                nodelatency = float(vals[i+1].decode('utf-8'))   
            i = i + 1         

        self.context.SetNeighborLatency(nodeid, nodeip, nodeport, nodelatency)
        

  