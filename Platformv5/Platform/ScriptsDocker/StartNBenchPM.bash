#!/bin/bash

service docker start

function startone {
    echo "Server at "$2":"$1
    echo "Exp at "$3":"$4
    echo "python Platform/BenchNodePM.py Source_IP=$2 Source_Port=$1 Exp_IP=$3 Exp_Port=$4 Debug=$5 &> output$1.txt &"
    python Platform/BenchNodePM.py "Source_IP=$2" "Source_Port=$1" "Exp_IP=$3" "Exp_Port=$4" "Debug=$5" &> output$1.txt &
}

#expects args in form
# number_to_run exp_ip exp_port start_port internet_profile Debug IP_Prefix
# 3 127.0.0.1 15000 11000 lo True 127.0
echo "Hello starting servers"
a=$4
myipcmd='ifconfig eno2 | grep inet | grep '$7" | awk '{print "'$2}'"' | cut -d':' -f2"
myip="`eval ${myipcmd}`"

for i in `seq 2 $1`; do
   echo "??"$2":"$3"??"
   ei=$2
   ep=$3
   startone $a $myip $ei $ep $6
   ((a++))
done
echo "python Platform/BenchNodePM.py Source_IP=$myip Source_Port=$a Exp_IP=$2 Exp_Port=$3 Debug=$6 &> output$a.txt"
python Platform/BenchNodePM.py "Source_IP=$myip" "Source_Port=$a" "Exp_IP=$2" "Exp_Port=$3" "Debug=$6" &> output$a.txt
