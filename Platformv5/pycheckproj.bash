#!/bin/bash

runOne(){
    pychecker $1 >> pcout.txt
}

cd /home/brian/Desktop/gradschool/DockerStuff/Platformv3/Platform

echo "Start" > pcout.txt
runOne BenchNodePM.py
runOne ExpPlatformManager.py

echo "Output in Platform/pcout.txt"
