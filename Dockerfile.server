FROM python:3.6
RUN pip install pipenv
COPY deeptracy/Pipfile deeptracy/Pipfile.lock ./
RUN pipenv install --system --deploy
COPY deeptracy ./deeptracy
#CMD ["python", "-u", "-m", "deeptracy"]
