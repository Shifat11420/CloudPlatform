from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator

class ReceiveReq(TCPReader):
    def GetResponse(self):
        return self.ReqAckMsgGen(self)         ##added self

    
