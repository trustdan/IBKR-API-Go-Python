# TraderAdmin Configuration Guide

This document provides detailed information about configuring TraderAdmin.

## Configuration File

TraderAdmin uses a YAML configuration file (`config.yaml`) located in the main application directory. 
A template file named `config.yaml.example` is provided for reference.

## Configuration Sections

### General Application Settings

```yaml
app:
  name: "TraderAdmin"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  data_dir: "./data"
  temp_dir: "./temp"
```

| Setting | Description | Default |
|---------|-------------|---------|
| `name` | Application name | TraderAdmin |
| `log_level` | Logging level | INFO |
| `data_dir` | Directory for persistent data | ./data |
| `temp_dir` | Directory for temporary files | ./temp |

### Interactive Brokers Connection

```yaml
ibkr:
  host: "127.0.0.1"  # TWS/Gateway host (localhost)
  port: 7497         # Paper trading port (use 7496 for live)
  client_id: 1       # Client ID to use
  read_only: false   # Set to true for read-only mode
```

| Setting | Description | Default |
|---------|-------------|---------|
| `host` | IBKR TWS/Gateway host address | 127.0.0.1 |
| `port` | IBKR TWS/Gateway port (7497 for paper, 7496 for live) | 7497 |
| `client_id` | Client ID for trading connection | 1 |
| `read_only` | Whether to use read-only API mode | false |

### Trading Settings

```yaml
trading:
  enabled: true                # Master switch for trading
  paper_trading: true          # Use paper trading
  trading_hours:
    start: "09:30"             # Eastern Time
    end: "16:00"               # Eastern Time
  max_positions: 10            # Maximum concurrent positions
  risk_per_trade: 1.0          # % of account to risk per trade
  emergency_stop_loss: 5.0     # Emergency stop % for portfolio
```

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Master switch for trading | true |
| `paper_trading` | Use paper trading | true |
| `trading_hours.start` | Trading start time (Eastern Time) | 09:30 |
| `trading_hours.end` | Trading end time (Eastern Time) | 16:00 |
| `max_positions` | Maximum number of concurrent positions | 10 |
| `risk_per_trade` | Percentage of account to risk per trade | 1.0 |
| `emergency_stop_loss` | Emergency stop loss percentage for the portfolio | 5.0 |

### Notification Settings

```yaml
notifications:
  enabled: true
  email:
    enabled: false
    smtp_host: "smtp.example.com"
    smtp_port: 587
    smtp_user: "user@example.com"
    smtp_pass: "your_password_or_app_key"
    recipients:
      - "alerts@example.com"
  
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Enable the alerting system | true |
| `email.enabled` | Enable email notifications | false |
| `email.smtp_host` | SMTP server hostname | - |
| `email.smtp_port` | SMTP server port | 587 |
| `email.smtp_user` | SMTP server username | - |
| `email.smtp_pass` | SMTP server password (or environment variable name) | - |
| `email.recipients` | List of email recipients | - |
| `slack.enabled` | Enable Slack notifications | false |
| `slack.webhook_url` | Slack webhook URL | - |

### Health Check Settings

```yaml
health_check:
  enabled: true
  port: 8080
  path: "/healthz"
```

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Enable health check endpoint | true |
| `port` | Port to use for health check server | 8080 |
| `path` | URL path for health check endpoint | /healthz |

## Environment Variables

You can use environment variables to override configuration settings, which is useful for sensitive information like passwords.

Format: `TRADERADMIN_SECTION_KEY`

Examples:

- `TRADERADMIN_IBKR_PORT=7496` (override the IBKR port)
- `TRADERADMIN_NOTIFICATIONS_EMAIL_SMTP_PASS=your_secure_password` (override SMTP password)

## Docker and Kubernetes

For containerized deployments, environment variables and mounted configuration files are supported.

Example Docker command:

```bash
docker run -v /path/to/config.yaml:/app/config.yaml -e TRADERADMIN_IBKR_HOST=tws-container traderadmin/orchestrator:latest
```

Example Kubernetes ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: traderadmin-config
  namespace: traderadmin
data:
  config.yaml: |
    app:
      name: "TraderAdmin"
      log_level: "INFO"
    ibkr:
      host: "tws-service"
      port: 7497
    # ...remainder of configuration...
``` 