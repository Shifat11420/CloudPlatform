from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *

class ReceiveExpInfo(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        ip = ""
        port = 0
        for val in vals:
            if(val == STR_IP):
                ip = (vals[i])
            if(val == STR_PORT):
                port = int(vals[i])
            i = i + 1
        self.context.AddExpMachine((ip,port))

class ReceiveExpNodeReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(",")
        i = 0
        exp_id = None
        exp_ip = None
        exp_port = 0
        for val in vals:
            if(val == STR_IP):
                exp_ip = vals[i+1]
            if(val == STR_PORT):
                exp_port = int(vals[i+1])
            if(val == STR_ID):
                exp_id = vals[i+1]
            i = i + 1
        self.context.AddExpNode(exp_id, exp_ip, exp_port)

