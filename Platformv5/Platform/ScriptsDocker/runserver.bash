#!/bin/bash

docker build --tag="blp_distplatform" .

docker run -privileged -p 130.39.225.248:8007:8007 blp_distplatform

bash Platform/ScriptsDocker/RunServer.bash 130.39.225.248 8007
