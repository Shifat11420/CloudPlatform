from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator, MessageGenerator

class ConnRespMGen(StringMessageGenerator):
    def __init__(self, in_context):
        dbgprint("Send ConnResp")
        strmsg = COMMAND_CONNRESP
        strmsg = strmsg + COMMA
        strmsg = strmsg + (in_context.idval)
        StringMessageGenerator.__init__(self, strmsg, in_context)

class ConnTestMGen(MessageGenerator):
    def __init__(self, in_context):
        dbgprint("ConnTest:init")
        MessageGenerator.__init__(self, in_context)
        self.finished = False
        self.firsttime = True
        self.countdown = 100

    def reset(self):
        MessageGenerator.reset(self)
        self.finished = False
        self.firsttime = True

    def read(self):
        if(self.finished):
            return None
        elif(self.firsttime):
            if(self.countdown == 0):
                self.finished = True
            self.firsttime = False
            msg = COMMAND_CONNTEST
            msg = msg + COMMA
            msg = msg + self.context.idval
            msg = msg + COMMA
            msg = msg + str(self.countdown)
            msg = msg + LINEDELIM
            self.countdown = self.countdown - 1
            return msg

