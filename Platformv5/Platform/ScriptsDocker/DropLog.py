import sys
import os

for afile in os.listdir('.'):
    if(("output" in afile) and (".txt" in afile)):
        with open(afile, 'r') as ifile:
            for line in ifile:
                print line
