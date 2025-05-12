Feature: Advanced Option Filters
  As an options trader
  I want to filter options by liquidity, Greeks, and other metrics
  So that I can find optimal trading opportunities

  Background:
    Given the TraderAdmin application is running
    And the user is on the Options tab

  Scenario: Filter options by open interest
    Given the options chain for "AAPL" is loaded
    When the user sets the minimum open interest to 1000
    Then only options with open interest greater than or equal to 1000 should be displayed

  Scenario: Filter options by bid-ask spread
    Given the options chain for "AAPL" is loaded
    When the user sets the maximum bid-ask spread percentage to 0.5
    Then only options with bid-ask spread percentage less than or equal to 0.5 should be displayed

  Scenario: Filter options by IV rank
    Given the options chain for "AAPL" is loaded
    When the user sets the minimum IV rank to 30
    And the user sets the maximum IV rank to 70
    Then only options with IV rank between 30 and 70 should be displayed

  Scenario: Filter options by Greek limits
    Given the options chain for "AAPL" is loaded
    When the user sets the maximum theta per day to 15
    And the user sets the maximum vega exposure to 0.8
    And the user sets the maximum gamma exposure to 0.05
    Then only options with acceptable Greek values should be displayed

  Scenario: Filter options by probability of profit
    Given the options chain for "AAPL" is loaded
    When the user sets the minimum probability out-of-the-money to 60
    Then only options with probability OTM greater than or equal to 60 should be displayed

  Scenario: Compute dynamic DTE based on ATR
    Given ATR is 10 for "AAPL"
    And the user enables dynamic DTE
    And the user sets the DTE coefficient to 1.5
    When the options chain for "AAPL" is loaded
    Then the optimal target DTE should be 15 days

  Scenario: Skip options expiring near earnings
    Given earnings for "AAPL" are in 2 days
    And the user sets skip earnings days to 3
    When the options chain for "AAPL" is loaded
    Then options expiring within 3 days of earnings should not be displayed
