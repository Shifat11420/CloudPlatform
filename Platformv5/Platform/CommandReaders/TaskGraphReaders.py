from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.FileMessageGenerator import TGObligFMG
from CommandMessageGenerators.TaskGraphMGs import IHaveObligMG, INeedObligMG
from DockerManagers.TGManager import TGManager
from Utilities.Const import *

class ReceiveTGQueueRdr(TCPReader):
    def HandleLine(self, data):
        dbgprint("RecieveTGQueueRdr:"+str(data))
        vals = data.split(",")
        nodeid = vals[1]
        tginfo = {}
        for i in range(2, len(vals), 2):
            tginfo[int(vals[i])] =  int(vals[i+1])
        self.context.RecNeighborTGInfo(nodeid, tginfo)
        
class DYNTaskObligRdr(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        self.taskid = ""
        self.filename = ""
        for val in vals:
            if(val == TASKID):
                self.taskid = vals[i]
            if(val == FILENAME):
                self.filename = vals[i]
            i = i + 1

    def GetResponse(self):
        bval = self.context.DoINeedOblig(self.taskid, self.filename)
        mgen = None
        if(bval):
            mgen = INeedObligMG(self.context, self.taskid, self.filename)
        else:
            mgen = IHaveObligMG(self.context, self.taskid, self.filename)
        return mgen

class IHaveObligRdr(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        self.taskid = ""
        self.filename = ""
        for val in vals:
            if(val == TASKID):
                self.taskid = vals[i]
            if(val == FILENAME):
                self.filename = vals[i]
            i = i + 1

    def WriteResponse(self, transp):
        self.context.ObligationSent(self.taskid, self.filename, transp)

class INeedObligRdr(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        self.taskid = ""
        self.filename = ""
        for val in vals:
            if(val == TASKID):
                self.taskid = vals[i]
            if(val == FILENAME):
                self.filename = vals[i]
            i = i + 1
            
    def GetResponse(self):
        filepath = GetFilePath(self.filename)
        return TGObligFMG(filepath, self.context, self.taskid)

class LinkReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("LocReader")
        vals = data.split(COMMA)
        i = 1
        self.ip = ""
        self.port = 0
        self.taskid = ""
        self.index = -1
        self.tag = ""
        self.rtaskid = ""
        for val in vals:
            if(val == STR_IP):
                self.ip = vals[i]
            if(val == STR_PORT):
                self.port = int(vals[i])
            if(val == TASKID):
                self.taskid = vals[i]
            if(val == REFTASKID):
                self.rtaskid = vals[i]
            if(val == TAG):
                self.tag = vals[i]
            if(val == INDEX):
                self.index = int(vals[i])
            i = i + 1

        self.context.GotLink(self.ip, self.port, self.taskid, self.rtaskid, self.tag, self.index)

    
class LocReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("LinkReader")
        vals = data.split(COMMA)
        i = 1
        self.ip = ""
        self.port = 0
        self.taskid = ""
        self.index = -1
        for val in vals:
            if(val == STR_IP):
                self.ip = vals[i]
            if(val == STR_PORT):
                self.port = int(vals[i])
            if(val == TASKID):
                self.taskid = vals[i]
            if(val == INDEX):
                self.index = int(vals[i])
            i = i + 1

        self.context.GotLocation(self.ip, self.port, self.taskid, self.index)

class RequirementSetRdr(TCPReader):
    def HandleLine(self, data):
        dbgprint("ReqSetReader:"+str(data))
        vals = data.split(COMMA)
        fromtaskid = vals[2]
        totaskid = vals[3]
        dbgprint("RSR:fromtaskid:"+str(fromtaskid)+":totaskid:"+str(totaskid))
        fnames = []
        for i in range(5, len(vals)):
            dbgprint("RSR:fname:"+str(vals[i]))
            fnames.append(vals[i])
        self.context.StartReceivingReqSet(fromtaskid, totaskid, fnames)
        
class RemoveForwarderRdr(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        taskid = vals[1]

        self.context.RemoveForwarder(taskid)

class TaskGraphHeaderRdr(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        tgid = ""
        tcount = 0
        for val in vals:
            if(val == TASKGRAPHID):
                tgid = vals[i]
            if(val == TASKCOUNT):
                tcount = int(vals[i])
            i = i + 1
        self.context.BeginReceiveTaskGraph(tgid, tcount)

class TaskContainerReader(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA)
        i = 1
        dbgprint("TCR In")
        dbgprint("TCR:data:"+str(data))
        new_cont_args = None
        self.filecount = 0
        filenames = []
        tgid = ""
        locind = 0
        ufreq = []
        apriority = 0
        for val in vals:
            if(val == ARGS):
                new_cont_args = vals[i]
            elif(val == FILECOUNT):
                self.filecount = int(vals[i])
            elif(val == ID):
                new_id = vals[i]
            elif(val == SOURCEIP):
                source_ip = vals[i]
            elif(val == TASKGRAPHID):
                tgid = vals[i]
            elif(val == LOCINDEX):
                locind = int(vals[i])
            elif(val == PRIORITY):
                apriority = int(vals[i])
            elif(val == UFILLREQ):
                ufreq.append(vals[i])
            elif(val == ISDOCKER):
                if(vals[i] == "True"):
                    isdocker = True
                else:
                    isdocker = False
            elif(val == SOURCEPORT):
                source_port = vals[i]
            elif(val == FILENAMES):
                dbgprint("TCR:FILENAMES")
                dbgprint("TCR:i:"+str(i))
                dbgprint("TCR:len(vals):"+str(len(vals)))
                for j in range(i, len(vals)):
                    if(len(vals[j]) == 0):
                        continue
                    dbgprint("TGR:APPEND:"+str(vals[j]))
                    filenames.append(vals[j])
            i = i + 1
        self.ContainerMgr = TGManager(new_cont_args, LocalizeFileNames(filenames), new_id, source_ip, source_port, isdocker, tgid, self.context, ufreq, locind, apriority)
        self.context.AddIncomingTGWork(self.ContainerMgr)
        
        self.finished = True

    def IsFinished(self):
        return self.finished


