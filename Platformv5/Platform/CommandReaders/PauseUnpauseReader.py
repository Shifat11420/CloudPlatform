from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *
import datetime

class PauseReader(TCPReader):
    def GetResponse(self):
        dbgprint("Received Pause Request")
        self.context.Pause()
        return StringMessageGenerator(COMMAND_RESPONDPAUSED)

class TimeUnpauseReader(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        dtval = datetime.datetime.strptime(vals[1], "%Y-%m-%dT%H:%M:%S.%f")
        self.context.SetUnpauseDatetime(dtval)
    def LoseConnection(self):
        return True
