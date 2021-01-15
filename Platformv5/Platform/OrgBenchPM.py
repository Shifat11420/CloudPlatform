from BenchNodePM import BenchNodePM

DEFAULT_CONN_THRESHOLD = 1.0
DEFAULT_MAX_GROUP_SIZE = 5

class OrgBenchPM(BenchNodePM):
    
    def __init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn=False):
        BenchNodePM.__init__(self, in_my_IP, in_my_Port, exp_ip, exp_port, ManagerOn)
        
        self.groupid = self.idval

        self.leadid = self.idval
        self.leadip = ""
        self.leadport = 0

        self.childids = []
        self.childips = {}
        self.childports = {}

        self.connthreshold = DEFAULT_CONN_THRESHOLD
        self.groupsize = 1
        self.maxgroupsize = DEFAULT_MAX_GROUP_SIZE

        #self.                                        ##

    def SetMaxGroupSize(self, newsize):
        self.groupsize = newsize

    def SetConnThreshold(self, newthreshold):
        self.connthreshold = newthreshold

    #def                                        ## 
