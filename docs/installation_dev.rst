.. _installation_dev:

Installation
============

.. toctree::
    :maxdepth: 3

    installation_dev

Python Version
--------------

We recommend using the latest version of Python 3. Deeptracy supports
Python 3.6 and newer.

Deeptracy Projects
------------------

Deeptracy has four repositories with each of its components:

* `Workers <http://github.com/BBVA/deeptracy>`_ main repository with celery tasks and plugins
* `Api <http://github.com/BBVA/deeptracy-api>`_ holds the Flask API
* `Dashboard <http://github.com/BBVA/deeptracy-dashboard>`_ has the front web
* `Core <http://github.com/BBVA/deeptracy-core>`_ shared library between workers and api projects. Data access components and plugins perks.

For develop, is recommended that you clone each repository under the same work dir:

::

    - deeptracy-project
    |- deeptracy
    |- deeptracy-api
    |- deeptracy-core
    |- deeptracy-dashboard

Virtual environments
--------------------

Is highly recommended to work with a single `virtual environment <https://virtualenv.pypa.io/en/stable/>`_
for all the projects by creating a single environment at the same level that the rest of the projects

::

    - deeptracy-project
    |- deeptracy
    |- deeptracy-api
    |- deeptracy-core
    |- deeptracy-dashboard
    |- .venv

.. _editable-mode-ref:

Deeptracy Core
--------------

Deeptracy core is a shared library that has common functionalities used in the rest of the projects. When developing is
recommended to install it in your virtualenv in
`editable mode <https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs>`_::

    $ cd deeptracy-core
    $ pip install -e .

This will instruct distutils to setup the core project in to `development mode <https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode>`_

Deeptracy Workers
-----------------

This project is a `Celery`_ project. You can install it with::

    $ cd deeptracy
    $ make install-requirements_dev

Deeptracy API
-------------

This project is a `Flask`_ project. You can install it with::

    $ cd deeptracy-api
    $ make install-requirements_dev

Dependencies
------------

These distributions will be installed automatically when installing Deeptracy.

* `Celery`_ is an asynchronous task queue/job queue based on distributed message passing
* `Redis`_ in-memory data structure store used as message broker in celery
* `Psycopg`_ PostgreSQL database adapter for Python
* `Pluginbase`_ for plugin management
* `Docker`_ most tasks are executed inside docker containers
* `PyYAML`_ parse yml files

.. _Celery: http://www.celeryproject.org/
.. _Redis: https://redis.io/
.. _Psycopg: http://initd.org/psycopg/docs/
.. _Pluginbase: http://pluginbase.pocoo.org/
.. _Docker: https://github.com/docker/docker-py
.. _PyYAML: https://pypi.python.org/pypi/PyYAML

Development dependencies
------------------------

These distributions will be installed for development and local testing

* `Bumpversion`_ control the version numbers in releases.
* `Sphinx`_ documentation generation
* `Flake8`_ for linting and code style
* `Coverage`_ checks code coverage
* `Behave`_ acceptance tests

.. _Bumpversion: https://github.com/peritus/bumpversion
.. _Sphinx: http://www.sphinx-doc.org/en/stable/#
.. _Flake8: https://pypi.python.org/pypi/flake8
.. _Coverage: https://coverage.readthedocs.io/en/coverage-4.4.1/
.. _Behave: http://pythonhosted.org/behave/
