# This feature is ONLY FOR LOCAL TESTING purposes as you need a LOCAL_PRIVATE_KEY in `test/acceptance/private_key/id_rsa`

Feature: Scan authenticated project repositories
  Deeptracy can clone repositories in projects

  Background: Database setup
    Given a clean system
    And a project with "ssh://git@globaldevtools.bbva.com:7999/bgls/test_deeptracy.git" repo with LOCAL_PRIVATE_KEY repo auth type exists in the database
    And a scan for lang "nodejs" in "quick" branch exists for the project

  @local
  Scenario:Patton generates valid output
    When a task for "prepare_scan" is added to celery for the scan
    And all celery tasks are done
    Then the scan folder is deleted
    And the vulnerabilities for the scan in the database exists
