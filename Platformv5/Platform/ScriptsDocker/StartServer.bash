#!/bin/bash

service docker start
python Platform/PlatformManager.py "Source_IP=$1" "Source_Port=$2"
