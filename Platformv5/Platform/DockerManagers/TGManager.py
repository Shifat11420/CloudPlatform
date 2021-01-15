from Utilities.Const import *
from CommandMessageGenerators.ContainerMessageGenerator import TGJobMG
from .SubContManager import ContainerManager                 ##. added
from .TGHelpers import LocationForwarder, JobRequirement        ##. added
import os

class TGManager(ContainerManager):

    def __init__(self,container_args, container_files, idstr, work_source_ip, work_source_port, isdocker, in_taskgraphid, context, in_req_ids, in_locind=0, in_priority=0):
        ContainerManager.__init__(self, container_args, container_files, idstr, work_source_ip, work_source_port, isdocker, context)
        self.requirements = {}
        for arid in in_req_ids:
            dbgprint("Adding UFR:"+str(arid))
            self.requirements[arid] = None
        self.outputcont = None
        self.succ_locations = {}
        self.pred_locations = {}
        self.obligids = []
        self.taskgraphid = in_taskgraphid
        self.locationindex = in_locind
        self.priority = in_priority
        self.fixargument()

    def fixargument(self):
        pref = "<Output"
        suff = ">"
        i = 0
        while True:
            atag = pref + str(i) + suff
            if not atag in self.cont_args:
                break
            ntag = self.idstr + "_" + str(i)
            self.cont_args = self.cont_args.replace(atag, ntag)
        

    def SetTGLoc(self, aid, ip, port, tag, index):
        dbgprint("SetTGLoc:"+str(aid))
        if(tag == "succ"):
            if(aid in self.succ_locations):
                if(index > self.succ_locations[aid].index):
                    lf = LocationForwarder(ip, port, index, aid)
                    self.succ_locations[aid] = lf
            else:
                dbgprint("SetTGLoc:succ:flat addition")
                lf = LocationForwarder(ip, port, index, aid)
                self.succ_locations[aid] = lf
        if(tag == "pred"):
            if(aid in self.pred_locations):
                if(index > self.pred_locations[aid].index):
                    lf = LocationForwarder(ip, port, index, aid)
                    self.pred_locations[aid] = lf
            else:
                lf = LocationForwarder(ip, port, index, aid)
                self.pred_locations[aid] = lf
        
    def AreReqsMet(self):
        dbgprint("ARM:"+str(self.idstr))
        keys = self.requirements.keys()
        for key in keys:
            if(self.requirements[key] is None):
                dbgprint("ARM:FAIL:"+str(key))
                return False
            dbgprint("ARM:PASS:"+str(key))
        return True

    def SetAllPredSucc(self, aip, aport):
        for aid in self.pred_locations:
            lf = LocationForwarder(aip, aport, 0, aid)
            self.pred_locations[aid] = lf
        for aid in self.succ_locations:
            lf = LocationForwarder(aip, aport, 0, aid)
            self.succ_locations[aid] = lf
        
    def ReceiveReq(self, rkey, rval):
        dbgprint("TGM:RecReq:"+str(rkey))
        self.requirements[rkey] = rval

    def ObligationSatisfied(self, oid):
        self.obligids.remove(oid)

    def JobOblig(self):
        i = 0
        fns = []
        while True:
            newfn = self.idstr +"_"+ str(i)
            if(os.path.isfile("Sandbox/"+newfn)):
                fns.append(newfn)
            else:
                break
            i = i + 1
            
        jr = JobRequirement(fns, "", "")
        return jr
            

    def Package(self):        
        if(self.IsRunning()):return None
        if(self.IsFinished()):return self.PackageResponse()
        return TGJobMG(self, self.context)
