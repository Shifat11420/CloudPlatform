import subprocess
import sys
import os
import time
import shutil
import random

def scpcommand(host, port, infolder, outfolder, prefix, postfix):
    cmd = 'scp -rP {0} {1}:{2}/{4}*{5} {3}'.format(port, host, infolder, outfolder, prefix, postfix)
    print("SCPCMD:"+cmd)
    os.system(cmd)


def sshcommand(host, port, cmd, readout=False):
    if(readout):
        ssh = subprocess.Popen(["ssh", "-p %s" % port, "%s" % host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if(result == []):
            err = ssh.stderr.readlines()
            print ("ERR SSH: %s" % err)
        else:
            return result
    else:
        ssh = subprocess.Popen(["ssh", "-p %s" % port, "%s" % host, cmd],
                               shell=False,
                               stdout=None,
                               stderr=None,
                               stdin=None)

    
def PullAllMchnFiles(in_mchnfile, adir, portnums, platnames, outfnames):
    if(os.path.exists(adir)):
        shutil.rmtree(adir)
    os.makedirs(adir)

    print ("PORTS:"+str(portnums))
    
    with open(in_mchnfile, 'r') as mfile:
        c = 0
        for line in mfile:
            l = line.split()
            for i in range(0, len(portnums[c])):
                pf = str(portnums[c][i])
                cmd = "docker cp "+platnames[c]+":output"+pf+".txt ."
                print ("CMD:"+cmd)
                sshcommand(l[0], l[1], cmd)
                time.sleep(5)
            time.sleep(10)
            scpcommand(l[0], l[1], "~", adir, "output", ".txt")
            time.sleep(5)
            c = c + 1
      
if(__name__ == "__main__"):
    PullAllMchnFiles(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], "")
