import os
import sys

infile = sys.argv[1]

with open(infile, 'r') as ifile:
    i = 0
    for line in ifile:
        if "error" in line or "Error" in line:
            if("error.ConnectionDone" in line):
                pass
            elif("error.ConnectionLost" in line):
                pass
            else:
                print("LINENUM:"+str(i))
                print(line)
        i = i + 1
