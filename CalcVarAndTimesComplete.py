import sys
import os
import numpy
import scipy
import scipy.stats
from datetime import datetime

#from stackoverflow http://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
def numpy_mean_conf(aset, confidence=0.95):
    a = 1.0*numpy.array(aset)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)
    return [m, m-h, m+h]

def writevals(lout, outfile):
    with open(outfile, 'w') as ofile:
        for linevals in lout:
            for avals in linevals:
                ofile.write(str(avals))
                ofile.write(",")
            ofile.write("\n")

def parseSecondValue(strTime):
    print("DBGTIME:"+strTime)
    vals = strTime.split(":")
    sec = float(vals[2])
    sec = sec + (60*int(vals[1]))
    sec = sec + (60*60*int(vals[0]))
    return sec

def confInterval(afile):
    totalsets = []
    firsttime = True
    with open(afile, 'r') as ifile:
        for line in ifile:
            vals = line.split(",")
            #print(str(vals))
        
            for i in range(len(vals)-1):
                if(firsttime):
                    totalsets.append([])
                if(i == 0):
                    totalsets[i].append(float(vals[i]))
                else:
                    totalsets[i].append(parseSecondValue(vals[i]))
            #totalsets[0].append(float(vals[0]))
            #totalsets[1].append(parseSecondValue(vals[1]))
            #totalsets[2].append(parseSecondValue(vals[2]))
            #totalsets[3].append(parseSecondValue(vals[3]))
            #totalsets[4].append(parseSecondValue(vals[4]))
            firsttime = False
    cfsets = []
    for aset in totalsets:
        cfsets.append(numpy_mean_conf(aset))
    #for i in range(5):
    #    print(str(totalsets[i]))
    #    cfsets.append(numpy_mean_conf(totalsets[i]))

    with open(afile, 'w') as ofile:
        for i in range(3):
            for aset in cfsets:
                ofile.write(str(aset[i]))
                ofile.write(",")
            ofile.write("\n")
    #with open(afile, 'a') as ofile:
    #    for i in range(3):
    #        for j in range(5):
    #            ofile.write(str(cfsets[j][i]))
    #            ofile.write(",")
    #        ofile.write("\n")
        

def calcVarAndTimes(indir, outfilename):
    
    lfinal = []
    filecount = 0
    for infile in os.listdir(indir):
        infilename = indir + infile
        lcounts = []
        csum = 0
        ltimes = []
        mode = 1
        count = 0
        starttime = None
        print("FILE:"+infilename)
        with open(infilename, 'r') as ifile:
            for line in ifile:
                count = count + 1
                print(line)
                if(count > 1):
                    if(mode == 1):
                        if(line.startswith("-----")):
                            mode = 2
                            continue
                        avals = line.strip().split(",")
                        vals = avals[1].split(":")
                        #set conversion removes accidental dups in 
                        #some datasets (but not all)
                        #when dbg logs are on.
                        acount = len(list(set(vals)))
                        lcounts.append(acount)
                        csum = csum + acount
                    elif(mode == 2):
                        if(starttime == None):
                            starttime = datetime.strptime(line.strip(),"%Y-%m-%d %H:%M:%S.%f")
                        else:
                            vals = line.split(",")
                            try:
                                atime = datetime.strptime(vals[1].strip(),"%Y-%m-%d %H:%M:%S.%f")
                                ltimes.append(atime)
                            except ValueError:
                                print("IGNOREDLINE:"+str(line))

        ltimes.sort()
        print(len(ltimes))
        #onefourtime = ltimes[len(ltimes)/4]
        #midtime = ltimes[len(ltimes)/2]
        #threefourtime = ltimes[len(ltimes)*3/4]
        #fintime = ltimes[len(ltimes) - 1]
        vsum = 0
        ave = csum / float(len(lcounts))
        for acount in lcounts:
            vsum = vsum + ((acount - ave) ** 2)
        var = vsum / float(len(lcounts))
        #lfinal.append([var, onefourtime-starttime, midtime-starttime, threefourtime-starttime, fintime-starttime])
        lfinal.append([])
        lfinal[filecount].append(var)
        for atime in ltimes:
            lfinal[filecount].append(atime-starttime)
        
        writevals(lfinal, outfilename)

        filecount = filecount + 1
            
    confInterval(outfilename)

if __name__ == "__main__":
    infiledir = sys.argv[1]
    outfile = sys.argv[2]
    calcVarAndTimes(infiledir, outfile)
