from CommandReaders.TCPReader import TCPReader

class TCPGetFile(TCPReader):
    def __init__(self, infilename, infolderpath, infilesize):
        self.filesize = infilesize
        self.filewritten = 0
        self.remainder = None
        self.filepath = ConcatePath(infolderpath, infilename)
        self.fileobject = None

    def HandleTCP(self, data):
        if self.remainder == None:
            if self.fileobject == None:
                self.fileobject = open(self.filepath, 'w')
            if self.filewritten + len(data) >= self.filesize:
                remain_ind = len(data) + self.filewritten - self.filesize
                writetofile = ""
                if remain_ind == 0:
                    writetofile = data
                    self.remainder = ""
                else:
                    writetofile = data[:-remain_ind]
                    self.remainder = data[-remain_ind:]
                self.fileobject.write(writetofile)
                self.fileobject.close()
                self.fileobject = None
            else:
                self.fileobject.write(data)
                self.filewritten += len(data)
        else:
            self.remainder += data


    def GetRemainder(self):
        return self.remainder

    def ConcatePath(v1, v2):
        if(not v1.endswith("/")):
            return v1 + "/" + v2
        return v1 + "/" + v2
