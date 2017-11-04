.. _testing_dev:

Testing
=======

Unit Tests
----------

For development is recommended to do unit tests to speedup the process (you don't need a full environment),
and only do acceptance and integration tests when the feature is ready and tested with unit tests.

.. warning:: Pipelines has a check on whether the test coverage has a minimum of code covered, so lowering the percentage
    of lines of code covered by unit tests is not an option. You can check your code coverage with ``make coverage``

Acceptance Tests
----------------

Code Coverage
-------------
