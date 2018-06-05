@only
Feature: Patton
  Patton should work as expected

  Background: Database setup
    Given a clean system
    And a project with "https://github.com/jspm/registry.git" repo exists in the database
    And a scan for lang "nodejs" in "master" branch exists for the project

  Scenario: Patton generates valid output
    When a task for "prepare_scan" is added to celery for the scan
    And all celery tasks are done
    #Then the scan folder is deleted
    #Then the vulnerabilities for the scan in the database exists
    And the scan state is DONE
    And the results for the scan in the database exists
