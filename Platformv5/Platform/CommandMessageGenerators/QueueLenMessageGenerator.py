from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class SendExpectCompTime(StringMessageGenerator):
    def __init__(self, in_context, ect):
        strmsg = COMMAND_RECEIVEEXPECTEDCOMPTIME
        strmsg = strmsg + COMMA + str(ect)
        StringMessageGenerator.__init__(self, strmsg, in_context)

class SendQueueLenMG(StringMessageGenerator):
    def __init__(self, in_context):
        strmsg = COMMAND_GETQUEUELEN
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        dbgprint("OneShot:"+str(self.__class__))
        return False


class QueueLenMessageGenerator(MessageGenerator):
    def __init__(self, in_context):
        MessageGenerator.__init__(self, in_context)
        self.finished = False
        self.firsttime = True

    def reset(self):
        MessageGenerator.reset(self)
        self.finished = False
        self.firsttime = True
        
    def read(self):
        if(self.finished):
            return None
        elif(self.firsttime):
            dbgprint("QLMG:Send")
            self.firsttime = False
            msg = COMMAND_RECEIVEQUEUELEN
            msg = msg + COMMA
            msg = msg + str(self.context.idval)
            msg = msg + COMMA
            msg = msg + str(self.context.GetQueueLen())
            msg = msg + LINEDELIM
            dbgprint("QLMG:Msg:"+msg)
            return msg
