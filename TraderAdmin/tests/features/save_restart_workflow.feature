Feature: Pause/Edit/Unpause Workflow
  As a trader
  I want to safely pause, edit, and unpause the trading system
  So that I can make configuration changes without disrupting active trades

  Scenario: Safely apply new settings
    Given containers are running
    When I click "Save & Restart"
    Then PauseStack is called
      And config.toml is backed up and updated
      And UnpauseStack is called
      And services log "Config reloaded"

  Scenario: Edit trading schedule
    Given I am on the Scheduling tab
    When I change trading_start_time to "10:00:00"
      And I change trading_end_time to "15:30:00"
      And I click "Save & Restart"
    Then the configuration is updated with the new times
      And the scheduler is reconfigured with the new times

Feature: Automated Trading Schedule
  As a trader
  I want to automate trading start and stop times
  So that I don't have to manually enable/disable trading

  Scenario: Auto-stop at end of day
    Given schedule.stop = "16:00"
      And trading_enabled = true
    When system time reaches 16:00
    Then trading_enabled is set to false

  Scenario: Auto-start next day
    Given schedule.start = "09:30"
      And trading_enabled = false
    When system time reaches 09:30
    Then trading_enabled is set to true

  Scenario: Skip non-trading days
    Given trading_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
      And current day is "Saturday"
    When scheduler is running
    Then trading_enabled remains false
      And no trading actions are performed
