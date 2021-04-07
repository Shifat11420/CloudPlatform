from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *


class LowperfReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(",".encode('utf-8'))
        i = 0
        node_id = None
        node_ip = None
        node_port = 0
        id_maxBench = None
        max_Bench = None
        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                node_ip = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == STR_PORT):
                node_port = int(vals[i+1].decode('utf-8'))
            if(val.decode('utf-8') == STR_ID):
                node_id = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == LOWESTPERFORMING_ID):
                id_maxBench = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == MAX_BENCH):
                max_Bench = float(vals[i+1].decode('utf-8'))    
            i = i + 1
        self.context.LowperfNode(node_id, node_ip, node_port, id_maxBench, max_Bench)