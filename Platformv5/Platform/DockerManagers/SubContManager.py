import uuid
import threading
from subprocess import call
import subprocess
from Utilities.Const import *
from Utilities.FileUtil import GetOutputFolder
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from CommandMessageGenerators.ResponseMessageGenerator import ResponseMessageGenerator

#container_args is a string, container_files is a list of strings
#idstr is used to identify this particular piece of work
#work_source_ip is a string
#work_source_port is a string or int
#context is a PlatformManager extension
class ContainerManager():
    def __init__(self, container_args, container_files, idstr, work_source_ip, work_source_port, isdocker, context):
        self.context = context
        self.cont_args = container_args
        self.cont_files = container_files
        self.idstr = idstr
        self.isdocker = isdocker
        self.work_source_ip = work_source_ip
        self.work_source_port = int(work_source_port)
        self.outfilename = ConcatePath(GetOutputFolder(),idstr)
        self.finished = False
        self.running = False

    def purgeBadFiles(self):
        self.cont_files = [x for x in self.cont_files if x != "Sandbox/"]

    def SetAllPredSucc(self, aip, aport):
        pass

    def ThreadStart(self):
        fout = open(self.outfilename, 'w')
        if(self.isdocker):
            if(len(self.cont_files) > 0):
                strLoad = ["docker", "load", "--input", self.cont_files[0]]
                dbgprint("Calling : " + str(strLoad))
                call(strLoad)
        dbgprint("Calling Container Process")
        dbgprint("CMD:"+self.cont_args)
        call(self.cont_args, stderr=subprocess.STDOUT, stdout=fout, shell=True)
        dbgprint("C Process Finished")
        self.finished = True
        
    def Start(self):
        from Utilities.Const import *
        self.running = True
        self.t = threading.Thread(target=self.ThreadStart)
        self.t.start()
        
    def IsRunning(self):
        return self.running

    def IsFinished(self):
        dbgprint("ContMgr:IsFinished:"+str(self.finished))
        return self.finished

    def Package(self):
        if(self.IsRunning()):return None
        if(self.IsFinished()):return self.PackageResponse()
        return ContainerMessageGenerator(self, self.context)

    def JobOblig(self):
        return None
    
    def PackageResponse(self):
        return ResponseMessageGenerator(self.idstr, self.outfilename, self.context)
