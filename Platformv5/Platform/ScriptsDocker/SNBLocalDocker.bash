#!/bin/bash

# SNBLocalDocker.bash - Starts local Platform Managers in Docker
#
# SNBLocalDocker starts platform managers on the local machine in Docker.
# Originally, it was written for StartNBenchPM, but also works for StartNTGPM.
#
# Eventually, it should be restructured so that the ethernet device and
# local network are parameterized differently, maybe also that the node
# type is parameterized.  The container name and version should also be
# parameterized.

# docker run --net="host" --privileged bpete16/distplatform:4.60 \
#        bash Platform/ScriptsDocker/StartNTGPM.bash \
#        3 127.0.0.1 15000 11000 lo True 127.0


# bash Platform/ScriptsDocker/StartNBenchPM.bash 5 127.0.0.1 15000 11000 lo True 127.0

docker run -it --net="host" --privileged bpete16/distplatform:4.60 bash -c "Platform/ScriptsDocker/StartNBenchPM.bash 5 127.0.0.1 15000 30000 lo True 127.0; while true; do sleep 10; done"