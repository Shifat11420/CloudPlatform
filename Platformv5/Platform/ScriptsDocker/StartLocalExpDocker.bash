#!/bin/bash

service docker start

function startone {
    echo "Starting Exp at "$1":"$2
    docker run --net="host" --privileged bpete16/distplatform:4.60 python Platform/ExpPlatformManager.py "Source_IP=$1" "Source_Port=$2" "Exp_File=$3" "Debug=True" "Exp_Index=0"
}

#expects args in form
# number_to_run exp_ip exp_port start_port internet_profile
# eth0 15000 Platform/ExpDefOne.txt
echo "Hello starting Exp servers"
myip=`ifconfig enp0s31f6 | grep inet | grep -v inet6 | awk '{print $2}' | cut -d':' -f2`

#startone $myip 15000 "JSONFiles/localtest.json"
startone 127.0.0.1 15000 "JSONFiles/localtest_tg.json"
