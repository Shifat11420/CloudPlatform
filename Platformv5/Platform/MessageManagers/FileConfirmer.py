from Utilities.Const import *

class FileConfirmer():
    def __init__(self, filelist, responsegen):
        self.filelist = []
        for val in filelist:
            v = GetFileNameFromPath(val)
            if(len(v) > 0):
                self.filelist.append(v)
        self.respgen = responsegen
        self.finished = False

    def FileResponded(self, filen, transp):
        dbgprint("File responded:"+filen)
        dbgprint("looking for:"+str(self.filelist))
        if filen in self.filelist:
            dbgprint("file in list")
            self.filelist.remove(filen)
            if len(self.filelist) == 0:
                dbgprint("list finished, responding")
                self.respgen.WriteResponse(transp)
                self.finished = True
                return False
        return True

    def IsFinished():
        return self.finished
