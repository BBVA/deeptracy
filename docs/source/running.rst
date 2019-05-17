Running Deeptracy
=================

Deeptracy service is composed of several pieces, a docker-compose project has been created in the compose directory in order to ease deployment and tests. These are the files and their purpose:

- .env Contains the environmental variable values needed to authenticate against a database server.
- deeptracy-config.env Contains the environmental variable values to configure the deeptracy server instance.
- docker-compose.yml Starts all the containers needed for the service. POSTGRES_HOST environment variable must be provided (in command line or ,env file) in order to provide the database to the containers if not using the database compose file.
- docker-compose-database.yml Starts a container with a postgresql database and configures the deeptracy containers to connect to this instance.
- Dockerfile.hasuracli and hasura directory Used for configuring GraphQL engine against Deeptracy's database.

Deploy with internal database
-----------------------------

In order to start a fully containerized environment run:

.. code-block:: console

    > docker-compose -f docker-compose.yml -f docker-compose-database.yml up


Deploy with external database
-----------------------------

If you want to run against an existing database server run:

.. code-block:: console

    > docker-compose -f docker-compose.yml -e POSTGRES_HOST=somehost up


Docker images
-------------

Each component of the Deeptracy server has been published as a container in the `BBVALabs' organization at Docker Hub <https://cloud.docker.com/u/bbvalabs/>`_. Each container can be configured by using environmental variables:

Buildbot
~~~~~~~~

The following variables are used to configure the Buildbot server container:

- DOCKER_HOST (default="unix://var/run/docker.sock") For container management.
- WORKER_IMAGE_AUTOPULL default=True) Pull needed images.
- WORKER_INSTANCES (default=16) Number of instances to start.
- WORKER_IMAGE_WHITELIST (default=*) Comma separated list of allowed image shell-like patterns.
- BUILDBOT_MQ_URL (default=None) MQ endpoint if used.
- BUILDBOT_MQ_REALM (default="buildbot") MQ realm if MQ is used.
- BUILDBOT_MQ_DEBUG (default=False) Activate MQ debug.
- BUILDBOT_WORKER_PORT (default=9989) TCP port used by buildbot workers.
- BUILDBOT_WEB_URL (default="http://localhost:8010/") URL of Buildbot's web UI.
- BUILDBOT_WEB_PORT (default=8010) Port in which Buildbot web UI is listening.
- BUILDBOT_WEB_HOST (default="localhost") Host in which Buildbot web UI is listening.
- BUILDBOT_DB_URL (default="sqlite://") Database used by Buildbot to store its state.
- DEEPTRACY_SERVER_CONFIG (default=None) Defaults to use in repository analysis.
- DEEPTRACY_WORKER_IMAGE (default="bbvalabsci/gitsec-worker") Image used to clone repository and parse deeptracy.yml file for repository configuration.
- DEEPTRACY_BACKEND_URL (default=None) URL of Deeptracy server to use.

Deeptracy
~~~~~~~~~

The following variables are used to configure the Deeptracy server container:

- POSTGRES_HOST (default=None) Database server name.
- POSTGRES_DB (default='deeptracy') Database name.
- POSTGRES_USER (default=None) Database username.
- POSTGRES_PASSWORD (default=None) Database password.
- REDIS_HOST (default=None) Redis' listening address.
- REDIS_PORT (default=6379) Redis' listening port.
- REDIS_DB (default=0) Redis' listening .
- BUILDBOT_API (default='http://deeptracy-buildbot:8010') Buildbot's URL.
- PATTON_HOST (default='patton.owaspmadrid.org:8000') Patton's host and port.
- SAFETY_API_KEY (default=None)
- BOTTLE_MEMFILE_MAX (default=2048)
- MAX_ANALYSIS_INTERVAL (default=86400)
- HOST (default='localhost') Server's listening address.
- PORT (default=8088) Server's listening port.
- DEBUG (default=False) Activate server debug mode.

By default the ports exposed by each server are:

- 8010 Buildbot server.
- 8080 GraphQL engine.
- 8088 Deeptracy server.
- 9989 Buildbot worker.
