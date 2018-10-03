ARG DC_VERSION
FROM owasp/dependency-check:$DC_VERSION
RUN /usr/share/dependency-check/bin/dependency-check.sh --updateonly -d /usr/share/dependency-check/notavolume

USER root
RUN apt-get update && apt-get install -y git-core && rm -rf /var/lib/apt/lists/*
COPY --from=bbvalabsci/buildbot-washer-worker:latest /washer /washer
COPY tasks.py /washer/
ENTRYPOINT ["/washer/entrypoint.sh"]
CMD ["/washer/tasks.py"]
