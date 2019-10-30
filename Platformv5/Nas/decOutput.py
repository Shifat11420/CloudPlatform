from os import listdir
from os.path import isfile, join


prefix = "Nas/rawout/"
parsedpref = "Nas/parsedout/"
postfix = "_out.txt"
parsedoutfile = "parsed_out.csv"

linestart_veri = " Verification    ="
linestart_time = " Time in seconds ="
linestart_mops = " Mop/s total     ="

def ParseOneFile(aclass, abench):
    with open(parsedpref + parsedoutfile, 'a') as ofile:
        ofile.write(aclass+","+abench+",")
        ver = ""
        time = ""
        mops = ""
        with open(prefix + aclass + "_" + abench + postfix, 'r') as afile:
            for line in afile:
                if line.startswith(linestart_veri):
                    if not "SUCCESSFUL" in line:
                        ver = "False"
                    else:
                        ver = "True"
                if line.startswith(linestart_time):
                    endline = line[len(linestart_time):]
                    time = endline.strip()
                if line.startswith(linestart_mops):
                    endline = line[len(linestart_mops):]
                    mops = endline.strip()
                    
        ofile.write(time + "," + mops + "," + ver + "\n")

def ParseAllFiles():

    with open(parsedpref + parsedoutfile, 'w') as ofile:
        ofile.write("class,bench,time,mops,verify\n")
    files = listdir(prefix)
    for afile in files:
        vals = afile.split("_")
        aclass = vals[0]
        abench = vals[1]
        ParseOneFile(aclass, abench)


def DumpOutput():
    with open(parsedpref + parsedoutfile, "r") as pfile:
        lcount = 0
        fsum = 0
        for line in pfile:
            if lcount > 0:
                lsplit = line.split(",")
                fsum = fsum + float(lsplit[2])

            lcount = lcount + 1

        print str((fsum/ (lcount - 1)))

ParseAllFiles()
DumpOutput()
