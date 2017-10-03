
Feature: RetireJS Plugin
  RetireJS Plugin should work as expected

  Background: Database setup
    Given a clean system
    And a plugin for "retirejs" exists in the plugin table for lang "nodejs"
    And a project with "https://github.com/jspm/registry.git" repo exists in the database
    And a scan for lang "nodejs" exists for the project

  Scenario: The plugin generates valid output
    When a task for "start_scan" is added to celery for the scan
    And all celery tasks are done
    Then the scan folder is deleted
    And 1 scan analysis is generated in the database
    And the results for the analysis in the database includes the results in the file
    # And the results for the scan in the database includes the results in the file



