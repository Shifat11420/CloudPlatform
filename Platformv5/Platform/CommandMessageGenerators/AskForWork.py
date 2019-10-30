from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class AskForWork(StringMessageGenerator):
    def __init__(self, in_context, killcount):
        strmsg = COMMAND_ASKFORWORK
        strmsg = strmsg + COMMA
        strmsg = strmsg + in_context.idval
        strmsg = strmsg + COMMA
        strmsg = strmsg + str(killcount)
        StringMessageGenerator.__init__(self, strmsg, in_context)
