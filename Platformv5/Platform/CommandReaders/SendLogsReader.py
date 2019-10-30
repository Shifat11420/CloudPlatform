from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.LogMsgGen import ReceiveLogMsgGen
from Utilities.Const import *

class SendLogsReader(TCPReader):
    def GetResponse(self):
        return ReceiveLogMsgGen(self.context)

class ReceiveLogsReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("ReceiveLog:"+data)
        self.context.storeLog(data)
