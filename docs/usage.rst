.. _usage:

Usage
=====

This section explain how to use Deeptracy. Once installed Deeptracy can be used as a service. This means that a
public API is exposed and all functionalities can be used through it.

Create Projects
~~~~~~~~~~~~~~~

Projects are the main object in the API. A project represents a single repository that you want to scan and monitorice
for vulnerabilities. You can't have more that one project with the same repository in the database.

To create projects you need to invoke the :ref:`create_project-ref` endpoint after any scan.

Launch Scans
~~~~~~~~~~~~

Every time a scan is launched, Deeptracy will check for the project dependencies. **If the dependencies have changed
from the last scan performed, the scan will begin**.

A scan is performed by cloning the project repository and running different plugins against the source code. You can
launch scans manually by calling the :ref:`create_scan-ref` endpoint or by :ref:`configuring-hook-ref`.

Spot Vulnerabilities
~~~~~~~~~~~~~~~~~~~~

Evey scan will run N analyzers (one for each plugin available in the system) and save the vulnerabilities found on the
database. Once all analyzers are done, all vulnerabilities are merged together and saved as a final vulnerability list.

You can access individual analyzer results with :ref:`get_analyzer_vulnerabilties-ref` endpoint or the final scan list
with the :ref:`get_scan_vulnerabilities-ref` endpoint.

Get Notified
~~~~~~~~~~~~

Every time a scan finishes, if your project have the information to receive notifications you will receive one with the
spotted vulnerabilities.

.. _configuring-hook-ref:

Configuring a hook for your project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure a hook in your repository, so every time a push is detected a scan will automatically launched for
your project. The url for the hook is ``{host}/api/1/webhook/``

* `Github <https://developer.github.com/webhooks/creating/>`_ Create a webhook for *PUSH* actions only
* `Bitbucket <https://confluence.atlassian.com/bitbucket/manage-webhooks-735643732.html>`_ Create a webhook for *PUSH* actions only
