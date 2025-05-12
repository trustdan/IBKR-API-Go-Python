Feature: Real-Time Monitoring & Alerts
  As a trader
  I want to monitor my trading metrics in real-time
  And receive alerts when thresholds are exceeded
  So that I can quickly respond to changing market conditions

  Scenario: Display real-time equity curve
    Given the monitoring dashboard is open
    When metrics data arrives every 5 seconds
    Then the equity curve line chart updates accordingly
    And the P&L value updates in real-time

  Scenario: View open positions
    Given the monitoring dashboard is open
    And there are active trading positions
    Then the positions table displays all open positions
    And shows symbol, quantity, entry price, current price, and P&L

  Scenario: Trigger high-latency alert
    Given maximum latency threshold is set to 200ms
    And a trade execution took 350ms
    When metrics are evaluated
    Then an alert is sent via each configured channel
    And the alert history shows the high-latency alert

  Scenario: Configure alert thresholds
    Given I am on the alerts tab
    When I set maximum latency to 300ms
    And I set minimum daily P&L to -500
    And I save the settings
    Then the configuration is updated with new thresholds
    And trading services are restarted

  Scenario: Test alert delivery
    Given valid email and Slack webhook are configured
    When I click "Send Test Alert"
    Then a test notification is delivered to each endpoint
    And a confirmation toast appears
