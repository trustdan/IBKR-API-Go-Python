Feature: IBKR Order Management
  As a trader
  I want to place, monitor, and cancel option spread orders
  So that I can execute my trading strategy effectively

  Background:
    Given I am connected to IBKR
    And I have a valid option spread for AAPL

  Scenario: Place a limit order for a bull call spread
    When I place a limit order for 1 contract
    Then the order should be submitted successfully
    And the order status should be tracked

  Scenario: Place a market order for a bear put spread
    When I place a market order for 2 contracts
    Then the order should be submitted successfully
    And the order should be filled at market price

  Scenario: Cancel an open order
    Given I have placed a limit order
    And the order is not yet filled
    When I cancel the order
    Then the order should be cancelled successfully

  Scenario: Handle order rejection
    Given the market is closed
    When I place a market order for 1 contract
    Then the order should be rejected
    And an appropriate error message should be logged 