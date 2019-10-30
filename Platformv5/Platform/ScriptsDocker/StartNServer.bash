#!/bin/bash

service docker start
python Platform/PlatformManager.py "Source_IP=$1" "Source_Port=$2"

#!/bin/bash

function startone {
    echo "Server at "$2":"$1
    python Platform/PlatformManager.py "Source_IP=$2" "Source_Port=$1" &
}

echo "Hello starting servers"
cd Platform
a=$4
myip=`ifconfig eth1 | grep inet | awk '{print $2}' | cut -d':' -f2`

for i in `seq 2 $1`; do
   startone $a $myip $2 $3
   ((a++))
done

python Platform/PlatformManager.py "Source_IP=$myip" "Source_Port=$a"
