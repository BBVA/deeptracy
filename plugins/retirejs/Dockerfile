FROM node:8

RUN npm install -g retire

RUN mkdir /opt/retire
ADD run_retire.sh /opt/retire
RUN chmod +x /opt/retire/run_retire.sh

CMD ["/opt/retire/run_retire.sh"]
