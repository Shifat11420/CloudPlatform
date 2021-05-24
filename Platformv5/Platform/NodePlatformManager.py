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
                        

                            if abs(int(self.location) - int(vals[2]))>= 50 and abs(int(self.location) - int(vals[2]))< 100: 
                                sleeptime = 0.0005*10
                                dbgprint("yay")
                            elif abs(int(self.location) - int(vals[2]))>= 100 and abs(int(self.location) - int(vals[2]))< 200: 
                                sleeptime = 0.001*10
                                dbgprint("yaay")
                            elif abs(int(self.location) - int(vals[2]))>= 200 and abs(int(self.location) - int(vals[2]))< 300: 
                                sleeptime = 0.003*10
                                dbgprint("yaaay")       
                            elif abs(int(self.location) - int(vals[2]))>= 300 and abs(int(self.location) - int(vals[2]))< 400: 
                                sleeptime = 0.005*10
                                dbgprint("yaaaay")        
                            elif abs(int(self.location) - int(vals[2]))>= 400:
                                sleeptime = 0.007*10
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
                            NeighborsLatencyList.append(avgLatency)
                              
                        dbgprint("Neighbors Latency Dict  : "+str(NeighborsLatencyDict))
                        dbgprint("Neighbors Latency List : "+str(NeighborsLatencyList))

                        # #######           new code for exp controller algo starts              ######

                        # portlist.append(int(self.Port))
                        # print("list of ports : ", portlist)

                        # NeighborsLatencyList.append(0.0)    
                        # print("all_LatencyList : ",NeighborsLatencyList)
                        
                        # all_LatencyList = [x for _,x in sorted(zip(portlist,NeighborsLatencyList))]

                        # dbgprint("All latency list : "+str(all_LatencyList))

                        # #######          new code for exp controller algo ends        ######


                        #max_latency = max(NeighborsLatencyList)
                        max_latency = max(NeighborsLatencyList)

                        for key in NeighborsLatencyDict:
                            for x in range(len(NeighborsLatencyDict[key])):
                                if max_latency == NeighborsLatencyDict[key][x]:
                                    id_maxlatency = key
                                                
                        sorted_NeighborsLatencyList = sorted(NeighborsLatencyList)
                        print("Sorted Neighbors Latency List : ", sorted_NeighborsLatencyList)

#########take out comments
                        # d={}        #dict for latency
                        # c={}        #dict  for id  
                        # for i in range(1,len( self.neighborInfos)+1):
                        #     #if len( self.neighborInfos)>=i:
                        #     d["the{0}th_highest_latency".format(i)] = sorted_NeighborsLatencyList[-i]
                        #     print(d)
                        #     dbgprint("the"+str(i)+"th_highest_latency is "+str(d["the{0}th_highest_latency".format(i)]))
                        # #dbgprint("the"+str(len( self.neighborInfos))+"th_highest_latency is "+str(d["the{0}th_highest_latency".format(len( self.neighborInfos))]))        
                                
                        #     for nid in  self.neighborInfos:
                        #         vals =  self.neighborInfos[nid]
                        #         for key in NeighborsLatencyDict:
                        #             for x in range(len(NeighborsLatencyDict[key])):
                        #                 if d["the{0}th_highest_latency".format(i)] == NeighborsLatencyDict[key][x]:
                        #                     c["id_{0}thmaxlatency".format(i)] = key
                        # for i in range(1,len( self.neighborInfos)+1):  #range(len( self.neighborInfos)):   
                        #     #if len( self.neighborInfos)>=i:                     
                        #     dbgprint("the"+str(i)+"th id is "+str(c["id_{0}thmaxlatency".format(i)]))  #i+1 to i

                        # dbgprint("highest_latency = "+str(d["the{0}th_highest_latency".format(1)])+ " and "+str(len( self.neighborInfos))+ "th_highest_latency = "+str( d["the{0}th_highest_latency".format(len( self.neighborInfos))]))
                        # max_latency = d["the{0}th_highest_latency".format(1)]
                        # id_maxlatency = c["id_{0}thmaxlatency".format(i)]
#########take out comments                       
                        drop_nbr_size = 0                       

                        ###########
                        # if len( self.neighborInfos)>13 and len( self.neighborInfos)<=18:
                        #     drop_nbr_size = 2
                        # if len( self.neighborInfos)>18 and len( self.neighborInfos)<=23:  
                        #     drop_nbr_size = 4  
                        # if len( self.neighborInfos)>23 and len( self.neighborInfos)<=28:
                        #     drop_nbr_size = 6  
                        # if len( self.neighborInfos)>28 and len( self.neighborInfos)<=33:
                        #     drop_nbr_size = 9
                        # if len( self.neighborInfos)>33 and len( self.neighborInfos)<=38:  
                        #     drop_nbr_size = 15    #12  
                        # if len( self.neighborInfos)>38 and len( self.neighborInfos)<=42:
                        #     drop_nbr_size = 18   #15      
                        # if len( self.neighborInfos)>42 and len( self.neighborInfos)<=45:
                        #     drop_nbr_size = 18   
                           
                        # ########################   local test only   ######################################
                        # if len( self.neighborInfos)>=5 and len( self.neighborInfos)<9:          
                        #     drop_nbr_size = 2  
                        # print("self location = ", self.location, "neighbor location = ", vals[2])      
                        # if (self.location == 10 and vals[2] ==51) or (self.location == 51 and vals[2] == 10):
                        #     pass
                        # if (self.location == 51 and vals[2] ==69) or (self.location == 69 and vals[2] == 51):
                        #     pass                                     
                        # if (self.location == 69 and vals[2] ==101) or (self.location == 101 and vals[2] == 69):
                        #     pass
                        # if (self.location == 101 and vals[2] ==149) or (self.location == 149 and vals[2] == 101):
                        #     pass
                        # if (self.location == 149 and vals[2] ==230) or (self.location == 230 and vals[2] == 149):
                        #     pass
                        # if (self.location == 230 and vals[2] ==301) or (self.location == 301 and vals[2] == 230):
                        #     pass
                        # else:
                        #     del self.neighborInfos[nid]
                        #     print("self port : ", self.Port, "neighbor deleted, port : ", vals[1])
                        # #################################################
                        
                        ########################   full graph test only   ######################################
                        # if (self.Port==11000) or (self.Port==12000) or (self.Port==13000) or (self.Port==14000) or (self.Port==15000) or (self.Port==16000) or (self.Port==17000) or(self.Port==18000) or (self.Port==19000) or ( self.Port==11100):                         
                        #     drop_nbr_size = 0
                        # else:
                        #     drop_nbr_size = 32    
                         

                        ###################################   DROP NEIGHBORS #####################
                        # print("DELETING slowest ",drop_nbr_size, " neighbors")
                        # for k in range(drop_nbr_size):
                        #     try:
                        #         if self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 11000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 12000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 13000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 14000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 15000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 16000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 17000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 18000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 19000 or self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1] == 11100 :
                        #             pass
                        #         else: 
                        #             dbgprint("deleting key "+str(k+1)+ " =  "+str( c["id_{0}thmaxlatency".format(k+1)])+" port : "+str(self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]][1]))           
                        #             del  self.neighborInfos[c["id_{0}thmaxlatency".format(k+1)]]
                        #     except KeyError:
                        #         print("neighbor is already droped")     
                        # # #######################################

                         
                        dbgprint("Maximum communication latency : "+str(max_latency)+" for ID "+str(id_maxlatency))                 
                                           
                        mgen = LatencyReportNode(self, self.idval, self.IP, self.Port, id_maxlatency, max_latency )
                        dbgprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        expprint("Sending Latency Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                        self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)   
                       
                        
                       

                        n=0
                        # # # ########################  delete neighbors local test only   ######################################
   
                        # for nid in list(self.neighborInfos):
                        #     vals = self.neighborInfos[nid] 
                        #     print("self location = ", self.location, "neighbor location = ", vals[2])      
                        #     if (int(self.Port) == 11100 and int(vals[1]) ==11105) or (int(self.Port) == 11105 and int(vals[1]) == 11100):
                        #         pass
                        #     elif (int(self.Port) == 11105 and int(vals[1]) ==11106) or (int(self.Port)== 11106 and int(vals[1]) == 11105):
                        #         pass                                     
                        #     elif (int(self.Port) == 11106 and int(vals[1]) ==11101) or (int(self.Port) == 11101 and int(vals[1]) == 11106):
                        #         pass
                        #     elif (int(self.Port) == 11101 and int(vals[1]) ==11102) or (int(self.Port) == 11102 and int(vals[1]) == 11101):
                        #         pass
                        #     elif (int(self.Port) == 11102 and int(vals[1]) ==11104) or (int(self.Port) == 11104 and int(vals[1]) == 11102):
                        #         pass
                        #     elif (int(self.Port) == 11104 and int(vals[1]) ==11103) or (int(self.Port) == 11103 and int(vals[1]) == 11104):
                        #         pass
                        #     elif (int(self.Port) == 11100 and int(vals[1]) ==12200) or (int(self.Port) == 12200 and int(vals[1]) == 11100):
                        #         pass
                        #     elif (str(self.Port).startswith("122") == True) and (str(vals[1]).startswith("122")==True):
                        #         pass
                        #     else:
                        #         del self.neighborInfos[nid]
                        #         print("self port : ", self.Port, "neighbor deleted, port : ", vals[1])
                        # # #################################################

                         # # ########################  delete neighbors cloud test only   ######################################
   
                        for nid in list(self.neighborInfos):
                            vals = self.neighborInfos[nid] 
                            print("self location = ", self.location, "neighbor location = ", vals[2])      
                            if (int(self.Port) == 11000 and int(vals[1]) ==14000) or (int(self.Port) == 14000 and int(vals[1]) == 11000):
                                pass
                            elif (int(self.Port) == 14000 and int(vals[1]) ==13000) or (int(self.Port)== 13000 and int(vals[1]) == 14000):
                                pass                                     
                            elif (int(self.Port) == 13000 and int(vals[1]) ==12000) or (int(self.Port) == 12000 and int(vals[1]) == 13000):
                                pass
                            elif (int(self.Port) == 12000 and int(vals[1]) ==17000) or (int(self.Port) == 17000 and int(vals[1]) == 12000):
                                pass
                            elif (int(self.Port) == 17000 and int(vals[1]) ==15000) or (int(self.Port) == 15000 and int(vals[1]) == 17000):
                                pass
                            elif (int(self.Port) == 15000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 15000):
                                pass
                            elif (int(self.Port) == 16000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 16000):
                                pass
                            elif (int(self.Port) == 19000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 19000):
                                pass                                                                                                              ##################
                            if (int(self.Port) == 11001 and int(vals[1]) ==14001) or (int(self.Port) == 14001 and int(vals[1]) == 11001):
                                pass
                            elif (int(self.Port) == 14001 and int(vals[1]) ==13001) or (int(self.Port)== 13001 and int(vals[1]) == 14001):
                                pass                                     
                            elif (int(self.Port) == 13001 and int(vals[1]) ==12001) or (int(self.Port) == 12001 and int(vals[1]) == 13001):
                                pass
                            elif (int(self.Port) == 12001 and int(vals[1]) ==17001) or (int(self.Port) == 17001 and int(vals[1]) == 12001):
                                pass
                            elif (int(self.Port) == 17001 and int(vals[1]) ==15001) or (int(self.Port) == 15001 and int(vals[1]) == 17001):
                                pass
                            elif (int(self.Port) == 15001 and int(vals[1]) ==16001) or (int(self.Port) == 16001 and int(vals[1]) == 15001):
                                pass
                            elif (int(self.Port) == 16001 and int(vals[1]) ==19001) or (int(self.Port) == 19001 and int(vals[1]) == 16001):
                                pass
                            elif (int(self.Port) == 19001 and int(vals[1]) ==18001) or (int(self.Port) == 18001 and int(vals[1]) == 19001):
                                pass                                                                                                              #######################
                            elif (int(self.Port) == 11002 and int(vals[1]) ==14002) or (int(self.Port) == 14002 and int(vals[1]) == 11002):
                                pass
                            elif (int(self.Port) == 14002 and int(vals[1]) ==13002) or (int(self.Port)== 13002 and int(vals[1]) == 14002):
                                pass                                     
                            elif (int(self.Port) == 13002 and int(vals[1]) ==12002) or (int(self.Port) == 12002 and int(vals[1]) == 13002):
                                pass
                            elif (int(self.Port) == 12002 and int(vals[1]) ==17002) or (int(self.Port) == 17002 and int(vals[1]) == 12002):
                                pass
                            elif (int(self.Port) == 17002 and int(vals[1]) ==15002) or (int(self.Port) == 15002 and int(vals[1]) == 17002):
                                pass
                            elif (int(self.Port) == 15002 and int(vals[1]) ==16002) or (int(self.Port) == 16002 and int(vals[1]) == 15002):
                                pass
                            elif (int(self.Port) == 16002 and int(vals[1]) ==19002) or (int(self.Port) == 19002 and int(vals[1]) == 16002):
                                pass
                            elif (int(self.Port) == 19002 and int(vals[1]) ==18002) or (int(self.Port) == 18002 and int(vals[1]) == 19002):
                                pass                                                                                                                   #######################
                            elif (int(self.Port) == 11003 and int(vals[1]) ==14003) or (int(self.Port) == 14003 and int(vals[1]) == 11003):
                                pass
                            elif (int(self.Port) == 14003 and int(vals[1]) ==13003) or (int(self.Port)== 13003 and int(vals[1]) == 14003):
                                pass                                     
                            elif (int(self.Port) == 13003 and int(vals[1]) ==12003) or (int(self.Port) == 12003 and int(vals[1]) == 13003):
                                pass
                            elif (int(self.Port) == 12003 and int(vals[1]) ==17003) or (int(self.Port) == 17003 and int(vals[1]) == 12003):
                                pass
                            elif (int(self.Port) == 17003 and int(vals[1]) ==15003) or (int(self.Port) == 15003 and int(vals[1]) == 17003):
                                pass
                            elif (int(self.Port) == 15003 and int(vals[1]) ==16003) or (int(self.Port) == 16003 and int(vals[1]) == 15003):
                                pass
                            elif (int(self.Port) == 16003 and int(vals[1]) ==19003) or (int(self.Port) == 19003 and int(vals[1]) == 16003):
                                pass
                            elif (int(self.Port) == 19003 and int(vals[1]) ==18003) or (int(self.Port) == 18003 and int(vals[1]) == 19003):
                                pass                                                                                                                #######################
                            elif (int(self.Port) == 11004 and int(vals[1]) ==14004) or (int(self.Port) == 14004 and int(vals[1]) == 11004):
                                pass
                            elif (int(self.Port) == 14004 and int(vals[1]) ==13004) or (int(self.Port)== 13004 and int(vals[1]) == 14004):
                                pass                                     
                            elif (int(self.Port) == 13004 and int(vals[1]) ==12004) or (int(self.Port) == 12004 and int(vals[1]) == 13004):
                                pass
                            elif (int(self.Port) == 12004 and int(vals[1]) ==17004) or (int(self.Port) == 17004 and int(vals[1]) == 12004):
                                pass
                            elif (int(self.Port) == 17004 and int(vals[1]) ==15004) or (int(self.Port) == 15004 and int(vals[1]) == 17004):
                                pass
                            elif (int(self.Port) == 15004 and int(vals[1]) ==16004) or (int(self.Port) == 16004 and int(vals[1]) == 15004):
                                pass
                            elif (int(self.Port) == 16004 and int(vals[1]) ==19004) or (int(self.Port) == 19004 and int(vals[1]) == 16004):
                                pass
                            elif (int(self.Port) == 19004 and int(vals[1]) ==18004) or (int(self.Port) == 18004 and int(vals[1]) == 19004):
                                pass                                                                                                                #########################
                            elif (int(self.Port) == 11000 and int(vals[1]) ==13000) or (int(self.Port)== 13000 and int(vals[1]) == 11000):
                                pass                                     
                            elif (int(self.Port) == 13000 and int(vals[1]) ==17000) or (int(self.Port) == 17000 and int(vals[1]) == 13000):
                                pass
                            elif (int(self.Port) == 17000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 17000):
                                pass
                            elif (int(self.Port) == 16000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 16000):
                                pass
                            elif (int(self.Port) == 14000 and int(vals[1]) ==12000) or (int(self.Port) == 12000 and int(vals[1]) == 14000):
                                pass
                            elif (int(self.Port) == 12000 and int(vals[1]) ==15000) or (int(self.Port) == 15000 and int(vals[1]) == 12000):
                                pass
                            elif (int(self.Port) == 15000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 15000):
                                pass
                            elif (int(self.Port) == 11000 and int(vals[1]) ==12000) or (int(self.Port) == 12000 and int(vals[1]) == 11000):
                                pass
                            elif (int(self.Port) == 11000 and int(vals[1]) ==17000) or (int(self.Port) == 17000 and int(vals[1]) == 11000):
                                pass
                            elif (int(self.Port) == 14000 and int(vals[1]) ==15000) or (int(self.Port) == 15000 and int(vals[1]) == 14000):
                                pass
                            elif (int(self.Port) == 13000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 13000):
                                pass
                            elif (int(self.Port) == 17000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 17000):
                                pass
                            elif (int(self.Port) == 14000 and int(vals[1]) ==17000) or (int(self.Port) == 17000 and int(vals[1]) == 17000):
                                pass
                            elif (int(self.Port) == 13000 and int(vals[1]) ==15000) or (int(self.Port) == 15000 and int(vals[1]) == 13000):
                                pass
                            elif (int(self.Port) == 12000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 12000):
                                pass
                            elif (int(self.Port) == 12000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 12000):
                                pass                                                                                                                  ########################
                            elif (int(self.Port) == 13000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 13000):
                                pass
                            elif (int(self.Port) == 13000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 13000):
                                pass 
                            elif (int(self.Port) == 14000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 14000):
                                pass                                                                                                                  ########################
                            elif (int(self.Port) == 14000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 14000):
                                pass
                            elif (int(self.Port) == 14000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 14000):
                                pass 
                            elif (int(self.Port) == 11000 and int(vals[1]) ==15000) or (int(self.Port) == 15000 and int(vals[1]) == 11000):
                                pass 
                            elif (int(self.Port) == 11000 and int(vals[1]) ==16000) or (int(self.Port) == 16000 and int(vals[1]) == 11000):
                                pass 
                            elif (int(self.Port) == 11000 and int(vals[1]) ==18000) or (int(self.Port) == 18000 and int(vals[1]) == 11000):
                                pass
                            elif (int(self.Port) == 11000 and int(vals[1]) ==19000) or (int(self.Port) == 19000 and int(vals[1]) == 11000):
                                pass
                            elif (str(self.Port).startswith("110") == True) and (str(vals[1]).startswith("110")==True):
                                pass
                            elif (str(self.Port).startswith("120") == True) and (str(vals[1]).startswith("120")==True):
                                pass
                            elif (str(self.Port).startswith("130") == True) and (str(vals[1]).startswith("130")==True):
                                pass
                            elif (str(self.Port).startswith("140") == True) and (str(vals[1]).startswith("140")==True):
                                pass
                            elif (str(self.Port).startswith("150") == True) and (str(vals[1]).startswith("150")==True):
                                pass
                            elif (str(self.Port).startswith("160") == True) and (str(vals[1]).startswith("160")==True):
                                pass
                            elif (str(self.Port).startswith("170") == True) and (str(vals[1]).startswith("170")==True):
                                pass
                            elif (str(self.Port).startswith("180") == True) and (str(vals[1]).startswith("180")==True):
                                pass
                            elif (str(self.Port).startswith("190") == True) and (str(vals[1]).startswith("190")==True):
                                pass
                            else:
                                # del self.neighborInfos[nid]
                                # print("self port : ", self.Port, "neighbor deleted, port : ", vals[1])
                                # #print("nothing, working locally")
                                print("nothing, working with random 20% graph")
                        # #################################################
                                                
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
