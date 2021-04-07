from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class AsktosleepExpNode(StringMessageGenerator):
    def __init__(self, in_context):
        strmsg = COMMAND_ASKTOSLEEPEXP
       
        StringMessageGenerator.__init__(self, strmsg, in_context)

