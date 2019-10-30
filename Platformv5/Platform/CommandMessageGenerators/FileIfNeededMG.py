from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
import os

class INeedFileMG(StringMessageGenerator):
    def __init__(self, a_filename, in_context):
        self.filename = a_filename
        strval = COMMAND_INEEDFILE
        strval += COMMA + FILENAME
        strval += COMMA + self.filename
        strval += COMMA + LINEDELIM
        StringMessageGenerator.__init__(self, strval, in_context)

    def OneShot(self):return False

class DoYouNeedFileMG(StringMessageGenerator):
    def __init__(self, a_filepath, in_context):
        self.filename = GetFileNameFromPath(a_filepath)
        dbgprint("DYNFMG")
        dbgprint("a_filepath:"+str(a_filepath))
        dbgprint("self.filename:"+str(self.filename))
        if(len(self.filename) == 0):
            raise Exception("Stop this from happening")
        strval = COMMAND_DOYOUNEEDFILE
        strval += COMMA + FILENAME
        strval += COMMA + self.filename
        strval += COMMA + LINEDELIM
        StringMessageGenerator.__init__(self, strval, in_context)

    def OneShot(self):return False

class IHaveFileMG(StringMessageGenerator):
    def __init__(self, a_filepath, in_context):
        self.filename = GetFileNameFromPath(a_filepath)
        strval = COMMAND_IHAVEFILE
        strval += COMMA + FILENAME
        strval += COMMA + self.filename
        strval += COMMA + LINEDELIM
        StringMessageGenerator.__init__(self, strval, in_context)
    
