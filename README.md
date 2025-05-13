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
- **Risk Management**: Implements position sizing and risk controls
- **Trade Execution**: Interfaces with Interactive Brokers for automated or semi-automated trading
- **Performance Tracking**: Tracks and reports on system performance
- **Dual Execution Modes**: Optimized for both paper trading and live trading environments
- **High-performance Scanner**: Go-based concurrent scanner processes 100+ symbols per second
- **Caching Strategy**: Efficient data management with intelligent caching
- **Robust Error Handling**: Comprehensive error recovery mechanisms
- **Alerting System**: Multi-channel notifications for trade and system events

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
Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ src/
Ã¢â€â€š   Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ app/              # Application-level code
Ã¢â€â€š   Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ brokers/          # Broker integration code
Ã¢â€â€š   Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ models/           # Data models and classes
Ã¢â€â€š   Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ strategies/       # Trading strategy implementations
Ã¢â€â€š   Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ trading/          # Core trading components
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ utils/            # Utility functions
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ config.yaml           # Configuration file

go/
Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ cmd/
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ scanner/          # Go scanner application
Ã¢â€Å"Ã¢â€â‚¬Ã¢â€â‚¬ pkg/                  # Shared Go packages
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ config.json           # Go scanner configuration
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

2. **Configure API Access (CRITICAL)**:
   * Launch TWS or IB Gateway and log in to your account
   * Navigate to **Edit > Global Configuration > API > Settings**:
     * Check **"Enable ActiveX and Socket Clients"**
     * Uncheck **"Read-Only API"** unless you only want read-only access
     * Set the **Socket Port** (default: 7497 for paper, 7496 for live)
     * Set **Master API client ID** to match your config file (typically "1")
     * Check **"Allow connections from localhost only"** if running locally
   * Navigate to **Edit > Global Configuration > API > Precautions**:
     * Check **"Bypass Order Precautions for API Orders"** to avoid confirmation dialogs

3. **Restart TWS After Configuration**:
   * After making changes to API settings, always close and restart TWS completely
   * This ensures all changes take effect properly

4. **Optimize for Reliability**:
   * In **Global Configuration > Lock and Exit**:
     * Set **"Never Lock Trader Workstation"** to prevent auto-logout
     * Enable **"Auto restart"** for uninterrupted operation
   * In **Global Configuration > General**:
     * Adjust **Memory Allocation** to 4000MB for optimal performance

### Critical Configuration Steps

#### 1. Configuration File Setup

Create a proper configuration file by copying the template:

```bash
# First time setup - copy template
cp config/config.template.toml config/config.toml
```

Then edit the file to include your actual IBKR account information:

```toml
[general]
  log_level = "INFO"

[ibkr_connection]
  host = "127.0.0.1"
  port = 7497  # Use 7497 for paper trading, 7496 for live trading
  client_id_trading = 1  # Must match Master API client ID in TWS
  client_id_data = 2
  account_code = "YOUR_IBKR_ACCOUNT_CODE"  # Replace with your actual account code from TWS
  read_only_api = false

# Other settings...
```

#### 2. Find Your IBKR Account Code

Your IBKR account code appears in the top right of TWS interface. It's typically in the format:

- Paper trading accounts: "DU1234567" or similar
- Live accounts: "U1234567" or similar

Use this exact account code in your config.toml file.

#### 3. Proper Docker Setup

Ensure Docker is installed and running correctly:

```powershell
# Check Docker status
docker info

# Create Docker network (only needed first time)
docker network create vertical-spread-network

# Clean up any existing containers
docker rm -f vertical-spread-go vertical-spread-python 2>$null

# Start the services
.\run-local.ps1
```

#### 4. Starting the TraderAdmin Application

```powershell
# Start the TraderAdmin application
Start-Process "C:\Users\<username>\IBKR-trader\build\bin\TraderAdmin-dev.exe"
```

#### 5. Connection Troubleshooting

If you experience connection issues:

1. **In TWS settings**:
   - Confirm "Master API client ID" is set to "1" (not blank)
   - If you get connection errors, try changing client IDs to different values (e.g., 123 and 124)
   - Add "127.0.0.1" to the trusted IPs list if using "Allow connections from localhost only"

2. **Complete restart sequence**:
   - Close TraderAdmin application
   - Close TWS/Gateway
   - Start TWS/Gateway
   - Wait for full login
   - Start TraderAdmin application

3. **Check error logs**:
   - Watch for specific error messages in TWS message center
   - Look for permission or connection errors

### Connecting the Trading Application

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
   * Make sure "Master API client ID" is not blank in TWS settings
   * Try standard client IDs (1, 2) instead of custom values
   * Restart TWS completely after changing settings

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

## Standard Installation

> 📝 **Note:** For Windows users, a convenient installer is now available. See the [Windows Installer](#windows-installer) section below.

### Prerequisites

- Interactive Brokers account and TWS/Gateway installed
- Python 3.10 or higher
- Go 1.21 or higher (if building from source)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto-vertical-spread-trader.git
   cd auto-vertical-spread-trader
   ```

2. For Python components:
   ```bash
   cd python
   # Using Poetry (recommended)
   poetry install

   # Or using pip
   pip install -r requirements.txt
   ```

3. For Go components:
   ```bash
   cd go
   go mod download
   ```

4. Install and set up pre-commit hooks:
   ```bash
   # Install pre-commit
   pip install pre-commit

   # Install the pre-commit hooks
   pre-commit install
   ```

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality and consistency. The hooks include:

- **File Ending Management**: Ensures all text files end with exactly one newline
- **Code Formatting**: Uses Black and isort for Python code formatting
- **Type Checking**: Runs mypy on core modules
- **YAML Validation**: Checks YAML file syntax
- **Large File Check**: Prevents committing large files accidentally

The pre-commit configuration is defined in `.pre-commit-config.yaml`. Key features:

1. **File Endings**:
   - Custom hook ensures all text files end with exactly one newline and removes trailing whitespace
   - Implemented using a Python script (`python/scripts/fix_file_endings.py`)
   - Automatically fixes file endings and trailing whitespace issues in a single pass
   - Works across all platforms (Windows, macOS, Linux)

2. **Code Quality**:
   - Formats Python code using Black
   - Sorts imports using isort
   - Runs mypy type checking on core modules

To manually run all pre-commit hooks on all files:
```bash
pre-commit run --all-files
```

To run a specific hook:
```bash
pre-commit run fix-file-endings-and-whitespace --all-files
```

5. Configure your system:
   - Copy `