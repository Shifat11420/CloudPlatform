#!/bin/bash

host=$1
port=$2

if [ -z "$host" ]; then
    host="localhost"
fi
if [ -z "$port" ]; then
    port=8007
fi

docker run --privileged -p $host:$port:$port bpete16/distplatform:0.4 /bin/bash Platform/ScriptsDocker/StartServer.bash $host $port
