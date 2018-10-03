FROM python:3.6
RUN pip install pipenv
COPY buildbot/Pipfile buildbot/Pipfile.lock ./
RUN pipenv install --system --deploy
COPY buildbot ./buildbot
#CMD ["python", "-u", "-m", "deeptracy"]
