from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.MessageRepeat import MsgMonitor
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from CommandMessageGenerators.AsktosleepExpMGen import AsktosleepExpNode
from CommandMessageGenerators.LatencyReportGenerator import LatencyReportNode
from CommandMessageGenerators.DropNbrbyLatencyMGen import DropNeighborMessageGenerator
from CommandMessageGenerators.PauseUnpauseMessageGenerator import TimeUnpauseMessageGenerator
from ExpDefinitions.ExpFactory import BuildExpDef
from Utilities.Const import *
from Utilities.Location import Location
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import SetOutputFolder, expprint
from datetime import datetime, timedelta
import threading
import time
import sys
import os              ##
from PlatformManager import PlatformManager
import re
import ast
import scipy.cluster.hierarchy
import scipy.spatial.distance as ssd
import numpy as np


listofbenches = []
portlist = []
lowPerformersDict = {}
listoflatencies = []
list_dictoflatencies = []
listIDtosend = []      #for MST
num_clusters = 9


class ExpPlatformManager(PlatformManager):
    def __init__(self, in_my_IP, in_my_Port, in_expdef, location, ManagerOn=True):
        PlatformManager.__init__(self, in_my_IP, in_my_Port, location)
        self.managerOn = ManagerOn
        self.expnodes = {}
        self.expnodeslock = threading.Lock()
        self.expdef = in_expdef
        self.exp_nodes_reported = False
        self.starttime =None
        self.expstarted = False
        self.logsgathered = False
        self.termsent = False
        dbgprint("Created Exp PM")

    def ExpManagerRun(self):
        #from Utilities.Const import *                               ##
        from datetime import datetime, timedelta
        dbgprint("EMR: " + str(self.exp_nodes_reported) + ":" + str(self.expdef is None))
        if(self.exp_nodes_reported or self.expdef is None):
            pass
        else:
            with self.expnodeslock:
                dbgprint("  "+str(len(self.expnodes)) + ":" + str(self.expdef.node_count))
                if(len(self.expnodes) >= self.expdef.node_count):
                    self.exp_nodes_reported = True
            if(self.exp_nodes_reported):
                self.startExperiment()
                self.starttime = datetime.now()
                self.expstarted = True

    def ManagerThreadRun(self):
        import time
        from datetime import datetime, timedelta
        #from Utilities.Const import *                     ##
        dbgprint("good way")
        self.terminate = False
        time.sleep(1)
        while(True):
            time.sleep(MANAGERCHECKTIME)
            if(self.termsent):
                dbgprint("Checking term")
                now = datetime.now()
                td = now - self.starttime
                if(td.total_seconds() > TERMTIME):
                    self.terminate = True
                    self.SafeStopServer()
                    self.dumpLogToStdOut()
                    break
            elif(self.logsgathered):
                dbgprint("checking log in")
                now = datetime.now()
                td  = now - self.starttime
                if(td.total_seconds() > LOGTIME):
                    self.compilelogs()
                    self.TerminateAll()
                    self.termsent = True
                    self.starttime = now
            elif(self.expstarted):
                dbgprint("checking exp")
                now = datetime.now()
                td = now - self.starttime
                dbgprint("current " + str(td.total_seconds()))
                dbgprint("bound   " + str(self.expdef.time))
                if(td.total_seconds() > self.expdef.time):
                    #self.GatherLogs()
                    self.logsgathered = True
                    self.starttime = now
            else:
                self.ExpManagerRun()
                

    def AddExpNode(self, newid, newip, newport, newlocation):
        #from Utilities.Const import *                   ##
        from Utilities.Location import Location
        with self.expnodeslock:
            self.expnodes[newid] =Location(newip, newport, newlocation)
        

#?
    def LatencyReportExpNode(self, node_id, node_ip, node_port, slowest_id, max_latency, NeighborsLatencyDictall): #, NeighborsLatencyList):   
        nodesPORTStodrop = []
        nbrtokeepports = []
        dict_dropnodes = {}
        list11 = []
        list12 = []
        list13 = []
        list14 = []
        list15 = []
        list16 = []
        list17 = []
        list18 = []
        list19 = []
        

        with self.expnodeslock:
            for key in self.expnodes:
                loc = self.expnodes[key]       

##?    algo   Algorithm by manually defining clusters      
                # if str(loc.port) == str(node_port): 
                #     NeighborsLatencyDictall= ast.literal_eval(str(NeighborsLatencyDictall))
                #     dbgprint("Dictionary for port "+str(loc.port)+" is : "+str(NeighborsLatencyDictall))
                #     for key, value in NeighborsLatencyDictall.items():
                #         if str(key) == str(loc.port):
                #             pass
                #         ###      for physical machines experiments only   ###
                #         elif str(key).startswith("110"):
                #             list11.append(value[0])
                #         elif str(key).startswith("120"):
                #             list12.append(value[0]) 
                #         elif str(key).startswith("130"):
                #             list13.append(value[0])        
                #         elif str(key).startswith("140"):
                #             list14.append(value[0])
                #         elif str(key).startswith("150"):
                #             list15.append(value[0]) 
                #         elif str(key).startswith("160"):
                #             list16.append(value[0]) 
                #         elif str(key).startswith("170"):
                #             list17.append(value[0])
                #         elif str(key).startswith("180"):
                #             list18.append(value[0]) 
                #         elif str(key).startswith("190"):
                #             list19.append(value[0])         
                        
                #         # ##      for virtual machines experiments only   ###
                #         # elif str(key).startswith("110") or str(key).startswith("120") or str(key).startswith("130") or str(key).startswith("140") or str(key).startswith("150"):
                #         #     list11.append(value[0])
                #         # elif str(key).startswith("160") or str(key).startswith("170") or str(key).startswith("180") or str(key).startswith("190") or str(key).startswith("200"):
                #         #     list12.append(value[0]) 
                #         # elif str(key).startswith("210") or str(key).startswith("220") or str(key).startswith("230") or str(key).startswith("240") or str(key).startswith("250"):
                #         #     list13.append(value[0])        
                #         # elif str(key).startswith("260") or str(key).startswith("270") or str(key).startswith("280") or str(key).startswith("290") or str(key).startswith("300"):
                #         #     list14.append(value[0])
                #         # elif str(key).startswith("310") or str(key).startswith("320") or str(key).startswith("330") or str(key).startswith("340") or str(key).startswith("350"):
                #         #     list15.append(value[0]) 
                #         # elif str(key).startswith("360") or str(key).startswith("370") or str(key).startswith("380") or str(key).startswith("390") or str(key).startswith("400"):
                #         #     list16.append(value[0]) 
                #         # elif str(key).startswith("410") or str(key).startswith("420") or str(key).startswith("430") or str(key).startswith("440") or str(key).startswith("450"):
                #         #     list17.append(value[0])
                #         # elif str(key).startswith("460") or str(key).startswith("470") or str(key).startswith("480") or str(key).startswith("490") or str(key).startswith("500"):
                #         #     list18.append(value[0]) 
                #         # elif str(key).startswith("510") or str(key).startswith("520") or str(key).startswith("530") or str(key).startswith("540") or str(key).startswith("550") or str(key).startswith("560"):
                #         #     list19.append(value[0])         
                    
                #     list11 = sorted(list11)
                #     list12 = sorted(list12)
                #     list13 = sorted(list13)
                #     list14 = sorted(list14)
                #     list15 = sorted(list15)
                #     list16 = sorted(list16)
                #     list17 = sorted(list17)
                #     list18 = sorted(list18)
                #     list19 = sorted(list19)
                #     dbgprint("list11 = "+str(list11))     
                #     dbgprint("list12 = "+str(list12))     
                #     dbgprint("list13 = "+str(list13))     
                #     dbgprint("list14 = "+str(list14))     
                #     dbgprint("list15 = "+str(list15))     
                #     dbgprint("list16 = "+str(list16))     
                #     dbgprint("list17 = "+str(list17))     
                #     dbgprint("list18 = "+str(list18))     
                #     dbgprint("list19 = "+str(list19))     
                    

                #     for key, value in NeighborsLatencyDictall.items():
                #         if len(list11)>0 and (list11[0] == value[0] or list11[1] == value[0]):
                #             nbrtokeepports.append(key)
                #         elif len(list12)>0 and (list12[0] == value[0] or list12[1] == value[0]):  
                #             nbrtokeepports.append(key)
                #         elif len(list13)>0 and (list13[0] == value[0] or list13[1] == value[0]):   
                #             nbrtokeepports.append(key)    
                #         elif len(list14)>0 and (list14[0] == value[0] or list14[1] == value[0]):
                #             nbrtokeepports.append(key)
                #         elif len(list15)>0 and (list15[0] == value[0] or list15[1] == value[0]): 
                #             nbrtokeepports.append(key)
                #         elif len(list16)>0 and (list16[0] == value[0] or list16[1] == value[0]):   
                #             nbrtokeepports.append(key) 
                #         elif len(list17)>0 and (list17[0] == value[0] or list17[1] == value[0]):
                #             nbrtokeepports.append(key)
                #         elif len(list18)>0 and (list18[0] == value[0] or list18[1] == value[0]):  
                #             nbrtokeepports.append(key)
                #         elif len(list19)>0 and (list19[0] == value[0] or list19[1] == value[0]):
                #             nbrtokeepports.append(key)         
                #         else:
                #             nodesPORTStodrop.append(key)     

                #     print("keys to keep = "+str(nbrtokeepports))

                #     print("keys to drop = "+str(nodesPORTStodrop))

                #     for eachport in list(nodesPORTStodrop):
                #         if str(loc.port).startswith("110") and str(eachport).startswith("110"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)
                #         elif str(loc.port).startswith("120") and str(eachport).startswith("120"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)  
                #         elif str(loc.port).startswith("130") and str(eachport).startswith("130"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("140") and str(eachport).startswith("140"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("150") and str(eachport).startswith("150"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("160") and str(eachport).startswith("160"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("170") and str(eachport).startswith("170"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("180") and str(eachport).startswith("180"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         elif str(loc.port).startswith("190") and str(eachport).startswith("190"):
                #             nodesPORTStodrop.remove(eachport)
                #             nbrtokeepports.append(eachport)    
                #         else:
                #             pass                            
                #     print("keys to drop again = "+str(nodesPORTStodrop))

                #     dnmg = DropNeighborMessageGenerator(self, nodesPORTStodrop)
                #     self.msgmon.sendGen(dnmg, loc.ip, loc.port)      

##?  algo

#?  Algorithm by auto defining clusters



        
            #dbgprint("Port "+str(node_port)+" has dict of latencies (not sorted) : "+str(NeighborsLatencyDictall))
            NeighborsLatencyDictall= ast.literal_eval(NeighborsLatencyDictall)  
            #print("type of NeighborsLatencyDictall =",type(NeighborsLatencyDictall))
            list_dictoflatencies.append(NeighborsLatencyDictall)

            if len(list_dictoflatencies) == len(self.expnodes):
                dbgprint("List of dictionary of all ports latency information = "+str(list_dictoflatencies))  
                print("type of list_dictoflatencies =",type(list_dictoflatencies))    



            #############********************  Rearrange latency information as a adjacent matrix  **************###########################
                        
                # Keys (ID value) in the first dictionary in the list will be the standard key list
                idoldict = list_dictoflatencies[0]
                idolkeylist = []
                for key in idoldict:
                    idolkeylist.append(key)
                dbgprint("Idol port key list: "+str(idolkeylist))  


                #Arrange all the dictionary [{key=ID:value=[latency],..},...] in the order of the keylist (Rearrange columns)
                #Output is in the form of tuple, not dictionary e.g. [[(key=ID,value=[latency]),..],...]
                Ordered_list_of_dictionary = []
                for i in range(len(list_dictoflatencies)):
                    Ordered_list_of_dictionary.append(sorted(list_dictoflatencies[i].items(), key=lambda i:idolkeylist.index(i[0])))
                dbgprint ("Ordered list of dictionary (as tuple) : "+str(Ordered_list_of_dictionary))    



                #Arrange as adjacent matrix, have all [0.0] values diagonally (Rearrange rows)
                count = -1     
                final_list = []
                while len(final_list)<len(Ordered_list_of_dictionary):
                    for k in range(len(Ordered_list_of_dictionary)):
                        count=count+1
                        # print("count = ", count)
                        for i,(a,b) in enumerate(Ordered_list_of_dictionary[k]):
                            # print("i =",i, "a =", a, " b=",b) 
                            if b== [0.0] and len(final_list)==i:
                                final_list.append(Ordered_list_of_dictionary[k])
                                # print("final list now", final_list)               
                dbgprint("final list = "+str(final_list))

                #Construct matrix with only latency values
                final_matrix = []
                for k in range(len(final_list)):   
                    tuplelist = final_list[k]
                    # print("tuple list = ", final_list[k])
                    matrow = []
                    for i,(a,b) in enumerate(final_list[k]):
                        # print("i =",i, "a =", a, " b=",b) 
                        matrow.append(b[0])
                    final_matrix.append(matrow)        
                dbgprint("final matrix : "+str(final_matrix))


                for i in range(len(final_matrix)):
                    for j in range(len(final_matrix[i])):
                        avgvalue = round((final_matrix[i][j]+ final_matrix[j][i])/2,3) # min(final_matrix[i][j], final_matrix[j][i])#(final_matrix[i][j]+ final_matrix[j][i])/2 #max(final_matrix[i][j], final_matrix[j][i])
                        final_matrix[i][j] = avgvalue
                        final_matrix[j][i] = avgvalue

                #print("final symmetric matrix : ",final_matrix)

                # convert the redundant n*n square matrix form into a condensed nC2 array
                distArray = ssd.squareform(final_matrix) # distArray[{n choose 2}-{n-i choose 2} + (j-i-1)] is the distance between points i and j

                #print(distArray)


                #Returns required number of clusters from linkage matrix
                #param: linkage_matrix -> linkage matrix generated from hierachical clustering
                #param: desired_cluster_count -> number of clusters required
                def get_clusters(linkage_matrix, desired_cluster_count):

                    #At the begining each node is a cluster itselt, so we current_cluster_count = #nodes
                    current_cluster_count = len(linkage_matrix) + 1
                    if desired_cluster_count > current_cluster_count or desired_cluster_count <= 0:
                        raise Exception("Invalid value for param desired_cluster_count...")

                    #cluster_dict: dictionary that contains the cluster_number as key and the nodes of that cluster as value
                    #at the beginning it should be like this {1:[1], 2:[2], 3:[3]...}
                    cluster_dict = {i:[i] for i in range(current_cluster_count)}

                    if desired_cluster_count < current_cluster_count:

                        next_cluster_seq = current_cluster_count
                        
                        #At each iteration we merge the two closest clusters. So number of clusters is reduced by 1
                        for i in range(linkage_matrix.shape[0]):
                            cluster_dict[next_cluster_seq] = cluster_dict[linkage_matrix[i, 0]] + cluster_dict[linkage_matrix[i, 1]]
                            del cluster_dict[linkage_matrix[i, 0]]
                            del cluster_dict[linkage_matrix[i, 1]]
                            current_cluster_count -= 1

                            if current_cluster_count == desired_cluster_count:
                                break
                            next_cluster_seq += 1
                        
                    return list(cluster_dict.values())

                clus = scipy.cluster.hierarchy.linkage(distArray, method='complete', metric='euclidean')
                print(clus)
                # for i in range(1, 11):
                #     dbgprint(str(i))
                #     dbgprint(str(get_clusters(clus, i)))
                dbgprint(str(get_clusters(clus, num_clusters)))
                clusters = get_clusters(clus, num_clusters)
                for i in range(len(clusters)):
                    for j in range(len(clusters[i])):
                        clusters[i][j] = str(idolkeylist[clusters[i][j]])
                dbgprint(str(clusters))  
                
                cluster1 = clusters[0]
                cluster2 = clusters[1]
                cluster3 = clusters[2]
                cluster4 = clusters[3]
                cluster5 = clusters[4]
                cluster6 = clusters[5]
                cluster7 = clusters[6]
                cluster8 = clusters[7]
                cluster9 = clusters[8]
                
                
        
        
                for i in range(len(clusters)):
                    for j in range(len(clusters[i])):
                        for v in range(len(list_dictoflatencies)):
                            if list_dictoflatencies[v][int(clusters[i][j])]==[0.0]: 
                                print(list_dictoflatencies[v])
                                dbgprint("clusters[i][j] "+str(clusters[i][j]))
                           
                                for key, value in list_dictoflatencies[v].items():   
                                    if str(key) in cluster1:
                                        list11.append(value[0])
                                    elif str(key) in cluster2:
                                        list12.append(value[0]) 
                                    elif str(key) in cluster3:
                                        list13.append(value[0]) 
                                    elif str(key) in cluster4:
                                        list14.append(value[0]) 
                                    elif str(key) in cluster5:
                                        list15.append(value[0]) 
                                    elif str(key) in cluster6:
                                        list16.append(value[0]) 
                                    elif str(key) in cluster7:
                                        list17.append(value[0]) 
                                    elif str(key) in cluster8:
                                        list18.append(value[0]) 
                                    elif str(key) in cluster9:
                                        list19.append(value[0])     
                                               
                                list11 = sorted(list11, reverse=True)
                                list12 = sorted(list12, reverse=True)
                                list13 = sorted(list13, reverse=True)
                                list14 = sorted(list14, reverse=True)
                                list15 = sorted(list15, reverse=True)
                                list16 = sorted(list16, reverse=True)
                                list17 = sorted(list17, reverse=True)
                                list18 = sorted(list18, reverse=True)
                                list19 = sorted(list19, reverse=True)
                        
                                dbgprint("list11 = "+str(list11))     
                                dbgprint("list12 = "+str(list12))     
                                dbgprint("list13 = "+str(list13)) 
                                dbgprint("list14 = "+str(list14))     
                                dbgprint("list15 = "+str(list15))     
                                dbgprint("list16 = "+str(list16)) 
                                dbgprint("list17 = "+str(list17))     
                                dbgprint("list18 = "+str(list18))     
                                dbgprint("list19 = "+str(list19)) 
                                
                        
                        
                                for key, value in list_dictoflatencies[v].items():
                                    if (len(list11)>3 and len(list11)<6 and (list11[0] == value[0] or list11[1] == value[0])) or (len(list11)>=6 and (list11[0] == value[0] or list11[1] == value[0] or list11[2] == value[0] or list11[3] == value[0])):
                                        if 0.0 in list11:
                                            pass
                                        else:  
                                            nodesPORTStodrop.append(key)
                                    elif (len(list12)>3 and len(list12)<6 and (list12[0] == value[0] or list12[1] == value[0])) or (len(list12)>=6 and (list12[0] == value[0] or list12[1] == value[0] or list12[2] == value[0] or list12[3] == value[0])):
                                        if 0.0 in list12:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key)
                                    elif (len(list13)>3 and len(list13)<6 and (list13[0] == value[0] or list13[1] == value[0])) or (len(list13)>=6 and (list13[0] == value[0] or list13[1] == value[0] or list13[2] == value[0] or list13[3] == value[0])):
                                        if 0.0 in list13:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key) 
                                    elif (len(list14)>3 and len(list14)<6 and (list14[0] == value[0] or list14[1] == value[0])) or (len(list14)>=6 and (list14[0] == value[0] or list14[1] == value[0] or list14[2] == value[0] or list14[3] == value[0])):
                                        if 0.0 in list14:
                                            pass
                                        else:  
                                            nodesPORTStodrop.append(key)
                                    elif (len(list15)>3 and len(list15)<6 and (list15[0] == value[0] or list15[1] == value[0])) or (len(list15)>=6 and (list15[0] == value[0] or list15[1] == value[0] or list15[2] == value[0] or list15[3] == value[0])):
                                        if 0.0 in list15:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key)
                                    elif (len(list16)>3 and len(list16)<6 and (list16[0] == value[0] or list16[1] == value[0])) or (len(list16)>=6 and (list16[0] == value[0] or list16[1] == value[0] or list16[2] == value[0] or list16[3] == value[0])):
                                        if 0.0 in list16:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key) 
                                    elif (len(list17)>3 and len(list17)<6 and (list17[0] == value[0] or list17[1] == value[0])) or (len(list17)>=6 and (list17[0] == value[0] or list17[1] == value[0] or list17[2] == value[0] or list17[3] == value[0])):
                                        if 0.0 in list17:
                                            pass
                                        else:  
                                            nodesPORTStodrop.append(key)
                                    elif (len(list18)>3 and len(list18)<6 and (list18[0] == value[0] or list18[1] == value[0])) or (len(list18)>=6 and (list18[0] == value[0] or list18[1] == value[0] or list18[2] == value[0] or list18[3] == value[0])):
                                        if 0.0 in list18:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key)
                                    elif (len(list19)>3 and len(list19)<6 and (list19[0] == value[0] or list19[1] == value[0])) or (len(list19)>=6 and (list19[0] == value[0] or list19[1] == value[0] or list19[2] == value[0] or list18[3] == value[0])):
                                        if 0.0 in list19:
                                            pass
                                        else:
                                            nodesPORTStodrop.append(key)                             
                                    else:
                                        nbrtokeepports.append(key)     

                                    dict_dropnodes[clusters[i][j]]=nodesPORTStodrop 
                                        
                        print("keys to keep = "+str(nbrtokeepports))
                        print("keys to drop = "+str(nodesPORTStodrop))                      
                        nbrtokeepports = []
                        nodesPORTStodrop = []
                        list11 = []
                        list12 = [] 
                        list13 = []
                        list14 = []
                        list15 = [] 
                        list16 = []
                        list17 = []
                        list18 = [] 
                        list19 = []
                        
        dbgprint("dict_dropnodes : "+str(dict_dropnodes))                
        with self.expnodeslock:
            for key in self.expnodes:
                loc = self.expnodes[key]                         
                for key, value in dict_dropnodes.items():                             
                    if str(key) == str(loc.port):    
                        dbgprint("loc.port or key : "+str(loc.port))
                        dbgprint("nodes to drop = "+str(value))
                        dnmg = DropNeighborMessageGenerator(self, value)
                        self.msgmon.sendGen(dnmg, loc.ip, loc.port)
                                




#?
    def BenchReportExpNode(self, node_id, node_ip, node_port, id_maxBench, max_Bench):  
        pass
    
                    


    def startExperiment(self):
        #from Utilities.Const import *                     ##
        from datetime import datetime, timedelta
        from Utilities.FileUtil import SetOutputFolder, expprint
        from CommandMessageGenerators.PauseUnpauseMessageGenerator import TimeUnpauseMessageGenerator
        with self.expnodeslock:
            self.expdef.startExperiment(self, self.expnodes)
            dbgprint("EPM:before sleep")
            time.sleep(30)
            dbgprint("EPM:After Sleep")
            dtstart = datetime.now()+timedelta(0,20)                             
            expprint("EXPSTARTTIME!!:"+str(dtstart))
            for key in self.expnodes:
                loc = self.expnodes[key]
                upmg = TimeUnpauseMessageGenerator(self, dtstart)
                self.msgmon.sendGen(upmg, loc.ip, loc.port)
                
    def GatherLogs(self):
        with self.expnodeslock:
            itval = 0
            for key in self.expnodes:
                dbgprint("ival!"+str(itval))
                itval = itval + 1
                loc = self.expnodes[key]
                self.msgmon.sendCommand(COMMAND_SENDLOGS, self, loc.ip, loc.port)
                time.sleep(10)
            #fact = MakeGenFact(COMMAND_SENDLOGS, self)
            #reactor.connectTCP(loc.ip, loc.port, fact)

    def TerminateAll(self):
        #from Utilities.Const import *                         ##
        #reactor.callFromThread(self.TerminateAllIRT)
    
        with self.expnodeslock:
            for key in self.expnodes:
                loc = self.expnodes[key]
                dbgprint("Sending Terminate:"+str(loc))
                self.msgmon.sendCommand(COMMAND_ENDSERVER, self, loc.ip, loc.port)

        
if __name__ == "__main__":
    global DEBUG
    print (sys.argv)
    argsFIP = ArgFIP(sys.argv)
    source_ip = argsFIP.get(DICT_SOURCE_IP)               ##
    port = int(argsFIP.get(DICT_SOURCE_PORT))             ##
    SetOutputFolder(argsFIP.get(DICT_FOLDER))             ##
    #expfilename = argsFIP[DICT_EXP_FILE]
    expfilename = argsFIP.get(DICT_EXP_FILE)              ##
    dbg = argsFIP.get(DICT_DEBUG)                         ##
    expindex = argsFIP.get(DICT_EXP_INDEX)                ##
    location = argsFIP.get(DICT_LOC)               ####
    print("location : ",location) 
    print (argsFIP)
    if(dbg == "True"):
        setDbg(True)
    else:
        setDbg(False)
    print ("Debug is "+str(DEBUG))                     ##
    expdef = BuildExpDef(expfilename, expindex)
    if(expdef is None):
        dbgprint("EXP Busted")
    else:
        pm = ExpPlatformManager(source_ip, port, expdef, location)
        pm.StartAll()


    
