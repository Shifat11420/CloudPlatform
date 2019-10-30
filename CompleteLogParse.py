import os
import sys
import shutil
from SuperBreakdown import BreakdownAll
from CalcVarAndTimesComplete import calcVarAndTimes
from GenTimeDiagramComplete import GenDir

def ParseFileBased(argfile, printincom = False):
    fsets = []
    i = 0
    with open(argfile, 'r') as ifile:
        fsets.append([])
        for line in ifile:
            line = line.strip()
            if(line == "*****"):
                fsets.append([])
                i = i + 1
            else:
                fsets[i].append(line)

    for ival in range(len(fsets[0])):

        try:
            shutil.rmtree(fsets[1][ival])
        except OSError:
            pass
        os.makedirs(fsets[1][ival])
        BreakdownAll(fsets[0][ival], fsets[1][ival], printincom)

    try:
        shutil.rmtree(fsets[3][0])
    except OSError:
        pass
    os.makedirs(fsets[3][0])
    
    for ival in range(len(fsets[1])):
        calcVarAndTimes(fsets[1][ival], fsets[2][ival])

    GenDir(fsets[3][0], fsets[4][0], fsets[5], fsets[6])
            
if(__name__=="__main__"):
    filedesc = sys.argv[1]
    printincom = False
    if(len(sys.argv) > 2):
        printincom = sys.argv[2] == 'True'
    ParseFileBased(filedesc, printincom)
