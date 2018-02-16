Quick start
===========

This document is a quick introduction for use Deeptracy Service

First of run Patton Server
++++++++++++++++++++++++++

1 - Install Docker Compose
-------------------------

`Install Docker Compose from this link <https://docs.docker.com/compose/install/>`_

2 - Create a docker-compose.yml file
-----------------------
Download Docker Compose file from `this link <https://github.com/BBVA/deeptracy/blob/master/docker-compose.yml>`_ or copy this code


.. code-block:: file

    version: '3'

    services:

      postgres:
        image: postgres:9.6-alpine
        environment:
          - POSTGRES_PASSWORD=postgres
        ports:
          - 5433:5433
        command: -p 5433

      redis:
        image: redis:3-alpine
        ports:
          - 6379:6379

      deeptracy:
        image: bbvalabs/deeptracy
        depends_on:
          - redis
          - postgres
        environment:
          - BROKER_URI=redis://redis:6379
          - DATABASE_URI=postgresql://postgres:postgres@postgres:5433/deeptracy
          - POSTGRES_URI=postgresql://postgres:postgres@postgres:5433
          - SHARED_VOLUME_PATH=/tmp/deeptracy
          - LOCAL_PRIVATE_KEY_FILE=/root/.ssh/id_rsa
          - PATTON_URI=http://0.0.0.0:8000
          # - EMAIL_SMTP_SERVER=xxx.xxx.xxx
          # - EMAIL_SMTP_PORT=xxx
          # - EMAIL_SMTP_USER=xxx@xxx.xxx
          # - EMAIL_SMTP_PASSWORD=xxxxx
          # - EMAIL_FROM=xxx@xxx.xxx
        ports:
          - 8000:8000
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
          - /tmp:/tmp
          - ./private_key:/root/.ssh/
        privileged: true
        command: ["./init_patton_db.sh"]

      deeptracy-api:
        image: bbvalabs/deeptracy-api
        depends_on:
          - redis
          - postgres
        ports:
          - 8080:8080
        environment:
          - BROKER_URI=redis://redis:6379
          - DATABASE_URI=postgresql://postgres:postgres@postgres:5433/deeptracy
          - SERVER_ADDRESS=0.0.0.0:8080
          - GUNICORN_WORKERS=1
          - LOG_LEVEL=INFO
        command: ["./wait-for-it.sh", "postgres:5433", "--", "/opt/deeptracy/run.sh"]


3 - Execute the docker-compose file
-----------------------
.. code-block:: bash

  > docker-compose up

4 - ENJOY DEEPTRACY WITH PATTON
-----------------------


