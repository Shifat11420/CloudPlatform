from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandReaders.TCPReader import TCPReader

class DropNeighborbyLatencyReader(TCPReader):
    ## done for MST from exp controller
    # def HandleLine(self, line):
    #     valsplitlist = line.split(COMMAND_DROPBYLATENCY.encode('utf-8'))
    #     listIDtosend = (valsplitlist[1].decode('utf-8'))
        
    #     self.context.DropNeighborbyLatency(listIDtosend)


    # ## done for new algo from exp controller 
    # def HandleLine(self, line):
    #     new_var = ";"
    #     vals = line.split(new_var.encode('utf-8'))
    #     i = 0
    #     close_listPORTtosend = []
    #     less_close_listPORTtosend = []
    #     far_listPORTtosend = []

    #     for val in vals:
    #         if(val.decode('utf-8') == CLOSEPORTS):
    #             close_listPORTtosend = vals[i+1].decode('utf-8')
    #         if(val.decode('utf-8') == LESSCLOSEPORTS):
    #             less_close_listPORTtosend = vals[i+1].decode('utf-8')
    #         if(val.decode('utf-8') == FARPORTS):
    #             far_listPORTtosend = vals[i+1].decode('utf-8')
    #         i = i + 1
    #     self.context.DropNeighborbyLatency(close_listPORTtosend, less_close_listPORTtosend, far_listPORTtosend)


    



    ## done for new algo from exp controller 
    def HandleLine(self, line):
        new_var = ";"
        vals = line.split(new_var.encode('utf-8'))
        i = 0
        nodesPORTStodrop = []
        
        for val in vals:
            if(val.decode('utf-8') == NODESPORTSTODROP):
                nodesPORTStodrop = vals[i+1].decode('utf-8')
            i = i + 1
        self.context.DropNeighborbyLatency(nodesPORTStodrop)

