Feature: IBKR Account Management
  As a trader
  I want to retrieve account and position information
  So that I can monitor my portfolio and risk

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve account summary
    When I request the account summary
    Then I should receive the account values
    And the summary should include cash balance and equity values

  Scenario: Retrieve current positions
    When I request my current positions
    Then I should receive a list of positions
    And each position should include symbol, quantity, and average cost

  Scenario: Handle position update events
    Given I have an open position in "AAPL"
    When a position update event occurs
    Then my position data should be updated accordingly
    And the update should be logged 