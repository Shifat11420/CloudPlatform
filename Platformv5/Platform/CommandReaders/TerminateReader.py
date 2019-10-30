from CommandReaders.TCPReader import TCPReader
from Utilities.Const import 

class TerminateReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("Terminate Read!")
        self.context.terminate = True
