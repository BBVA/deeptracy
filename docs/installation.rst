.. _installation:

Installation
============

.. toctree::
    :maxdepth: 3

    installation

Components
----------

Deeptracy has four main components:

* :ref:`worker-ref` is responsible of extracting project dependencies, cloning repositories, notifications and more.
* :ref:`api-ref` this is the main entrance for actions
* :ref:`dashboard-ref` this is the dashboard for visual information on the system
* :ref:`patton-ref` is responsible to match dependencies with vulnerabilities

Each of this components is shipped as a docker image. You can find them in the
public deeptracy dockerhub https://hub.docker.com/search/?isAutomated=0&isOfficial=0&page=1&pullCount=0&q=deeptracy&starCount=0.

Beside the components of Deeptracy, the system needs two more things to work:

* `Postgres`_ database to store projects, scans and so on
* `Redis`_ in-memory data structure store used as message broker

.. _Postgres: https://www.postgresql.org/?&
.. _Redis: https://redis.io/

This two components can be launched as a docker containers, but you can also install
them without docker.

.. note::
    Note that if you want to run the containers by hand (no docker-compose) you need to create a custom network yourself.
    You can use docker-compose to run all deeptracy components at once (see :ref:`environment-up-ref`)

::

    $ docker network create deeptracy
    $ docker run --network=deeptracy -p 5432:5432 -d --name=postgres -e POSTGRES_PASSWORD=postgres postgres:alpine
    $ docker run --network=deeptracy -p 6379:6379 -d --name=redis redis:3-alpine

.. _worker-ref:

Deeptracy Workers
-----------------

Workers are celery processes. You can launch any number of workers **on the same hosts**. As they are celery workers
connected to a broker (redis), they will take tasks to even the workload.

One of the tasks performed by the workers is cloning repositories. For this, you need to **mount the same volume
in each worker from the host**, where the repositories will be cloned. This volume (*SHARED_VOLUME_PATH*)
will be mounted in various containers that the worker uses to perform distinct tasks.

::

    $ docker run -d -e BROKER_URI=redis://redis:6379 \
		   -e DATABASE_URI=postgresql://postgres:postgres@postgres:5432/deeptracy \
		   -e SHARED_VOLUME_PATH=/tmp/deeptracy \
		   -e PLUGINS_LOCATION=/opt/deeptracy/plugins \
		   -v /tmp:/tmp \
		   --network=deeptracy \
		   bbvalabs/deeptracy:latest

.. warning:: Because the repository to scan is only downloaded once, you can't have workers on different hosts,
    as the source code for the project is only present int he hosts that perform the task to download it.

The workers performs almost all the task inside docker containers. The worker image has docker installed, but you
can mount the docker socket from the host in to the worker containers, so the docker in the host would be used.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

This are the environment variables needed by the workers

* **BROKER_URI** Url to the redis broker (Ex. redis://127.0.0.1:6379)
* **DATABASE_URI** Url to the postgres database (Ex. postgresql://postgres:postgres@127.0.0.1:5432/deeptracy)
* **SHARED_VOLUME_PATH** Path in the host to mount as a volume in Docker images. this folder
    is going to be used to clone projects to be scanned. (Ex. /tmp/deeptracy)
* **LOCAL_PRIVATE_KEY_FILE** If you wanna clone private repositories, you can specify a private key file to
    be used when cloning such repos.

.. _api-ref:

Deeptracy API
-------------

The API component provides the access point to interact with deeptracy.

::

    docker run -d -e BROKER_URI=redis://redis:6379 \
		   -e DATABASE_URI=postgresql://postgres:postgres@postgres:5432/deeptracy \
		   -e SERVER_ADDRESS=0.0.0.0:8080 \
		   -e GUNICORN_WORKERS=5 \
		   -p 8080:8080 \
		   --network=deeptracy \
		   bbvalabs/deeptracy-api:latest



.. _dashboard-ref:

Deeptracy Dashboard
-------------------

With the dashboard you have a visual representation of the system. You can also access scan results, vulnerabilities
and more.

::

    docker run -d -e BROKER_URI=redis://redis:6379 \
		   -e DATABASE_URI=postgresql://postgres:postgres@postgres:5432/deeptracy \
		   -e SERVER_ADDRESS=localhost:8080
		   -p 8000:8000 \
		   --network=deeptracy \
		   bbvalabs/deeptracy-dashboard:latest

.. _patton-ref:

Path Patton
-----------

Path Patton is the responsible of matching dependencies with vulnerabilities. It has its own database (you can use a
namespace in a shared postgresql database) and it has an auto-sync mechanism with the vulnerabilities database.

::

    docker run -d -e BROKER_URI=redis://redis:6379 \
		   -e DATABASE_URI=postgresql://postgres:postgres@postgres:5432/patton \
		   -p 8001:8001 \
		   --network=deeptracy \
		   bbvalabs/path-patton:latest

.. _environment-up-ref:

Bringing up the environment
---------------------------

As all the pieces are shipped as Docker containers, is easy to bring up an environment.
You can find an example with code to launch Deeptracy in a single AWS instance in the
`deploy <https://github.com/BBVA/deeptracy/tree/master/deploy>`_ folder.

This is an example of a complete Docker Compose file that launch a complete working environment.

::

    version: '3'

    services:
      deeptracy:
        image: bbvalabs/deeptracy
        depends_on:
          - redis
          - postgres
        environment:
          - BROKER_URI=redis://redis:6379
          - DATABASE_URI=postgresql://postgres:postgres@postgres:5432/deeptracy
          - SHARED_VOLUME_PATH=/tmp/deeptracy
          - LOCAL_PRIVATE_KEY_FILE=/tmp/id_rsa
          - PLUGINS_LOCATION=/opt/deeptracy/plugins
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
          - /tmp:/tmp
        privileged: true
        command: ["./wait-for-it.sh", "postgres:5432", "--", "/opt/deeptracy/run.sh"]

      deeptracy-api:
        image: bbvalabs/deeptracy-api
        depends_on:
          - redis
          - postgres
        ports:
          - 8080:8080
        environment:
          - BROKER_URI=redis://redis:6379
          - DATABASE_URI=postgresql://postgres:postgres@postgres:5432/deeptracy
          - SERVER_ADDRESS=0.0.0.0:8080
          - GUNICORN_WORKERS=1
          - LOG_LEVEL=DEBUG
        command: ["./wait-for-it.sh", "postgres:5432", "--", "/opt/deeptracy/run.sh"]

      path-patton:
        image: bbvalabs/path-patton
        depends_on:
          - redis
          - postgres
        ports:
          - 8001:8001
        environment:
          - BROKER_URI=redis://redis:6379
          - DATABASE_URI=postgresql://postgres:postgres@postgres:5432/patton
          - LOG_LEVEL=DEBUG
        command: ["./wait-for-it.sh", "postgres:5432", "--", "/opt/deeptracy/run.sh"]

      deeptracy-dashboard:
        image: bbvalabs/deeptracy-dashboard
        ports:
          - 80:8080
        environment:
          - SERVER_ADDRESS=localhost:8080

      postgres:
        image: postgres:9.6-alpine
        ports:
          - 5432:5432
        environment:
          - POSTGRES_PASSWORD=postgres
        command: -p 5432

      redis:
        image: redis:3-alpine
        ports:
          - 6379:6379

This docker compose will bring up an environment ready to be used. You can access the dashboard at ``localhost``
