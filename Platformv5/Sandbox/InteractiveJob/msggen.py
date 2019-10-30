
from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class SendObligMG(StringMessageGenerator):
    def __init__(self, in_context, obligid):
        strmsg = COMMAND_OBLIGATION + COMMA + str(obligid) 
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        return False

class RequestInclLockMG(StringMessageGenerator):
    def __init__(self, in_context, token):
        strmsg = COMMAND_REQINCLLOCK + COMMA + str(token)
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        return False

class RequestExclLockMG(StringMessageGenerator):
    def __init__(self, in_context, token):
        strmsg = COMMAND_REQEXCLLOCK + COMMA + str(token)
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        return False

class ProvideInclLockMG(StringMessageGenerator):
    def __init__(self, in_context, token):
        strmsg = COMMAND_PROVIDEINCLLOCK + COMMA + str(token)
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        return False

class DenyInclLockMG(StringMessageGenerator):
    def __init__(self, in_context, token):
        strmsg = COMMAND_DENYINCLLOCK + COMMA + str(token)
        StringMessageGenerator.__init__(self, strmsg, in_context)
    
class SendObligAckMG(StringMessageGenerator):
    def __init__(self, in_context, ack_id):
        strmsg = COMMAND_OBLIGACK + COMMA + str(ack_id)
        StringMessageGenerator.__init__(self, strmsg, in_context)

class SendReqMG(StringMessageGenerator):
    def __init__(self, in_context, req_id):
        strmsg = COMMAND_REQUIREMENT + COMMA + str(req_id)
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):
        return False

class SendReqAckMG(StringMessageGenerator):
    def __init__(self, in_context, ack_id):
        strmsg = COMMAND_REQACK + COMMA + str(ack_id)
        StringMessageGenerator.__init__(self, strmsg, in_context)
