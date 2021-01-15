from subprocess import call
import subprocess
from Utilities.Const import *

DEFAULT_VALUE = 3.0

def GetRValueFromNAS():
    dbgprint("GetRValueFromNAS")
    fout = open("nasoutput.txt", 'w')
    #strLoad = ["docker", "load", "--input", "Sandbox/nascont.tar"]
    #call(strLoad)
    call("/bin/bash Nas/runnasspec.bash --class W --bench cg", stderr=subprocess.STDOUT, stdout=fout, shell=True)
    timeval = "0"
    with open("nasoutput.txt", 'r') as nfile:
        val = nfile.read()
        dbgprint("NASVal:"+str(val)+":")
        try:
            dbgprint("parsed out:"+str(val.split(",")[7]))
            timeval = val.split(",")[7]
        except IndexError:
            print ("ERR:"+str(val))                         ##
            timeval = DEFAULT_VALUE
    return timeval
