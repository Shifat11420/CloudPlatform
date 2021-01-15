from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator
from CommandMessageGenerators.FileMessageGenerator import FileMessageGenerator
import os

class ResponseMessageGenerator(MessageGenerator):
    def __init__(self, a_id, a_filepath, in_context):
        MessageGenerator.__init__(self, in_context)
        self.filepath = a_filepath
        self.idstr = str(a_id)
        self.finished = False
        self.filemgr = None

    def reset(self):
        MessageGenerator.reset(self)
        self.finished = False
        self.filemgr = None

    def read(self):
        if(self.finished):
            return None
        if(self.filemgr == None):
            self.filemgr = FileMessageGenerator(self.filepath, self.context)
        val = self.filemgr.read()
        if(val == None):
            strval = COMMAND_CONTAINERRESPONSE
            strval += COMMA + ID
            strval += COMMA + self.idstr
            strval += COMMA + FILENAME
            strval += COMMA + GetFileNameFromPath(self.filepath)
            strval += COMMA + LINEDELIM
            self.finished = True
            return strval
        return val
