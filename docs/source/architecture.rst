Architecture
============



Components
----------

DeepTracy is composed of several components described in the following diagram:


.. blockdiag::
   :desctable:

    blockdiag {
        class component [color="white"];
        orientation = portrait;

        user [
            label="User",
            shape=actor,
            description="A system capable of requesting new vulnerability analysis and retrieving results"];

        postgresql [
            label="PostgreSQL",
            class="component",
            icon="https://raw.githubusercontent.com/docker-library/docs/01c12653951b2fe592c1f93a13b4e289ada0e3a1/postgres/logo.png",
            description="Persistence layer"];

        buildbot [
            label="BuildBot",
            class="component",
            icon="https://www.google-melange.com/archive/gsoc/2015/orgs/buildbot/logo-200.png",
            description="Dependency extraction"];
        hasura [
            label="Hasura",
            class="component",
            icon="https://d1qb2nb5cznatu.cloudfront.net/startups/i/820697-7da6f327870c08c1f39c09a0e1801b31-medium_jpg.jpg?buster=1441133201",
            description="Provides data API for the user"];
        deeptracy-server [
            label="DeepTracy Server",
            width=152,
            class="component",
            icon="https://raw.githubusercontent.com/BBVA/deeptracy/develop/docs/_static/deeptracy-logo-small.png",
            description="Task orchestration through control API"];

        buildbot, deeptracy-server -> postgresql [label="Write"];
        deeptracy-server -> buildbot [label="Schedule"];

        user -> deeptracy-server [label="Control"];
        user -> hasura [label="Query"];
        deeptracy-server -> user [label="Feedback"];

        hasura -> postgresql [label="Read", style=dotted]; 
    }


Interactions
------------

The following activity diagram summarizes the normal interaction among the
components of the system.

.. note::

   This conceptual diagram describe the type of interactions but not how they
   are performed. In other words, this diagram does not describe if the
   interactions are synchronous nor asynchronous.


.. actdiag::
   :desctable:

    actdiag {
      requestscan -> schedule -> dependencyextraction -> dependencyscan ->
      reportdependencies -> schedulevulnerabilityscan ->
      userfeedback -> requestresult -> retrieveresult -> consumeresult

      lane user {
         label = "User"
         requestscan [
             label="Request Vulnerability Scan",
             description="User request to schedule a vulnerability scan over a source repository"];
         requestresult [
             label="Request Results",
             description="Using GraphQL© query language the user request the scan information"];
         consumeresult [
             label="Consume Results",
             description=":)"];
      }

      lane deeptracy-server {
         schedule [
             label="Schedule Dependency Extraction",
             description="Ask buildbot to perform the dependency extraction process in the given repository/commit"
         ];
         schedulevulnerabilityscan [
             label="Vulnerability Scan",
             description="Scan for vulnerabilities on the retrieved dependencies using vulnerability providers",
             stacked];
         userfeedback [
             label="User Feedback",
             description="The provided webhook is called back to acknowledge the user that the scan is finished"
         ];
      }

      lane buildbot {
         dependencyextraction [
             label="Dependency Extraction Task",
             description="Use washer docker containers to extract dependencies"];
         reportdependencies [
             label="Report Dependencies",
             description="Report dependency list to DeepTracy Server"];
      }

      lane washer {
         dependencyscan [
             label = "Extract Dependencies",
             stacked,
             description="Launch docker containers with the appropiate environments and extract project(s) dependencies"];
      }

      lane hasura {
         retrieveresult [
             label = "Retrieve Results",
             description="Results are queried and retrieved from the database"];
      }
      
    }

