from Utilities.Const import *
from Utilities.FileUtil import expprint
from datetime import datetime

class VectorContainer():
    def __init__(self):
        #vector is qlen in x, bench in y
        #we want to move towards smaller queuelen, larger bench?? why larger bench
        self.flowvector = []

        #this will be added to improve local node score and avoid movement
        self.stasisvector = []

        self.swapTimes = []

        self.starttime = None
        self.expectedComp = 1.0

    def getFlowVector(self):
        ntime = datetime.now()
        difftime = ntime - self.starttime
        expprint("GETFLOW_STIME:"+str(self.starttime))
        expprint("GETFLOW_NTIME:"+str(ntime))
        expprint("GETFLOW_diffsec:"+str(difftime.total_seconds()))
        
        for x in range(len(self.swapTimes)):
            if(self.swapTimes[x] > difftime.total_seconds()):
                expprint("GETFLOW_ind:"+str(x))
                return self.flowvector[x]
        expprint("GETFLOW_ind:last")
        return self.flowvector[len(self.flowvector)-1]

    def getStasisVector(self):
        ntime = datetime.now()
        difftime = ntime - self.starttime
        for x in range(len(self.swapTimes)):
            if(self.swapTimes[x] > difftime.total_seconds()):
                return self.stasisvector[x]
        return self.stasisvector[len(self.stasisvector)-1]

    def setSwapTimes(self, v_input):
        
        self.swapTimes = v_input
    
    def setFlowVector(self, v_input):
        self.flowvector = v_input
                
    def setStasisVector(self, v_input):
        self.stasisvector = v_input
