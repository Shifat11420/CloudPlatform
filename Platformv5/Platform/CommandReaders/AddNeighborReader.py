from Utilities.Const import *
from CommandReaders.TCPReader import TCPReader

class AddNeighborReader(TCPReader):
    
    def HandleLine(self, line):
        vals = line.split(",")
        i = 0
        neighbor_ip = None
        neighbor_port = 0
        neighbor_id = None
        for val in vals:
            if(val == STR_IP):
                neighbor_ip = vals[i+1]
            if(val == STR_PORT):
                neighbor_port = int(vals[i+1])
            if(val == STR_ID):
                neighbor_id = vals[i+1]
            i = i + 1
        self.context.AddNeighbor(neighbor_ip, neighbor_port, neighbor_id)

class DeleteNeighborReader(TCPReader):
    
    def HandleLine(self, line):
        vals = line.split(",")
        i = 0
        neighbor_ip = None
        neighbor_port = 0
        for val in vals:
            if(val == STR_IP):
                neighbor_ip = vals[i+1]
            if(val == STR_PORT):
                neighbor_port = int(vals[i+1])
            i = i + 1
        self.context.DeleteNeighbor(neighbor_ip, neighbor_port)

