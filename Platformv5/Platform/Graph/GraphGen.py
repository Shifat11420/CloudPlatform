import random
from datetime import datetime

DEBUG = True

def pdbg(val):
    if(DEBUG):
        print(val)

def mirror(matrix):
    othermatrix = []
    for x in range(len(matrix)):
        othermatrix.append({})
    for x in range(len(matrix)):
        othermatrix[x][x] = False
        for key in matrix[x]:
            othermatrix[key][x] = matrix[x][key]
            othermatrix[x][key] = matrix[x][key]

    return othermatrix

class GraphGen():
    def __init__(self, seedval = None):
        if(seedval is None):
            pass
        else:
            random.seed(seedval)

    def GetBoolProb(self, p_con):
        fval = random.random()
        if(fval < p_con):
            return True
        return False
        
    # from stackoverflow.com/questions/20171901/how-to-generate-random-graphs
    def ErdosRenyiConnected(self, nodecount, p_con):
        setlist = []
        connmatrix = []
        conncount = []
        for x in range(0, nodecount):
            setlist.append(x)
            conncount.append(0)

        for x in range(0, nodecount):
            connmatrix.append({})
            for y in range(x+1, nodecount):
                val = self.GetBoolProb(p_con)
                connmatrix[x][y] = (val)
                if(val):
                    conncount[x] = conncount[x] + 1
                    conncount[y] = conncount[y] + 1
                    toreplace = setlist[y]
                    for z in range(len(setlist)):
                        if(setlist[z] == toreplace):
                            setlist[z] = setlist[x]

        #so I test if each node is connected and 
        while(True):
            firstset = setlist[0]
            secondset = firstset
            for i in range(len(setlist)):
                if(setlist[i] != firstset):
                    secondset = setlist[i]
                    break
            if(firstset == secondset):
                break
            pdbg("FS:"+str(firstset))
            pdbg("SS:"+str(secondset))
            firstsetind = -1
            secondsetint = -1
            firstsetmincon = nodecount+10
            secondsetmincon = nodecount+10
            for i in range(len(setlist)):
                if(setlist[i] == firstset):
                    if(firstsetmincon > conncount[i]):
                        firstsetmincon = conncount[i]
                        firstsetind = i
                if(setlist[i] == secondset):
                    if(secondsetmincon > conncount[i]):
                        secondsetmincon = conncount[i]
                        secondsetind = i
            
            if(firstsetind > secondsetind):
                connmatrix[secondsetind][firstsetind] = True
            else:
                connmatrix[firstsetind][secondsetind] = True
            conncount[firstsetind] = conncount[firstsetind] + 1
            conncount[secondsetind] = conncount[secondsetind] + 1

            for i in range(len(setlist)):
                if(setlist[i] == secondset):
                    setlist[i] = firstset

        connmatrix = mirror(connmatrix)

        return connmatrix


    def fullgraphConnected(self, nodecount):
        setlist = []
        connmatrix = []
        conncount = []
        for x in range(0, nodecount):
            setlist.append(x)
            conncount.append(0)

        for x in range(0, nodecount):
            connmatrix.append({})
            for y in range(x+1, nodecount):
                val = True 
                connmatrix[x][y] = (val)
                if(val):
                    conncount[x] = conncount[x] + 1
                    conncount[y] = conncount[y] + 1
                    toreplace = setlist[y]
                    for z in range(len(setlist)):
                        if(setlist[z] == toreplace):
                            setlist[z] = setlist[x]

        #so I test if each node is connected and 
        while(True):
            firstset = setlist[0]
            secondset = firstset
            for i in range(len(setlist)):
                if(setlist[i] != firstset):
                    secondset = setlist[i]
                    break
            if(firstset == secondset):
                break
            pdbg("FS:"+str(firstset))
            pdbg("SS:"+str(secondset))
            firstsetind = -1
            secondsetint = -1
            firstsetmincon = nodecount+10
            secondsetmincon = nodecount+10
            for i in range(len(setlist)):
                if(setlist[i] == firstset):
                    if(firstsetmincon > conncount[i]):
                        firstsetmincon = conncount[i]
                        firstsetind = i
                if(setlist[i] == secondset):
                    if(secondsetmincon > conncount[i]):
                        secondsetmincon = conncount[i]
                        secondsetind = i
            
            if(firstsetind > secondsetind):
                connmatrix[secondsetind][firstsetind] = True
            else:
                connmatrix[firstsetind][secondsetind] = True
            conncount[firstsetind] = conncount[firstsetind] + 1
            conncount[secondsetind] = conncount[secondsetind] + 1

            for i in range(len(setlist)):
                if(setlist[i] == secondset):
                    setlist[i] = firstset

        connmatrix = mirror(connmatrix)

        return connmatrix        
