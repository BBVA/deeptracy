.. _usage_dev:

Usage
=====

.. toctree::
    :maxdepth: 3

    usage_dev

Makefiles & Dotenv
------------------

To standardize tasks among repositories, each repository have a ``Makefile`` that can be used to perform common tasks.
By executing ``make`` in the root of each project you can get a detailed list of tasks that can be performed.

When executing tasks with make, we also provide a ``.dot-env`` mechanism to have local environment variables for each
project. So, the first time you perform any make task, you will be prompted for the required environment variables for
that project.

Keep in mind that you can always change the local environment for a project by editing the ``.env`` file generated
in the project root folder.

This is a sample of common tasks that can be performed with make::

    $ make
    clean                remove all build, test, coverage and Python artifacts
    test                 run tests quickly with py.test
    test-all             run tests on every python version with tox
    lint                 check style with flake8
    coverage             check code coverage
    docs                 generate and shows documentation
    run                  launch the application
    at_local             run acceptance tests without environemnt. You need to start your own environment (for dev)
    at_only              run acceptance tests without environemnt, and just features marked as @only (for dev)
    at                   run acceptance tests in complete docker environment


.. _local-environment-ref:

Local environment
-----------------

You can have a full functional working local environment to do integration or acceptance tests. En the workers and API
projects you can find a ``docker-compose-yml`` file that will launch a postgres and a redis container::

    $ cd deeptracy
    $ docker-compose up

Once the database and the broker are in place, now you can launch each project issuing a ``make run`` on each of them.

Development flow
----------------

You should be doing unit test to test the new features. When you are working in **deeptracy** or in **deeptracy-api**
is likely you will also need to work in **deeptracy-core**. If you installed the core in :ref:`editable-mode-ref` you
will see the changes in the core from the other projects as soon as they are made.

Once the new feature is covered and tested with unit tests, you can launch a :ref:`local-environment-ref` and run
the acceptance tests in the local environment with ``make at_local``
