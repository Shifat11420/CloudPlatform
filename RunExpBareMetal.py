import subprocess
import sys
import os
import time
#import random
from GrabAllLogs import PullAllMchnFiles

remotedir = "/users/gb"
remotenet = "eno2"

distplatform = "bpete16/distplatform"
platformdir = "Platformv5"
platfile = "plat.tar"

debug = "False"
#bashfile = "StartNTGPM.bash"
bashfile = "StartNBenchPM.bash"

safe = False
runs = range(5)

def scpcommand(host, port, infolder, filename, outfolder):
    os.system('scp -P {0} {1}:{2}/{3} {4}/{3}'.format(port, host, infolder, filename, outfolder))

def scppush(host, port, filename, infolder, outfolder):
    os.system('rsync -ve "ssh -p {0}" {1}/{2} {3}:{4}/{2}'.format(port, infolder, filename, host, outfolder))

def sshcommand(host, port, cmd, readout=False):
    print("BEFORESSH:HOST:"+str(host)+" PORT:"+str(port)+"CMD:"+str(cmd))
    if readout:
        ssh = subprocess.Popen(["ssh", "-p %s" % port, "%s" % host, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            err = ssh.stderr.readlines()
            print("ERR SSH: %s" % err)
        else:
            return result
    else:
        ssh = subprocess.Popen(["ssh", "-p %s" % port, "%s" % host, cmd],
                               shell=False,
                               stdout=None,
                               stderr=None,
                               stdin=None)

def getIP(host, port, prefix):
    bc = "ifconfig | grep inet | grep " + prefix + " | awk '{print $2}' | cut -d':' -f2"

    vals = sshcommand(host, port, bc, readout=True)
    return vals[0].strip()

def loadDocker(host, port, dockerfile):
    cmd = 'docker load --input '+dockerfile
    sshcommand(host, port, cmd)
    time.sleep(120)

def runC(host, port, ipc, portc, version, numnodes, expfile, outfile, dockerfile, expindex, cpuset):
    cscmd = ""
    if not cpuset == "x":
        cscmd = '--cpuset-cpus="'+cpuset+'"'

    loadDocker(host, port, dockerfile)
    time.sleep(30)
    cmd = 'docker run '+cscmd+' --net="host" --privileged '+distplatform+':'+str(version)+' python Platform/ExpPlatformManager.py "SourceIP=' + str(ipc) + '" "Source_Port=' + str(portc) + '" "Exp_File='+str(expfile)+ '" "Debug=True" "Exp_Index=' + str(expindex) +'" &> ' + outfile + ' &'

    sshcommand(host, port, cmd)
    print("COMMANDCTRL:"+cmd)

#def dropAllLogs(mchnFile):
#    print("\nSTART CARING\n")
#    with open(mchnFile, 'r') as mfile:
#        for line in mfile:
#            l = line.split()
#            dropLogs(l[0], l[1])
#    print("\nSTOP CARING\n")

#def dropLogs(host, port):
#    cmd = "docker exec distplat python Platform/ScriptsDocker/DropLog.py"
#    sshcommand(host, port, cmd)

def runNodes(host, port, version, numnodes, ipc, portc, startport, dockerfile, ipprefix, cpuset, contname, outfname):
    cscmd = ""
    if not cpuset == "x":
        cscmd = '--cpuset-cpus="'+cpuset+'"'
    cmd = 'docker run '+cscmd+' --net="host" --name="'+contname+'" --privileged '+distplatform+':'+str(version)+' /bin/bash Platform/ScriptsDocker/' +bashfile + ' ' + str(numnodes) + ' ' + str(ipc) + ' ' + str(portc) + ' ' + str(startport) + ' ' + remotenet + ' '+debug+' ' + ipprefix + ' &>'+outfname+' &'

    sshcommand(host, port, cmd)
    print("COMMANDNODES:"+cmd)

    #for i in range(int(numnodes)):
    #    cmd = 'docker run --net="host" --privileged '+distplatform+':'+str(version)+' python Platform/LoadSim.py'
    #    sshcommand(host, port, cmd)

def runTerminate(host, port):
    cmd = "docker kill $(docker ps -a -q)"
    sshcommand(host, port, cmd)
    time.sleep(10)
    if not safe:
        cmd = "rm *.txt"
        sshcommand(host, port, cmd)
        cmd = "docker rm -f $(docker ps -a -q)"
        sshcommand(host, port, cmd)
        time.sleep(10)
        cmd = "docker rmi $(docker images -q)"
        sshcommand(host, port, cmd)
        time.sleep(10)

def killExperiment(mchnfile):
    mchn = []
    with open(mchnfile, 'r') as mfile:
        for line in mfile:
            l = line.split()
            mchn.append(l)

    for i in range(0, len(mchn)):
        print("before term:"+mchn[i][0]+":"+mchn[i][1])
        runTerminate(mchn[i][0], mchn[i][1])

def pushPlatform(in_mchnfile):
    #mchn = []
    with open(in_mchnfile, 'r') as mfile:
        for line in mfile:
            l = line.split()
            l.append(0)
            scppush(l[0], l[1], platfile, platformdir, "~")

#mchn[0] is controller
#mchn[i][2] is perf modifier
#mchn[i][3] is how many nodes to run, must be filled in

#def allocateNodes(mchn, numnodes):
#    ptot = 0
#    leftover = numnodes
#    for i in range(1, len(mchn)):
#        ptot = ptot + mchn[i][2]

#    for i in range(1, len(mchn)):
#        nodes = int(numnodes * mchn[i][2] / ptot)
#        leftover = leftover - nodes
#        mchn[i][3] = nodes

#    while leftover > 0:
#        for i in range(1, len(mchn)):
#            mchn[i][3] = mchn[i][3] + 1
#            leftover = leftover - 1
#            if leftover == 0:
#                break

def setPlatFile(in_expfile):
    global platfile
    tv = []
    with open(in_expfile, 'r') as oexpfile:
        vals = oexpfile.read()
        tv = vals.split()
    platfile = tv[5]

def runExperiment(in_expfile, in_mchnfile, outfilename, expindex):
    #global platfile
    tv = []
    mchn = []
    machineNodePorts = []
    with open(in_expfile, 'r') as oexpfile:
        vals = oexpfile.read()
        tv = vals.split()
    with open(in_mchnfile, 'r') as mfile:
        for line in mfile:
            l = line.split()
            #mperf = random.randint(int(tv[3]), int(tv[4]))
            #l.append(mperf)
            l.append(0)
            mchn.append(l)

    version = tv[0]
    onumnodes = int(tv[1])
    expfilename = tv[2]
    ipprefix = tv[3]
    loutdir = tv[4]
    #platfile = tv[5]


    ipc = getIP(mchn[0][0], mchn[0][1], ipprefix)
    ipc = ipc.decode('utf8')
    portc = 8007

    runC(mchn[0][0], mchn[0][1], ipc, portc, version, onumnodes, expfilename, outfilename, platfile, expindex, mchn[0][3])

    time.sleep(5)

    decval = onumnodes

    print("Total Node Count:"+str(decval))

    #allocateNodes(mchn, decval)

    # while decval > 0:
    #     for i in range(1, len(mchn)):
    #         decval = decval - 1
    #         mchn[i][3] = mchn[i][3] + 1
    #         if decval == 0:
    #             break

    print("MchnVector:"+str(mchn))

    startports = 11000
    loads = []
    for i in range(1, len(mchn)):
        if not(mchn[i][0] in loads):
            loadDocker(mchn[i][0], mchn[i][1], platfile)
            loads.append(mchn[i][0])

    time.sleep(30)
    machineNodePorts.append([])
    platint = 0
    platnames = [""]
    outfnames = [""]
    for i in range(1, len(mchn)):
        runNodes(mchn[i][0], mchn[i][1], version, mchn[i][2], ipc, portc, startports, platfile, ipprefix, mchn[i][3], "distplat"+str(platint), "outclient"+str(platint)+".txt")
        platnames.append("distplat"+str(platint))
        outfnames.append("outclient"+str(platint)+".txt")
        platint = platint + 1
        machineNodePorts.append([])
        machineNodePorts[i] = []
        for j in range(0, int(mchn[i][2])):
            machineNodePorts[i].append([])
            machineNodePorts[i][j] = startports + j
        print ("Running " + str(mchn[i][2]) + " nodes")
        startports = startports + 1000

    return [mchn[0][0], mchn[0][1], platnames, machineNodePorts, loutdir, outfnames]

if len(sys.argv) == 2:
    killExperiment(sys.argv[1])
else:
    killExperiment(sys.argv[1])
    print("after kill")
    setPlatFile(sys.argv[2])
    pushPlatform(sys.argv[1])
    time.sleep(30)
    #runExperiment(sys.argv[2], sys.argv[1], "primetrial")
    #print("after run experiment prime")
    #time.sleep(4*60)

    #for x in (range(51,56)+range(20, 40)):
    for x in runs:
        print("EXPNUM!!  "+str(x)+"  !!")
        ofname = "outputexp800c"+str(x)+".txt"
        basemchn = runExperiment(sys.argv[2], sys.argv[1], ofname, x)
        print("AfterExp")
        time.sleep(900)
        print("AfterSleep")
        scpcommand(basemchn[0], basemchn[1], remotedir, ofname, basemchn[4])
        subfolder = basemchn[4] + "extra"+str(x)+"/"
        print("BeforePull")
        #dropAllLogs(sys.argv[1])
        PullAllMchnFiles(sys.argv[1], subfolder, basemchn[3], basemchn[2], basemchn[5])
        #REMEMBER TO TAKE NEX TTHING OUT!!
        #break
        print("AfterPull")
        time.sleep(60*2)
        killExperiment(sys.argv[1])
        time.sleep(10)
