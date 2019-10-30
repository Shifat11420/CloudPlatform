from CommandReaders.TCPReader import TCPReader
from Utilities.Const import *
from Utilities.FileUtil import expprint

def parseVSet(text):
    fcind = text.index(",")
    tsub = text[fcind+1:]
    vals = tsub.split(";")
    expprint("parsevset:"+str(text))
    v = []
    for x in range(0, len(vals)-1):
        vvals = vals[x].split(COMMA)
        subv = []
        for y in range(0, len(vvals)-1):
            subv.append(float(vvals[y]))
        v.append(subv)
    return v

class SwapTimesReader(TCPReader):
    def HandleLine(self, data):
        dbgprint("SwapTimesReader")
        v = []
        vals = data.split(COMMA)
        for x in range(1,len(vals) -1):
            v.append(float(vals[x]))
        self.context.VContainer.setSwapTimes(v)

class StasisVectorReader(TCPReader):
    def HandleLine(self, data):
        expprint("ReceiveStasisVector"+str(data))
        v = parseVSet(data)
        self.context.VContainer.setStasisVector(v)

class FlowVectorReader(TCPReader):
    def HandleLine(self, data):
        expprint("ReceiveFlowVector"+str(data))
        v = parseVSet(data)
        self.context.VContainer.setFlowVector(v)
