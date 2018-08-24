Configuration File
==================

DeepTracy's analysis is driven by a YAML configuration file.


Load Strategy
-------------

This configuration file can be load from several places:

 * Analyzed respository root directory.
 * On the POST analysis request (not implemented yet).
 * Automatically generated from the analyzed repository using heuristics (not
   implemented yet).


File Format
-----------

`projects` key
~~~~~~~~~~~~~~

A list of `projects` to be scanned.


`projects:<name>:type`
~~~~~~~~~~~~~~~~~~~~~~

The name of the buildbot-washer docker image to be used for this scan.


`projects:<name>:strategy`
~~~~~~~~~~~~~~~~~~~~~~~~~~

The name of the buildbot-washer task to be executed by the image.

.. note::

    This value depends on the `type`


`projects:<name>:unimportant`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Boolean value. If `true` the scan will continue even if this particular scan
fails.


`projects:<name>:config`
~~~~~~~~~~~~~~~~~~~~~~~~

Object containing the particular configuration of the strategy.

.. note::

    Some of the key-value pairs in this object are specific to the `type`
    while others may be common to all of them.

`projects:<name>:config:path`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The location to be scanned relative to the project root.


Configuration Example
---------------------

.. code-block:: yaml

    projects:
        backend:
            type: deeptracy-python:2.7
            strategy: requirement_file
            unimportant: false
            config:
                path: src/backend
                requirement: requirements.txt
        backend2:
            type: deeptracy-mvn:3.5-jdk-9
            strategy: mvn_dependencytree
            unimportant: false
            config:
                path: src/backend2
        frontend:
            type: deeptracy-node:8
            strategy: npm_install
            unimportant: false
            config:
                path: src/frontend

