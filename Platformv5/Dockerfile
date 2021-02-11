#FROM jpetazzo/dind
#RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
#RUN apt-get install -y net-tools
#RUN apt-get update && apt-get install -y \
#    python
#RUN apt-get install -y python-twisted


FROM ubuntu:18.04
RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.8 -y
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3.8 /usr/bin/python

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update && apt-get install -y net-tools
RUN apt-get update && apt-get install -y python3-twisted
RUN apt-get update && apt-get install -y fort77
RUN apt-get update && apt-get install -y libf2c2-dev

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD Platform Platform
ADD JSONFiles JSONFiles
ADD Sandbox Sandbox
ADD Nas Nas
CMD /bin/bash Platform/ScriptsDocker/StartServer.bash
