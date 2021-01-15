from Utilities.Const import *
from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator

class AskForWorkReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecieveAskForWork")
        vals = data.split(",".encode('utf-8'))
        nodeid = vals[1].decode('utf-8')
        killcount = int(vals[2].decode('utf-8'))
        self.context.HandleWorkRequest(nodeid, killcount)

#    def GetResponse(self):
#        dbgprint("Received Work Request")
#        worktosend = self.context.GetWorkToSend()
#        if(worktosend == None):
#            return TerminateMessageGenerator(self.context)
#        return ContainerMessageGenerator(worktosend, self.context)
