Feature: IBKR Market Data Retrieval
  As a trader
  I want to retrieve real-time market data and option chains
  So that I can make informed trading decisions

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve current market data for a stock
    When I request market data for "AAPL"
    Then I should receive the current price data
    And the data should include bid, ask, and last price

  Scenario: Handle market data for invalid symbol
    When I request market data for an invalid symbol "INVALID"
    Then I should receive an error response
    And an appropriate error message should be logged

  Scenario: Retrieve option chain for a stock
    When I request the option chain for "AAPL"
    Then I should receive a list of available options
    And the options should include calls and puts
    And each option should have price and Greek data

  Scenario: Handle option chain for invalid symbol
    When I request the option chain for an invalid symbol "INVALID"
    Then I should receive an empty list
    And an appropriate error message should be logged 