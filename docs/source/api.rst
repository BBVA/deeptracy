API
===

DeepTracy API is divided in two parts: a *control* API and a *query* API.


Control API
-----------

The control API is provided by **DeepTracy Server** service and allows the user
to manage the scanning tasks with a minimal REST API.


.. autobottle:: deeptracy.web:application


Query API
---------

The query API is provided by **Hasura** service allowing the user retrieve any
report structure she wants using GraphQL language.

The complete reference manual for Hasura can be found here_.

The following example illustrate how to request all the vulnerabilities for a
given analysis:

.. http:get:: /v1alpha1/graphql

   Perform the given query and return a JSON object with the results.

   **Example request**

   .. sourcecode:: http
   
      POST /v1alpha1/graphql HTTP/1.1
      Content-Type: application/json

        {
          "query": "{\n    analysis (where: {id: {_eq: \"904a2117-1da1-4c9c-a3d5-b03262f53d97\"}}){\n      state\n      installations {\n      \tspec\n        artifact {\n            name\n          \tversion\n            vulnerabilities {\n              provider\n              reference\n              details\n            }\n        }\n      }\n    }\n}\n",
          "variables": null
        }


   **Example response**

   .. sourcecode:: http


      HTTP/1.1 200 OK
      Transfer-Encoding: chunked
      Date: Fri, 24 Aug 2018 11:21:03 GMT
      Server: Warp/3.2.22
      Access-Control-Allow-Origin: http://localhost:8080
      Access-Control-Allow-Credentials: true
      Access-Control-Allow-Methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
      Content-Type: application/json; charset=utf-8

        {
          "data": {
            "target": [
              {
                "repository": "https://github.com/nilp0inter/gitsectest",
                "analyses": [
                  {
                    "state": "SUCCESS",
                    "installations": [
                      {
                        "artifact": {
                          "name": "Django",
                          "version": "1.4.4",
                          "vulnerabilities": [
                            {
                              "reference": "CVE-2013-1443",
                              "details": {
                                "cve": "CVE-2013-1443",
                                "score": 5,
                                "summary": "The authentication framework (django.contrib.auth) in Django 1.4.x before 1.4.8, 1.5.x before 1.5.4, and 1.6.x before 1.6 beta 4 allows remote attackers to cause a denial of service (CPU consumption) via a long password which is then hashed."
                              },
                              "provider": "patton"
                            }
                          ],
                          "source": "pypi"
                        },
                        "spec": "django",
                        "id": "c4cc6c32-de4e-457d-a1b0-14adeeeaeec4"
                      },
                      {
                        "artifact": {
                          "name": "org.springframework.boot:spring-boot-starter-web",
                          "version": "1.1.5.RELEASE",
                          "vulnerabilities": [],
                          "source": "central.maven.org"
                        },
                        "spec": "org.springframework.boot:spring-boot-starter-web:jar:1.1.5.RELEASE:compile",
                        "id": "b0ea360d-60a4-4817-a4f3-978f44bd2d95"
                      },
                      {
                        "artifact": {
                          "name": "y18n",
                          "version": "3.2.1",
                          "vulnerabilities": [],
                          "source": "https://registry.npmjs.org/y18n/-/y18n-3.2.1.tgz"
                        },
                        "spec": "y18n@^3.2.1",
                        "id": "fce4863f-db14-4702-849d-0315d324c2e2"
                      }
                    ],
                    "id": "4b200a05-f514-40fc-94b5-12ec5dbe5985",
                    "started": "2018-08-24T12:08:02.852095"
                  }
                ],
                "commit": "a5a01ca69ac99c793ec5af1bbc190f518d8fc412"
              }
            ]
          }
        }

   :query query: GraphQL query
   :query variables: List of variables to be used within the GraphQL query.


An example request using `curl`.

.. code-block:: bash

   $ curl 'http://localhost:8080/v1alpha1/graphql' \
          -H 'Content-Type: application/json' \
          --data-binary '
            {"query":"
               {
                 analysis (where: {id: {_eq: \"904a2117-1da1-4c9c-a3d5-b03262f53d97\"}}){
                   state
                   installations {
                     spec
                     artifact {
                       name
                       version
                       vulnerabilities {
                         provider
                         reference
                         details
                       }
                     }
                   }
                 }
               }",
            "variables":null}'

.. _here: https://docs.hasura.io/1.0/graphql/manual/queries/index.html
