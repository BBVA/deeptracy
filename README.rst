.. |docs_deeptracy| image:: https://readthedocs.org/projects/deeptracy/badge/?version=latest
  :target: http://deeptracy.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. |travis_deeptracy| image:: https://travis-ci.org/BBVA/deeptracy.svg?branch=master
  :target: https://travis-ci.org/BBVA/deeptracy
  :alt: Build Status

.. |docker_deeptracy| image:: https://dockerbuildbadges.quelltext.eu/status.svg?organization=bbvalabs&repository=deeptracy
  :target: https://hub.docker.com/r/bbvalabs/deeptracy/
  :alt: Dockerhub Build

.. |travis_deeptracy_api| image:: https://travis-ci.org/BBVA/deeptracy-api.svg?branch=master
  :target: https://travis-ci.org/BBVA/deeptracy-api
  :alt: API Build Status

.. |docker_deeptracy_api| image:: https://dockerbuildbadges.quelltext.eu/status.svg?organization=bbvalabs&repository=deeptracy-api
  :target: https://hub.docker.com/r/bbvalabs/deeptracy-api/
  :alt: Dockerhub Build

.. |travis_deeptracy_core| image:: https://travis-ci.org/BBVA/deeptracy-core.svg?branch=master
  :target: https://travis-ci.org/BBVA/deeptracy-core
  :alt: Core Build Status

.. |pypi_deeptracy_core| image:: https://img.shields.io/pypi/v/deeptracy-core.svg
  :target: https://pypi.python.org/pypi/deeptracy-core
  :alt: PyPI package


+------------+-------------------------+-----------------------+-----------------------+
| Deeptracy  | |docs_deeptracy|        | |travis_deeptracy|    | |docker_deeptracy|    |
+------------+-------------------------+-----------------------+-----------------------+
| API        | |travis_deeptracy_api|  | |docker_deeptracy_api||                       |
+------------+-------------------------+-----------------------+-----------------------+
| CORE       | |travis_deeptracy_core| | |pypi_deeptracy_core| |                       |
+------------+-------------------------+-----------------------+-----------------------+

Deeptracy
=========

Deeptracy scans your project dependencies to spot vulnerabilities


.. image::  https://raw.githubusercontent.com/BBVA/deeptracy/develop/docs/_static/deeptracy-logo-small.png
  :alt: Deeptracy logo
  :width: 250 px


+----------------+----------------------------------------------+
|Project site    | https://github.com/bbva/deeptracy            |
+----------------+----------------------------------------------+
|Project sides   | https://github.com/bbva/deeptracy-api        |
|                | https://github.com/bbva/deeptracy-core       |
+----------------+----------------------------------------------+
|Issues          | https://github.com/bbva/deeptracy/issues/    |
+----------------+----------------------------------------------+
|Documentation   | https://deeptracy.readthedocs.org/           |
+----------------+----------------------------------------------+
|DockerHub       | https://hub.docker.com/r/bbvalabs/deeptracy/ |
+----------------+----------------------------------------------+

Deeptracy in a few words
========================

Is a meta tool to analyze the security issues in third party libraries used in your project.

Why?
====

There're **many different tools for analyze third party vulnerabilities** for many languages, **but there is not a
unique tool that works well for all of them**.

We've created **this project to simplify this process** and you can focus only in the important: your project.

**Deeptracy** can choose the most suitable security tools for each languages and notify the spotted vulnerabilities in
the project dependencies.

Documentation
=============

Go to documentation site: https://deeptracy.readthedocs.org/

Contributing to Deeptracy
=========================

You can contribute to Deeptracy in a few different ways:

- Submit issues through `issue tracker <https://github.com/BBVA/deeptracy/issues>`_ on GitHub.
- If you wish to make code changes, or contribute something new, please follow the
`GitHub Forks / Pull requests model <https://help.github.com/articles/fork-a-repo/>`_: fork the
`Deeptracy Repo <https://github.com/bbva/deeptracy/>`_, make the changes and propose it back by submitting a pull request.

License
=======

This project is distributed under `Apache License <https://github.com/BBVA/deeptracy/blob/master/LICENSE>`_
