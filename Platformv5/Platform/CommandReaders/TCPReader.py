from abc import ABCMeta, abstractmethod
from Utilities.Const import *

class TCPReader():
    def __init__(self, in_context):
        self.context = in_context
        self.nextHandlerBase = None
        self.finished = False

    def HandleLine(self, data):pass

    def GetRemainder(self):
        return None

    def SetToRaw(self):
        return False

    def IsFinished(self):
        return True

    def SetNextHandler(self, nextHandler):
        self.nextHandlerBase = nextHandler

    def GetNextHandler(self):
        return self.nextHandlerBase

    def GetResponse(self):
        return None

    def WriteResponse(self, transp):
        val = self.GetResponse()
        if(val != None):
            dbgprint("Writing Response")
            val.WriteResponse(transp)

    def LoseConnection(self):
        return False

    def AddReactor(self, rController):
        pass
