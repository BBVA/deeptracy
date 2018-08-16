ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION
RUN pip install pipenv

COPY --from=bbvalabsci/buildbot-washer-worker:latest /washer /washer
COPY tasks.py /washer/
ENTRYPOINT ["/washer/entrypoint.sh"]
CMD ["/washer/tasks.py"]
