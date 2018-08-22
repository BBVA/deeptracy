ARG MVN_VERSION
FROM maven:$MVN_VERSION

COPY --from=bbvalabsci/buildbot-washer-worker:latest /washer /washer
COPY tasks.py /washer/
ENTRYPOINT ["/washer/entrypoint.sh"]
CMD ["/washer/tasks.py"]
