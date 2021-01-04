import os
import sys
from datetime import datetime
from DrawUsageDiagram import drawOnePlot

FINISH_PREF = "SendMessage:ReceiveFile,Filename,"
START_PREF = "Starting Container"
EXPSTARTTIME = "EXPSTARTTIME!!:"

def ParseTime(strtime):
    starttime = datetime.strptime(strtime.strip(),"%Y-%m-%d %H:%M:%S.%f")
    return starttime

def ParseFinishIDAndTime(line):
    svals = line.split(FINISH_PREF)
    tvals = svals[1].split(",")
    idval = int(tvals[0])
    print ("PARSEFINTIME:"+str(tvals))
    timeval = ParseTime(tvals[3].strip())
    return [idval, timeval]

def ParseStartIDAndTime(line):
    svals = ""
    endval = ""
    tvals = ""
    idval = ""
    timestr = ""
    timeval = "" 
    if "ID:" not in line:
        pass
    else: 
        svals = line.split("ID:")
        endval = svals[len(svals)-1]
        tvals = endval.split("2021-")
        idval = int(tvals[0])
        timestr = "2021-"+tvals[1]
        timeval = ParseTime(timestr.strip())    
    return [idval, timeval]

def ParseExpStartTime(line):
    svals = line.split(EXPSTARTTIME)
    tvals = svals[1].split("2021-")
    timestr = "2021-"+tvals[1]
    timeval = ParseTime(timestr.strip())
    return timeval

def findMachineUsageOneFile(afilename):
    starttimes = {}
    fintimes = {}
    oldline = ""
    getnextfinish = False
    with open(afilename, 'r') as ifile:
        for line in ifile:
            if(getnextfinish):
                rval = ParseFinishIDAndTime(oldline + line)
                fintimes[rval[0]] = rval[1]
                getnextfinish = False
            if(EXPSTARTTIME in line):
                return [ParseExpStartTime(line)]
            if FINISH_PREF in line:
                oldline = line
                getnextfinish = True
            elif START_PREF in line:
                rval = ParseStartIDAndTime(line)
                starttimes[rval[0]] = rval[1]
    return [starttimes, fintimes]

def fmudir(adir):
    datavals = []
    filenames = []
    starttime = None
    for afile in os.listdir(adir):
        filenames.append(afile)
        ffile = adir + afile
        rval = findMachineUsageOneFile(ffile)
        if(len(rval) == 1):
            starttime = rval[0]
        else:
            datavals.append(rval)
    return [starttime, datavals, filenames]
    
if __name__ == "__main__":
    adir = sys.argv[1]
    twothings = fmudir(adir)
    stime = twothings[0]
    data = twothings[1]
    files = twothings[2]
    drawOnePlot(stime, data, files)
