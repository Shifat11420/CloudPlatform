from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *


class BenchReportReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(",".encode('utf-8'))
        i = 0
        exp_id = None
        exp_ip = None
        exp_port = 0
        id_maxBench = None
        max_Bench = None
        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                exp_ip = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == STR_PORT):
                exp_port = int(vals[i+1].decode('utf-8'))
            if(val.decode('utf-8') == STR_ID):
                exp_id = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == LOWESTPERFORMING_ID):
                id_maxBench = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == MAX_BENCH):
                max_Bench = float(vals[i+1].decode('utf-8'))    
            i = i + 1
        self.context.BenchReportExpNode(exp_id, exp_ip, exp_port, id_maxBench, max_Bench)