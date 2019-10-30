from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.FileIfNeededMG import IHaveFileMG
from Utilities.Const import *

class TCPFileDataReader(TCPReader):
    def __init__(self, in_filepath, in_filesize, sub_file_count, in_context, in_taskid=""):
        TCPReader.__init__(self, in_context)
        self.filehandler = open(in_filepath, 'wb')
        self.filesize = int(in_filesize)
        self.writtenbytecount = 0
        self.finished = False
        self.remainder = None
        self.filename = GetFileNameFromPath(in_filepath)
        self.sub_file_count = sub_file_count
        self.taskid = in_taskid

    def HandleLine(self, line):
        towrite = self.filesize - self.writtenbytecount
        if(towrite >= len(line)):
            self.writtenbytecount += len(line)
            self.filehandler.write(line)
            if(towrite == len(line)):
                self.filehandler.close()
                self.finished = True
                self.remainder = None
        else:
            valtowrite = line[:towrite]
            leftover = line[towrite:]
            self.filehandler.write(valtowrite)
            self.filehandler.close()
            self.finished = True
            self.remainder = leftover

    def SetToRaw(self):
        return False

    def IsFinished(self):
        return self.finished

    def GetRemainder(self):
        return self.remainder

    def GetResponse(self):
        if(self.taskid == ""):
            return IHaveFileMG(self.filename, self.context)
        else:
            return IHaveObligMG(self.context, self.taskid, self.filename)

    def GetNextHandler(self):
        if(self.sub_file_count == 0):
            return None
        else:
            nfc = self.sub_file_count -1
            return TCPFileReader(self.context, nfc)

class TCPFileReader(TCPReader):

    def __init__(self, in_context, sub_file_count=0):
        TCPReader.__init__(self, in_context)
        self.finished = False
        self.sub_file_count = sub_file_count
        dbgprint("TCPFileReader created")
        self.taskid = ""

    def HandleLine(self, line):
        vals = line.split(COMMA)
        i = 0
        for val in vals:
            if(val == FILENAME):
                self.filename = vals[i+1]
            if(val == FILESIZE):
                self.filesize = vals[i+1]
            if(val == TASKID):
                self.taskid = vals[i+1]
            i = i + 1
        self.finished = True

    def SetToRaw(self):
        return True

    def IsFinished(self):
        return self.finished

    def GetNextHandler(self):
        return TCPFileDataReader(GetFilePath(self.filename), self.filesize, self.sub_file_count, self.context, self.taskid)
