
Feature: RetireJS Plugin
  RetireJS Plugin should work as expected

  Scenario: The plugin generates valid output
    Given a project with "https://github.com/jspm/registry.git" repo exists in the database
    When a scan with "nodejs" is added to celery for the project
    And all celery tasks are done
    Then a scan folder with the cloned repo exists
    And the results for retirejs exists in a file in the scanned folder
    And the results for the scan in the database includes the results in the file



