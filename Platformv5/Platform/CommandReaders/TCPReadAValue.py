from CommandReaders.TCPReader import TCPReader

class TCPReadAValue(TCPReader):

    def __init__(self, indelim):
        self.remainder = None
        self.value = None
        self.delim = indelim
        self.buf = ""

    def HandleTCP(self, data):
        if self.remainder == None:
            self.buf += data
            if(self.buf.find(self.delim)):
                delimind = self.buf.find(self.delim)
                self.value = self.buf[:delimind]
                self.remainder = self.buf[delimind+1:]
        else:
            self.remainder += self.buf

    
    def GetRemainder(self):
        return self.remainder

    def GetValue(self):
        return self.value

class TCPGetValue():
    def __init__(self, indelim):
        self.delim = indelim
        self.reader = None
        self.lastrem = ""
        
    def GetValue(self, data, notdoneval):                     ##added self
        if(self.reader == None):
            self.reader = TCPReadAValue(self.delim)
            data = self.lastrem + data
            self.lastrem = ""
        self.reader.HandleTCP(data)
        if(self.reader.GetRemainder() != None):
            self.lastrem = self.reader.GetRemainder()
            val = self.reader.GetValue()
            self.reader = None
            return val
        return notdoneval

    def GetRemainder(self):                 ##added self
        return self.lastrem
