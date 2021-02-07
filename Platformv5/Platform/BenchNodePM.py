from NodePlatformManager import NodePlatformManager
from Utilities.Const import *
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import SetOutputFolder, expprint
from DistMethods.DistFactory import getRedistDict
from DistMethods.CalcGradDescent import CalcSubLevel
from DistMethods.VectorContainer import VectorContainer
from CommandMessageGenerators.QueueLenMessageGenerator import QueueLenMessageGenerator
from CommandMessageGenerators.BenchMessageGenerator import BenchMessageGenerator
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from CommandMessageGenerators.ComboMsgGen import ComboGen
from CommandMessageGenerators.AskForWork import AskForWork
import datetime
from twisted.python.compat import xrange                                ##added import

DEFAULT_CONN_TIME = 100

class BenchNodePM(NodePlatformManager):
    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn=False):
        NodePlatformManager.__init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn)

        self.neighborQueueLen = {}
        self.neighborSubQueueLen = {}
        self.neighborBench = {}
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
                self.redistributeWork()

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
        
            nconn = self.neighborConn[nid]
            conntotal = conntotal + nconn
            nconns.append(nconn)

            nids.append(nid)

                

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
                vals = self.neighborInfos[nid]
                for i in xrange(0, dictResults[nid]):
                    worktosend = self.GetWorkToSend()
                    if not worktosend is None:
                        mgen = ContainerMessageGenerator(worktosend, self)
                        dbgprint("RDWORK:SENDING:"+str(worktosend.idstr))
                        dbgprint("RDWORK:DEST:"+str(vals[0])+":"+str(vals[1]))
                        self.msgmon.sendGen(mgen, vals[0], vals[1])
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
    if(dbg == "True"):
        setDbg(True)
    else:
        setDbg(False)
    print ("Debug is "+str(DEBUG))                        ##

    pm = BenchNodePM(source_ip, port, exp_ip, exp_port)
    pm.StartAll()
