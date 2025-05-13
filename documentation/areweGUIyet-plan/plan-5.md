Absolutely! Let's get "Plan 5: Real-Time Monitoring & Alerts" refined and echoed back to you.

Here's the revised plan:

Markdown

### Revised Plan 5: Real-Time Monitoring & Alerts

**Timeline:** ~1 - 1.5 weeks

**Preamble:** This phase focuses on providing visibility into the trading system's performance and critical operational states. We will define key metrics, implement backend services to collect and expose this data, create a frontend dashboard to visualize metrics, and build an alert system to notify users of important events or threshold breaches.

**Objective:** Develop a monitoring dashboard in the GUI for real-time insights and an alert system configurable via `config.toml` to proactively inform users about predefined conditions.

------

#### 5.1 Define Key Metrics & Data Structures

1.  **Identify Core Metrics:**
    * **Portfolio Level:**
        * Real-time Equity (value of all positions + cash)
        * Total Realized P&L (today)
        * Total Unrealized P&L (current open positions)
        * Number of Open Positions
        * Buying Power / Available Capital
    * **Trade Level (Aggregated):**
        * Number of Trades Executed (today: total, wins, losses)
        * Win Rate (today)
        * Average Win Amount, Average Loss Amount
    * **System Health & Performance:**
        * IBKR Connection Status (already in `statusStore`, but relevant here)
        * Service/Container Status (e.g., orchestrator, scanner - from `statusStore`)
        * Average Order Execution Latency (ms)
        * Number of API Errors (e.g., IBKR API errors, internal errors)
        * Last Successful Data Sync Time (e.g., for market data scanner)

2.  **Go Backend: Define Metric Structures:**
    * Create Go structs to represent the metrics payload that will be sent to the frontend.
        *Example:*
        ```go
        // backend/models/metrics.go
        package models

        import "time"

        type PortfolioMetrics struct {
            Timestamp         time.Time `json:"timestamp"`
            Equity            float64   `json:"equity"`
            RealizedPNLToday  float64   `json:"realizedPnlToday"`
            UnrealizedPNL     float64   `json:"unrealizedPnl"`
            OpenPositionsCount int      `json:"openPositionsCount"`
            BuyingPower       float64   `json:"buyingPower"`
        }

        type TradeStatsToday struct {
            ExecutedCount int     `json:"executedCount"`
            WinCount      int     `json:"winCount"`
            LossCount     int     `json:"lossCount"`
            WinRate       float64 `json:"winRate"` // Calculated: WinCount / ExecutedCount
        }

        type SystemHealthMetrics struct {
            AvgOrderLatencyMs   float64 `json:"avgOrderLatencyMs"`
            ApiErrorCount       int     `json:"apiErrorCount"`
            LastDataSync      time.Time `json:"lastDataSync"`
        }

        // Overall metrics payload
        type AllMetrics struct {
            Portfolio PortfolioMetrics  `json:"portfolio"`
            Trades    TradeStatsToday   `json:"trades"`
            System    SystemHealthMetrics `json:"system"`
            // Potentially a list of individual open positions
        }
        ```

------

#### 5.2 Backend: Metrics Collection & Alerting Service

1.  **Metrics Collection & Aggregation (Go Backend):**
    * The Go backend (or a dedicated metrics service if architecture dictates) will be responsible for collecting/calculating metrics.
    * This might involve:
        * Receiving events/data from the Python orchestrator (e.g., trade executions, P&L updates) via an internal mechanism (e.g., gRPC, NATS, or even polling if simpler).
        * Querying IBKR for portfolio and position data.
        * Maintaining in-memory counters or a simple time-series store for some metrics.
    * Implement a Wails Go function: `GetLatestMetrics() (models.AllMetrics, error)` that compiles and returns the current state of all defined metrics.

2.  **Alert Configuration in `config.toml`:**
    * Define a new section for alert thresholds and notification channels.
        ```toml
        # In TraderAdmin/config/config.toml
        [alerts_config]
        enabled = true

        [alerts_config.thresholds]
        max_order_latency_ms = 1000
        min_daily_realized_pnl = -500.00 # Alert if P&L drops below this
        max_portfolio_drawdown_percentage_today = 5.0 # Alert if equity drops by X% from start of day
        max_api_errors_per_hour = 10

        [alerts_config.notifications.email]
        enabled = false
        recipients = ["your_email@example.com", "another_email@example.com"]
        # SMTP server settings might be needed here or read from env vars
        # smtp_host = "smtp.example.com"
        # smtp_port = 587
        # smtp_user = "user"
        # smtp_password = "password_env_var"

        [alerts_config.notifications.slack]
        enabled = false
        webhook_url = "YOUR_SLACK_WEBHOOK_URL_ENV_VAR" # Store sensitive URLs in env vars

        # Add other channels like SMS (Twilio) if needed
        ```

3.  **Alert Evaluation & Notification Logic (Python Orchestrator or dedicated Go service):**
    * This service periodically (or event-driven):
        1.  Fetches the latest metrics (either internally or by calling `GetLatestMetrics` if metrics are centralized in Go).
        2.  Loads alert thresholds from its current configuration.
        3.  Compares current metric values against configured thresholds.
        4.  If a threshold is breached:
            * Constructs an alert message.
            * Sends notifications via enabled channels (Email, Slack, etc.). Use appropriate libraries for each channel.
            * Implement basic de-duplication/throttling to avoid alert storms (e.g., don't send the same alert every second).
    * Implement a Wails Go function: `TestAlertNotification(channelType string, message string) error` for the GUI to trigger test alerts.

------

#### 5.3 Frontend: Monitoring Dashboard & Alerts UI

1.  **New Svelte Tab: `MonitoringTab.svelte`:**
    * This tab will display the metrics.
    * Create a Svelte store `metricsStore.ts` to hold the `AllMetrics` data.
    * Periodically call the `GetLatestMetrics()` Wails function (e.g., every 5-10 seconds) and update `metricsStore`.
    * **Layout:**
        * **Key Metric Panels:** Display important numbers clearly (e.g., Equity, Daily P&L, Open Positions Count, Avg Latency).
        * **Charts (using a library like Chart.js, Recharts, or a simpler Svelte-specific one):**
            * **Equity Curve:** A line chart showing portfolio equity over time (requires storing historical snapshots of equity, which might be a v2 for this chart). For v1, it could be a simple display of current equity.
            * **Daily P&L Trend:** A simple bar or line showing P&L for the current day.
        * **Open Positions Table:** A sortable table listing current open positions with symbol, quantity, entry price, current price, unrealized P&L.
        * **System Status Indicators:** Clearly show IBKR connection, service health.

2.  **New Svelte Tab: `AlertsConfigurationTab.svelte`:**
    * Use the `<DynamicForm />` component to render input fields for all parameters under `[alerts_config]` in `config.toml`.
    * This includes enabling/disabling alerts, setting thresholds, and configuring notification channel details (email addresses, webhook URLs).
    * **"Test Alert" Buttons:** For each configured and enabled notification channel (e.g., "Test Email Alert", "Test Slack Alert"), add a button.
        * Clicking this button calls the `TestAlertNotification(channel, "This is a test alert from TraderAdmin.")` Wails backend function.
    * Changes made here update the `configStore`. The main "Apply Configuration" button (from Phase 4) will save these settings to `config.toml` and trigger service restarts/reloads.

------

#### 5.4 Testing & Validation (Behavior Defined with Gherkin)

```gherkin
Feature: Real-Time Monitoring Dashboard and Alerting System

  Scenario: Displaying Real-Time Portfolio Metrics on Dashboard
    Given the TraderAdmin application is running and connected to IBKR
    And the backend metrics service is collecting portfolio data
    When the 'MonitoringTab' in the GUI fetches metrics periodically
    Then the dashboard displays the current Equity, Realized P&L, and Open Positions Count
    And these values update approximately every 5-10 seconds

  Scenario: Triggering a High Order Latency Alert
    Given the alert configuration 'max_order_latency_ms' is set to 200
    And an order execution takes 250ms
    And the alert system (Python orchestrator or Go service) evaluates metrics
    Then an alert notification is triggered
    And sent via all enabled channels (e.g., email, Slack) with details about the high latency

  Scenario: Configuring Email Alert Notification Details
    Given the user navigates to the 'AlertsConfigurationTab'
    When the user enables email notifications
    And enters "test@example.com" in the email recipients field
    And clicks "Apply Configuration" to save changes
    Then the 'config.toml' is updated with the new email alert settings
    And the alert service reloads the new configuration

  Scenario: Testing Email Alert Delivery from GUI
    Given email notifications are enabled and configured with a valid recipient and SMTP settings
    When the user clicks the "Test Email Alert" button on the 'AlertsConfigurationTab'
    Then the backend 'TestAlertNotification' function is called for the email channel
    And a sample email alert is successfully delivered to the configured recipient(s)

  Scenario: Alert Throttling (Conceptual)
    Given a 'max_api_errors_per_hour' threshold is set to 10
    And 11 API errors occur within a few minutes
    When the alert system evaluates this condition
    Then an alert for "Excessive API Errors" is sent
    And if more API errors occur immediately after, the same alert is not re-sent for a configurable cooldown period (e.g., 15 minutes)
```

------

#### 5.5 Deliverables for Phase 5

- Defined Go structs for metrics (`models.AllMetrics`).
- Go backend Wails function `GetLatestMetrics()` to provide current metric data.
- Python orchestrator (or dedicated Go service) logic for evaluating alert conditions based on `config.toml` and sending notifications via configured channels (e.g., Email, Slack).
- Go backend Wails function `TestAlertNotification()` to test alert delivery.
- A new `MonitoringTab.svelte` in the GUI displaying key metrics and basic charts, with data updating periodically.
- A new `AlertsConfigurationTab.svelte` allowing users to configure alert thresholds and notification channels, and test them.
- Updated `config.toml` template with `[alerts_config]` section.
- Passing Gherkin scenarios for dashboard updates and alert triggering/testing.

------

> **Conclusion of Initial Development Phases:** With Plan 5 complete, the TraderAdmin GUI will have a solid foundation: core setup, dynamic configuration, advanced trading filters, robust operational workflows, and essential monitoring/alerting capabilities. Future work can focus on more advanced charting, strategy backtesting UIs, detailed performance analytics, and further refinements.
