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

        ##  Graph generation with Erdos-Renyi
        self.graphgen = GraphGen(self.expindex + self.graphseed)
        
        matrix = self.graphgen.ErdosRenyiConnected(self.node_count, self.prob_connected)

        # ##  Full graph Graph generation 
        # self.graphgen = GraphGen(self.expindex)
        
        # matrix = self.graphgen.fullgraphConnected(self.node_count)

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
############################# for converting bytedata to str
    # data = None
    # with open(in_filename, 'r') as jfile:                       ## commented out
    #     data = aload(jfile.read())                              ##
    # if(data is None):return None                                

    bytedata = None
    with open(in_filename, 'r') as jfile:
        bytedata = aload(jfile.read())                   ##
    if(bytedata is None):return None                      ##

    data = {}
    for key, value in bytedata.items():
            #print("type of data key", type(key))             #bytes
            key  = key.decode('utf-8') 
            #print("type of new data key", type(key))          #str
            
            if type(value) == dict:
                dict1 = {}
                for key1, val in value.items():
                    key1  = key1.decode('utf-8') 
                    
                    if type(val) == list:
                        list0 = []
                        for i in range(len(val)):
                            val[i]=val[i].decode('utf-8')
                            #print("second===", key1 , val[i]) 
                            list0.append(val[i])
                            dict1[key1] = list0
                        
                    else:
                        val = val.decode('utf-8')      
                        #print("third===", key1 , val) 
                        dict1[key1] = val
                data[key] = dict1 
            elif type(value) == list:
                list1 = []
                for i in range(len(value)):
                    if type(value[i]) == list:
                        list2 = []
                        for k in range(len(value[i])):
                            value[i][k] = value[i][k].decode('utf-8')
                            #print("fourth===", key , value[i][k])
                            list2.append(value[i][k])
                        list1.append(list2)
                        data[key] = list1
                    else:
                        value[i] = value[i].decode('utf-8')   
                        #print("fifth===", key , value[i])
                        list1.append(value[i])
                        data[key] = list1
            else:
                value = value.decode('utf-8')      
                #print("first===", key , value)              
                data[key] = value

######################

    vals = []
    lofl = []
    if data.get("vec_stases") is not None:            ##            syntax changes
        #for l in data['vec_stases']:
        for l in data.get("vec_stases"):                 ##fix to avoid key error
            for v in l:
                vals.append(float(v))
            lofl.append(vals)
            vals = []
    retval.vec_stases = lofl
    lofl = []
    vals = []
    if data.get("vec_flows") is not None:          ##
        #for l in data['vec_flows']:
        for l in data.get("vec_flows"):                         ##fix to avoid key error
            for v in l:
                vals.append(float(v))
            lofl.append(vals)
            vals = []
    retval.vec_flows = lofl

    vals = []
    if data.get("swapTimes") is not None:          ##                  syntax changes
        for v in data.get("swapTimes"):                            ##fix to avoid key error
        #for v in data['swapTimes']:
            vals.append(float(v))
    retval.swapTimes = vals
    #retval.expectedTime = float(data['expectedTime'])
    retval.node_count = int(data.get("node_count"))                        ##
    retval.prob_work_alloc = float(data.get("prob_work_alloc"))                ##
    retval.prob_connected = float(data.get("prob_connected"))               ##
    retval.exp_time = int(data.get("exp_time"))                            ##           syntax changes
    retval.container_count = int(data.get("container_count"))               ##
    retval.graphseed = int(data.get("graphseed"))                             ##
    
    #retval.cp_args = data['container_params']['args']
    retval.cp_args = (data.get("container_params")).get("args")               ##
    #retval.cp_files = data['container_params']['files']
    retval.cp_files = (data.get("container_params")).get("files")             ## syntax changes
    
    #if(data['container_params']['isdocker'] == "True"):
    if((data.get("container_params")).get("isdocker") == "True"):
        retval.cp_isdocker = True
    else:
        retval.cp_isdocker = False
    return retval
