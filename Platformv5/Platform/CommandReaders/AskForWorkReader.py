from Utilities.Const import *
from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator

class AskForWorkReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecieveAskForWork")
        vals = data.split(",")
        nodeid = vals[1]
        killcount = int(vals[2])
        self.context.HandleWorkRequest(nodeid, killcount)

#    def GetResponse(self):
#        dbgprint("Received Work Request")
#        worktosend = self.context.GetWorkToSend()
#        if(worktosend == None):
#            return TerminateMessageGenerator(self.context)
#        return ContainerMessageGenerator(worktosend, self.context)
