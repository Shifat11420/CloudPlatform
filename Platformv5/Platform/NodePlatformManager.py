from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
#from tcp_latency import measure_latency              ##
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.MessageRepeat import MsgMonitor
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from CommandMessageGenerators.LatencyReportGenerator import LatencyReportNode
from CommandMessageGenerators.LatencyMessageGenerator import LatencyMessageGenerator
from Utilities.Const import *
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import expprint, SetOutputFolder
import threading
import time
import socket
import datetime
import sys
from PlatformManager import PlatformManager
from DockerManagers.NasManager import GetRValueFromNAS
import ast


DEFAULTBENCHTIME = 400
NeighborsLatencyDict = {}
NeighborsLatencyList = []
avgLatencyList = []
n = 1
LatencyList = []
portlist = []
all_LatencyList = []



class NodePlatformManager(PlatformManager):
    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, location, ManagerOn=True):
        PlatformManager.__init__(self, in_my_IP, in_my_Port, location)
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
        self.location = location

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
                        #########
                        
                        ###############

        elif(self.ExecContainer.IsFinished()):
            dbgprint("ExecFinished:"+str(self.ExecContainer.idstr))
            self.SendExecFinished()
            self.workhistory[self.ExecContainer.idstr] = (datetime.datetime.now() - self.workstarts[self.ExecContainer.idstr]).total_seconds()
            self.ExecContainer = None
    
    def ReportToExp(self):
        mgen = ReceiveExpNode(self, self.idval, self.IP, self.Port, self.location)           ##
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
                global n              
                while (n>0):
                    dbgprint("mgr_on for latency test")
                
                    with self.neighborInfoLock:
                        for nid in self.neighborInfos:
                            vals = self.neighborInfos[nid]
                            dbgprint("my neighbor vals : "+str(vals))
                            dbgprint("Selfid: "+str(self.idval)+" Self_location: "+str(self.location)+" Neighbor , ID : "+str(nid)+ " IP address: "+str(vals[0])+" Port :"+ str(vals[1])+" Location :"+ str(vals[2]))
                            portlist.append(int(vals[1]))
                        

                            if abs(int(self.location) - int(vals[2]))> 50 and abs(int(self.location) - int(vals[2]))<= 100: 
                                sleeptime = 0.0005   ##0.5ms
                            elif abs(int(self.location) - int(vals[2]))> 100 and abs(int(self.location) - int(vals[2]))<= 200: 
                                sleeptime = 0.001    ##1ms
                            elif abs(int(self.location) - int(vals[2]))> 200 and abs(int(self.location) - int(vals[2]))<= 300: 
                                sleeptime = 0.003     ##3ms      
                            elif abs(int(self.location) - int(vals[2]))> 300 and abs(int(self.location) - int(vals[2]))<= 400: 
                                sleeptime = 0.005     ##10ms              
                            elif abs(int(self.location) - int(vals[2]))> 400:
                                sleeptime = 0.007    ##14ms                       
                            else:
                                sleeptime = 0.0

                          

                            host = vals[0] 
                            port = vals[1] 
                            #sleeptime = 0.0
                            
                            try:
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.settimeout(5)

                            except socket.error as err:  
                                print ("socket creation failed with error %s" %(err))
                                
                            start_time = time.time() *1000   #converted from seconds to milliseconds
                            
                            time.sleep(sleeptime)

                            try:
                                s.connect((host, int(port)))
                                s.shutdown(socket.SHUT_RD)
                            except socket.timeout:
                                pass
                            except OSError:
                                pass
                             
                            s.sendall(b'1')
                            data = s.recv(1) 
                            time.sleep(sleeptime)

                            end_time = time.time() *1000  #converted from seconds to milliseconds

                            rtt = end_time-start_time    

                            dbgprint("RTT :"+str(rtt))
                            summ = 0.0
                            for i in range(3):
                                LatencyList.append(rtt)
                                summ = summ + rtt
                            #print("list : ", LatencyList)    
                            avgLatency = summ/3
                            #print("avg : ", avg)
                            
                       
                            dbgprint("Average communication latency of neighbor : ID : "+str(nid)+" IP : "+str(vals[0])+" PORT : "+str(vals[1])+" LOCATION : "+str(vals[2])+" is "+str(avgLatency))

                            if vals[1] in NeighborsLatencyDict:
                                NeighborsLatencyDict[vals[1]].append(avgLatency)
                            else:
                                NeighborsLatencyDict.update({vals[1]:[avgLatency]})                           
                            NeighborsLatencyList.append(avgLatency)

                            ##insert is a function to put an element into a dictionary to a specific position
                            insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] + list(obj.items()) + list(_dict.items())[pos:])}
                            NeighborsLatencyDictall = insert(NeighborsLatencyDict, {self.Port:[0.0]},0)
                              
                             
                            mgen = LatencyMessageGenerator(self, self.idval, self.IP, self.Port, avgLatency)         #*
                            dbgprint("Sending Latency info to "+str(vals[0])+":"+str(vals[1]))
                            self.msgmon.sendGen(mgen, vals[0], vals[1]) #*

                        dbgprint("Neighbors Latency Dict  : "+str(NeighborsLatencyDict))
                        dbgprint("Neighbors Latency List : "+str(NeighborsLatencyList))
                        dbgprint("Neighbors Latency Dict All : "+str(NeighborsLatencyDictall))
                        
                        # #NeighborsLatencyDict[self.idval] = [0.0]
                        

                        # #######           new code for exp controller algo starts              ######

                        portlist.append(int(self.Port))
                        print("list of ports : ", portlist)

                        NeighborsLatencyList.append(0.0)    
                        print("all_LatencyList : ",NeighborsLatencyList)
                        
                        all_LatencyList = [x for _,x in sorted(zip(portlist,NeighborsLatencyList))]

                        dbgprint("All latency list : "+str(all_LatencyList))

                        # #######          new code for exp controller algo ends        ######


                        #max_latency = max(NeighborsLatencyList)
                        max_latency = max(NeighborsLatencyList)
                        
                        sorted_NeighborsLatencyList = []
                        for key in NeighborsLatencyDict:
                            for x in range(len(NeighborsLatencyDict[key])):
                                if max_latency == NeighborsLatencyDict[key][x]:
                                    id_maxlatency = key
                                                
                        sorted_NeighborsLatencyList = sorted(NeighborsLatencyList)
                        print("Sorted Neighbors Latency List : ", sorted_NeighborsLatencyList)
                             

                       
#?
                        ######### sending latency information to experiment controller ############# 
                        dbgprint("Maximum communication latency : "+str(max_latency)+" for PORT "+str(id_maxlatency))                 
                                           
                        mgen = LatencyReportNode(self, self.idval, self.IP, self.Port, id_maxlatency, max_latency, NeighborsLatencyDictall)#,NeighborsLatencyList )
                        dbgprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        expprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)   
#?                                                                    
                        
                self.NodeManagerRun()
            else:
                if(not (self.unpause_datetime is None)):
                    if(datetime.datetime.now() > self.unpause_datetime):
                        self.managerOn = True

#?

    def DropNeighborbyLatency(self, nodesPORTStodrop):

      
         # ############## another ALGORITHM implementation  ##############   
        # ## ast.literal_eval transforms string representation of a list to a list
        nodesPORTStodrop = ast.literal_eval(nodesPORTStodrop)
        #dbgprint("From ID: "+str(self.idval)+" port : "+str(self.Port)+" received list of nodes ports to drop : "+str(nodesPORTStodrop))
 
        with self.neighborInfoLock:
            for nid in list(self.neighborInfos):
                vals = self.neighborInfos[nid] 
 
                for i in range(len(nodesPORTStodrop)):
                    if nodesPORTStodrop[i] == vals[1]:
                        # dbgprint("Deleting neighbor port : "+str(vals[1]))
                        # del self.neighborInfos[nid]
                        pass

    # #      #  # ############## another ALGORITHM implementation ends ##############            
#?     

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

    def AddNeighbor(self, n_IP, n_Port, n_loc, n_ID):
        dbgprint("Adding Neighbor:ID"+str(n_ID)+":Port:"+str(n_Port)+" :Location: "+str(n_loc))
        with self.neighborInfoLock:
            tpl = (n_IP, n_Port, n_loc)
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
