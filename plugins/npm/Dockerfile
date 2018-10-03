ARG NODE_VERSION
FROM node:$NODE_VERSION

COPY --from=bbvalabsci/buildbot-washer-worker:latest /washer /washer
COPY tasks.py /washer/
ENTRYPOINT ["/washer/entrypoint.sh"]
CMD ["/washer/tasks.py"]
