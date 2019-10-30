from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class FlowVectorMGen(StringMessageGenerator):
    def __init__(self, in_context, vset):
        dbgprint("FlowVectorMGen")
        strmsg = COMMAND_FLOWVECTOR + COMMA
        for vec in vset:
            for val in vec:
                strmsg = strmsg + str(val) + COMMA
            strmsg = strmsg + ";"
        StringMessageGenerator.__init__(self, strmsg, in_context)

class StasisVectorMGen(StringMessageGenerator):
    def __init__(self, in_context, vset):
        dbgprint("StasisVectorMGen")
        strmsg = COMMAND_STASISVECTOR + COMMA
        for vec in vset:
            for val in vec:
                strmsg = strmsg + str(val) + COMMA
            strmsg = strmsg + ";"
        StringMessageGenerator.__init__(self, strmsg, in_context)

class SwapTimesMGen(StringMessageGenerator):
    def __init__(self, in_context, vvals):
        dbgprint("SwapTimesMGen")
        strmsg = COMMAND_SWAPTIMES  + COMMA
        for val in vvals:
            strmsg = strmsg + str(val) + COMMA
        StringMessageGenerator.__init__(self, strmsg, in_context)
