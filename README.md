# Auto Vertical Spread Trader

[![CI/CD Pipeline](https://github.com/trustdan/ibkr-trader/actions/workflows/ci.yml/badge.svg)](https://github.com/trustdan/ibkr-trader/actions/workflows/ci.yml)
[![Python Status](https://img.shields.io/github/actions/workflow/status/trustdan/ibkr-trader/ci.yml?label=python)](https://github.com/trustdan/ibkr-trader/actions/workflows/ci.yml)
[![Go Status](https://img.shields.io/github/actions/workflow/status/trustdan/ibkr-trader/ci.yml?label=go)](https://github.com/trustdan/ibkr-trader/actions/workflows/ci.yml)
[![Docker Image](https://img.shields.io/docker/pulls/trustdan/auto-vertical-spread-python)](https://hub.docker.com/r/trustdan/auto-vertical-spread-python)
[![Docker Image](https://img.shields.io/docker/pulls/trustdan/auto-vertical-spread-go)](https://hub.docker.com/r/trustdan/auto-vertical-spread-go)

An automated trading system that implements vertical spread trading strategies using Interactive Brokers (IBKR) API. The system scans for specific technical patterns, selects optimal option spreads, and handles trade execution for equity options.

## Overview

This project is a hybrid Python-Go trading system designed for automated option spread trading. It combines:

- **Python Orchestrator**: Handles business logic, strategy implementation, trade execution, and risk management
- **Go Scanner Service**: Provides high-performance concurrent market scanning
- **Interactive Brokers Integration**: Connects to IBKR for market data and trade execution
- **Backtesting Framework**: Allows evaluation of strategies on historical data

The system is designed to identify technical patterns in equities, select optimal vertical spreads based on configurable criteria, and execute trades with proper risk management controls.

## Features

- **Automated Technical Analysis**: Scans for specific patterns using custom-built strategies
- **Option Chain Analysis**: Analyzes option chains to find optimal vertical spread opportunities
- **Enhanced Option Filtering**: Greater-fidelity controls for precise spread selection based on 22+ parameters
- **Risk Management**: Implements position sizing and risk controls
- **Trade Execution**: Interfaces with Interactive Brokers for automated or semi-automated trading
- **Performance Tracking**: Tracks and reports on system performance
- **Dual Execution Modes**: Optimized for both paper trading and live trading environments
- **High-performance Scanner**: Go-based concurrent scanner processes 100+ symbols per second
- **Caching Strategy**: Efficient data management with intelligent caching
- **Robust Error Handling**: Comprehensive error recovery mechanisms
- **Alerting System**: Multi-channel notifications for trade and system events
- **Intuitive Admin UI**: TraderAdmin GUI for easy configuration and monitoring

## Trading Strategies

The system implements four primary technical strategies:

1. **High Base Strategy**: Identifies stocks trading near resistance with strong momentum
2. **Low Base Strategy**: Identifies stocks trading near support with weak momentum
3. **Bull Pullback Strategy**: Identifies uptrends with temporary pullbacks
4. **Bear Rally Strategy**: Identifies downtrends with temporary rallies

Each strategy is configurable with parameters for technical indicators, thresholds, and trade timing.

## System Architecture

The system follows a modular architecture designed for flexibility and extensibility:

```
python/
├── src/
│   ├── app/              # Application-level code
│   ├── brokers/          # Broker integration code
│   ├── models/           # Data models and classes
│   ├── strategies/       # Trading strategy implementations
│   ├── trading/          # Core trading components
│   └── utils/            # Utility functions
└── config.yaml           # Configuration file

go/
├── cmd/
│   └── scanner/          # Go scanner application
├── pkg/                  # Shared Go packages
└── config.json           # Go scanner configuration
```

## Interactive Brokers Integration

This trading system is designed to work seamlessly with Interactive Brokers (IBKR) and leverages the TWS API for market data and order execution. This section provides comprehensive guidance on setting up and operating the system with IBKR's trading platforms.

### Prerequisites

* **Interactive Brokers Account**:
  * IBKR Pro account (live or paper trading)
  * Latest stable release of TWS or IB Gateway
  * Ensure Java is installed (both TWS and IB Gateway are Java applications)

* **Software Requirements**:
  * Docker Desktop (preferred) or manual setup using Python 3.8+ and Go 1.20+
  * Pre-commit hooks installed (for development)

### Setting Up TWS or IB Gateway

1. **Download Software**:
   * [Trader Workstation (TWS)](https://www.interactivebrokers.com/en/trading/tws.php)
   * [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)
   * Recommended: Use offline versions to avoid automatic updates

2. **Configure API Access**:
   * Launch TWS or IB Gateway and log in to your account
   * Navigate to **Edit > Global Configuration > API > Settings**:
     * Check **"Enable ActiveX and Socket Clients"**
     * Uncheck **"Read-Only API"**
     * Note the **Socket Port** (default: 7497 for paper, 7496 for live)

   ![TWS API Configuration](https://www.interactivebrokers.com/campus/wp-content/uploads/sites/2/2023/06/API-settings-700x489.png)

3. **Optimize for Reliability**:
   * In **Global Configuration > Lock and Exit**:
     * Set **"Never Lock Trader Workstation"** to prevent auto-logout
     * Enable **"Auto restart"** for uninterrupted operation
   * In **Global Configuration > API > Precautions**:
     * Enable bypass options for API orders to eliminate confirmation dialogs
   * In **Global Configuration > General**:
     * Adjust **Memory Allocation** to 4000MB for optimal performance

4. **Allow API Connections**:
   * Uncheck **"Allow connections from localhost only"** if connecting remotely
   * Add your application's IP address to **"Trusted IPs"** section

### Connecting the Trading Application

1. **Configure the Application**:
   * Copy `config.yaml.example` to `config.yaml`
   * Set your IBKR connection parameters:

   ```yaml
   IBKR:
     host: 127.0.0.1  # Use actual IP if connecting to a remote TWS
     port: 7497       # Paper trading port (7496 for live)
     clientId: 1      # Unique client ID
   ```

2. **Market Data Requirements**:
   * Ensure you have appropriate market data subscriptions for the instruments you plan to trade
   * For paper accounts, enable market data sharing from your live account in Account Management
   * Option trading requires specific option data subscriptions

3. **Paper Trading Setup**:
   * Create a paper trading account through Account Management
   * Enable market data sharing from your live account to your paper account
   * Allow up to 24 hours for market data sharing to take effect

### Running the Application

The system connects to Interactive Brokers using the ib_insync library, which provides a more Pythonic interface to the TWS API. Key features include:

1. **Connection Management**:
   * The application handles connection initiation and monitors connection status
   * Automatic reconnection attempts if the connection is lost
   * TWS API limits to 50 messages per second from the client

2. **Data Handling**:
   * Real-time market data streaming for scanning opportunities
   * Historical data retrieval for strategy backtesting
   * Account and position monitoring

3. **Order Execution**:
   * Vertical spreads are constructed as bracket orders
   * Risk management rules enforce position sizing limits
   * Order status monitoring and execution reporting

4. **Operational Best Practices**:
   * Always restart TWS/IB Gateway weekly or enable auto-restart
   * Monitor API connection status through the application logs
   * Review execution reports and position data for accuracy

### Troubleshooting

1. **Connection Issues**:
   * Verify TWS/IB Gateway is running and configured for API access
   * Confirm the socket port in your config matches the TWS settings
   * Check that your IP address is in the TWS "Trusted IPs" list

2. **Data Issues**:
   * Verify market data subscriptions for the instruments you're trading
   * Check TWS market data connection status (green indicator in TWS)
   * Paper accounts may have delayed or limited market data

3. **Order Issues**:
   * Review TWS logs for rejected orders
   * Verify account permissions for the instruments you're trading
   * Check available buying power and margin requirements

### Advanced Configuration

1. **Client ID Management**:
   * Use unique client IDs for each application instance
   * Set a Master Client ID in TWS to receive all order updates

2. **Performance Optimization**:
   * Increase TWS memory allocation for faster data processing
   * Use IB Gateway instead of TWS for lower resource consumption
   * Consider direct FIX API connection for high-frequency applications

For more detailed information about the TWS API, refer to the [Interactive Brokers API Documentation](https://interactivebrokers.github.io/tws-api/).

## Quick Start with Docker

The easiest way to run the system is using Docker:

### Prerequisites

- Docker Desktop installed and running
- Internet connection to pull images
- Interactive Brokers TWS or IB Gateway running (for trading)

### Running Locally

1. Using the provided scripts:

   **On Windows (PowerShell):**
   ```powershell
   # Run with latest version
   .\run-local.ps1

   # Or specify a specific tag/version
   .\run-local.ps1 develop
   ```

   **On Linux/Mac:**
   ```bash
   # Make the script executable
   chmod +x run-local.sh

   # Run with latest version
   ./run-local.sh

   # Or specify a specific tag/version
   ./run-local.sh develop
   ```

2. The services will be available at:
   - Go scanner: http://localhost:50051
   - Go metrics: http://localhost:2112
   - Python orchestrator: http://localhost:8000

3. To stop the services:
   ```
   docker stop vertical-spread-go vertical-spread-python
   ```

4. To view logs:
   ```
   docker logs vertical-spread-go -f
   docker logs vertical-spread-python -f
   ```

### Windows Installer

We now provide an NSIS-based installer for Windows users that:

1. **Verifies system requirements** including:
   - Docker Desktop
   - Kubernetes
   - TWS/IB Gateway availability
2. **Installs the application** with proper Windows integration:
   - Desktop and Start Menu shortcuts
   - Registry entries
   - Configuration management
3. **Provides uninstallation** with option to preserve configuration files

To install:
1. Download the latest `TraderAdmin-Setup-1.0.0.exe` release
2. Run the installer and follow the prompts
3. Launch from Start Menu or Desktop shortcut

### Daily Operator Workflow

| Step | Action                                                       |
| ---- | ------------------------------------------------------------ |
| 1    | **Start Docker Desktop** (brings up k8s)                    |
| 2    | `kubectl apply -k deploy/` – spins up the trading pods      |
| 3    | **Launch TWS / IB Gateway** and log in                      |
| 4    | **Run TraderAdmin** • *Save* performs `Pause → write config → Unpause + SIGUSR1` |

### Key Features

- **Live Container Status**: Monitor running containers in real-time
- **Edit Configuration**: Modify trading parameters through an intuitive GUI
- **Pause/Unpause Stack**: Temporarily halt trading while making changes
- **Hot Reload**: Apply configuration changes without restarting containers
- **System Status Checks**: Verify Docker, Kubernetes, and TWS availability

### Configuration Management

The system now uses TOML format for configuration, providing better interoperability between Python and Go services. Both services include signal handlers (SIGUSR1) and file watchers to detect and reload configuration changes automatically.

### Kubernetes Integration

The trader components are now fully Kubernetes-ready with:
- Persistent volume for shared configuration
- Proper container labeling for discovery
- Read-only config mounts for services

### Implementation Details

See the full implementation details in:
- `trader-admin/README.md` - Overview of the implementation
- `trader-admin/IMPLEMENTATION.md` - Technical implementation details
- `trader-admin/INSTALLER_GUIDE.md` - Guide for the Windows installer
- `trader-admin/NSIS-README.md` - Technical details of the installer implementation
- `trader-admin/TraderAdmin/README.md` - User guide for the TraderAdmin tool

## Advanced Options Strategy Controls

The system now includes enhanced options strategy controls for greater precision in vertical spread trading. These controls allow for more sophisticated spread selection based on multiple dimensions of filtering.

### Options Parameter Categories

The options settings are organized into six key categories, providing comprehensive control over spread selection:

1. **Liquidity & Execution-Quality Filters**
   - `Min Open Interest`: Ensures sufficient contract liquidity (default: 1000)
   - `Max Bid/Ask Spread %`: Caps the relative spread to avoid overpaying (default: 0.5%)

2. **Implied-Volatility Regime**
   - `Min/Max IV Rank`: Control when to trade based on volatility regime
   - `Min Call/Put IV Skew`: Identify and filter based on directional skew

3. **Greek-Based Risk Controls**
   - `Max Theta Per Day`: Limit daily time decay exposure
   - `Max Vega Exposure`: Control volatility risk
   - `Max Gamma Exposure`: Prevent overly "pin-risky" positions

4. **Probability & Expected-Move Metrics**
   - `Min Probability of Profit`: Trade only spreads with sufficient POP
   - `Max Width vs Expected Move`: Ensure spread width is proportional to expected move

5. **Event & Calendar Controls**
   - `Days Before Earnings/Ex-Div`: Avoid trading before key events
   - `DTE from ATR`: Dynamically adjust expiration based on volatility

6. **Strike-Selection Flexibility**
   - `Strike Offset`: Choose number of strikes away from ATM
   - `Spread Width`: Set spread width in number of strikes

### Using the Enhanced Controls

These controls can be configured through:

1. **TraderAdmin GUI**:
   - Navigate to the "Options" tab
   - Adjust parameters in each of the six sections
   - Click "Save & Restart" to apply changes

2. **Configuration File**:
   - Edit `config.toml` under the `[Options]` section
   - Parameters are grouped by category with comments
   - Signal handlers will automatically reload configuration

### Configuration Example

```toml
[Options]
  # Basic Options Settings
  min_dte = 30
  max_dte = 45
  min_delta = 0.3
  max_delta = 0.5
  max_spread_cost = 500
  min_reward_risk = 1.5

  # Liquidity & Execution-Quality Filters
  min_open_interest = 1000
  max_bid_ask_spread_pct = 0.5

  # Implied-Volatility Regime
  min_iv_rank = 0.0
  max_iv_rank = 100.0
  min_call_put_skew_pct = 0.0

  # Greek-Based Risk Controls
  max_theta_per_day = 10.0
  max_vega_exposure = 0.4
  max_gamma_exposure = 0.4

  # Probability & Expected-Move Metrics
  min_prob_of_profit = 65.0
  max_width_vs_move_pct = 150.0

  # Event & Calendar Controls
  days_before_earnings = 5
  days_before_ex_div = 3
  dte_from_atr = false
  atr_coefficient = 2.0

  # Strike-Selection Flexibility
  strike_offset = 1
  spread_width = 1
```

### Recommended Trading Configurations

Here are some example configurations for different trading styles:

#### Conservative Income Strategy
```toml
min_prob_of_profit = 75.0
min_open_interest = 2000
max_bid_ask_spread_pct = 0.3
min_iv_rank = 50.0
max_theta_per_day = 5.0
days_before_earnings = 14
```

#### Volatility Expansion Strategy
```toml
min_iv_rank = 25.0
max_iv_rank = 75.0
max_vega_exposure = 0.6
min_reward_risk = 2.0
strike_offset = 2
spread_width = 2
```

#### Event-Based Strategy
```toml
days_before_earnings = 0  # Enable trading around earnings
max_vega_exposure = 0.2   # Reduce vega to control earnings volatility risk
min_prob_of_profit = 60.0 # Slightly lower probability due to event premium
dte_from_atr = true       # Dynamic DTE based on stock volatility
atr_coefficient = 3.0     # Higher coefficient for more volatile stocks
```

### Implementation Details

The enhanced options filtering is implemented across several components:

1. **Frontend**: Parameters are exposed in the Options tab of the TraderAdmin GUI
2. **Configuration**: Values stored in `config.toml` with sensible defaults
3. **Python Filtering**: `OptionSpreadFilter` provides comprehensive spread filtering
4. **Decision Logic**: `SpreadManager` applies filters and ranks spread opportunities

For more advanced usage, see the full implementation in the `python/src/options/` directory.

### How It Works

1. The system receives option chain data from IBKR
2. The `SpreadManager` selects potential vertical spreads
3. Each spread is filtered through all enabled criteria
4. Remaining spreads are ranked by reward/risk ratio
5. The best qualified spread is selected for trading

This comprehensive filtering ensures that only the highest-quality option spreads meeting your exact specifications are selected for trading.
