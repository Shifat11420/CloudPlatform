from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class LatencyReportNode(StringMessageGenerator):
    def __init__(self, in_context, src_id, src_ip, src_port, slowest_id, max_latency, NeighborsLatencyDictall): #, NeighborsLatencyList):
        strmsg = COMMAND_LATENCYREPORTNODE
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
        strmsg = strmsg + COMMA
        strmsg = strmsg + SLOWESTNODE   ##
        strmsg = strmsg + COMMA        ##   
        strmsg = strmsg + SLOWEST_ID       ##
        strmsg = strmsg + COMMA
        strmsg = strmsg + str(slowest_id)
        strmsg = strmsg + COMMA
        strmsg = strmsg + MAX_LATENCY     ##
        strmsg = strmsg + COMMA 
        strmsg = strmsg + str(max_latency)
        strmsg = strmsg + COMMA
        strmsg = strmsg + LATENCY_DICT     ##
        strmsg = strmsg + str(NeighborsLatencyDictall)
        # strmsg = strmsg + COMMA 
        # strmsg = strmsg + LATENCY_LIST     ##
        # strmsg = strmsg + str(NeighborsLatencyList)
  

        StringMessageGenerator.__init__(self, strmsg, in_context)