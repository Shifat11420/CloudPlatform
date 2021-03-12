from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class BenchReportNode(StringMessageGenerator):
    def __init__(self, in_context, src_id, src_ip, src_port, id_maxBench, max_Bench):
        strmsg = COMMAND_BENCHREPORTNODE
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
        strmsg = strmsg + LOWESTPERFORMINGNODE   ##
        strmsg = strmsg + COMMA        ##   
        strmsg = strmsg + LOWESTPERFORMING_ID       ##
        strmsg = strmsg + COMMA
        strmsg = strmsg + id_maxBench            ##
        strmsg = strmsg + COMMA
        strmsg = strmsg + MAX_BENCH     ##
        strmsg = strmsg + COMMA 
        strmsg = strmsg + str(max_Bench)      ##
  

        StringMessageGenerator.__init__(self, strmsg, in_context)