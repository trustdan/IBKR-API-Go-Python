### Plan 5: Real-Time Monitoring & Alerts

**Timeline:** ~1 week
 **Objective:** Build a live performance dashboard with charts and configure a flexible alerting system (Email, SMS, Slack, Webhooks) so traders stay informed of key events.

------

#### 5.1 Define Metrics & Data Flows

1. **Key Metrics to Surface**

   - **Equity Curve** (realÃ¢â‚¬Âtime P&L)
   - **Daily P&L** (cumulative since 00:00)
   - **Trades Executed Today** (count + win/loss ratio)
   - **Open Positions** (list with entry price, P&L)
   - **Execution Latency** (avg + max order round-trip time)
   - **Error Rates** (counts by component)

2. **Data Collection**

   - Each service (Python orchestrator, Go scanner) emits events via a central **metrics API**:

     ```go
     // example endpoint in Go
     func (a *API) GetMetrics() (MetricsPayload, error) { Ã¢â‚¬Â¦ }
     ```

   - Events pushed on each trade/execution via gRPC or HTTP to a lightweight **metrics store** in memory or Redis.

------

#### 5.2 Backend: Metrics & Alerts Services

1. **Metrics Service**

   - In the Go backend, implement `GetMetrics()` pulling from in-memory counters and store snapshots every N seconds.

   - Expose via Wails:

     ```go
     func (a *API) GetMetrics() (Metrics, error)
     ```

2. **Alert Manager**

   - Read alert thresholds from `config.toml` under `[alerts]` section:

     ```toml
     [alerts]
     max_latency_ms = 500
     min_daily_pnl = -1000
     notify_email = "trader@example.com"
     slack_webhook = "https://hooks.slack.com/Ã¢â‚¬Â¦"
     ```

   - In Python orchestrator, on each metric update, evaluate rules:

     ```python
     if latency_ms > cfg.alerts.max_latency_ms:
         alert_system.notify("High latency", Ã¢â‚¬Â¦)
     ```

   - Use pluggable backends: SMTP, Twilio, Slack Webhook.

------

#### 5.3 Frontend: Dashboard & Visualization

1. **New `MonitoringTab.svelte`**

   - **Metrics Panel**: numeric readouts for Equity, Daily P&L, Trades, Latency, Errors.
   - **Charts**:
     - **Equity Curve**: line chart of equity vs. time.
     - **Execution Latency**: bar chart or sparkline.
   - **Open Positions Table**: symbol, entry, current P&L.

2. **Data Fetch Loop**

   ```ts
   import { writable } from 'svelte/store';
   export const metrics = writable<Metrics>(null);

   setInterval(async () => {
     const m = await api.GetMetrics();
     metrics.set(m);
   }, 5000);
   ```

3. **Visualization**

   - Use a lightweight charting library (e.g. Recharts) to draw line and bar charts.
   - No hard-coded colorsÃ¢â‚¬â€use defaults for theme consistency.

------

#### 5.4 Alert Configuration UI

1. **`AlertsTab.svelte`**
   - Inputs for each threshold (latency, P&L, error count).
   - Fields for notification endpoints (email address list, Slack webhook URL, SMS numbers).
   - Ã¢â‚¬Å“Test AlertÃ¢â‚¬Â button to send a sample notification.
2. **Save & Validate**
   - Bind to `config.alerts.*`
   - On Ã¢â‚¬Å“Save AlertsÃ¢â‚¬Â, run the same `saveAndRestart(config)` flow to persist.

------

#### 5.5 Cucumber/Gherkin Scenarios

```gherkin
Feature: RealÃ¢â‚¬ÂTime Monitoring & Alerts
  Scenario: Display realÃ¢â‚¬Âtime equity curve
    Given trading has begun
    When Metrics arrive every 5 seconds
    Then the Equity Curve line chart updates accordingly

  Scenario: Trigger highÃ¢â‚¬Âlatency alert
    Given max_latency_ms = 200
    And a trade execution took 350 ms
    When metrics are evaluated
    Then an alert is sent via each configured channel

  Scenario: Test alert delivery from GUI
    Given valid email and Slack webhook in alerts config
    When user clicks Ã¢â‚¬Å“Test AlertÃ¢â‚¬Â
    Then a sample notification is delivered to each endpoint
```

------

#### 5.6 Deliverables

- **Metrics API** in Go backend and in-memory store
- **Alert Manager** in Python orchestrator with SMTP/Slack/Twilio hooks
- **Monitoring Tab** with numeric panels and live charts
- **Alerts Tab** for threshold configuration and test notifications
- Comprehensive **Gherkin tests** for dashboard updates and alert workflows

------

With Plan 5 complete, youÃ¢â‚¬â„¢ll have a fully instrumented, self-alerting trading terminalÃ¢â‚¬â€closing the loop on visibility and proactive risk management. Let me know if youÃ¢â‚¬â„¢d like to dive deeper into any piece!

