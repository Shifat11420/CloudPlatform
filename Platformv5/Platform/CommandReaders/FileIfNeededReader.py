from Utilities.Const import *
from CommandReaders.TCPReader import TCPReader
from CommandMessageGenerators.FileIfNeededMG import INeedFileMG, IHaveFileMG
from CommandMessageGenerators.FileMessageGenerator import FileMessageGenerator
import os.path

class FileNameReader(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA.encode('utf-8'))
        i = 1
        for val in vals:
            if(val.decode('utf-8') == FILENAME):
                self.filename = vals[i].decode('utf-8')
            i = i + 1

class IHaveFileReader(FileNameReader):

    def WriteResponse(self, transp):
        self.context.ReactorFileSent(self.filename, transp)

class INeedFileReader(FileNameReader):

    def GetResponse(self):
        dbgprint("INFR:"+self.filename)
        filepath = GetFilePath(self.filename)
        return FileMessageGenerator(filepath, self.context)

class DoYouNeedFileReader(FileNameReader):

    def GetResponse(self):
        filepath = GetFilePath(self.filename)
        fileexists = os.path.exists(filepath)
        if not fileexists:
            return INeedFileMG(self.filename, self.context)
        return IHaveFileMG(self.filename, self.context)
