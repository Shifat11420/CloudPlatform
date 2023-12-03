from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class DropNeighborMessageGenerator(StringMessageGenerator):
    ## done for MST from exp controller
    # def __init__(self, in_context,  listIDtosend):
    #     strmsg = COMMAND_DROPBYLATENCY
    #     strmsg = strmsg + str(listIDtosend)
 
    #     StringMessageGenerator.__init__(self, strmsg, in_context)


    ## done for new algo from exp controller
    # def __init__(self, in_context,  close_listPORTtosend, less_close_listPORTtosend, far_listPORTtosend):
    #     strmsg = COMMAND_DROPBYLATENCYNEWALGO
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + CLOSEPORTS
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + str(close_listPORTtosend)
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + LESSCLOSEPORTS
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + str(less_close_listPORTtosend)
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + FARPORTS
    #     strmsg = strmsg + SEMICOLON 
    #     strmsg = strmsg + str(far_listPORTtosend)
 
    #     StringMessageGenerator.__init__(self, strmsg, in_context)

    ##this gives only list ports of nodes to drop    
    def __init__(self, in_context,  nodesPORTStodrop):
        strmsg = COMMAND_DROPBYLATENCYNEWALGO
        strmsg = strmsg + SEMICOLON 
        strmsg = strmsg + NODESPORTSTODROP
        strmsg = strmsg + SEMICOLON 
        strmsg = strmsg + str(nodesPORTStodrop)
         
        StringMessageGenerator.__init__(self, strmsg, in_context)    