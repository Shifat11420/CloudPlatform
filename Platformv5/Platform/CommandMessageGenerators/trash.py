from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
class NewLeaderAcceptMG(StringMessageGenerator):
    def __init__(self, in_context):
        strmsg = COMMAND_LEADERACCEPT + COMMA + in_context.idval
        StringMessageGenerator.__init__(self, strmsg, in_context)
    def OneShot(self):return False

class NewLeaderRejectMG(StringMessageGenerator):
    def __init__(self, in_context):
        strmsg = COMMAND_LEADERREJECT + COMMA + in_context.idval
        StringMessageGenerator.__init__(self, strmsg, in_context)
    def OneShot(self):return False
