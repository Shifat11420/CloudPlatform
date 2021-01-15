from Utilities.Const import *
from Utilities.FileUtil import expprint
from CommandReaders.TCPReader import TCPReader
import sys
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator   ##added import


class HelloReader(TCPReader):
    def GetResponse(self):
        dbgprint("Received Hello Request")
        return StringMessageGenerator(COMMAND_RESPONDHELLO+LINEDELIM, self.context)

class HelloResponder(TCPReader):
    def IsFinished(self):
        dbgprint("Received Hello Response")
        return True

class TerminateReader(TCPReader):
    def LoseConnection(self):
        dbgprint("Received Terminate Request")
        return True

class EndServerReader(TCPReader):
    
    def LoseConnection(self):
        expprint("BeforeFlush")
        sys.stdout.flush()
        #BRIAN - If Logs disappear, recomment out next line
        #to make server only respond to direct kill
        self.context.terminate = True
        return True
