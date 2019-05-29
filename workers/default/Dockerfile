FROM bbvalabsci/buildbot-washer-worker:latest
RUN apk update && apk upgrade && apk add --no-cache git openssh-client
RUN touch notasks.py
CMD ["/washer/entrypoint.sh", "notasks.py"]
