#!/bin/bash

# SNBLocal.bash - Starts local Platform Managers
#
# SNBLocal starts platform managers on the local machine without Docker.
# Originally, it was written for StartNBenchPM, but also works for StartNTGPM.
#
# Eventually, it should be restructured so that the ethernet device and
# local network are parameterized differently, maybe also that the node
# type is parameterized.

# bash Platform/ScriptsDocker/StartNBenchPM.bash \
#      3 127.0.0.1 15000 11000 lo True 127.0
bash Platform/ScriptsDocker/StartNTGPM.bash \
     3 127.0.0.1 15000 11000 lo True 127.0
