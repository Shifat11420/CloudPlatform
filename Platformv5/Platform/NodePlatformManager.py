from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from tcp_latency import measure_latency              ##
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.MessageRepeat import MsgMonitor
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from CommandMessageGenerators.LatencyReportGenerator import LatencyReportNode
from Utilities.Const import *
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import expprint, SetOutputFolder
import threading
import time
import datetime
import sys
from PlatformManager import PlatformManager
from DockerManagers.NasManager import GetRValueFromNAS


DEFAULTBENCHTIME = 400
NeighborsLatencyDict = {}
NeighborsLatencyList = []
timeout = 10
runs = 5
avgLatencyList = []



# host = 'lo'
# sport = '20000'
# dport = '20003'
# delay = '1000ms'



class NodePlatformManager(PlatformManager):
    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn=True):
        PlatformManager.__init__(self, in_my_IP, in_my_Port)
        self.managerOn = ManagerOn
        self.neighborInfos = {}
        self.workqueue = []
        self.Exp_IP = exp_ip
        self.Exp_Port = exp_port
        self.neighborInfoLock = threading.Lock()
        self.incomingqueue = {}
        self.workqueuelock = threading.Lock()
        self.incomingqueuelock = threading.Lock()
        self.ExecContainer = None
        self.completedworklock = threading.Lock()
        self.completedwork = []
        self.unpause_datetime = None
        self.benchresults = ""
        self.benchdate = datetime.datetime.now()
        self.benchresettime = DEFAULTBENCHTIME
        self.workhistory = {}
        self.workstarts = {}

    def StartAll(self):
        #from Utilities.Const import *                 ##
        PlatformManager.StartAll(self)
        dbgprint("starting filewaiter")
        self.fileWaitThread = threading.Thread(target=self.WaitForFiles)
        self.fileWaitThread.start()

    def WaitForFiles(self):
        #from Utilities.Const import *                      ##
        while(True):
            dbgprint("In WaitForFiles")
            time.sleep(5)
            if(self.terminate):
                dbgprint("WaitForFiles OVER")
                break
            with self.incomingqueuelock:
                lkeys = list(self.incomingqueue.keys())
                dbgprint("Before incqueue")
                for key in lkeys:
                    cm = self.incomingqueue[key]
                    allfilesfound = True
                    for f in cm.cont_files:
                        dbgprint("Does file:"+f+" exist?")
                        fileexists = os.path.exists(f)
                        if not fileexists:
                            dbgprint("No")
                            allfilesfound = False
                            break
                    if allfilesfound:
                        with self.workqueuelock:
                            dbgprint("selfid:"+str(self.idval)+"Moving from queue key:"+str(key)+":")
                            self.workqueue.append(cm)
                            del self.incomingqueue[key]
                        self.RespondToNewWork()
                self.filewaitextra()

    def filewaitextra(self):
        pass
    
    def RespondToNewWork(self):
        pass

    def GetBench(self):
        if(len(self.workhistory) == 0):
            return DEFAULTJOBTIME
        else:
            sumv = 0
            for key in self.workhistory:
                sumv = sumv + self.workhistory[key]
            return sumv/float(len(self.workhistory))
    
    def oldGetBench(self):
        getNewBench = False
        if(self.benchresults == ""):
            getNewBench = True
        else:
            tdiff = (datetime.datetime.now() - self.benchdate).total_seconds()
            if(tdiff > self.benchresettime):
                getNewBench = True
        if(getNewBench):
            val = GetRValueFromNAS()
            dbgprint("BenchResults:"+str(val)+":")
            expprint("CalcBench:"+str(val)+":")
            try:
                self.benchresults = float(val)
            except ValueError:
                self.benchresults = 0
        return self.benchresults

    def GetQueueLen(self):
        return len(self.workqueue)

    def AddCompletedWorkFile(self, idstr, filename):
        expprint("WORKDONE:"+idstr+" TIME:"+str(datetime.datetime.now())+"FIN")
        with self.completedworklock:
            self.completedwork.append(filename)

    def GetWorkToSend(self):
        with self.workqueuelock:
            if(len(self.workqueue) < 1):
                return None
            return self.workqueue.pop(0)

    def SetNeighborBench(self, in_nodeid, in_nodebench):
        pass
        
    def SendExecFinished(self):
        dbgprint("Send Executing Container Finished")
        if(self.ExecContainer != None):
            resp = self.ExecContainer.PackageResponse()
            toip = self.ExecContainer.work_source_ip
            toport = self.ExecContainer.work_source_port
            self.msgmon.sendGen(resp, toip, toport)

    def NoWorkToDo(self):
        pass

    def IsThereWorkToDo(self):
        if(len(self.workqueue) == 0):
            return False
        return True

    def GetWorkToDo(self):
        
        return self.workqueue.pop(0)
            
    def NodeManagerRun(self):
        dbgprint("NodeManagerRun")
        if(self.ExecContainer == None):
            dbgprint("execcont = None")
            with self.workqueuelock:
                if(not self.IsThereWorkToDo()):
                    dbgprint("nothing in queue")
                    self.NoWorkToDo()
                    pass
                else:
                    dbgprint("queuelen:" + str(len(self.workqueue)))
                    self.ExecContainer = self.GetWorkToDo()
                    if(not (self.ExecContainer is None)):
                        dbgprint("Starting Container selfid:"+str(self.idval))
                        expprint("Starting Container selfid:"+str(self.idval)+" ID:"+str(self.ExecContainer.idstr))
                        self.ExecContainer.Start()
                        dbgprint("Container Start Sent")
                        self.workstarts[self.ExecContainer.idstr] = datetime.datetime.now()
        elif(self.ExecContainer.IsFinished()):
            dbgprint("ExecFinished:"+str(self.ExecContainer.idstr))
            self.SendExecFinished()
            self.workhistory[self.ExecContainer.idstr] = (datetime.datetime.now() - self.workstarts[self.ExecContainer.idstr]).total_seconds()
            self.ExecContainer = None
    
    def ReportToExp(self):
        mgen = ReceiveExpNode(self, self.idval, self.IP, self.Port)
        dbgprint("Sending To Exp at:"+str(self.Exp_IP)+":"+str(self.Exp_Port))
        expprint("Sending To Exp at:"+str(self.Exp_IP)+":"+str(self.Exp_Port))
        self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)

    def ManagerThreadRun(self):
        self.terminate = False
        time.sleep(1)
        self.ReportToExp()
        #n=1

        
        while(True):
            time.sleep(MANAGERCHECKTIME)
            dbgprint("npm_mtr")
            dbgprint("unpause_time:"+str(self.unpause_datetime))
            
            if(self.terminate):
                self.SafeStopServer()
                break
            if(self.managerOn):  
                dbgprint("mgr_on")

                #######################################                
                #while (n>0):
                dbgprint("mgr_on for latency test")
            
                with self.neighborInfoLock:
                    for nid in self.neighborInfos:
                        vals = self.neighborInfos[nid]
                        dbgprint("Selfid: "+str(self.idval)+" Neighbor , ID : "+str(nid)+ " IP address: "+str(vals[0])+" Port :"+ str(vals[1]))

                        # dbgprint("locport b4 : "+str(vals[1]))
                        # if vals[1] == 20000:
                        #     dbgprint("locport after : "+str(vals[1]))
                        #     os.system('sudo tc qdisc add dev {0} root handle 1: prio priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'.format(host, vals[1], dport, delay))
                        #     os.system('sudo tc qdisc add dev {0} parent 1:2 handle 20: netem delay {3}'.format(host, vals[1], dport, delay))
                        #     os.system('sudo tc filter add dev {0} parent 1:0 protocol ip u32 match ip sport {1} 0xffff flowid 1:2'.format(host, vals[1], dport, delay))
                        #     os.system('sudo tc filter add dev {0} parent 1:0 protocol ip u32 match ip dport {2} 0xffff flowid 1:2'.format(host, vals[1], dport, delay))

                        LatencyList = measure_latency(vals[0], vals[1], runs, timeout)
                        summ = 0.0
                        for i in range(len(LatencyList)):
                            summ = summ + LatencyList[i]
                        avgLatency = summ/runs                        
                        dbgprint("Average communication latency of neighbor : ID : "+str(nid)+" IP : "+str(vals[0])+" PORT : "+str(vals[1])+" is "+str(avgLatency))

                        if nid in NeighborsLatencyDict:
                            NeighborsLatencyDict[nid].append(avgLatency)
                        else:
                            NeighborsLatencyDict.update({nid:[avgLatency]})   
                        dbgprint("Neighbors Latency Dict  : "+str(NeighborsLatencyDict))
                        
                        NeighborsLatencyList.append(avgLatency)
                        dbgprint("Neighbors Latency List : "+str(NeighborsLatencyList))
                        max_latency = max(NeighborsLatencyList)

                        for key in NeighborsLatencyDict:
                            for x in range(len(NeighborsLatencyDict[key])):
                                if max_latency == NeighborsLatencyDict[key][x]:
                                    id_maxlatency = key
                                    print("key  =  ", key)
                        
                    dbgprint("Maximum communication latency : "+str(max_latency)+" for ID "+str(id_maxlatency))
                    
                    mgen = LatencyReportNode(self, self.idval, self.IP, self.Port, id_maxlatency, max_latency )
                    dbgprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                    expprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                    self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)   
                        #n=0                        
                    ##############################
                    ###############
                        
                self.NodeManagerRun()
            else:
                if(not (self.unpause_datetime is None)):
                    if(datetime.datetime.now() > self.unpause_datetime):
                        self.managerOn = True

    def Pause(self):
        self.managerOn = False
    def UnPause(self):
        self.managerOn = True
    def SetUnpauseDatetime(self, newdatetime):
        dbgprint("Set Datetime to:" + str(newdatetime))
        self.unpause_datetime = newdatetime

    def AddIncomingWork(self, cont_mgr):
        with self.incomingqueuelock:
            dbgprint("Adding to incque key, selfid:"+str(self.idval)+" toadd:"+str(cont_mgr.idstr)+":")
            self.incomingqueue[cont_mgr.idstr] = cont_mgr

    #def MoveWorkToRealQueue(self, id_to_move):
    #    while(not(id_to_move in self.incomingqueue)):
    #        dbgprint("KLUDGEWAIT selfid:"+str(self.idval)+" id:"+str(id_to_move)+" not found in len:"+str(len(self.incomingqueue)))
    #        time.sleep(4)
    #    with self.incomingqueuelock:
    #        with self.workqueuelock:
    #            dbgprint("selfid:"+str(self.idval)+"Moving from queue key:"+str(id_to_move)+":")
    #            self.workqueue.append(self.incomingqueue[id_to_move])
    #            del self.incomingqueue[id_to_move]

    def AddNeighbor(self, n_IP, n_Port, n_ID):
        dbgprint("Adding Neighbor:ID"+str(n_ID)+":Port:"+str(n_Port))
        with self.neighborInfoLock:
            tpl = (n_IP, n_Port)
            self.neighborInfos[n_ID] = tpl

    def DeleteNeighbor(self, n_IP, n_Port, n_ID):
        with self.neighborInfoLock:
            del self.neighborInfos[n_ID]


'''
if __name__ == "__main__":
    
    argsFIP = ArgFIP(sys.argv)
    source_ip = argsFIP[DICT_SOURCE_IP]
    port = int(argsFIP[DICT_SOURCE_PORT])
    SetOutputFolder(argsFIP[DICT_FOLDER])
    exp_ip = argsFIP[DICT_EXP_IP]
    exp_port = argsFIP[DICT_EXP_PORT]
    
    pm = NodePlatformManager(source_ip, port, exp_ip, exp_port)
    pm.StartAll()
'''
