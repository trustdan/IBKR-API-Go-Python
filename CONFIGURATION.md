# TraderAdmin Configuration Guide

This document provides a detailed description of the configuration options available in TraderAdmin's central `config.toml` file. Understanding these settings is crucial for properly configuring and optimizing your trading environment.

## Configuration File Location

The primary configuration file is located at:
- `config/config.toml` in the application directory

Changes to this file take effect after clicking "Apply Configuration" in the GUI, which safely pauses services, updates the configuration, and restarts services.

## Configuration Sections

### General Settings

```toml
[general]
log_level = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `log_level` | Controls the verbosity of application logs | "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" | "INFO" |

### IBKR Connection Settings

```toml
[ibkr_connection]
host = "localhost"              # IBKR TWS/Gateway host address
port = 7497                     # IBKR TWS/Gateway port
client_id_trading = 1           # Client ID for trading connection
client_id_data = 2              # Client ID for data connection
account_code = "YOUR_ACCOUNT"   # IBKR account code
read_only_api = false           # Whether to use read-only API mode
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `host` | IBKR TWS/Gateway host address | Any valid hostname or IP | "localhost" |
| `port` | IBKR TWS/Gateway port | 1-65535 | 7497 (paper) or 7496 (live) |
| `client_id_trading` | Client ID for trading connection | 1-999999 | 1 |
| `client_id_data` | Client ID for data connection | 1-999999 | 2 |
| `account_code` | IBKR account identifier | Valid IBKR account code | "" |
| `read_only_api` | Prevents placing actual orders if true | true, false | false |

### Trading Parameters

```toml
[trading_parameters]
global_max_concurrent_positions = 10     # Maximum number of concurrent positions
default_risk_per_trade_percentage = 1.0  # Percentage of account to risk per trade
emergency_stop_loss_percentage = 5.0     # Portfolio-level emergency stop loss percentage
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `global_max_concurrent_positions` | Maximum number of concurrent positions | 1+ | 10 |
| `default_risk_per_trade_percentage` | Percentage of account to risk per trade | 0.1-5.0 | 1.0 |
| `emergency_stop_loss_percentage` | Emergency stop loss percentage for the portfolio | 1.0-20.0 | 5.0 |

### Options Filters

```toml
[options_filters]
# Liquidity
min_open_interest = 500                     # Minimum open interest for an option contract
max_bid_ask_spread_percentage = 0.6         # Maximum bid-ask spread as percentage of mark price

# Volatility
use_iv_rank_filter = true                   # Whether to filter based on IV rank
min_iv_rank = 25.0                          # Minimum IV rank percentile
max_iv_rank = 75.0                          # Maximum IV rank percentile
use_iv_skew_filter = false                  # Whether to filter based on IV skew
min_put_call_iv_skew_percentage = -10.0     # Minimum put-call IV skew percentage
max_put_call_iv_skew_percentage = 20.0      # Maximum put-call IV skew percentage

# Probability & Risk/Reward
use_pop_filter = true                       # Whether to filter based on probability of profit
min_probability_of_profit_percentage = 55.0 # Minimum probability of profit percentage
use_width_vs_expected_move_filter = true    # Whether to filter based on spread width vs expected move
max_spread_width_vs_expected_move_percentage = 120.0 # Maximum spread width as percentage of expected move
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `min_open_interest` | Minimum open interest for an option contract | 0+ | 500 |
| `max_bid_ask_spread_percentage` | Maximum bid-ask spread as percentage of mark price | 0.0-5.0 | 0.6 |
| `use_iv_rank_filter` | Whether to filter based on IV rank | true, false | true |
| `min_iv_rank` | Minimum IV rank percentile | 0.0-100.0 | 25.0 |
| `max_iv_rank` | Maximum IV rank percentile | 0.0-100.0 | 75.0 |
| `use_iv_skew_filter` | Whether to filter based on IV skew | true, false | false |
| `min_put_call_iv_skew_percentage` | Minimum put-call IV skew percentage | -50.0-100.0 | -10.0 |
| `max_put_call_iv_skew_percentage` | Maximum put-call IV skew percentage | -50.0-100.0 | 20.0 |
| `use_pop_filter` | Whether to filter based on probability of profit | true, false | true |
| `min_probability_of_profit_percentage` | Minimum probability of profit percentage | 0.0-100.0 | 55.0 |
| `use_width_vs_expected_move_filter` | Whether to filter based on spread width vs expected move | true, false | true |
| `max_spread_width_vs_expected_move_percentage` | Maximum spread width as percentage of expected move | 0.0-300.0 | 120.0 |

### Greek Limits

```toml
[greek_limits]
use_greek_limits = true       # Whether to apply Greek limits to positions
max_abs_position_delta = 0.50 # Maximum absolute delta exposure per position
max_abs_position_gamma = 0.05 # Maximum absolute gamma exposure per position
max_abs_position_vega = 10.0  # Maximum absolute vega exposure per position
min_position_theta = 0.10     # Minimum positive theta decay per day per position
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `use_greek_limits` | Whether to apply Greek limits to positions | true, false | true |
| `max_abs_position_delta` | Maximum absolute delta exposure per position | 0.0-1.0 | 0.50 |
| `max_abs_position_gamma` | Maximum absolute gamma exposure per position | 0.0-0.2 | 0.05 |
| `max_abs_position_vega` | Maximum absolute vega exposure per position | 0.0-50.0 | 10.0 |
| `min_position_theta` | Minimum positive theta decay per day per position | 0.0-10.0 | 0.10 |

### Trade Timing

```toml
[trade_timing]
# Dynamic DTE Calculation
use_dynamic_dte = true             # Whether to use dynamic DTE calculation
target_dte_mode = "ATR_MULTIPLE"   # "FIXED", "ATR_MULTIPLE", or "VOLATILITY_INDEX"
dte_atr_period = 14                # ATR period for DTE calculation
dte_atr_coefficient = 1.2          # Coefficient to multiply ATR by for DTE calculation
fixed_target_dte = 45              # Used if target_dte_mode = "FIXED"
min_dte = 7                        # Minimum days to expiration
max_dte = 90                       # Maximum days to expiration

# Event Avoidance
avoid_earnings_days_before = 3    # Number of days before earnings to avoid
avoid_earnings_days_after = 1     # Number of days after earnings to avoid
avoid_ex_dividend_days_before = 2 # Number of days before ex-dividend date to avoid
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `use_dynamic_dte` | Whether to use dynamic DTE calculation | true, false | true |
| `target_dte_mode` | Mode for calculating target DTE | "FIXED", "ATR_MULTIPLE", "VOLATILITY_INDEX" | "ATR_MULTIPLE" |
| `dte_atr_period` | ATR period for DTE calculation | 1-100 | 14 |
| `dte_atr_coefficient` | Coefficient to multiply ATR by for DTE calculation | 0.1-5.0 | 1.2 |
| `fixed_target_dte` | Fixed target DTE to use if not using dynamic calculation | 1-365 | 45 |
| `min_dte` | Minimum days to expiration | 0-365 | 7 |
| `max_dte` | Maximum days to expiration | 1-365 | 90 |
| `avoid_earnings_days_before` | Number of days before earnings to avoid | 0-30 | 3 |
| `avoid_earnings_days_after` | Number of days after earnings to avoid | 0-30 | 1 |
| `avoid_ex_dividend_days_before` | Number of days before ex-dividend date to avoid | 0-30 | 2 |

### Trading Schedule

```toml
[trading_schedule]
enabled = true              # Master switch for the scheduler
start_time_utc = "13:30"    # Trading start time in HH:MM format (UTC)
stop_time_utc = "20:00"     # Trading stop time in HH:MM format (UTC)
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri"] # Days when trading is allowed
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `enabled` | Master switch for the scheduler | true, false | true |
| `start_time_utc` | Trading start time in HH:MM format (UTC) | Valid time HH:MM | "13:30" (9:30 AM ET) |
| `stop_time_utc` | Trading stop time in HH:MM format (UTC) | Valid time HH:MM | "20:00" (4:00 PM ET) |
| `days_of_week` | Days of the week when trading is allowed | "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" | ["Mon", "Tue", "Wed", "Thu", "Fri"] |

### Alerts Configuration

```toml
[alerts_config]
enabled = true                # Enable the alerting system

[alerts_config.thresholds]
max_order_latency_ms = 1000   # Maximum acceptable order latency in milliseconds
min_daily_realized_pnl = -500.0 # Minimum acceptable daily realized P&L
max_portfolio_drawdown_percentage_today = 5.0 # Maximum acceptable portfolio drawdown percentage for the day
max_api_errors_per_hour = 10  # Maximum acceptable API errors per hour

[alerts_config.notifications.email]
enabled = false
recipients = ["your_email@example.com", "another_email@example.com"]
smtp_host = "smtp.example.com"
smtp_port = 587
smtp_user = "user"
smtp_pass = "password_env_var"

[alerts_config.notifications.slack]
enabled = false
webhook_url = "YOUR_SLACK_WEBHOOK_URL_ENV_VAR"  # Store sensitive URLs in env vars
```

| Parameter | Description | Possible Values | Default |
|-----------|-------------|-----------------|---------|
| `enabled` | Enable the alerting system | true, false | true |
| `max_order_latency_ms` | Maximum acceptable order latency in milliseconds | 0+ | 1000 |
| `min_daily_realized_pnl` | Minimum acceptable daily realized P&L | Any number | -500.0 |
| `max_portfolio_drawdown_percentage_today` | Maximum acceptable portfolio drawdown percentage for the day | 0-100 | 5.0 |
| `max_api_errors_per_hour` | Maximum acceptable API errors per hour | 0+ | 10 |
| Email `enabled` | Enable email notifications | true, false | false |
| Email `recipients` | List of email recipients | Valid email addresses | [] |
| Email `smtp_host` | SMTP server hostname | Valid hostname | "" |
| Email `smtp_port` | SMTP server port | 1-65535 | 587 |
| Email `smtp_user` | SMTP server username | String | "" |
| Email `smtp_pass` | SMTP server password (or environment variable name) | String | "" |
| Slack `enabled` | Enable Slack notifications | true, false | false |
| Slack `webhook_url` | Slack webhook URL (or environment variable name) | Valid URL | "" |

## Tips for Configuration

1. **Start Conservative:** Begin with smaller position sizes and risk settings while testing.
2. **Greek Limits:** Pay particular attention to the Greek limits to manage risk exposure.
3. **Schedule:** Configure trading hours to match your market's session (remembering UTC conversion).
4. **Alerts:** Configure alerts to be notified of any issues with your trading system.

## Applying Configuration Changes

After making changes to the configuration in the GUI:
1. Review your changes carefully before applying
2. Click the "Apply Configuration" button in the GUI
3. The system will:
   - Pause trading services
   - Validate and save your configuration
   - Restart the services with the new configuration

Always test your configuration changes during market hours when you can monitor the system's behavior. 