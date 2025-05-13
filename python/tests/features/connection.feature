Feature: IBKR Connection Management
  As a trader
  I want to connect to IBKR TWS/Gateway
  So that I can interact with the trading platform

  Background:
    Given the IBKR TWS/Gateway is running
    And I have valid connection parameters

  Scenario: Successful connection to IBKR
    When I connect to IBKR
    Then the connection should be established
    And account information should be available

  Scenario: Failed connection to IBKR
    Given the IBKR TWS/Gateway is not running
    When I attempt to connect to IBKR
    Then the connection should fail
    And an appropriate error message should be logged

  Scenario: Disconnection from IBKR
    Given I am connected to IBKR
    When I disconnect from IBKR
    Then the connection should be terminated
    And the system should handle the disconnection gracefully 