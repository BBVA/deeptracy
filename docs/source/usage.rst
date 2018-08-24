Usage
=====

.. seqdiag::

   seqdiag {
     user -> deeptracy [label="POST /analysis/", note="{\n 'repository': 'xxx',\n 'commit': 'yyy',\n 'webhook': 'http://user/webhook'\n}"];
     user <- deeptracy [label="200 OK", note="{'id': 'f676d67f-55b5-4b5c-9e10-84ba453766b0'}"];

     === Eventually the scan will finish ===

     user <- deeptracy [label="POST /webhook", note="{\n 'id': 'f676d67f-55b5-4b5c-9e10-84ba453766b0',\n 'state': 'SUCCESS'\n}"];
     user -> deeptracy [label="200 OK"];

     === The user retrieve a report ===

     user -> hasura [label="POST /v1alpha1/graphql", note="{\n 'query': '...',\n 'variables': '...'\n}"];
     user <- hasura [label="200 OK", note="{\n ... \n}"];

   }


The sequence diagram above shows the typical usage workflow.
