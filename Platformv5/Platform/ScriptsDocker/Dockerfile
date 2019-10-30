FROM jpetazzo/dind
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update && apt-get install -y \
    python
RUN apt-get install -y python-twisted

ADD Platform Platform
CMD /bin/bash Platform/ScriptsDocker/StartServer.bash
