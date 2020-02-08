#!/bin/bash

# StartNTGPM - Start N TaskGraph Platform Managers
#
# StartNTGPM starts and initializes several TaskGraph platform managers.
# It is called from RunExp[Safe]BareMetal.py and SNBLocal[Docker].bash.
#
# Usage: Platform/ScriptsDocker/StartNTGPM N eip eport port dev debug prefix
#
# Parameters:
#   $1: N	number of platform managers to start
#   $2: eip	experiment controller IP address
#   $3: eport	experiment controller port
#   $4: port	platform manager port
#   $5: dev	network device
#   $6: debug	debug flag
#   $7: prefix	IP address prefix
#
# StartNTGPM starts Docker service even if it is run without docker (why?).
# It then finds its own IP address from the provided network device (why?).
# Finally, it starts N platform managers on ports port..port+N-1.
#
# Examples:
#
# Platform/ScriptsDocker/StartNTGPM 3 127.0.0.1 15000 11000 lo True 127.0
# Platform/ScriptsDocker/StartNTGPM 46 10.10.1.1 8007 11000 eno2 False 10.10


service docker start

echo "StartNTGPM.bash: starting servers"

function startone {
    # usage: startone ip port eip eport debug
    echo "Server at "$2":"$1
    echo "Exp at "$3":"$4
    echo "python Platform/TaskGraphPM.py Source_IP=$2 Source_Port=$1 \\"
    echo "       Exp_IP=$3 Exp_Port=$4 Debug=$5 &> output$1.txt &"
    python Platform/TaskGraphPM.py "Source_IP=$2" "Source_Port=$1" \
	   "Exp_IP=$3" "Exp_Port=$4" "Debug=$5" &> output$1.txt &
}

# Find IP address
# Why does this use "cut -d':' -f2"?
myipcmd='ifconfig '$5' | grep inet | grep '$7" | awk '{print "'$2}'"' | cut -d':' -f2"
myip="`eval ${myipcmd}`"

echo "myipcmd=$myipcmd"
echo "myip=$myip"

n=$1
eip=$2
eport=$3
port=$4
for i in `seq 2 $n`; do
   startone $port $myip $eip $eport $6
   ((port++))
done
echo "Server at "$2":"$1
echo "Exp at "$2":"$3
echo "python Platform/TaskGraphPM.py Source_IP=$myip Source_Port=$port \\"
echo "       Exp_IP=$eip Exp_Port=$eport Debug=$6 &> output$port.txt &"
python Platform/TaskGraphPM.py "Source_IP=$myip" "Source_Port=$port" \
       "Exp_IP=$eip" "Exp_Port=$eport" "Debug=$6" &> output$port.txt
