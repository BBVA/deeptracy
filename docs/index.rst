:orphan:

.. image::  https://raw.githubusercontent.com/BBVA/deeptracy/develop/docs/_static/deeptracy-logo-small.png
   :alt: Deeptracy: spot vulnerabilities in your dependencies
   :width: 250 px

.. attention::
    This documentation is a work in progress. We are currently in development phase and changing things in a daily basis.

What is Deeptracy?
==================

Deeptracy is a tool that can scan projects to find vulnerabilities in its dependencies. It works by accessing the source
code of repositories and extracting the dependencies list to match them against the
`NIST NVD Data Feeds <https://nvd.nist.gov/vuln/data-feeds>`_

Deeptracy perks:

* Deployed as docker containers
* Scalable
* Usable inside deployment pipelines
* Multi-language (Scan projects in Python, Java, Javascript and more)
* Reactive (we monitor new vulnerabilities and warn you if any affects your dependencies)
* Open Source :D

Welcome to Deeptracy
====================

Welcome to Deeptracy's documentation. This documentation is divided into two different parts.
One is the :ref:`userdocs-ref` which include installation and usage, and the other is the
:ref:`developer-ref` which include :ref:`sourcecode-ref` documentation, local environment, testing
and so on.

.. include:: user.rst
.. include:: developer.rst
.. include:: modules.rst
