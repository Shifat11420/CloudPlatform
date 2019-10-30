from CommandMessageGenerators.MessageGenerator import StringMessageGenerator, MessageGenerator
from Utilities.Const import *

class AddNeighborMessageGenerator(StringMessageGenerator):
    def __init__(self, context, n_ip, n_port, n_id):
        strmsg = COMMAND_ADDNEIGHBOR
        strmsg = strmsg + COMMA 
        strmsg = strmsg + STR_IP 
        strmsg = strmsg + COMMA 
        strmsg = strmsg + n_ip 
        strmsg = strmsg + COMMA 
        strmsg = strmsg + STR_PORT
        strmsg = strmsg + COMMA 
        strmsg = strmsg + str(n_port)
        strmsg = strmsg + COMMA
        strmsg = strmsg + STR_ID
        strmsg = strmsg + COMMA
        strmsg = strmsg + str(n_id)
        StringMessageGenerator.__init__(self, strmsg, context)
