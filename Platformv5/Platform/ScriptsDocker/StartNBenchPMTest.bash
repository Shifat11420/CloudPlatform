#!/bin/bash

service docker start

function startone {
    echo "Server at "$2":"$1
    echo "Exp at "$3":"$4

}

#expects args in form
# number_to_run exp_ip exp_port start_port
echo "Hello starting servers"
a=$4
myip=`ifconfig eth0 | grep inet | awk '{print $2}' | cut -d':' -f2`

for i in `seq 2 $1`; do
   echo "??"$2":"$3"??"
   ei=$2
   ep=$3
   startone $a $myip $ei $ep
   ((a++))
done

