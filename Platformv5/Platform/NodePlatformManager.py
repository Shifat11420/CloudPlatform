from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
#from tcp_latency import measure_latency              ##
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
import socket
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
n = 1
m=2

LatencyList = []

#host = 'lo'
# sport = '30000'
# dport = '30003'
#delay = '10ms'



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
                global n,m               
                while (n>0):
                    dbgprint("mgr_on for latency test")
                
                    with self.neighborInfoLock:
                        for nid in self.neighborInfos:
                            vals = self.neighborInfos[nid]
                            dbgprint("my neighbor vals : "+str(vals))
                            dbgprint("Selfid: "+str(self.idval)+" Self_location: "+str(self.location)+" Neighbor , ID : "+str(nid)+ " IP address: "+str(vals[0])+" Port :"+ str(vals[1])+" Location :"+ str(vals[2]))

                        

                            if abs(int(self.location) - int(vals[2]))>= 50 and abs(int(self.location) - int(vals[2]))< 100: 
                                sleeptime = 0.0005
                                dbgprint("yay")
                            elif abs(int(self.location) - int(vals[2]))>= 100 and abs(int(self.location) - int(vals[2]))< 200: 
                                sleeptime = 0.001
                                dbgprint("yaay")
                            elif abs(int(self.location) - int(vals[2]))>= 200 and abs(int(self.location) - int(vals[2]))< 300: 
                                sleeptime = 0.003
                                dbgprint("yaaay")       
                            elif abs(int(self.location) - int(vals[2]))>= 300 and abs(int(self.location) - int(vals[2]))< 400: 
                                sleeptime = 0.005
                                dbgprint("yaaaay")        
                            elif abs(int(self.location) - int(vals[2]))>= 400:
                                sleeptime = 0.007
                                dbgprint("yaaaayyyy")                             
                            else:
                                sleeptime = 0.0
                                dbgprint("nay")

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

                            if nid in NeighborsLatencyDict:
                                NeighborsLatencyDict[nid].append(avgLatency)
                            else:
                                NeighborsLatencyDict.update({nid:[avgLatency]})   
                            #dbgprint("Neighbors Latency Dict  : "+str(NeighborsLatencyDict))
                            
                            NeighborsLatencyList.append(avgLatency)
                            #dbgprint("Neighbors Latency List : "+str(NeighborsLatencyList))
                            #max_latency = max(NeighborsLatencyList)

                          
                            # for key in NeighborsLatencyDict:
                            #     for x in range(len(NeighborsLatencyDict[key])):
                            #         if max_latency == NeighborsLatencyDict[key][x]:
                            #             id_maxlatency = key
                                        #print("key 1 =  ", key)
                                    # if second_highest_latency == NeighborsLatencyDict[key][x]:
                                    #     id_2ndmaxlatency = key
                                    #     print("key 2 =  ", key)    
                        dbgprint("Neighbors Latency Dict  : "+str(NeighborsLatencyDict))
                        dbgprint("Neighbors Latency List : "+str(NeighborsLatencyList))
                                                
                        sorted_NeighborsLatencyList = sorted(NeighborsLatencyList)

                        max_latency = sorted_NeighborsLatencyList[-1]
                        second_highest_latency = sorted_NeighborsLatencyList[-2]
                        third_highest_latency = sorted_NeighborsLatencyList[-3]
                        fourth_highest_latency = sorted_NeighborsLatencyList[-4]
                        fifth_highest_latency = sorted_NeighborsLatencyList[-5]
                        sixth_highest_latency = sorted_NeighborsLatencyList[-6]
                        seventh_highest_latency = sorted_NeighborsLatencyList[-7]
                        eighth_highest_latency = sorted_NeighborsLatencyList[-8]
                        ninth_highest_latency = sorted_NeighborsLatencyList[-9]
                        tenth_highest_latency = sorted_NeighborsLatencyList[-10]
                        if len(self.neighborInfos)>25:
                            eleventh_highest_latency = sorted_NeighborsLatencyList[-11]
                            twelveth_highest_latency = sorted_NeighborsLatencyList[-12]
                            thirteenth_highest_latency = sorted_NeighborsLatencyList[-13]
                            fourteenth_highest_latency = sorted_NeighborsLatencyList[-14]
                            fifteenth_highest_latency = sorted_NeighborsLatencyList[-15]
 
 

                        dbgprint("highest_latency = "+str(max_latency)+" and second_highest_latency = "+str(second_highest_latency))

                        for nid in self.neighborInfos:
                            vals = self.neighborInfos[nid]
                            for key in NeighborsLatencyDict:
                                for x in range(len(NeighborsLatencyDict[key])):
                                    if max_latency == NeighborsLatencyDict[key][x]:
                                        id_maxlatency = key
                                    if second_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_2ndmaxlatency = key
                                    if third_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_3rdmaxlatency = key
                                    if fourth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_4thmaxlatency = key
                                    if fifth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_5thmaxlatency = key   
                                    if sixth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_6thmaxlatency = key
                                    if seventh_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_7thmaxlatency = key
                                    if eighth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_8thmaxlatency = key
                                    if ninth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_9thmaxlatency = key
                                    if tenth_highest_latency == NeighborsLatencyDict[key][x]:
                                        id_10thmaxlatency = key 
                                    if len(self.neighborInfos)>25:      
                                        if eleventh_highest_latency == NeighborsLatencyDict[key][x]:
                                            id_11thmaxlatency = key
                                        if twelveth_highest_latency == NeighborsLatencyDict[key][x]:
                                            id_12thmaxlatency = key
                                        if thirteenth_highest_latency == NeighborsLatencyDict[key][x]:
                                            id_13thmaxlatency = key
                                        if fourteenth_highest_latency == NeighborsLatencyDict[key][x]:
                                            id_14thmaxlatency = key
                                        if fifteenth_highest_latency == NeighborsLatencyDict[key][x]:
                                            id_15thmaxlatency = key                
                                         
                        dbgprint("Maximum communication latency : "+str(max_latency)+" for ID "+str(id_maxlatency))                 
                        print("key 1 =  ", id_maxlatency)            
                        print("key 2 =  ", id_2ndmaxlatency)
                        print("key 3 =  ", id_3rdmaxlatency)
                        print("key 4 =  ", id_4thmaxlatency)
                        print("key 5 =  ", id_5thmaxlatency)   
                        print("key 6 =  ", id_6thmaxlatency)            
                        print("key 7 =  ", id_7thmaxlatency)
                        print("key 8 =  ", id_8thmaxlatency)
                        print("key 9 =  ", id_9thmaxlatency)
                        print("key 10 =  ", id_10thmaxlatency) 
                        if len(self.neighborInfos)>25:      
                            print("key 11 =  ", id_11thmaxlatency)            
                            print("key 12 =  ", id_12thmaxlatency)
                            print("key 13 =  ", id_13thmaxlatency)
                            print("key 14 =  ", id_14thmaxlatency)
                            print("key 15 =  ", id_15thmaxlatency)
                        
                        mgen = LatencyReportNode(self, self.idval, self.IP, self.Port, id_maxlatency, max_latency )
                        dbgprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        expprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)   
                        ############################
                        # if len(self.neighborInfos)>10:                            
                        #     for nid in self.neighborInfos:
                        #         vals = self.neighborInfos[nid]
                        #         if nid == id_maxlatency:
                        #             del self.neighborInfos[nid]
                        #             dbgprint("deleted 1st slow link neighbor id: "+str(nid)+"Port : "+str(vals[1]))
                        #             break
                        #         if nid == id_2ndmaxlatency:
                        #             # del self.neighborInfos[nid]
                        #             # dbgprint("deleted 2nd slow link neighbor id: "+str(nid)+"Port : "+str(vals[1]))
                        #             break
                                    # if abs(int(self.location) - int(vals[2]))> 80 and abs(int(self.location) - int(vals[2]))< 100: 
                                    #     del self.neighborInfos[nid]
                                    #     dbgprint("deleted neighbor id: "+str(nid)+"Port : "+str(vals[1]))
                                    #     break
                        ####################################
                        if len(self.neighborInfos)>25:
                            print("DELETING 15 neighbors")
                            print("deleting key 1 =  ", id_maxlatency, " port : ", self.neighborInfos[id_maxlatency][1])            
                            print("deleting key 2 =  ", id_2ndmaxlatency, " port : ", self.neighborInfos[id_2ndmaxlatency][1])
                            print("deleting key 3 =  ", id_3rdmaxlatency, " port : ", self.neighborInfos[id_3rdmaxlatency][1])
                            print("deleting key 4 =  ", id_4thmaxlatency, " port : ", self.neighborInfos[id_4thmaxlatency][1])
                            print("deleting key 5 =  ", id_5thmaxlatency, " port : ", self.neighborInfos[id_5thmaxlatency][1])
                            print("deleting key 6 =  ", id_6thmaxlatency, " port : ", self.neighborInfos[id_6thmaxlatency][1])            
                            print("deleting key 7 =  ", id_7thmaxlatency, " port : ", self.neighborInfos[id_7thmaxlatency][1])
                            print("deleting key 8 =  ", id_8thmaxlatency, " port : ", self.neighborInfos[id_8thmaxlatency][1])
                            print("deleting key 9 =  ", id_9thmaxlatency, " port : ", self.neighborInfos[id_9thmaxlatency][1])
                            print("deleting key 10 =  ", id_10thmaxlatency, " port : ", self.neighborInfos[id_10thmaxlatency][1])
                            print("deleting key 11 =  ", id_11thmaxlatency, " port : ", self.neighborInfos[id_11thmaxlatency][1])            
                            print("deleting key 12 =  ", id_12thmaxlatency, " port : ", self.neighborInfos[id_12thmaxlatency][1])
                            print("deleting key 13 =  ", id_13thmaxlatency, " port : ", self.neighborInfos[id_13thmaxlatency][1])
                            print("deleting key 14 =  ", id_14thmaxlatency, " port : ", self.neighborInfos[id_14thmaxlatency][1])
                            print("deleting key 15 =  ", id_15thmaxlatency, " port : ", self.neighborInfos[id_15thmaxlatency][1])
                            del self.neighborInfos[id_maxlatency]
                            del self.neighborInfos[id_2ndmaxlatency]
                            del self.neighborInfos[id_3rdmaxlatency]
                            del self.neighborInfos[id_4thmaxlatency]
                            del self.neighborInfos[id_5thmaxlatency]        
                            del self.neighborInfos[id_6thmaxlatency]
                            del self.neighborInfos[id_7thmaxlatency]
                            del self.neighborInfos[id_8thmaxlatency]
                            del self.neighborInfos[id_9thmaxlatency]
                            del self.neighborInfos[id_10thmaxlatency] 
                            del self.neighborInfos[id_11thmaxlatency]
                            del self.neighborInfos[id_12thmaxlatency]
                            del self.neighborInfos[id_13thmaxlatency]
                            del self.neighborInfos[id_14thmaxlatency]
                            del self.neighborInfos[id_15thmaxlatency] 


                        if len(self.neighborInfos)>20 and len(self.neighborInfos)<=25:
                            print("DELETING 10 neighbors")
                            print("deleting key 1 =  ", id_maxlatency, " port : ", self.neighborInfos[id_maxlatency][1])            
                            print("deleting key 2 =  ", id_2ndmaxlatency, " port : ", self.neighborInfos[id_2ndmaxlatency][1])
                            print("deleting key 3 =  ", id_3rdmaxlatency, " port : ", self.neighborInfos[id_3rdmaxlatency][1])
                            print("deleting key 4 =  ", id_4thmaxlatency, " port : ", self.neighborInfos[id_4thmaxlatency][1])
                            print("deleting key 5 =  ", id_5thmaxlatency, " port : ", self.neighborInfos[id_5thmaxlatency][1])
                            print("deleting key 6 =  ", id_6thmaxlatency, " port : ", self.neighborInfos[id_6thmaxlatency][1])            
                            print("deleting key 7 =  ", id_7thmaxlatency, " port : ", self.neighborInfos[id_7thmaxlatency][1])
                            print("deleting key 8 =  ", id_8thmaxlatency, " port : ", self.neighborInfos[id_8thmaxlatency][1])
                            print("deleting key 9 =  ", id_9thmaxlatency, " port : ", self.neighborInfos[id_9thmaxlatency][1])
                            print("deleting key 10 =  ", id_10thmaxlatency, " port : ", self.neighborInfos[id_10thmaxlatency][1])
                            del self.neighborInfos[id_maxlatency]
                            del self.neighborInfos[id_2ndmaxlatency]
                            del self.neighborInfos[id_3rdmaxlatency]
                            del self.neighborInfos[id_4thmaxlatency]
                            del self.neighborInfos[id_5thmaxlatency]        
                            del self.neighborInfos[id_6thmaxlatency]
                            del self.neighborInfos[id_7thmaxlatency]
                            del self.neighborInfos[id_8thmaxlatency]
                            del self.neighborInfos[id_9thmaxlatency]
                            del self.neighborInfos[id_10thmaxlatency]     


                        if len(self.neighborInfos)>15 and len(self.neighborInfos)<=20:
                            print("DELETING 5 neighbors")
                            print("deleting key 1 =  ", id_maxlatency, " port : ", self.neighborInfos[id_maxlatency][1])            
                            print("deleting key 2 =  ", id_2ndmaxlatency, " port : ", self.neighborInfos[id_2ndmaxlatency][1])
                            print("deleting key 3 =  ", id_3rdmaxlatency, " port : ", self.neighborInfos[id_3rdmaxlatency][1])
                            print("deleting key 4 =  ", id_4thmaxlatency, " port : ", self.neighborInfos[id_4thmaxlatency][1])
                            print("deleting key 5 =  ", id_5thmaxlatency, " port : ", self.neighborInfos[id_5thmaxlatency][1])    
                            del self.neighborInfos[id_maxlatency]
                            del self.neighborInfos[id_2ndmaxlatency]
                            del self.neighborInfos[id_3rdmaxlatency]
                            del self.neighborInfos[id_4thmaxlatency]
                            del self.neighborInfos[id_5thmaxlatency]

                        n=0
                                                
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
