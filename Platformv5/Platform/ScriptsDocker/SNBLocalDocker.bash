#!/bin/bash

#docker run --net="host" --privileged bpete16/distplatform:4.60 bash Platform/ScriptsDocker/StartNBenchPM.bash 3 96.125.113.52 15000 11000 enp0s31f6 True 96.125
docker run --net="host" --privileged bpete16/distplatform:4.60 bash Platform/ScriptsDocker/StartNTGPM.bash 3 127.0.0.1 15000 11000 lo True 127.0
