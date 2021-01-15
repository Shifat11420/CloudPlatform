from Utilities.Const import *
from DockerManagers.SubContManager import StartContainer
from CommandReaders.TCPReader import TCPReader

class JobReader(TCPReader):

    def BuildCommandStringArray(self):
        strarr = ['docker', 'run']
        strarr.append(self.imagename)
        strarr.append(self.command)
        strarr.append('"'+self.args+'"')
        return ' '.join(strarr)

    def __init__(self):
        self.finished = False

    def HandleLine(self, line):
        vals = line.split(COMMA.encode('utf-8'))
        i = 0
        for val in vals:
            if(val.decode('utf-8') == IMAGE):
                self.imagename = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == ARGS):
                self.args = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == COMMAND):
                self.command = vals[i+1].decode('utf-8')
            if(val.decode('utf-8') == ARGSFILE):
                f = open(GetFilePath(val.decode('utf-8')), 'r')
                self.args = f.read()
                f.close()
            i = i + 1

        cmd_str = self.BuildCommandStringArray()
        dbgprint(str(cmd_str))
        StartContainer(cmd_str)
        self.finished = True

    def SetToRaw(self):
        return False

    def IsFinished(self):
        return self.finished

    def GetNextHandler(self):
        return None
