from CommandMessageGenerators.NeighborMessageGenerator import AddNeighborMessageGenerator
from CommandMessageGenerators.ComboMsgGen import ComboGen
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from CommandMessageGenerators.VectorMGen import StasisVectorMGen, FlowVectorMGen, SwapTimesMGen
from CommandMessageGenerators.QueueLenMessageGenerator import SendExpectCompTime
import json
from Utilities.jsonfixer import aload
from Utilities.Const import *
from DockerManagers.SubContManager import ContainerManager
from DockerManagers.TGManager import TGManager
#from twisted.python.compat import xrange                              ##added import
from numpy.random.tests import data                                   ##added import
from ExpDefinitions.BenchDefinition import BenchDefinition            ##added import

class TaskGraphDefinition():
    def __init__(self):
        self.node_count = 0
        self.time = 0
        self.graph = []
        self.container_managers = {}
        self.work_alloc = {}
        self.vec_stases = []
        self.vec_flows = []
        self.swapTimes = []
        self.expectedTime = 0.0
    
    #expnodes is a dict of id : Locations
    def startExperiment(self, context, expnodes):
        if(len(expnodes) < len(self.graph)):
            dbgprint("PROBLEM:len(expnodes) < len(self.graph):"+str(len(expnodes)) + ":" + str(len(self.graph)))
            pass
        else:
        
            nids = []
            for nid in expnodes:
                nids.append(nid)
            for i in range(0, len(self.graph)):                        ##xrange in python2 to range in python3
                neighbors = self.graph[i]
                mgens = []
                for neigh in neighbors:
                    neigh_id = nids[neigh]
                    neigh_ip = expnodes[neigh_id].ip
                    neigh_port = expnodes[neigh_id].port
                    mgen = AddNeighborMessageGenerator(context, neigh_ip, neigh_port, neigh_id)
                    mgens.append(mgen)
                mgen = SendExpectCompTime(context, self.expectedTime)
                mgens.append(mgen)
                mgen = SwapTimesMGen(context, self.swapTimes)
                mgens.append(mgen)
                mgen = FlowVectorMGen(context, self.vec_flows)
                mgens.append(mgen)
                mgen = StasisVectorMGen(context, self.vec_stases)
                mgens.append(mgen)
                cbgen = ComboGen(context, mgens)
                context.msgmon.sendGen(cbgen, expnodes[nids[i]].ip, expnodes[nids[i]].port)

            dbgprint("work_alloc_len:"+str(len(self.work_alloc)))
            for nodeindex in self.work_alloc:
                neigh_id = nids[nodeindex]
                neigh_ip = expnodes[neigh_id].ip
                neigh_port = int(expnodes[neigh_id].port)
                mgens = []
                for cont_id in self.work_alloc[nodeindex]:
                    dbgprint("cmtofind:" + str(cont_id))
                    self.container_managers[cont_id].context = context
                    self.container_managers[cont_id].work_source_ip = neigh_ip
                    self.container_managers[cont_id].work_source_port = neigh_port
                    self.container_managers[cont_id].SetAllPredSucc(neigh_ip, neigh_port)
                    cmgen = self.container_managers[cont_id].Package()
                    context.msgmon.sendGen(cmgen, neigh_ip, neigh_port)
                    #mgens.append(cmgen)
                #cbgen = ComboGen(context, mgens)
                #context.msgmon.sendGen(cbgen, neigh_ip, neigh_port)
            
def benchBuildFromFile(in_filename):

    retval = BenchDefinition()

    with open(in_filename, 'r') as jfile:
        retval.data = aload(jfile.read())
    if(retval.data is None):return None

    #so at the top level the file has kv pairs
    #   node_count  value is int
    #   exp_time - value is int 
    #   graph - value is list of lists
    #   containers - value is dictionary
    #      args - exact argument to call to start work
    #      files - files to possess.  First file must be zip which can be docker loaded
    #      idstr - string that uniquely identifies work
    #   work_alloc - list of lists.  sub lists start with node index, other elements are container idstrs

    vals = []
    lofl = []
    for l in data['vec_stases']:
        for v in l:
            vals.append(float(v))
        lofl.append(vals)
        vals = []
    retval.vec_stases = lofl
    vals = []
    lofl = []
    
    for l in data['vec_flows']:
        for v in l:
            vals.append(float(v))
        lofl.append(vals)
        vals = []
    retval.vec_flows = lofl
    
    #for v in data['vec_flow_end']:
    #    vals.append(float(v))
    #retval.vec_flow_end = vals

    vals = []
    for v in data['swapTimes']:
        vals.append(float(v))
    retval.swapTimes = vals
    retval.node_count = int(retval.data['node_count'])
    retval.time = int(retval.data['exp_time'])
    retval.graph = [[int(x) for x in y] for y in retval.data['graph']]



    
    for contset in retval.data['containers']:
        cm = ContainerManager(contset['args'], contset['files'], contset['idstr'], '','0', contset['isdocker'],  None)
        dbgprint("cmid:" + str(cm.idstr))
        retval.container_managers[cm.idstr] = cm

    
        
    for alloc in retval.data['work_alloc']:
        nodeind = int(alloc[0])
        retval.work_alloc[nodeind] = []
        for val in range(1, len(alloc)):                             ## python 2 xrange to python3 range
            retval.work_alloc[nodeind].append(alloc[val])
    return retval
    #retval.graph.append([int(x) for x in retval.data['graph']
    
    # with open(in_filename, 'r') as in_file:
    #     mode = 0
    #     i = 0
    #     for line in in_file:
    #         if ( i == 0):
    #             retval.node_count = int(line)
    #         elif (i == 1):
    #             retval.time = int(line)
    #         else:
    #             if(line == "WORK"):
    #                 mode = 1
    #             elif (mode == 0):
    #                 retval.graph.append([int(x) for x in line.split(",")])
    #             else:
                    
                
    #         i = i + 1
    # return retval
