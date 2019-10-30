import os
import sys

def getfinids(fname):

    oneids = []
    with open(fname, 'r') as ifile:
        for line in ifile:
            if "ExecFinished:" in line:
                idval = int(line.split(":")[1][:-1])
                oneids.append(idval)
    return oneids

def getinitial(fname):
    
    pripref = "PRIORITY:"
    dpref = "DEP:"
    prilist = {}
    predlist = {}

    with open(fname, 'r') as ifile:
        for line in ifile:
            if pripref in line:
                vals = line[:-1].split(":")
                prilist[int(vals[2])] = int(vals[1])
                predlist[int(vals[2])] = []

    with open(fname, 'r') as ifile:
        for line in ifile:
            if dpref in line:
                vals = line[:-1].split(":")
                p = int(vals[1])
                s = int(vals[2])
                predlist[s].append(p)

    for key in prilist:
        print(str(key) + ":" + str(prilist[key])+"  "+str(predlist[key]))

    print("-----")


fgen = "tg_firsttest.txt"
fone = "tg_workers.txt"
ftwo = "tg_worker2.txt"

fidone = getfinids(fone)
print("ONE:"+str(fidone))

fidtwo = getfinids(ftwo)
print("TWO:"+str(fidtwo))



getinitial(fgen)

