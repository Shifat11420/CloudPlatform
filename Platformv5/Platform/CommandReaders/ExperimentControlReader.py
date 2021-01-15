from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from Utilities.Const import *

class ReceiveExpInfo(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA.encode('utf-8'))
        i = 1
        ip = ""
        port = 0
        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                ip = (vals[i].decode('utf-8'))
            if(val == STR_PORT):
                port = int(vals[i].decode('utf-8'))
            i = i + 1
        self.context.AddExpMachine((ip,port))

class ReceiveExpNodeReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(",".encode('utf-8'))
        i = 0
        exp_id = None
        exp_ip = None
        exp_port = 0
        for val in vals:
            if(val.decode('utf-8') == STR_IP):
                exp_ip = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == STR_PORT):
                exp_port = int(vals[i+1].decode('utf-8'))
            if(val.decode('utf-8') == STR_ID):
                exp_id = vals[i+1].decode('utf-8')
            i = i + 1
        self.context.AddExpNode(exp_id, exp_ip, exp_port)

