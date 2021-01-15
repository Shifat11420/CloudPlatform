from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator
import os

class FileMessageGenerator(MessageGenerator):
    def __init__(self, a_filepath, in_context):
        MessageGenerator.__init__(self, in_context)
        self.filepath = a_filepath
        self.fhandler = None
        dbgprint("FMR:created:"+a_filepath)
        self.filesize = os.path.getsize(self.filepath)
        self.command = COMMAND_RECEIVEFILE
        self.extra = ""

    def reset(self):
        MessageGenerator.reset(self)
        self.fhandler = None

    def read(self):
        if(self.fhandler == None):
            strval = self.command
            strval += COMMA + FILENAME 
            strval += COMMA + str(GetFileNameFromPath(self.filepath))

            strval += self.extra
            
            strval += COMMA + FILESIZE
            strval += COMMA + str(self.filesize)
            strval += COMMA + LINEDELIM
            self.fhandler = open(self.filepath, 'rb')
            dbgprint("FMG:opened file at "+self.filepath)
            if(self.fhandler is None):
                dbgprint("FMG:PROBLEM!")
            return strval

        val = self.fhandler.read(FILECHUNK).decode('utf-8')
        if(not val):
            self.fhandler.close()
            self.fhandler = None
            val = None
        return val


class TGObligFMG(FileMessageGenerator):
    def __init__(self, a_filepath, in_context, a_taskid):
        FileMessageGenerator.__init__(self, a_filepath, in_context)
        self.taskid = a_taskid
        self.command = COMMAND_RECEIVETASKOBLIG
        self.extra = COMMA + TASKID + COMMA + self.taskid
