FROM jpetazzo/dind
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get install -y net-tools
RUN apt-get update && apt-get install -y \
    python
RUN apt-get install -y python-twisted
RUN apt-get install -y fort77
RUN apt-get install -y libf2c2-dev

ADD Platform Platform
ADD JSONFiles JSONFiles
ADD Sandbox Sandbox
ADD Nas Nas
CMD /bin/bash Platform/ScriptsDocker/StartServer.bash
