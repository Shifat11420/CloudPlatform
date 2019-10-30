from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class SendBenchMG(StringMessageGenerator):
    def __init__(self, in_context):
        dbgprint("Send Bench")
        strmsg = COMMAND_GETBENCH
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        dbgprint("OneShot:"+str(self.__class__))
        return False


class BenchMessageGenerator(MessageGenerator):
    def __init__(self, in_context):
        dbgprint("BMG:init")
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
            self.firsttime = False
            self.finished = True
            msg = COMMAND_RECEIVEBENCH
            msg = msg + COMMA
            msg = msg + self.context.idval
            msg = msg + COMMA
            msg = msg + str(self.context.GetBench())
            msg = msg + LINEDELIM
            return msg
