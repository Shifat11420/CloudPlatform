from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class ReceiveExpNode(StringMessageGenerator):
    def __init__(self, in_context, src_id, src_ip, src_port):
        strmsg = COMMAND_RECEIVEEXPNODE
        strmsg = strmsg + COMMA 
        strmsg = strmsg + STR_ID
        strmsg = strmsg + COMMA
        strmsg = strmsg + src_id
        strmsg = strmsg + COMMA
        strmsg = strmsg + STR_IP 
        strmsg = strmsg + COMMA 
        strmsg = strmsg + src_ip 
        strmsg = strmsg + COMMA 
        strmsg = strmsg + STR_PORT
        strmsg = strmsg + COMMA 
        strmsg = strmsg + str(src_port)
        StringMessageGenerator.__init__(self, strmsg, in_context)
