FROM python:3.6
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
COPY deeptracy ./deeptracy
#CMD ["python", "-u", "-m", "deeptracy"]
