from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *

class TimeUnpauseMessageGenerator(StringMessageGenerator):
    def __init__(self, in_context, dtval):
        msg = COMMAND_UNPAUSETIME +COMMA+ dtval.isoformat() 
        StringMessageGenerator.__init__(self, msg, in_context)
