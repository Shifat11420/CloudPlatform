from NodePlatformManager import NodePlatformManager
from Utilities.Const import *
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import SetOutputFolder, expprint
from DistMethods.DistFactory import getRedistDict
from DistMethods.DistFactory import getRedistDict_3D
from DistMethods.CalcGradDescent import CalcSubLevel
from DistMethods.VectorContainer import VectorContainer
from CommandMessageGenerators.QueueLenMessageGenerator import QueueLenMessageGenerator
from CommandMessageGenerators.BenchMessageGenerator import BenchMessageGenerator
from CommandMessageGenerators.LatencyReportGenerator import LatencyReportNode
from CommandMessageGenerators.BenchReportGenerator import BenchReportNode
from CommandMessageGenerators.LowperfMessageGenerator import LowperfNode
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from CommandMessageGenerators.ComboMsgGen import ComboGen
from CommandMessageGenerators.AskForWork import AskForWork
import datetime
import time
#from twisted.python.compat import xrange                                ##added import

DEFAULT_CONN_TIME = 100
NeighborsBenchDict = {}
NeighborsBenchList = []
n=1



class BenchNodePM(NodePlatformManager):
    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, location, ManagerOn=False):
        NodePlatformManager.__init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, location, ManagerOn)

        self.neighborQueueLen = {}
        self.neighborSubQueueLen = {}
        self.neighborBench = {}
        self.neighborLatency = {}   #*
        self.neighborConn = {}
        self.nConnStartTimes = {}
        self.intervalCount = 0
        self.mgrinterval = BNM_BASEINTERVAL
        self.lastnowork = datetime.datetime.now()
        self.VContainer = VectorContainer()
        self.expectCompTime = None
        


    def SendWorkRequest(self):
        with self.neighborInfoLock:
            if(len(self.neighborInfos) > 0):
                tpl = self.neighborInfos.pop(0)
                self.neighborInfos.append(tpl)
        if(tpl != None):
            self.msgmon.sendCommand(COMMAND_ASKFORWORK, self, tpl[0], tpl[1])

    def SetExpectCompTime(self, atime):
        self.expectCompTime = atime
            
    def SetNeighborQueueLen(self, n_ID, n_queuelen):
        dbgprint("set nq:" + str(n_ID))
        self.neighborQueueLen[n_ID] = n_queuelen

    def SetNeighborSubQueues(self, n_ID, subIDs, sublens):
        dbgprint("set subnq:" + str(n_ID))
        self.neighborQueueLen[n_ID] = {}
        for i, q in zip(subIDs, sublens):
            if(i == self.idval):
                pass
            elif(i in self.neighborQueueLen):
                pass
            else:
                self.neighborQueueLen[n_ID][i] = q
        
        
    def SetNeighborBench(self, n_ID, n_bench):
        dbgprint("set nb:"+str(n_ID))
        dbgprint("Set NBench:"+str(n_ID)+":"+str(n_bench))
        self.neighborBench[n_ID] = float(n_bench)


    def SetNeighborLatency(self, n_ID, nodeip, nodeport, n_latency):  
        dbgprint("set nlat:"+str(n_ID))
        dbgprint("Set NLatency:"+str(n_ID)+":"+str(n_latency))
        self.neighborLatency[n_ID] = float(n_latency)
        #dbgprint("just the dictionary : "+str(self.neighborLatency))
  

    def SetNeighborConn(self, n_ID, n_conn):
        dbgprint("set conn:" + str(n_ID))
        self.neighborConn[n_ID] = n_conn

    def TestConnection(self, nid):
        self.nConnStartTimes[nid] = datetime.datetime.now()
        if(not nid in self.neighborConn):
            self.neighborConn[nid] = DEFAULT_CONN_TIME

    def ReportConnTestFinished(self, n_ID):
        tval = datetime.datetime.now()
        val = (tval - (self.nConnStartTimes[n_ID])).total_seconds()
        self.SetNeighborConn(n_ID, val)

    def HandleWorkRequest(self, rnodeid, killcount):
        if(killcount > 0):
            killcount = killcount - 1
            self.NoWorkToDo(killcount, rnodeid)

    def SetUnpauseDatetime(self, newdatetime):
        self.VContainer.starttime = newdatetime
        NodePlatformManager.SetUnpauseDatetime(self, newdatetime)
        
    def NoWorkToDo(self, killcount = STARTKILLCOUNT, exempt = ""):
        NodePlatformManager.NoWorkToDo(self)
        dtn = datetime.datetime.now()
        if((dtn - self.unpause_datetime).total_seconds() < STOPNOWORK):
            td = dtn - self.lastnowork
            if(td.total_seconds() > NOWORK_SECONDS):
                self.mgrinterval = 1
                self.lastnowork = dtn
                for nid in self.neighborInfos:
                    if(nid != exempt):
                        vals = self.neighborInfos[nid]
                        mgen = AskForWork(self, killcount)
                        self.msgmon.sendGen(mgen, vals[0], vals[1])

    def GetOtherMGensForNeighbors(self):
        return []

    def LowperfNode(self, node_id, node_ip, node_port, id_maxBench, max_Bench):  
        dbgprint("Current node ID : "+str(id_maxBench)+" is the lowest performing neighbor from IP : "+str(node_ip)+" and port : "+str(node_port)+" with BENCH = "+str(max_Bench) )  
        dbgprint("node_ip : "+str(node_ip)+" node_port : "+str(node_port))
        dbgprint("self_ip : "+str(source_ip)+" self_port : "+str(port))


                    
    def NodeManagerRun(self):
        dbgprint("BM_NodeManagerRun")
        NodePlatformManager.NodeManagerRun(self)

        self.intervalCount = self.intervalCount + 1
        if(self.intervalCount >= self.mgrinterval):
            self.intervalCount = 0
            self.mgrinterval = BNM_BASEINTERVAL
            othermgens = self.GetOtherMGensForNeighbors()
            with self.neighborInfoLock:
                for nid in self.neighborInfos:
                    vals = self.neighborInfos[nid]
                    
                    mgen = BenchMessageGenerator(self)
                    dbgprint("Sending Bench/QL to "+str(vals[0])+":"+str(vals[1]))
                    self.msgmon.sendGen(mgen, vals[0], vals[1])

                    mgen = QueueLenMessageGenerator(self)
                    self.msgmon.sendGen(mgen, vals[0], vals[1])

                    for omgen in othermgens:
                        comgen = omgen.clone()
                        self.msgmon.sendGen(comgen, vals[0], vals[1])

                    self.TestConnection(nid)
                #self.redistributeWork()
                self.redistributeWork_3D()         #*

                for nid in list(self.neighborLatency):              #*
                    myneighbrLatency = float(self.neighborLatency[nid])         #*                             
                    dbgprint("Latency of neighbor : ID : "+str(nid)+" is "+str(myneighbrLatency))        #*

        #################### working with performance (Bench info)
                for nid in list(self.neighborBench):
                    myneighbrBench = float(self.neighborBench[nid])                                      
                    dbgprint("Bench of neighbor : ID : "+str(nid)+" is "+str(myneighbrBench))

                    if nid in NeighborsBenchDict:
                        NeighborsBenchDict[nid].append(myneighbrBench)
                    else:
                        NeighborsBenchDict.update({nid:[myneighbrBench]})                              
                    NeighborsBenchList.append(myneighbrBench)
                    #dbgprint("Neighbors Bench List : "+str(NeighborsBenchList))
                    max_Bench = max(NeighborsBenchList)

                    for key in NeighborsBenchDict:
                        for x in range(len(NeighborsBenchDict[key])):
                            if max_Bench == NeighborsBenchDict[key][x]:
                                id_maxBench = key
                                #print("key  =  ", key)
                       
                    dbgprint("Maximum Bench : "+str(max_Bench)+" for ID "+str(id_maxBench))
                    
                if not NeighborsBenchDict == {}:  
                    dbgprint("Final Neighbors Bench List : "+str(NeighborsBenchList))    
                    dbgprint("Final Neighbors Bench Dict  : "+str(NeighborsBenchDict))    
                    dbgprint("Final Maximum Bench : "+str(max_Bench)+" for ID "+str(id_maxBench)) 
                    try:
                        max_bench_IP =  self.neighborInfos[id_maxBench][0]
                        max_bench_PORT =  self.neighborInfos[id_maxBench][1]
                        dbgprint("Maximum bench i.e. lowest performing node, ID : "+str(id_maxBench)+ " IP address : "+str(max_bench_IP)+" Port : "+ str(max_bench_PORT))          
                    except KeyError:
                        print("neighbor is droped")    
                                                      
                    # if len(self.neighborInfos)>12:                            
                    #     for nid in self.neighborInfos:
                    #         vals = self.neighborInfos[nid]
                    #         if nid == id_maxBench:
                    #             # del self.neighborInfos[nid]
                    #             # dbgprint("deleted neighbor id: "+str(nid)+"Port : "+str(vals[1]))
                    #             break


                ############Sending to lowest performing node ##############
                    # mgen = LowperfNode(self, self.idval, self.IP, self.Port, id_maxBench, max_Bench )
                    # dbgprint("Sending to lowest performing node "+str(self.neighborInfos[id_maxBench][0])+":"+str(self.neighborInfos[id_maxBench][1]))
                    # self.msgmon.sendGen(mgen, self.neighborInfos[id_maxBench][0] , self.neighborInfos[id_maxBench][1])

                    mgen = BenchReportNode(self, self.idval, self.IP, self.Port, id_maxBench, max_Bench )
                    dbgprint("Sending maximum bench Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                    expprint("Sending maximum bench Report To Exp at: "+str(self.Exp_IP)+":"+str(self.Exp_Port))
                    self.msgmon.sendGen(mgen, self.Exp_IP, self.Exp_Port)   

                NeighborsBenchDict.clear() 
                NeighborsBenchList.clear()                        
        ###################       
        
    def AsktosleepExp(self, exp_id, exp_ip, exp_port):
        #global n
        dbgprint("This node, ip :"+str(source_ip)+" port : "+str(port)+" is the lowest performer")   
     
            
    def RespondToNewWork(self):
        NodePlatformManager.RespondToNewWork(self)
        if(self.GetQueueLen() > 2):
            self.mgrinterval = 1
                
    def redistributeWork(self):
        btotal = 0
        qltotal = 0
        nids = []
        nbenches = []
        nsublevels = []
        nsubleveldict = CalcSubLevel(self.neighborSubQueueLen)
        nqls = []
        nconns = []
        #if(self.GetQueueLen() <= 1):
        #    dbgprint("not enough to redist")
        #    return
        dbgprint("In redistWork")
        nids.append(self.idval)
        nbenches.append(float(self.GetBench()))
        nqls.append(self.GetQueueLen())
        nsublevels.append(0)
        mybench = self.GetBench()
        btotal = float(mybench)
        #next line used to be shortcut to stop last job movement
        qltotal = self.GetQueueLen()
        conntotal = 0
        nsublvltotal = 0
        for nid in self.neighborQueueLen:
            if not nid in nsubleveldict:
                nsublevels.append(0)
            else:
                nsublevels.append(nsubleveldict[nid])
                nsublvltotal = nsublvltotal + nsubleveldict[nid]
            if not nid in self.neighborBench:
                self.neighborBench[nid] = float(mybench)
            nbench = float(self.neighborBench[nid])
            btotal = btotal + nbench
            nbenches.append(nbench)
            nql = self.neighborQueueLen[nid]
            qltotal = qltotal + nql
            nqls.append(nql)
        
            try:
                nconn = self.neighborConn[nid]
                conntotal = conntotal + nconn
                nconns.append(nconn)
                nids.append(nid)
                
            except KeyError:
                print("this neighbor is deleted")
                nconn = 0
            #nconn = self.neighborConn[nid]     #.get(nid, 0)         ######fix it
            # print("nconn indi nid", nid)
            # print("nconn indi", nconn)
            
        # print("nconn list : ", nconns)
        # print("nids  : ", nids)
            # nids.append(nid)
            # print("nids  : ", nid)

                

        # ideas at this point.
        #1.  As a baseline, maintain one constant min queue length,
        #      redistribute in order to maintain that queue length
        #      This will probably be average at propagation
        #      Pretty good at maintaining throughput as long as computer fully
        #      Utilized.
        
        #2.  Flow direction.  issue is moving stuff efficently away
        #      In order to know where to move stuff, plot qlen and bench
        #      .  choose a vector which represents ideal combination of 
        #      the two, and move work in amounts relevant to the
        #      magnitude of the 2d distance and the dot product with the 
        #      direction vector.
        dictResults = getRedistDict(self.VContainer, nids, nbenches, btotal, nqls, qltotal, nsublevels, nsublvltotal)
        dbgprint("RDWORK:"+str(len(dictResults)))
        dbgprint("QL:"+str(self.GetQueueLen()))
        for nid in dictResults:
            if(nid != self.idval):
                #mgens = []
                dbgprint("RDWORK:REDIST!")
                try:
                    vals = self.neighborInfos[nid]
                    for i in range(0, dictResults[nid]):
                        worktosend = self.GetWorkToSend()
                        if not worktosend is None:
                            mgen = ContainerMessageGenerator(worktosend, self)
                            dbgprint("RDWORK:SENDING:"+str(worktosend.idstr))
                            dbgprint("RDWORK:DEST:"+str(vals[0])+":"+str(vals[1]))
                            self.msgmon.sendGen(mgen, vals[0], vals[1])       
                except KeyError:
                    print("No ID exist!")                
                    #mgens.append(mgen)
                #cmgen = ComboGen(self, mgens)
                #vals = self.neighborInfos[nid]
                #self.msgmon.sendGen(cmgen, self, vals[0], vals[1])


    ##redistribute work for 3D scheduling
    def redistributeWork_3D(self):
        btotal = 0
        qltotal = 0
        latencytotal = 0          #*
        nids = []
        nbenches = []
        nsublevels = []
        nsubleveldict = CalcSubLevel(self.neighborSubQueueLen)
        nqls = []
        nlatencies = []     #*
        nconns = []
        
        
        dbgprint("In redistWork")
        nids.append(self.idval)
        nbenches.append(float(self.GetBench()))
        nqls.append(self.GetQueueLen())
        nlatencies.append(0.0)        #*
        nsublevels.append(0)
        mybench = self.GetBench()
        btotal = float(mybench)
        latencytotal = 0.0               #*

        #next line used to be shortcut to stop last job movement
        qltotal = self.GetQueueLen()
        conntotal = 0
        nsublvltotal = 0
        for nid in self.neighborQueueLen:
            if not nid in nsubleveldict:
                nsublevels.append(0)
            else:
                nsublevels.append(nsubleveldict[nid])
                nsublvltotal = nsublvltotal + nsubleveldict[nid]
            if not nid in self.neighborBench:
                self.neighborBench[nid] = float(mybench)          
            # if not nid in self.neighborLatency:
            #     self.NeighborsLatencyDict[nid] = 0.0             

            
            nbench = float(self.neighborBench[nid])
            btotal = btotal + nbench
            nbenches.append(nbench)

            nql = self.neighborQueueLen[nid]
            qltotal = qltotal + nql
            nqls.append(nql)

            nlatency = float(self.neighborLatency[nid])          #*
            latencytotal = latencytotal + nlatency                #*
            nlatencies.append(nlatency)                           #*

        
            try:
                nconn = self.neighborConn[nid]
                conntotal = conntotal + nconn
                nconns.append(nconn)
                nids.append(nid)
                
            except KeyError:
                print("this neighbor is deleted")
                nconn = 0
            
        dictResults = getRedistDict_3D(self.VContainer, nids, nbenches, btotal, nqls, qltotal, nsublevels, nsublvltotal, nlatencies, latencytotal)   #* for 3D scheduling
        dbgprint("RDWORK:"+str(len(dictResults)))
        dbgprint("QL:"+str(self.GetQueueLen()))
        for nid in dictResults:
            if(nid != self.idval):
                #mgens = []
                dbgprint("RDWORK:REDIST!")
                try:
                    vals = self.neighborInfos[nid]
                    for i in range(0, dictResults[nid]):
                        worktosend = self.GetWorkToSend()
                        if not worktosend is None:
                            mgen = ContainerMessageGenerator(worktosend, self)
                            dbgprint("RDWORK:SENDING:"+str(worktosend.idstr))
                            dbgprint("RDWORK:DEST:"+str(vals[0])+":"+str(vals[1]))
                            self.msgmon.sendGen(mgen, vals[0], vals[1])       
                except KeyError:
                    print("No ID exist!")                
                    #mgens.append(mgen)
                #cmgen = ComboGen(self, mgens)
                #vals = self.neighborInfos[nid]
                #self.msgmon.sendGen(cmgen, self, vals[0], vals[1])         

if __name__ == "__main__":
    global DEBUG
    argsFIP = ArgFIP(sys.argv)
    print (sys.argv)                                            ##
    source_ip = argsFIP.get(DICT_SOURCE_IP)
    port = int(argsFIP.get(DICT_SOURCE_PORT))
    SetOutputFolder(argsFIP.get(DICT_FOLDER))
    #exp_ip = argsFIP[DICT_EXP_IP]
    exp_ip = argsFIP.get(DICT_EXP_IP)
    exp_port = argsFIP.get(DICT_EXP_PORT)
    print (argsFIP)                                    ##
    dbg = argsFIP.get(DICT_DEBUG)
    location = argsFIP.get(DICT_LOC)               ####
    print("location : ",location)                       ####
    if(dbg == "True"):
        setDbg(True)
    else:
        setDbg(False)
    print ("Debug is "+str(DEBUG))                        ##

    pm = BenchNodePM(source_ip, port, exp_ip, exp_port, location)                   ####
    pm.StartAll()
