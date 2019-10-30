import os
import sys
from BreakDownPlus import BreakLog

def BreakdownAll(infolder, outfolder, logincomplete=False):
    for val in os.listdir(infolder):
        if(os.path.isdir(infolder + val)):
            outval = outfolder + val + ".csv"
            BreakLog(infolder+val+"/", outval, logincomplete)

if __name__ == "__main__":
    if(len(sys.argv) > 3):
        BreakdownAll(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        BreakdownAll(sys.argv[1], sys.argv[2])
