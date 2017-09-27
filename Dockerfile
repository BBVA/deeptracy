FROM python:3.6

# install docker
RUN curl -sSL https://get.docker.com/ | /bin/bash

RUN mkdir /tmp/install
WORKDIR /tmp/install

# add dependencies
ADD requirements* /tmp/install/
RUN pip install -r /tmp/install/requirements.txt

# add sources
ADD deeptracy /tmp/install/deeptracy
ADD README.rst /tmp/install
ADD setup.py /tmp/install

# install sources and romove them
RUN pip install -U .
RUN rm -rf /tmp/install

# add run script
RUN mkdir /opt/deeptracy
WORKDIR /opt/deeptracy
ADD wait-for-it.sh /opt/deeptracy
ADD run.sh /opt/deeptracy
RUN chmod +x /opt/deeptracy/run.sh

CMD ["/opt/deeptracy/run.sh"]
