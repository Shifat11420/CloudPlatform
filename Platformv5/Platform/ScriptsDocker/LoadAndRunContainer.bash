#!/bin/bash
service docker start
docker load --input $1
docker run $2
