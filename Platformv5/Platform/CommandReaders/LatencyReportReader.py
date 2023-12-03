from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *


class LatencyReportReader(TCPReader):
    def HandleLine(self, line):
        valsplitlist = line.split(LATENCY_DICT.encode('utf-8'))

        vals = valsplitlist[0].split(",".encode('utf-8'))
        i = 0
        exp_id = None
        exp_ip = None
        exp_port = 0
        slowest_id = None
        max_latency = None
        NeighborsLatencyDictall = {}
        #NeighborsLatencyList = []
        
        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                exp_ip = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == STR_PORT):
                exp_port = int(vals[i+1].decode('utf-8'))
            if(val.decode('utf-8') == STR_ID):
                exp_id = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == SLOWEST_ID):
                slowest_id = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == MAX_LATENCY):
                max_latency = float(vals[i+1].decode('utf-8')) 
            # if(val.decode('utf-8') == LATENCY_DICT):
            #     NeighborsLatencyDictall = (vals[i+1].decode('utf-8'))       
            # #if(val.decode('utf-8') == LATENCY_LIST):
            # NeighborsLatencyList = (valsplitlist[1].decode('utf-8'))    
            NeighborsLatencyDictall = (valsplitlist[1].decode('utf-8'))         
            i = i + 1
        self.context.LatencyReportExpNode(exp_id, exp_ip, exp_port, slowest_id, max_latency,NeighborsLatencyDictall)#, NeighborsLatencyList)

