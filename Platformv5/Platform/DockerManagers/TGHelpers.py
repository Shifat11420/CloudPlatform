from Utilities.Const import *
from CommandMessageGenerators.TaskGraphMGs import LocMG, RequirementSetMG, LinkMG
from CommandMessageGenerators.FileIfNeededMG import DoYouNeedFileMG
import threading

class TGJobColl():
    def __init__(self):
        self.mylock = threading.Lock()
        self.bypriority = {}
        self.byjkey = {}
        self.minkey = -1
        self.maxkey = -1

    def length(self):
        return len(self.byjkey)

    def addjob(self, atgjob):
        with self.mylock:
            self.byjkey[atgjob.idstr] = atgjob
            if(not atgjob.priority in self.bypriority):
                self.bypriority[atgjob.priority] = []
            self.bypriority[atgjob.priority].append(atgjob.idstr)
            if(self.minkey == -1 or self.minkey > atgjob.priority):
                self.minkey = atgjob.priority
            if(self.maxkey == -1 or self.maxkey < atgjob.priority):
                self.maxkey = atgjob.priority

    def getpricounts(self):
        dpc = {}
        with self.mylock:
            for key in self.bypriority:
                dpc[key] = len(self.bypriority[key])
        return dpc

    def getJobToWork(self):
        dbgprint("In GJTW:MINKEY:"+str(self.minkey)+"MAXKEY:"+str(self.maxkey))
        dbgprint("GJTWLen:"+str(self.length()))
        toretkey = None
        with self.mylock:
            for i in range(self.minkey, self.maxkey+1):
                if(i in self.bypriority):
                    for kval in self.bypriority[i]:
                        ajob = self.byjkey[kval]
                        dbgprint("Checking job:"+str(ajob.idstr))
                        if(ajob.AreReqsMet()):
                            dbgprint("Reqs met!")
                            toretkey = kval
                            break
                        else:
                            dbgprint("Reqs fail.")
                    if(not(toretkey is None)):
                        break
        if(not(toretkey is None)):
            dbgprint("Returning TGJOB!")
            return self.popjob(toretkey)
        return None

    def GetMgensForNeighbors(self, pridict, nkeys, myid):
        dictforneighbors = {}
        dbgprint("GMFN:pridict:"+str(pridict))
        dbgprint("GMFN:nkeys:"+str(nkeys))
        dbgprint("GMFN:myid:"+str(myid))
        for i in range(len(nkeys)):
            dictforneighbors[nkeys[i]] = []
        with self.mylock:
            for pkey in pridict:
                for i in range(len(nkeys)):
                    if(nkeys[i] == myid):
                        continue
                    if(nkeys[i] in pridict[pkey]):
                        jcount = pridict[pkey][nkeys[i]]
                        for j in range(jcount):
                            if(len(self.bypriority[pkey]) > 0):
                                ajkey = self.bypriority[pkey][0]
                                ajob = self.popjobunlocked(ajkey)
                                mgen = ajob.Package()
                                dictforneighbors[nkeys[i]].append(mgen)
                            else:
                                break
        return dictforneighbors

    def getjob(self, akey):
        ajob = None
        with self.mylock:
            ajob = self.byjkey[akey]
        return ajob

    def hasjob(self, akey):
        return akey in self.byjkey

    def popjobunlocked(self, ajkey):
        atgjob = self.byjkey[ajkey]
        del self.byjkey[ajkey]
        self.bypriority[atgjob.priority].remove(atgjob.idstr)
        return atgjob
        

    def popjob(self, ajkey):
        atgjob = None
        with self.mylock:
            atgjob = self.popjobunlocked(ajkey)
        return atgjob

    def joblist(self):
        toret = []
        with self.mylock:
            for akey in self.byjkey:
                toret.append(self.byjkey[akey])
        return toret

class LocationForwarder():
    def __init__(self, aip, aport, aindex, ataskid):
        self.ip = aip
        self.port = aport
        self.index = aindex
        self.taskid = ataskid

    def MakeLocMG(self, acontext):
        
        return LocMG(acontext, self.ip, self.port, self.taskid, self.index+1)

    def MakeLinkMG(self, acontext, refid, tag):

        return LinkMG(acontext, self.ip, self.port, self.taskid, refid, tag, self.index+1)
    
class JobRequirement():
    def __init__(self, in_filenames, in_taskid, in_fromid):
        self.filenames = in_filenames
        self.taskid = in_taskid
        self.fromid = in_fromid

    def package(self, in_context):
        mgs = []
        mgs.append(RequirementSetMG(in_context, self.fromid, self.taskid, self.filenames))
        for fname in self.filenames:
            mgs.append(DoYouNeedFileMG(fname, in_context))
        return mgs
