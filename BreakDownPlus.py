import os
import sys


SMSG = "SendMessage:"
SCONT = "Starting Container"

RFILE = "ReceiveFile"
CRESP = "ContainerResponse"
#REXP = "ReceiveExpNode"
RQL = "ReceiveQueueLen"
RBEN = "ReceiveBench"
RCONT = "ReceiveContainer"
DYNF = "DoYouNeedFile"
#TUP = "Sending Msg: TimeUnpause,"
WDON = "WORKDONE:"
#BENVAL = "BenVal"

ListTerms = [SCONT, CRESP, RCONT]
CountTerms = [RFILE, RQL, DYNF]

EXPSTART = "EXPSTARTTIME!!:"
START = "StartTime"

def BreakExpLog(iFile):
    expinfo = {}
    expinfo[RCONT] = []
    for line in iFile:
        if(EXPSTART in line):
            vals = line.split(EXPSTART)
            tval = vals[1].strip()
            tval2 = "2020-" + tval.split("2020-")[1]
            expinfo[START]=tval2
        if(RCONT in line):
            vals = line.split(",")
            if(not (vals[4] in expinfo[RCONT])):
                expinfo[RCONT].append(vals[4])

    return expinfo

def BreakNodeLog(iFile):
    nodeinfo = {}
    nodeinfo[WDON] = []
    nodeinfo["L"] = {}
    nodeinfo["C"] = {}
    nodeinfo["X"] = {}
    nodeinfo["X"][RBEN] = []
    for val in ListTerms:
        nodeinfo["L"][val] = []
    for val in CountTerms:
        nodeinfo["C"][val] = 0
    for line in iFile:
        if(RBEN in line):
            vals = line.split(",")
            if(len(vals) == 3):
                bval = vals[len(vals)-1].split("\n")
                bvalue =bval[0].strip()
                if(len(bvalue) > 0):
                    if(not "-" in bvalue):
                        if(not bvalue in nodeinfo["X"][RBEN]):
                            nodeinfo["X"][RBEN].append(bvalue)
        else:    
            for val in CountTerms:
                if(val in line):
                    nodeinfo["C"][val] = nodeinfo["C"][val] + 1
            if(WDON in line):
                print(line)
                lsplit = line.split("TIME:")
                mval = lsplit[1].strip()
                mval2 = mval.split("FIN")
                tval = mval2[0].strip()
                lsplit = line.split("WORKDONE:")
                idval = lsplit[1].split(" ")[0]
                nodeinfo[WDON].append([idval, tval])
            
            for val in ListTerms:
                if(val in line): # and not 'SandUnhandled' in line):
                    idval = "ERR"
                    if(val == SCONT):
                        lsplit = line.split("ID:")
                        mval = lsplit[1].strip()
                        mval2 = mval.split("2019-")
                        mval3 = mval2[0]
                        idval = mval3
                    else:
                        lsplit1 = line.split("ID,")
                        lsplit2 = lsplit1[1].split(",")
                        idval = lsplit2[0]
                    nodeinfo["L"][val].append(idval)
    return nodeinfo

def ValidityCheck(nodeinfos, expinfo):
    badcount = 0
    donevals = []
    for aFileInfo in nodeinfos:
        for tup in nodeinfos[aFileInfo][WDON]:
            if(not (tup[1] in donevals)):
                donevals.append(tup[0])

    donevals.sort()

    rc = sorted(expinfo[RCONT])
    print("DVLen:"+str(len(donevals)))
    print("DV:"+str(donevals))
    print("RCLen:"+str(len(rc)))
    print("RC:"+str(rc))
    if(not (START in expinfo)):
        print("ERR:NOSTART")
        badcount = -1
        return badcount
    for idval in expinfo[RCONT]:
        if(not idval in donevals):
            print("ERR:NO:"+str(idval))
            badcount = badcount + 1
    return badcount
        
def BreakLog(indir, outfilename, outputbad = False):
    lines = {}
    expinfo = None
    wdoneset = []
    for aFile in os.listdir(indir):
        print("BREAKDOWN:"+indir+aFile)
        with open(indir+aFile, 'r') as iFile:
            if("exp" in aFile):
                expinfo = BreakExpLog(iFile)
            else:
                lines[aFile] = BreakNodeLog(iFile)
                wdoneset = wdoneset + lines[aFile][WDON]

    bc = ValidityCheck(lines, expinfo)
    if(bc == 0):
        outfilename = outfilename + "OK.csv"
    else:
        outfilename = outfilename + "BAD_"+str(bc)+".csv"
        print(outfilename)
        if(not outputbad):
            return

    with open(outfilename, 'w') as oFile:
        oFile.write("Names,StartCont,RecFile,ContResp,BenVal,RecExpNode,RecQL,RecBench,RecCont,DoYouNeedFile\n")
        for aFileName in lines.keys():
            print("OUTFILE:"+aFileName)
            fbvals = [float(x) for x in lines[aFileName]["X"][RBEN]]
            bave = sum(fbvals) / float(len(fbvals))
            oFile.write(aFileName+",")
            oFile.write(":".join(lines[aFileName]["L"][SCONT])+",")
            oFile.write(str(lines[aFileName]["C"][RFILE])+",")
            oFile.write(":".join(lines[aFileName]["L"][CRESP])+",")
            oFile.write(str(bave))
            oFile.write(",x,")
            oFile.write(str(lines[aFileName]["C"][RQL])+",")
            oFile.write(":".join(lines[aFileName]["X"][RBEN])+",")
            oFile.write(":".join(lines[aFileName]["L"][RCONT])+",")
            oFile.write(str(lines[aFileName]["C"][DYNF])+"\n")

        oFile.write("-----\n")
        oFile.write(expinfo[START]+"\n")

        for lval in wdoneset:
            oFile.write(",".join(lval) + "\n")
        
            

            
if __name__ == "__main__":
    if(len(sys.argv) > 3):
        BreakLog(sys.argv[1], sys.argv[2], sys.argv[3] == 'True')
    else:
        BreakLog(sys.argv[1], sys.argv[2])
