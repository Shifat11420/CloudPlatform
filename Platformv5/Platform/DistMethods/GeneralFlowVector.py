from Utilities.Const import *
from Utilities.FileUtil import expprint
import math
from math import floor              ##added import

def normalizeDict(vdict):
    ndict = {}
    sums = []
    for key in vdict:
        for i in range(len(vdict[key])):
            if(i == len(sums)):
                sums.append(0)
            sums[i] = sums[i] + vdict[key][i]

    for key in vdict:
        for i in range(len(vdict[key])):
            ndict[key].append(vdict[key][i] / sums[i])

    return ndict

def getDPVals(nvdict, mykey, fvec, svec):
    rDict = {}
    sumv = 0
    for key in nvdict:
        mvec = nvdict[key]
        if(key == mykey):
            for i in range(len(mvec)):
                mvec[i] = mvec[i] + svec[i]

        val = 0
        for i in range(len(fvec)):
            val = val + (fvec[i] * mvec[i])
        if(val < 0):
            val = 0
        rDict[key] = val
        sumv = sumv + val

    for key in rDict:
        rDict[key] = rDict[key]/sumv
    return rDict

def allocJobs(dictMCoeff, jobids):
    jlen = len(jobids)
    mjlen = jlen
    ltupextra = []
    dictCount = {}
    for key in dictMCoeff:
        mval = dictMCoeff[key] * jlen
        dictCount[key] = floor(mval)
        mjlen = mjlen - floor(mval)
        ltupextra.append([key, mval - floor(mval)])

    ltupextra = sorted(ltupextra, key=lambda tup: tup[1])
    for tup in ltupextra:
        if(mjlen <= 0):
            break
        dictCount[tup[0]] = dictCount[tup[0]] + 1
        mjlen = mjlen - 1

    dictJobs = {}
    mjids = jobids
    for key in dictCount:
        dictJobs[key] = []
        for i in range(dictCount[key]):
            dictJobs[key].append(mjids.pop())

    return dictJobs
        

def getRedistGenFlow(JobVecCollList, own_mchn_key, other_mchn_keys, mchn_vdict):

    nvdict = normalizeDict(mchn_vdict)

    rDict = {}
    rDict[own_mchn_key] = []
    for key in other_mchn_keys:
        rDict[key] = []

    for jvc in JobVecCollList:
        if(len(jvc.jobids) == 0):
            continue

        mchnFloats = getDPVals(nvdict, own_mchn_key, jvc.flowvector, jvc.stasisvector)
        
        reallocDict = allocJobs(mchnFloats, jvc.jobids)

        for key in reallocDict:
            rDict[key] = rDict[key] + reallocDict[key]

    return rDict
