FROM python:3.6

# install docker
RUN curl -sSL https://get.docker.com/ | /bin/bash

# add sources
RUN mkdir /tmp/install
ADD . /tmp/install

# install sources and romove them
WORKDIR /tmp/install
RUN pip install -U .
RUN rm -rf /tmp/install

# add run script
RUN mkdir /opt/deeptracy
ADD run.sh /opt/deeptracy
RUN chmod +x /opt/deeptracy/run.sh

CMD ["/opt/deeptracy/run.sh"]
