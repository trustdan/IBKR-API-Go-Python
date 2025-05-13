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

#### 3. Verify TWS/Gateway API Settings

The API settings in TWS must be correctly configured for the connection to work:

1. **Mandatory API Settings**:
   - Open TWS and go to **Edit > Global Configuration > API > Settings**
   - Ensure **"Enable ActiveX and Socket Clients"** is checked
   - Verify the **Socket Port** matches your config.yaml (7497 for paper trading)
   - Check that **Master API client ID** is set to 1 (or matches your config)
   - Click **Apply** after making changes, then **OK**
   - **IMPORTANT**: Restart TWS completely after changing API settings

2. **API Precautions**:
   - Go to **Edit > Global Configuration > API > Precautions**
   - Enable **"Bypass Order Precautions for API Orders"** to prevent order confirmations
   - Other precaution settings can be adjusted based on your trading needs

3. **API Security Settings**:
   - In TWS API Settings, verify **"Allow connections from localhost only"** is checked
   - If connecting from a different machine, add its IP to the **"Trusted IPs"** list

#### 4. Configure Network and Firewall Settings

Windows Firewall and network settings can block the TWS API connection:

1. **Add Windows Firewall Exception**:
   - Open Windows Defender Firewall with Advanced Security (run as administrator)
   - Click **Inbound Rules** > **New Rule**
   - Select **Port** > **TCP**
   - Enter the TWS API port (7497 for paper trading, 7496 for live)
   - Select **Allow the connection** > **Next**
   - Apply the rule to all profiles (Domain, Private, Public)
   - Name it "TWS API" and save

2. **Run TWS as Administrator**:
   - Right-click on the TWS shortcut and select **Run as administrator**
   - This grants TWS additional permissions needed for network operations

3. **Check if TWS API is Listening**:
   - In PowerShell, run: `Test-NetConnection -ComputerName localhost -Port 7497`
   - If the port is open, the connection should succeed
   - If closed, API in TWS is not activated or a firewall is blocking it

#### 5. Proper Docker Setup

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

### Advanced TWS API Configuration and Troubleshooting

#### Detailed Connection Troubleshooting

If you're experiencing persistent connection issues with the TWS API:

1. **Verify TWS API Service is Running**:
   - Run this Python script to test the connection directly:
   
   ```python
   import socket
   
   def check_tws_ports():
       """Check if TWS API ports are open."""
       host = "127.0.0.1"
       ports = [7497, 7496, 4001, 4002]
       
       for port in ports:
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.settimeout(3)
           result = sock.connect_ex((host, port))
           status = "OPEN" if result == 0 else "CLOSED"
           print(f"Port {port}: {status}")
           sock.close()
   
   if __name__ == "__main__":
       print("Checking TWS API ports...")
       check_tws_ports()
   ```

2. **TWS Connection Sequence**:
   - Follow this exact sequence for most reliable connection:
     1. Start TWS and fully log in
     2. Wait 2-3 minutes for all services to initialize
     3. Verify API settings (Enable ActiveX and Socket Clients)
     4. Start your application
   - The API often requires TWS to be fully initialized before connecting

3. **Alternative API Ports**:
   - If port 7497 isn't working, try changing to alternative ports in TWS:
     - 4001: Standard IB Gateway port
     - 7496: Standard TWS live trading port
     - 5000: Custom port option (less likely to have conflicts)
   - Remember to update both TWS settings and your config.yaml file

4. **Test with Different Client IDs**:
   - Try using a unique client ID (e.g., 10, 123, etc.)
   - Multiple applications connecting with the same client ID can cause conflicts
   - Update both the Master API client ID in TWS and in your config

5. **Socket Connection Issues**:
   - Ensure no other applications are using the same port
   - Check if anti-virus or security software is blocking the connection
   - Try temporarily disabling Windows Defender Firewall for testing

#### Advanced API Configuration Options

1. **Connection Security Hardening**:
   - Restrict connections to trusted IPs only
   - Use read-only API for monitoring applications
   - Apply API request throttling in your application (max 50 requests/second)

2. **API Account Permissions**:
   - Some accounts may have restrictions on API access
   - Contact IBKR support to verify your account has API trading permissions
   - Paper trading accounts should have full API access by default

3. **API Logging and Debugging**:
   - Enable API message logging in TWS:
     - In API Settings, check "Create API message log file"
     - Option to include market data in the log (large file size warning)
   - Review TWS API logs in the TWS logs directory

4. **Error Handling and Recovery**:
   - Implement exponential backoff for reconnection attempts
   - Cache essential data to handle temporary disconnections
   - Monitor connection status and implement health checks

5. **Multiple API Connections**:
   - Single TWS instance can support multiple API connections
   - Each connection must use a unique client ID
   - Be aware of overall request rate limits (50/second across all connections)

#### Common Connection Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 1100 | "Connectivity between IB and TWS has been lost" | Restart TWS and reconnect |
| 2104 | "Market data farm connection is OK" | Informational only |
| 2108 | "Market data farm connection is inactive but should be available" | Wait for reconnection |
| 10061 | "Connection refused" | TWS not running or API not enabled |
| 504 | "Not connected" | Application needs to reconnect to TWS |
| 502 | "Couldn't connect to TWS" | TWS not running or wrong port/IP |

Understanding these errors can help diagnose and resolve connection issues more efficiently.

#### 6. Starting the TraderAdmin Application

```powershell
# Start the TraderAdmin application
Start-Process "C:\Users\<username>\IBKR-trader\build\bin\TraderAdmin-dev.exe"
```

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

#### 1. API Connection Issues

If you're experiencing connection issues between the application and TWS:

* **TWS API Connectivity**:
  * Verify TWS or IB Gateway is running and fully initialized
  * Confirm API settings are properly configured (Edit > Global Configuration > API)
  * Check that your client ID matches between TWS and your configuration
  * Ensure the API port is correctly set (default: 7497 for paper, 7496 for live)
  * Try different client IDs if conflicts occur with other applications
  * Make sure to click Apply and restart TWS after changing settings

* **Network & Firewall**:
  * Add a Windows Firewall exception for the TWS API port (TCP: 7497/7496)
  * Run both TWS and your application as Administrator
  * Check if antivirus software or security tools are blocking the connection
  * Test if the port is actually listening: `Test-NetConnection -ComputerName localhost -Port 7497`
  * On some networks, try changing to a different port (4001, 5000) in both TWS and config

* **Windows-Specific Issues**:
  * Windows Security can block connections even with firewall exceptions
  * Right-click TWS > Properties > Compatibility > Run as administrator
  * Use the "netstat -ano" command to see if another process is using the port
  * After changing TWS settings, always do a full restart (not just logout)

* **Connection Sequence Matters**:
  * Start TWS first and let it fully initialize (can take 2-3 minutes)
  * After TWS is running, verify API settings are enabled
  * Then start your trading application
  * If connection fails, close everything and restart in this exact sequence

#### 2. Data Issues

* **Market Data Availability**:
  * Verify market data subscriptions for the instruments you're trading
  * Check TWS market data connection status (green indicator in TWS)
  * Paper accounts may have delayed or limited market data
  * Some data may require additional market data subscriptions

* **Data Quality Issues**:
  * Some option data may be missing or incomplete
  * Check for stale or frozen data (especially on paper trading accounts)
  * Verify your account has the appropriate market data permissions

#### 3. Order Issues

* **Order Rejections**:
  * Review TWS logs for rejected orders and specific error messages
  * Verify account permissions for the instruments you're trading
  * Check available buying power and margin requirements
  * Ensure spread orders are properly constructed
  * Option spreads may have specific margin or permission requirements

* **Order Execution Delays**:
  * API orders may experience slight delays compared to direct TWS orders
  * Market data delays can impact execution quality
  * Check connection stability if experiencing consistent delays

#### 4. System and Configuration Diagnostics

For persistent problems, use the included diagnostic utilities:

```python
# Connection diagnostic utility
python tools/check_tws_connection.py

# API configuration checker
python tools/verify_api_config.py

# Account permissions validator
python tools/validate_account_permissions.py
```

#### 5. Common Error Messages and Solutions

| Error Message | Possible Cause | Solution |
|---------------|---------------|----------|
| "Could not connect to TWS" | TWS not running or API not enabled | Start TWS, enable API, check port |
| "Connection refused" | Port blocked or incorrect | Check firewall, verify port settings |
| "Data farm connection is inactive" | Market data connection issue | Wait for TWS to establish market data connection |
| "Order rejected: Invalid contract" | Contract specification incorrect | Verify symbol, expiration, strike price |
| "Order rejected: No permissions" | Account lacks permissions | Contact IBKR to add required permissions |
| "Order rejected: Insufficient funds" | Inadequate buying power | Check account balance and margin requirements |
| "Missing or invalid account" | Account code incorrect | Verify account code from TWS matches config |

If problems persist after trying these solutions, check the application logs for detailed error messages and consider contacting IBKR support for account-specific issues.

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

### Advanced TWS API Troubleshooting Tools

To address persistent TWS connectivity issues, we have developed specialized diagnostic tools that can help identify and resolve common problems:

#### 1. TWS Connectivity Fix Tool

This comprehensive tool diagnoses and fixes connectivity issues between your application and TWS/IB Gateway, with a focus on Windows firewall rules.

```bash
# Run in diagnostic mode (will not make changes)
python tools/tws_connectivity_fix.py

# Run with --apply to automatically fix detected issues (requires admin privileges)
python tools/tws_connectivity_fix.py --apply
```

Key features:
- Detects if TWS is running
- Checks all standard TWS API ports (7497, 7496, 4001, 4002)
- Inspects Windows Firewall status and rules
- Creates proper inbound firewall rules when run with --apply
- Generates a continuous port monitoring script for real-time connection testing

#### 2. Direct IB_Insync Connection Test

Tests direct connection to TWS using the ib_insync library with multiple configurations to find a working setup:

```bash
# Run basic test with automatic configuration detection
python tools/test_ibinsync_direct.py

# Try all possible connection configurations
python tools/test_ibinsync_direct.py --try-all

# Test with specific parameters
python tools/test_ibinsync_direct.py --host 127.0.0.1 --port 7497 --client-id 5 --timeout 30
```

Key features:
- Tests multiple host, port, and client ID combinations
- Checks port availability before attempting connection
- Retrieves account information when connected
- Provides specific configuration recommendations based on successful connections

#### 3. API Configuration Verification

Validates your API configuration settings against best practices:

```bash
python tools/verify_api_config.py
```

Key features:
- Checks config.yaml for proper IBKR settings
- Verifies port accessibility
- Suggests improvements to configuration

#### Using These Tools in Sequence

For the most effective troubleshooting, use these tools in the following sequence:

1. First, run `python tools/check_tws_connection.py` to verify TWS is running and accessible
2. Then run `python tools/tws_connectivity_fix.py --apply` to fix firewall and port issues
3. Next, run `python tools/test_ibinsync_direct.py --try-all` to find a working connection configuration
4. Finally, update your config.yaml with the recommended settings from the successful test

These utilities have been specifically designed to address the connection issues commonly experienced with the Interactive Brokers API, especially on Windows systems where firewall configurations can block the socket connections required by the TWS API.