from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.MessageRepeat import MsgMonitor
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from CommandMessageGenerators.LatencyReportGenerator import LatencyReportNode
from CommandMessageGenerators.PauseUnpauseMessageGenerator import TimeUnpauseMessageGenerator
from ExpDefinitions.ExpFactory import BuildExpDef
from Utilities.Const import *
from Utilities.Location import Location
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import SetOutputFolder, expprint
from datetime import datetime, timedelta
import threading
import time
import sys
from PlatformManager import PlatformManager

class ExpPlatformManager(PlatformManager):
    def __init__(self, in_my_IP, in_my_Port, in_expdef, ManagerOn=True):
        PlatformManager.__init__(self, in_my_IP, in_my_Port)
        self.managerOn = ManagerOn
        self.expnodes = {}
        self.expnodeslock = threading.Lock()
        self.expdef = in_expdef
        self.exp_nodes_reported = False
        self.starttime =None
        self.expstarted = False
        self.logsgathered = False
        self.termsent = False
        dbgprint("Created Exp PM")

    def ExpManagerRun(self):
        #from Utilities.Const import *                               ##
        from datetime import datetime, timedelta
        dbgprint("EMR: " + str(self.exp_nodes_reported) + ":" + str(self.expdef is None))
        if(self.exp_nodes_reported or self.expdef is None):
            pass
        else:
            with self.expnodeslock:
                dbgprint("  "+str(len(self.expnodes)) + ":" + str(self.expdef.node_count))
                if(len(self.expnodes) >= self.expdef.node_count):
                    self.exp_nodes_reported = True
            if(self.exp_nodes_reported):
                self.startExperiment()
                self.starttime = datetime.now()
                self.expstarted = True

    def ManagerThreadRun(self):
        import time
        from datetime import datetime, timedelta
        #from Utilities.Const import *                     ##
        dbgprint("good way")
        self.terminate = False
        time.sleep(1)
        while(True):
            time.sleep(MANAGERCHECKTIME)
            if(self.termsent):
                dbgprint("Checking term")
                now = datetime.now()
                td = now - self.starttime
                if(td.total_seconds() > TERMTIME):
                    self.terminate = True
                    self.SafeStopServer()
                    self.dumpLogToStdOut()
                    break
            elif(self.logsgathered):
                dbgprint("checking log in")
                now = datetime.now()
                td  = now - self.starttime
                if(td.total_seconds() > LOGTIME):
                    self.compilelogs()
                    self.TerminateAll()
                    self.termsent = True
                    self.starttime = now
            elif(self.expstarted):
                dbgprint("checking exp")
                now = datetime.now()
                td = now - self.starttime
                dbgprint("current " + str(td.total_seconds()))
                dbgprint("bound   " + str(self.expdef.time))
                if(td.total_seconds() > self.expdef.time):
                    #self.GatherLogs()
                    self.logsgathered = True
                    self.starttime = now
            else:
                self.ExpManagerRun()

    def AddExpNode(self, newid, newip, newport):
        #from Utilities.Const import *                   ##
        from Utilities.Location import Location
        with self.expnodeslock:
            self.expnodes[newid] =Location(newip, newport)

    def LatencyReportExpNode(self, node_id, node_ip, node_port, slowest_id, max_latency):   
        listoflatencies = []
        with self.expnodeslock:
            for key in self.expnodes:
                loc = self.expnodes[key]             
                #dbgprint("Sending a command to remove slowest node:"+str(loc))                  
                if key == slowest_id:
                    listoflatencies.append(max_latency)
                    dbgprint("Delete node, ID : "+str(key)+" IP : "+str(loc.ip)+" Port : "+str(loc.port)) 
            dbgprint("List of latencies : "+str(listoflatencies))  
            listoflatencies = [x for x in listoflatencies]
            listoflatencies.sort(reverse=True)
            sortedlist = [x for x in listoflatencies]  
            dbgprint("Sorted list of latencies : "+str(listoflatencies))       


    def startExperiment(self):
        #from Utilities.Const import *                     ##
        from datetime import datetime, timedelta
        from Utilities.FileUtil import SetOutputFolder, expprint
        from CommandMessageGenerators.PauseUnpauseMessageGenerator import TimeUnpauseMessageGenerator
        with self.expnodeslock:
            self.expdef.startExperiment(self, self.expnodes)
            dbgprint("EPM:before sleep")
            time.sleep(30)
            dbgprint("EPM:After Sleep")
            dtstart = datetime.now()+timedelta(0,20)                             
            expprint("EXPSTARTTIME!!:"+str(dtstart))
            for key in self.expnodes:
                loc = self.expnodes[key]
                upmg = TimeUnpauseMessageGenerator(self, dtstart)
                self.msgmon.sendGen(upmg, loc.ip, loc.port)

    def GatherLogs(self):
        with self.expnodeslock:
            itval = 0
            for key in self.expnodes:
                dbgprint("ival!"+str(itval))
                itval = itval + 1
                loc = self.expnodes[key]
                self.msgmon.sendCommand(COMMAND_SENDLOGS, self, loc.ip, loc.port)
                time.sleep(10)
            #fact = MakeGenFact(COMMAND_SENDLOGS, self)
            #reactor.connectTCP(loc.ip, loc.port, fact)

    def TerminateAll(self):
        #from Utilities.Const import *                         ##
        #reactor.callFromThread(self.TerminateAllIRT)
    
        with self.expnodeslock:
            for key in self.expnodes:
                loc = self.expnodes[key]
                dbgprint("Sending Terminate:"+str(loc))
                self.msgmon.sendCommand(COMMAND_ENDSERVER, self, loc.ip, loc.port)

        
if __name__ == "__main__":
    global DEBUG
    print (sys.argv)
    argsFIP = ArgFIP(sys.argv)
    source_ip = argsFIP.get(DICT_SOURCE_IP)               ##
    port = int(argsFIP.get(DICT_SOURCE_PORT))             ##
    SetOutputFolder(argsFIP.get(DICT_FOLDER))             ##
    #expfilename = argsFIP[DICT_EXP_FILE]
    expfilename = argsFIP.get(DICT_EXP_FILE)              ##
    dbg = argsFIP.get(DICT_DEBUG)                         ##
    expindex = argsFIP.get(DICT_EXP_INDEX)                ##
    print (argsFIP)
    if(dbg == "True"):
        setDbg(True)
    else:
        setDbg(False)
    print ("Debug is "+str(DEBUG))                     ##
    expdef = BuildExpDef(expfilename, expindex)
    if(expdef is None):
        dbgprint("EXP Busted")
    else:
        pm = ExpPlatformManager(source_ip, port, expdef)
        pm.StartAll()

    
