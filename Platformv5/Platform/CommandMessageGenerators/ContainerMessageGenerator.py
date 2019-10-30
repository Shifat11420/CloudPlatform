from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator
from CommandMessageGenerators.FileIfNeededMG import DoYouNeedFileMG
from MessageManagers.FileConfirmer import FileConfirmer
import os


class ContainerMessageGenerator(MessageGenerator):
    def __init__(self, a_container_manager, in_context):
        MessageGenerator.__init__(self, in_context)
        self.cont_mgr = a_container_manager
        self.firsttime = True
        self.finished = False
        self.command = COMMAND_RECEIVECONTAINER
        self.extramgs = []
        self.extratags = ""

    def OneShot(self): 
        dbgprint("CMG:Don't Quit!")
        return False

    def reset(self):
	MessageGenerator.reset(self)
        self.firsttime = True
        self.finished = False
        
    def read(self):
        if(self.finished):
            return None
        elif(self.firsttime):
            self.cont_mgr.purgeBadFiles()
            
            self.extramgind = 0
            self.firsttime = False
            strval = self.command
            strval += COMMA + ARGS
            strval += COMMA + self.cont_mgr.cont_args
            strval += COMMA + ID
            strval += COMMA + self.cont_mgr.idstr
            strval += COMMA + SOURCEIP
            strval += COMMA + self.cont_mgr.work_source_ip
            strval += self.extratags
            strval += COMMA + ISDOCKER
            strval += COMMA + str(self.cont_mgr.isdocker)
            strval += COMMA + SOURCEPORT
            strval += COMMA + str(self.cont_mgr.work_source_port)
            strval += COMMA + FILECOUNT
            strval += COMMA + str(len(self.cont_mgr.cont_files))
            strval += COMMA + FILENAMES

            #finalstrval = COMMAND_QUEUECONTAINER
            #finalstrval += COMMA + ID
            #finalstrval += COMMA + self.cont_mgr.idstr
            #finalstrval += COMMA + LINEDELIM

            #dbgprint("adding queue command:"+finalstrval)
            #finmg = StringMessageGenerator(finalstrval, self.context)
            #filerec = FileConfirmer(self.cont_mgr.cont_files, finmg)

            #self.context.ReactorReceiverAdd(filerec)

            
            for i in range(0, len(self.cont_mgr.cont_files)):
                strval += COMMA + GetFileNameFromPath(self.cont_mgr.cont_files[i])
            strval += COMMA + LINEDELIM
            self.fileindex = 0
            dbgprint("DoYouNeedFile?:"+GetFileNameFromPath(self.cont_mgr.cont_files[self.fileindex]))
            self.filemgen = DoYouNeedFileMG(GetFileNameFromPath(self.cont_mgr.cont_files[self.fileindex]), self.context)
            return strval
        else:
            val = None
            while(self.extramgind < len(self.extramgs)):
                dbgprint("EMG:"+self.extramgs[self.extramgind].__class__.__name__)
                val = self.extramgs[self.extramgind].read()
                if(val == None):
                    self.extramgind = self.extramgind + 1
                    if(self.extramgind == len(self.extramgs)):
                        break
                    else:
                        continue
                else:
                    return val
            while(val == None):
                val = self.filemgen.read()
                if(val == None):
                    self.fileindex = self.fileindex + 1
                    dbgprint("Len cont_files:"+str(len(self.cont_mgr.cont_files)))
                    if(self.fileindex >= len(self.cont_mgr.cont_files)):
                        self.finished = True
                        return None
                    dbgprint("self.fileindex:"+str(self.fileindex))
                    dbgprint("actual cont_files:"+str(self.cont_mgr.cont_files))
                    self.filemgen = DoYouNeedFileMG(GetFileNameFromPath(self.cont_mgr.cont_files[self.fileindex]), self.context)
                    dbgprint("DoYouNeedFile?:"+GetFileNameFromPath(self.cont_mgr.cont_files[self.fileindex]))
                else:
                    return val


class TGJobMG(ContainerMessageGenerator):
    def __init__(self, a_tgm, in_context):
        ContainerMessageGenerator.__init__(self, a_tgm, in_context)
        self.extramgs = []
        for skey in a_tgm.succ_locations:
            dbgprint("Make Succ MG")
            self.extramgs.append(a_tgm.succ_locations[skey].MakeLinkMG(in_context, a_tgm.idstr, "succ"))
        
        for okey in a_tgm.pred_locations:
            self.extramgs.append(a_tgm.pred_locations[okey].MakeLinkMG(in_context, a_tgm.idstr, "pred"))
        self.command = COMMAND_RECEIVETGJOB
        self.extratags = COMMA + TASKGRAPHID + COMMA + a_tgm.taskgraphid
        self.extratags += COMMA + LOCINDEX + COMMA + str(a_tgm.locationindex)
        self.extratags += COMMA + PRIORITY + COMMA + str(a_tgm.priority)
   
        dbgprint("TGJobMG:reqslen:"+str(len(a_tgm.requirements)))
        for rkey in a_tgm.requirements:
            self.extratags += COMMA + UFILLREQ + COMMA + rkey
            if(not(a_tgm.requirements[rkey] is None)):
                self.extramgs = self.extramgs + a_tgm.requirements[rkey].package(in_context)

        dbgprint("TGJobMG:extratags:"+str(self.extratags))
        
