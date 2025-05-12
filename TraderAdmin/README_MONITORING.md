# Real-Time Monitoring & Alerts

This document explains how to use the Real-Time Monitoring and Alerts features of the TraderAdmin application.

## Monitoring Dashboard

The Monitoring Dashboard provides real-time metrics and visualizations of your trading activity.

### Key Metrics Panel

The top section displays critical metrics at a glance:

- **Equity**: Current total account equity value
- **Daily P&L**: Profit and loss for the current trading day
- **Trades**: Number of trades executed today with win/loss ratio
- **Execution Latency**: Average and maximum order execution time in milliseconds
- **Errors**: Count of system errors with error type breakdown

### Equity Curve Chart

The Equity Curve chart shows your account equity over time, allowing you to visualize:

- Performance trends
- Drawdowns
- Periods of growth

### Execution Latency Chart

The Latency chart displays:

- Average order execution latency
- Maximum order execution latency

High latency can affect trading performance, especially for strategies that depend on quick executions.

### Open Positions Table

The Open Positions table shows all your current positions with:

- Symbol
- Quantity
- Entry Price
- Current Price
- P&L (color-coded green for profit, red for loss)
- Strategy type

### Refresh Controls

- **Auto-refresh**: Data automatically refreshes at the selected interval
- **Refresh rate**: Choose between 2, 5, 10, or 30 seconds
- **Manual refresh**: Click "Refresh Now" to update immediately

## Alerts Configuration

The Alerts tab allows you to set up automated notifications when important thresholds are exceeded.

### Alert Thresholds

Configure when alerts should be triggered:

- **Maximum Latency (ms)**: Alert when order execution time exceeds this value
- **Minimum Daily P&L ($)**: Alert when daily P&L falls below this threshold
- **Maximum Errors**: Alert when error count exceeds this value

### Notification Channels

Configure where alerts should be sent:

#### Email Alerts

1. Check "Enable Email Alerts"
2. Enter the email address where alerts should be sent

#### Slack Alerts

1. Check "Enable Slack Alerts"
2. Enter your Slack Webhook URL
   - To create a webhook URL in Slack, go to: App Directory -> Incoming Webhooks -> Add Configuration

### Alert Triggers

Choose which events should trigger alerts:

- **Alert on Errors**: Send notifications for system errors
- **Alert on Trades**: Send notifications when trades are executed

### Testing Alerts

You can test your alert configuration:

1. Select an alert type from the dropdown
2. Click "Send Test Alert"
3. Verify the notification arrives via your configured channels

## How It Works

### Metrics Collection

- Each trading service (Python orchestrator, Go scanner) collects metrics about its operations
- Metrics are aggregated and stored in memory or in a lightweight database
- The UI polls for updates at the configured refresh rate

### Alert Evaluation

- Alert thresholds are checked against current metrics regularly
- When a threshold is exceeded, the Alert Manager creates and sends notifications
- Alert history is maintained for reference

### Notification Delivery

- Email notifications use SMTP to deliver messages
- Slack notifications use Slack's Incoming Webhook API
- Both channels include details about the alert condition and relevant metrics

## Troubleshooting

- **No metrics data**: Verify the trading services are running
- **Slow updates**: Try increasing the refresh rate
- **Missing alerts**: Check the alert configuration and notification settings
- **Email delivery issues**: Verify SMTP settings and recipient address
- **Slack delivery issues**: Check webhook URL and Slack channel configuration
