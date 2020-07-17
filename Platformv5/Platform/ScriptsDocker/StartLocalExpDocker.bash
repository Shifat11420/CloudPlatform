#!/bin/bash

# StartLocalExpDocker.bash - Starts local Experiment Controller
#
# StartLocalExpDocker starts an experiment controller locally in Docker.
#
# Eventually, the network address or device, the port number, and the
# JSON file should be parameterized differently.

service docker start

echo "StartLocalExpDocker.bash: starting experiment controller"

function startone {
    # usage: startone eip eport json
    echo "Starting Exp at "$1":"$2
    echo "docker run --net="host" --privileged bpete16/distplatform:4.60 \\"
    echo "       python Platform/ExpPlatformManager.py \\"
    echo "              Source_IP=$1 Source_Port=$2 \\"
    echo "              Exp_File=$3 Debug=True Exp_Index=0"
    docker run --net="host" --privileged bpete16/distplatform:4.60 \
	   python Platform/ExpPlatformManager.py \
	          "Source_IP=$1" "Source_Port=$2" \
	          "Exp_File=$3" "Debug=True" "Exp_Index=0"
}

# Find IP address
# Why does this use "cut -d':' -f2"?
eip=`ifconfig lo | grep inet | grep -v inet6 | awk '{print $2}' | cut -d':' -f2`

echo "eip=$eip  (not used, 127.0.0.1 is hardwired)"

#startone $eip 15000 "JSONFiles/localtest.json"
startone 127.0.0.1 15000 "JSONFiles/localtest_tg.json"
