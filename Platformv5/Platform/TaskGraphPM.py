from BenchNodePM import BenchNodePM
from NodePlatformManager import NodePlatformManager
from DistMethods.CalcGradDescent import CalcSubLevel
from DistMethods.DistFactory import getRedistDict, getTGRedistDict
from Utilities.FileInputTokenize import ArgFIP
from DockerManagers.TGHelpers import TGJobColl, LocationForwarder, JobRequirement
from CommandMessageGenerators.TaskGraphMGs import TGQueueMG, LocMG
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from Utilities.FileUtil import SetOutputFolder, expprint
from Utilities.Const import *
import threading
import os.path

class TaskGraphPM(BenchNodePM):

    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn=False):
        BenchNodePM.__init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn=False)

        self.forwarders = {}
        self.tgjobs = TGJobColl()
        self.incomingtgjobs = {}
        self.incomingjrlock = threading.Lock()
        self.incomingjr = {}
        self.tgqueuelock = threading.Lock()
        self.obligs = {}
        self.incomingtotalgraphs = {}
        self.neighbor_tginfos = {}

    def findLocation(self, jkey):
        for ajob in self.tgjobs.joblist():
            if(jkey == ajob.idstr):
                return LocMG(self, self.IP, self.Port, jkey)
        if(jkey in self.forwarders):
            return self.forwarders[jkey].MakeLocMG(self)
        return None

    def RemoveForwarder(self, jkey, index):
        if(self.forwarders[jkey].index <= index):
            del self.forwarders[jkey]

    def packageJob(self, jkey, newip, newport):
        self.forwarders[jkey] = self.tgjobs.getjob(jkey).makeForwarder(newip, newport)
        pkg = None
        mover = None
        with self.tgqueuelock:
            mover = self.tgjobs.popjob(jkey)
        if(not (mover is None)):
            pkg = mover.package()
            for sid in mover.succ_locations:
                loc = mover.succ_locations[sid]
                lmg = LocMG(self, newip, newport, sid)
                self.msgmon.sendGen(lmg, loc.ip, loc.port)
            for pid in mover.pred_locations:
                loc = mover.pred_locations[pid]
                lmg = LocMG(self, newip, newport, pid)
                self.msgmon.sendGen(lmg, loc.ip, loc.port)
                
        return pkg

    
    def DoINeedOblig(self, taskid, filename):
        if(os.path.isfile(filename)):
            return False
        return True

    def ObligationSent(self, taskid, filename, transp):
        del self.obligs[taskid][filename]
        if(len(self.obligs[taskid]) == 0):
            del self.obligs[taskid]

    def GotLink(self, in_ip, in_port, ataskid, areftaskid, atag, aindex):
        dbgprint("GotLink?")
        lf = LocationForwarder(in_ip, in_port, aindex, ataskid)
        atgjob = None
        if(self.tgjobs.hasjob(areftaskid)):
            atgjob = self.tgjobs.getjob(areftaskid)
        if(areftaskid in self.incomingtgjobs):
            atgjob = self.incomingtgjobs[areftaskid]
        if(atgjob is None):
            dbgprint("Link sent to dead end")
            #May need to follow up with forwarder here!!!!
            #Consider after debugging some!
            #Possible?
        if(atag == "succ"):
            if(ataskid in atgjob.succ_locations):
                if(atgjob.succ_locations[ataskid].index < aindex):
                    dbgprint("updating succ")
                    atgjob.succ_locations[ataskid] = lf
            else:
                dbgprint("assigning succ")
                atgjob.succ_locations[ataskid] = lf
        if(atag == "pred"):
            if(ataskid in atgjob.pred_locations):
                if(atgjob.pred_locations[ataskid].index < aindex):
                    dbgprint("inc_updating pred")
                    atgjob.pred_locations[ataskid] = lf
            else:
                dbgprint("inc_assigning pred")
                atgjob.pred_locations[ataskid] = lf
        

    def updateJobIfNeeded(self, atgjob, ataskid, lf):
        if(ataskid in atgjob.succ_locations):
            if(atgjob.succ_locations[ataskid].index < lf.index):
                atgjob.succ_locations[ataskid] = lf
        if(ataskid in atgjob.pred_locations):
            if(atgjob.pred_locations[ataskid].index < lf.index):
                atgjob.pred_locations[ataskid] = lf
        

    def GotLocation(self, in_ip, in_port, ataskid, aindex):
        
        dbgprint("GotLocation:"+str(ataskid)+str(atag)+str(aindex))
        lf = LocationForwarder(in_ip, in_port, aindex, ataskid)
        if(ataskid in self.forwarders):
            dbgprint("in forwarders")
            if(self.forwarders[ataskid].index < lf.index):
                self.forwarders[ataskid] = lf
        dbgprint("  GotLocation:tgjobslen"+str(self.tgjobs.length()))
        for atgjob in self.tgjobs.joblist:
            self.updateJobIfNeeded(atgjob, ataskid, lf)
        for key, atgjob in self.incomingtgjobs.iteritems():
            self.updateJobIfNeeded(atgjob, ataskid, lf)
                    
    def StartReceivingReqSet(self, fromtaskid, totaskid, fnames):
        jr = JobRequirement(fnames, totaskid, fromtaskid)
        dbgprint("SRS:"+str(totaskid))
        with self.incomingjrlock:
            if(not totaskid in self.incomingjr):
                self.incomingjr[totaskid] = []
            self.incomingjr[totaskid].append(jr)

    def BeginReceivingTaskGraph(self, tgid, tcount):
        self.incomingtotalgraphs[tgid] = tcount

    def AddIncomingTGWork(self, tgm):
        dbgprint("Got TG Work:"+str(tgm.idstr))
        self.incomingtgjobs[tgm.idstr] = tgm

    def IsThereWorkToDo(self):
        if(NodePlatformManager.IsThereWorkToDo(self)):
            return True
        
        if(self.tgjobs.length() > 0):
            return True
        return False

    def RecNeighborTGInfo(self, nid, tginfos):
        dbgprint("RecNeighborTGInfo")
        self.neighbor_tginfos[nid] = tginfos

    def GetTGQueueInfo(self):
        return self.tgjobs.getpricounts()

    def GetOtherMGensForNeighbors(self):
        dl = self.GetTGQueueInfo()
        return [TGQueueMG(self, self.idval, dl)]
    
    def GetWorkToDo(self):
        bestjob = self.tgjobs.getJobToWork()
        if(bestjob is None):
            if(len(self.workqueue) > 0):
                return self.workqueue.pop(0)
        return bestjob

    def SendExecFinished(self):
        dbgprint("TG Send Executing Container Finished")
        if(self.ExecContainer != None):
            resp = self.ExecContainer.PackageResponse()

            if(not resp is None):
                toip = self.ExecContainer.work_source_ip
                toport = self.ExecContainer.work_source_port
                self.msgmon.sendGen(resp, toip, toport)

            jr = self.ExecContainer.JobOblig()
            dbgprint("got jrs?")
            if(not jr is None):
                dbgprint("yes!")
                succ_loc = self.ExecContainer.succ_locations
                dbgprint("len succ_loc:"+str(len(succ_loc)))
                for key in succ_loc:
                    jr.taskid = key
                    jr.fromid = self.ExecContainer.idstr
                    loc = succ_loc[key]
                    mgens = jr.package(self)
                    for mgen in mgens:
                        dbgprint("Sending JR MGEN")
                        self.msgmon.sendGen(mgen, loc.ip, loc.port)
                    
            
    def filewaitextra(self):
        lkeys = list(self.incomingtotalgraphs.keys())
        for key in lkeys:
            actualcount = 0
            for tgjob in self.tgjobs.joglist:
                if(tgjob.taskgraphid == key):
                    actualcount += 1
            if(actualcount == self.incomingtotalgraphs[key]):
                del self.incomingtotalgraphs[key]
        with self.incomingjrlock:
            lkeys = list(self.incomingjr.keys())
            for key in lkeys:
                jrlen = len(self.incomingjr[key])-1
                for i in xrange(jrlen, -1, -1):

                
                    jr = self.incomingjr[key][i]
                    dbgprint("FW:checking:incomingjr:from:"+str(jr.fromid)+":to:"+str(jr.taskid))
                    
                    allfilesfound = True
                    for f in jr.filenames:
                        dbgprint("FW:Filename:"+str(f))
                        if(not os.path.exists(f)):
                            dbgprint("FW:NOTFOUND")
                            allfilesfound = False
                            break
                    if(allfilesfound):
                        dbgprint("FW:AFF:"+str(jr.taskid) + ":" + str(jr.fromid))
                        if(jr.taskid in self.incomingtgjobs):
                            dbgprint("FW:inincoming")
                            tgjob = self.incomingtgjobs[jr.taskid]
                            tgjob.ReceiveReq(jr.fromid, jr)

                            del self.incomingjr[key][i]
                            if(len(self.incomingjr[key]) == 0):
                                del self.incomingjr[key]
                        elif(self.tgjobs.hasjob(jr.taskid)):
                            dbgprint("FW:inqueue")
                            tgjob = self.tgjobs.getjob(jr.taskid)
                            tgjob.ReceiveReq(jr.fromid, jr)
                            del self.incomingjr[key][i]
                            if(len(self.incomingjr[key]) == 0):
                                del self.incomingjr[key]
                   
                        elif(jr.taskid in self.forwarders):
                            dbgprint("FW:inforwarders")
                            mgens = jr.package(self)
                            locfw = self.forwarders[jr.taskid]
                            dbgprint("FW:fwdloc:"+str(locfw.ip)+":"+str(locfw.port))
                            for mgen in mgens:
                                self.msgmon.sendGen(mgen, locfw.ip, locfw.port)
                            del self.incomingjr[key]
                        else:
                            dbgprint("ERROR job req to nowhere!")    
        from Utilities.Const import *        
        dbgprint("FW:Before incqueue")
        lkeys = list(self.incomingtgjobs.keys())
        for key in lkeys:
            cm = self.incomingtgjobs[key]
            allfilesfound = True
            for f in cm.cont_files:
                dbgprint("FW:Does file:"+f+" exist?")
                fileexists = os.path.exists(f)
                if not fileexists:
                    dbgprint("No")
                    allfilesfound = False
                    break
            if allfilesfound:
                with self.workqueuelock:
                    dbgprint("FW:selfid:"+str(self.idval)+"Moving from queue key:"+str(key)+":")
                    self.tgjobs.addjob(cm)
                    #self.checkReqs(cm)
                    del self.incomingtgjobs[key]
                self.RespondToNewWork()
                    
    #def checkReqs(self, cm):
        
                
    def redistributeWork(self):
        btotal = 0
        qltotal = 0
        nids = []
        nbenches = []
        nsublevels = []
        nsubleveldict = CalcSubLevel(self.neighborSubQueueLen)

        ntgsets = []
        
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

        ltg = self.GetTGQueueInfo()

        ntgsets.append(ltg)

        mybench = self.GetBench()
        btotal = float(mybench)
        #next line used to be shortcut to stop last job movement
        qltotal = self.GetQueueLen()
        conntotal = 0
        nsublvltotal = 0
        dbgprint("TaskGraph:redist:MYID:"+str(self.idval))
        dbgprint("TaskGraph:redist:"+str(self.neighborQueueLen))
        for nid in self.neighborQueueLen:

            ntgsets.append(self.neighbor_tginfos[nid])
            
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

        dictTGMoves = getTGRedistDict(self.VContainer, nids, nbenches, btotal, ntgsets)

        dnmgens = self.tgjobs.GetMgensForNeighbors(dictTGMoves, nids, self.idval)

        for nid in dnmgens:
            if(nid != self.idval):
                vals = self.neighborInfos[nid]
                for mgen in dnmgens[nid]:
                    self.msgmon.sendGen(mgen, vals[0], vals[1])
        
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
    print sys.argv
    source_ip = argsFIP[DICT_SOURCE_IP]
    port = int(argsFIP[DICT_SOURCE_PORT])
    SetOutputFolder(argsFIP[DICT_FOLDER])
    exp_ip = argsFIP[DICT_EXP_IP]
    exp_port = argsFIP[DICT_EXP_PORT]
    print argsFIP
    dbg = argsFIP[DICT_DEBUG]
    if(dbg == "True"):
        setDbg(True)
    else:
        setDbg(False)
    print "Debug is "+str(DEBUG)

    pm = TaskGraphPM(source_ip, port, exp_ip, exp_port)
    pm.StartAll()
