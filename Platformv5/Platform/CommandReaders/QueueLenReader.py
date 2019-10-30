from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.QueueLenMessageGenerator import QueueLenMessageGenerator
from Utilities.Const import *

class SendQueueLenReader(TCPReader):
    def GetResponse(self):
        dbgprint("SendQueueLenReader")
        return QueueLenMessageGenerator(self.context)

class RecieveExpectCompTime(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecExpectCompTime")
        vals = data.split(",")
        self.context.SetExpectCompTime(float(vals[1]))
    
class ReceiveQueueLenReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("ReceiveQueueLenReader")
        vals = data.split(",")
        nodeid = vals[1]
        nodequeuelen = int(vals[2])
        self.context.SetNeighborQueueLen(nodeid, nodequeuelen)

class ReceiveSubQueueLenReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("RSQLReader")
        vals = data.split(",")
        basenodeid = vals[1]
        subids = []
        subqlens = []
        for i in range(2, len(vals)-1, 2):
            subids.append(vals[i])
            subqlens.append(int(vals[i+1]))

        self.context.SetNeighborSubQueues(basenodeid, subids, subqlens)
