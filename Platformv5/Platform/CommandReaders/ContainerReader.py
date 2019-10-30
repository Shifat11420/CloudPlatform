from CommandReaders.TCPReader import TCPReader
from DockerManagers.SubContManager import ContainerManager
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator
from Utilities.Const import *

class ContainerResponseReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(COMMA)
        i = 1
        for val in vals:
            if(val == FILENAME):
                filename = vals[i]
            if(val == ID):
                idstr = vals[i]
            i = i + 1
        self.context.AddCompletedWorkFile(idstr, filename)

    #def GetResponse(self):
    #    return TerminateMessageGenerator(self.context)

class ContainerQueueReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(COMMA)
        i = 1
        for val in vals:
            if(val == ID):
                self.context.MoveWorkToRealQueue(vals[i])
            i = i + 1
        self.finished = True

    def IsFinished(self):
        return self.finished

    #def GetResponse(self):
    #    return TerminateMessageGenerator(self.context)

class ContainerReader(TCPReader):

    def HandleLine(self, line):
        vals = line.split(COMMA)
        i = 1

        new_cont_args = None
        self.filecount = 0
        filenames = []
        for val in vals:
            if(val == ARGS):
                new_cont_args = vals[i]
            elif(val == FILECOUNT):
                self.filecount = int(vals[i])
            elif(val == ID):
                new_id = vals[i]
            elif(val == SOURCEIP):
                source_ip = vals[i]
            elif(val == ISDOCKER):
                if(vals[i] == "True"):
                    isdocker = True
                else:
                    isdocker = False
            elif(val == SOURCEPORT):
                source_port = vals[i]
            elif(val == FILENAMES):
                for j in range(i, len(vals)):
                    filenames.append(vals[j])
            i = i + 1
        self.ContainerMgr = ContainerManager(new_cont_args, LocalizeFileNames(filenames), new_id, source_ip, source_port, isdocker, self.context)
        self.context.AddIncomingWork(self.ContainerMgr)
        
        self.finished = True

    def IsFinished(self):
        return self.finished

