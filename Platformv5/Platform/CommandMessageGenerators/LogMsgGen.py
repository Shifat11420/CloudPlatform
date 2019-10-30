from Utilities.Const import *
from Utilities.LogStream import LogStream
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class SendLogMsgGen(StringMessageGenerator):
    def __init__(self, in_context):
        strmsg = COMMAND_SENDLOGS
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):return False

class FMsgGen(MessageGenerator):
    def __init__(self, cmd, readable, in_context):
        MessageGenerator.__init__(self, in_context)
        self.readable = readable
        self.firsttime = True
        self.cmd = cmd
    
    def read(self):
        val = self.readable.read()
        if(not (val is None)):
            dbgprint("SENDLOG:"+val)
            return self.cmd + COMMA + val
        else:
            dbgprint("SENDLOG:NONE")

    def reset(self):
        MessageGenerator.reset(self)
        self.readable.reset()

class ReceiveLogMsgGen(FMsgGen):
    def __init__(self, in_context):
        ls = LogStream(in_context.getPFileName(), in_context.getDFileName(), str(in_context.idval)+"_")
        FMsgGen.__init__(self, COMMAND_RECEIVELOGS, ls, in_context)
        self.finished = False
