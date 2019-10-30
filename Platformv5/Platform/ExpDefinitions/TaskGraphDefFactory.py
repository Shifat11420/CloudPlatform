
import random
import json
from Utilities.Const import *
from Utilities.jsonfixer import aload
from Graph.GraphGen import GraphGen
from ExpDefinitions.BenchDefinition import BenchDefinition
from ExpDefinitions.TaskGraphDefinition import TaskGraphDefinition

from DockerManagers.SubContManager import ContainerManager
from DockerManagers.TGManager import TGManager

class TaskGraphDefFactory():
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
        self.tg_mat_dim = 0
        self.tg_prob_connected = 0.0
        self.tg_args = ""
        self.tg_files = ""
        self.tg_isdocker = False
        self.tg_outfilenames = []

    def build(self):
        retval = TaskGraphDefinition()
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

        jcv = 0
        for x in range(self.container_count):
            cm = ContainerManager(self.cp_args,self.cp_files,str(jcv), '','0', self.cp_isdocker, None)
            jcv += 1
            dbgprint("cmid:" + str(cm.idstr))
            retval.container_managers[cm.idstr] = cm
            wind = random.randint(0, len(workstarters)-1)
            retval.work_alloc[workstarters[wind]].append(str(jcv))


        priorityd = {}
        p_to_s = {}
        s_to_p = {}
        for x in range(self.tg_mat_dim):
            for y in range(self.tg_mat_dim):
                maxp = 0
                p_to_s[(x,y)] = []
                s_to_p[(x,y)] = []
                if(x - 1 >= 0):
                    if(y - 1 >= 0):
                        if(random.random() < self.tg_prob_connected):
                            dbgprint("Dep:From:"+str(x-1)+","+str(y-1))
                            dbgprint("Dep:To:"+str(x)+","+str(y))
                            maxp = max(maxp, priorityd[(x-1,y-1)]+1)
                            p_to_s[(x-1,y-1)].append((x,y))
                            s_to_p[(x,y)].append((x-1,y-1))
                    if(random.random() < self.tg_prob_connected):
                        dbgprint("Dep:From:"+str(x-1)+","+str(y))
                        dbgprint("Dep:To:"+str(x)+","+str(y))
                        maxp = max(maxp, priorityd[(x-1,y)]+1)
                        p_to_s[(x-1,y)].append((x,y))
                        s_to_p[(x,y)].append((x-1,y))
                if(y - 1 >= 0):
                    if(random.random() < self.tg_prob_connected):
                        dbgprint("Dep:From:"+str(x)+","+str(y-1))
                        dbgprint("Dep:To:"+str(x)+","+str(y))
                        maxp = max(maxp, priorityd[(x,y-1)]+1)
                        p_to_s[(x,y-1)].append((x,y))
                        s_to_p[(x,y)].append((x,y-1))
                priorityd[(x,y)] = maxp
                    

        tgmsdict = {}
        #conns will have key that is pred to value that is succ.
        for x in range(self.tg_mat_dim):
            for y in range(self.tg_mat_dim):
                tgm = TGManager(self.tg_args, self.tg_files, str(jcv), '','0', self.tg_isdocker, "0", None, [], 0, priorityd[(x,y)])
                dbgprint("PRIORITY:"+str(priorityd[(x,y)]) + ":" + str(tgm.idstr))

                tgmsdict[(x,y)] = tgm
                #following may be wrong
                dbgprint("cmid:" + str(tgm.idstr))
                retval.container_managers[tgm.idstr] = tgm
                wind = random.randint(0, len(workstarters)-1)
                retval.work_alloc[workstarters[wind]].append(str(jcv))
                jcv += 1

        for x in range(self.tg_mat_dim):
            for y in range(self.tg_mat_dim):
                for predloc in s_to_p[(x,y)]:
                    dbgprint("Adding pred to :"+str(x)+","+str(y))
                    predid = tgmsdict[predloc].idstr
                    tgmsdict[(x,y)].requirements[predid] = None
                    tgmsdict[(x,y)].pred_locations[predid] = []
                for succloc in p_to_s[(x,y)]:
                    dbgprint("Adding succ to :"+str(x)+","+str(y))
                    succid = tgmsdict[succloc].idstr
                    dbgprint("DEP:"+tgmsdict[(x,y)].idstr+":"+succid)
                    tgmsdict[(x,y)].succ_locations[succid] = []
            
        return retval

def TGFFromFile(in_filename, expindex):

    retval = TaskGraphDefFactory(expindex)

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
    print("DEF:cp_files:"+str(retval.cp_files))
    if(data['container_params']['isdocker'] == "True"):
        retval.cp_isdocker = True
    else:
        retval.cp_isdocker = False


    retval.tg_args = data['taskgraph_job_params']['args']
    retval.tg_files = data['taskgraph_job_params']['files']
    if(data['taskgraph_job_params']['isdocker'] == "True"):
        retval.tg_isdocker = True
    else:
        retval.tg_isdocker = False

    retval.tg_mat_dim = int(data['taskgraph_params']['matrix_dim'])
    retval.tg_prob_connected = float(data['taskgraph_params']['prob_connected'])
    
    
    return retval
