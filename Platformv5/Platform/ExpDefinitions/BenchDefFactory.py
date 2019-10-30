import random
import json
from Utilities.Const import *
from Utilities.jsonfixer import aload
from Graph.GraphGen import GraphGen
from ExpDefinitions.BenchDefinition import BenchDefinition

from DockerManagers.SubContManager import ContainerManager

class BenchDefFactory():
    def __init__(self, in_expindex):
        self.expindex = int(in_expindex)
        self.node_count = 0
        self.prob_work_alloc = 0.0
        self.prob_connected = 0.0
        self.exp_time = 0
        self.container_count = 0
        self.cp_args = ""
        self.cp_files = ""
        self.cp_isdocker = True
        self.vec_stases = []
        self.vec_flows = []
        self.graphseed = 0
        self.swapTimes = []
        #self.expectedTime = 0.0

    def build(self):
        retval = BenchDefinition()
        retval.time = self.exp_time
        retval.node_count = self.node_count
        retval.vec_stases = self.vec_stases
        retval.vec_flows = self.vec_flows
        #retval.expectedTime = self.expectedTime
        retval.swapTimes = self.swapTimes
        self.graphgen = GraphGen(self.expindex + self.graphseed)
        
        matrix = self.graphgen.ErdosRenyiConnected(self.node_count, self.prob_connected)

        print("GeneratedGraph")
        print(matrix)
        print("EndGeneratedGraph")

        workstarters = []
        for x in range(len(matrix)):
            retval.work_alloc[x] = []
            if(random.random() < self.prob_work_alloc):
                workstarters.append(x)
            retval.graph.append([])
            for key in matrix[x]:
                if(matrix[x][key]):
                    retval.graph[x].append(key)

        if(len(workstarters) == 0):
            workstarters.append(0)

        for x in range(self.container_count):
            cm = ContainerManager(self.cp_args,self.cp_files,str(x), '','0', self.cp_isdocker, None)
            dbgprint("cmid:" + str(cm.idstr))
            retval.container_managers[cm.idstr] = cm
            wind = random.randint(0, len(workstarters)-1)
            retval.work_alloc[workstarters[wind]].append(str(x))

        return retval

def BFFromFile(in_filename, expindex):

    retval = BenchDefFactory(expindex)

    data = None
    with open(in_filename, 'r') as jfile:
        data = aload(jfile.read())
    if(data is None):return None

    vals = []
    lofl = []
    for l in data['vec_stases']:
        for v in l:
            vals.append(float(v))
        lofl.append(vals)
        vals = []
    retval.vec_stases = lofl
    lofl = []
    vals = []
    for l in data['vec_flows']:
        for v in l:
            vals.append(float(v))
        lofl.append(vals)
        vals = []
    retval.vec_flows = lofl

    vals = []
    for v in data['swapTimes']:
        vals.append(float(v))
    retval.swapTimes = vals
    #retval.expectedTime = float(data['expectedTime'])
    retval.node_count = int(data['node_count'])
    retval.prob_work_alloc = float(data['prob_work_alloc'])
    retval.prob_connected = float(data['prob_connected'])
    retval.exp_time = int(data['exp_time'])
    retval.container_count = int(data['container_count'])
    retval.graphseed = int(data['graphseed'])
    
    retval.cp_args = data['container_params']['args']
    retval.cp_files = data['container_params']['files']
    if(data['container_params']['isdocker'] == "True"):
        retval.cp_isdocker = True
    else:
        retval.cp_isdocker = False
    return retval
