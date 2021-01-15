from CommandReaders.TCPReader import TCPReader
from DockerManagers.SubContManager import ContainerManager
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator
from Utilities.Const import *

class ContainerResponseReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(COMMA.encode('utf-8'))
        i = 1
        for val in vals:
            if(val.decode('utf-8') == FILENAME):
                filename = vals[i].decode('utf-8')
            if(val.decode('utf-8') == ID):
                idstr = vals[i].decode('utf-8')
            i = i + 1
        self.context.AddCompletedWorkFile(idstr, filename)

    #def GetResponse(self):
    #    return TerminateMessageGenerator(self.context)

class ContainerQueueReader(TCPReader):
    def HandleLine(self, line):
        vals = line.split(COMMA).encode('utf-8')
        i = 1
        for val in vals:
            if(val.decode('utf-8') == ID):
                self.context.MoveWorkToRealQueue(vals[i].decode('utf-8'))
            i = i + 1
        self.finished = True

    def IsFinished(self):
        return self.finished

    #def GetResponse(self):
    #    return TerminateMessageGenerator(self.context)

class ContainerReader(TCPReader):

    def HandleLine(self, line):
        vals = line.split(COMMA.encode('utf-8'))
        i = 1

        new_cont_args = None
        self.filecount = 0
        filenames = []
        for val in vals:
            if(val.decode('utf-8') == ARGS):
                new_cont_args = vals[i].decode('utf-8')
            elif(val.decode('utf-8') == FILECOUNT):
                self.filecount = int(vals[i].decode('utf-8'))
            elif(val.decode('utf-8') == ID):
                new_id = vals[i].decode('utf-8')
            elif(val.decode('utf-8') == SOURCEIP):
                source_ip = vals[i].decode('utf-8')
            elif(val.decode('utf-8') == ISDOCKER):
                if(vals[i].decode('utf-8') == "True"):
                    isdocker = True
                else:
                    isdocker = False
            elif(val.decode('utf-8') == SOURCEPORT):
                source_port = vals[i].decode('utf-8')
            elif(val.decode('utf-8')== FILENAMES):
                for j in range(i, len(vals)):
                    filenames.append(vals[j].decode('utf-8'))
            i = i + 1
        self.ContainerMgr = ContainerManager(new_cont_args, LocalizeFileNames(filenames), new_id, source_ip, source_port, isdocker, self.context)
        self.context.AddIncomingWork(self.ContainerMgr)
        
        self.finished = True

    def IsFinished(self):
        return self.finished

