from Utilities.Const import *
from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator

class AsktosleepExpReader(TCPReader):
    def HandleLine(self):
        dbgprint("RecieveAsktosleepExp")
        self.context.AsktosleepExp(self.context)    