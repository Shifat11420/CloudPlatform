from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

MAXCOUNTDOWN = 50

class ConnTestMGen(MessageGenerator):
    def __init__(self, in_context):
        MessageGenerator.__init__(self, in_context)
        countdown = MAXCOUNTDOWN

    def read(self):
        if(self.countdown == 0):                                      ##added self
            return None
        else:
            countdown = countdown - 1
            return COMMAND_CONNTEST + COMMA + str(countdown) + LINEDELIM                   ## correct spelling from COMMTEST

    def reset(self):
        MessageGenerator.reset(self)
        countdown = MAXCOUNTDOWN

class ConnRespMGen(StringMessageGenerator):
    def __init__(self, in_context):
        
        dbgprint("ConnRespMGen")
        strmsg = COMMAND_CONNRESP+COMMA+self.in_context.idval + LINEDELIM
        StringMessageGenerator.__init__(self, strmsg, in_context)
