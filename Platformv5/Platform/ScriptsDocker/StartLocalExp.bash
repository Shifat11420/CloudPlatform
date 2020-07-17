#!/bin/bash

service docker start

function startone {
    echo "Starting Exp at "$1":"$2
    python Platform/ExpPlatformManager.py "Source_IP=$1" "Source_Port=$2" "Exp_File=$3" "Debug=True" "Exp_Index=0"
}

#expects args in form
# internet_profile exp_port exp_file
# enp0s31f6 15000 Platform/ExpDefOne.txt
echo "Hello starting Exp servers"
myip=`ifconfig lo | grep inet | grep -v inet6 | awk '{print $2}' | cut -d':' -f2`

#startone $myip 15000 "JSONFiles/localtest.json"
startone 127.0.0.1 15000 "JSONFiles/localtest_tg.json"
