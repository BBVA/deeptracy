# This feature is ONLY FOR LOCAL TESTING purposes as you need a LOCAL_PRIVATE_KEY in `test/acceptance/private_key/id_rsa`

Feature: Scan authenticated project repositories
  Deeptracy can clone repositories in projects

  Background: Database setup
    Given a clean system
    And a plugin for "retirejs" exists in the plugin table for lang "nodejs"
    And a project with "ssh://git@globaldevtools.bbva.com:7999/bglai/automodeling-front.git" repo with LOCAL_PRIVATE_KEY repo auth type exists in the database
    And a scan for lang "nodejs" exists for the project

  @local
  Scenario: The plugin generates valid output
    When a task for "start_scan" is added to celery for the scan
    And all celery tasks are done
    Then the scan folder is deleted
    And 1 scan analysis is generated in the database
    And the results for the analysis in the database exists
