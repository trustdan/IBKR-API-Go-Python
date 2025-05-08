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

## Standard Installation

If you prefer not to use Docker, you can set up the system directly:

### Prerequisites

- Python 3.8+
- Go 1.20+
- Interactive Brokers account and TWS/Gateway installed
- Either IBKR Paper Trading or Live Trading account

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
   - Copy `config.yaml.example` to `config.yaml`
   - Edit settings to match your requirements and risk tolerance
   - Set your IBKR credentials via environment variables or in the config

## Usage

### Basic Operations

1. **Run a Market Scan**:
   ```
   python python/src/run_trader.py scan --symbols symbols.txt --strategies HIGH_BASE BULL_PULLBACK
   ```

2. **Run in Trading Mode**:
   ```
   python python/src/run_trader.py trade --symbols symbols.txt --config config.yaml
   ```

3. **Check Trader Status**:
   ```
   python python/src/run_trader.py status
   ```

4. **Run Backtesting**:
   ```
   python python/src/run_trader.py backtest --start-date 2023-01-01 --end-date 2023-12-31 --strategies HIGH_BASE
   ```

### Configuration

The system is highly configurable through the `config.yaml` file. Key configuration areas include:

- **Trading Mode**: Switch between paper and live trading
- **Strategy Parameters**: Customize technical indicators and thresholds
- **Risk Parameters**: Set max positions, trade size, and other risk controls
- **Option Selection Criteria**: Configure option spread selection criteria
- **IBKR Connection**: Set connection parameters for TWS/Gateway

Example configuration:

```yaml
# Trading Strategies Configuration

# Strategy Parameters
HIGH_BASE_MAX_ATR_RATIO: 2.0
HIGH_BASE_MIN_RSI: 60

# Risk Management
RISK_PER_TRADE: 0.02  # 2% account risk per trade
MAX_POSITIONS: 5
MAX_DAILY_TRADES: 3

# Option Selection
MIN_DTE: 30
MAX_DTE: 45
MIN_DELTA: 0.30
MAX_DELTA: 0.50
MAX_SPREAD_COST: 500
MIN_REWARD_RISK: 1.5
```

## Advanced Usage

### Building Your Own Docker Images

You can build your own Docker images:

```bash
# Build Go scanner
cd go
docker build -t local/auto-vertical-spread-go:latest -f Dockerfile .

# Build Python orchestrator
cd python
docker build -t local/auto-vertical-spread-python:latest -f Dockerfile .
```

### Using Docker Compose for Development

A Docker Compose configuration is provided for local development:

```bash
# Start the development environment
docker-compose up -d

# View logs
docker-compose logs -f
```

### Kubernetes Deployment

For production deployments, Kubernetes manifests are available in the `kubernetes/` directory.

## Development and Testing

### Python Tests
```bash
cd python
pytest
```

### Go Tests
```bash
cd go
go test ./...
```

### Code Quality
```bash
# Python linting and type checking
cd python
black .
mypy .

# Go linting
cd go
golangci-lint run
```

## Safety Features

The system includes multiple safety mechanisms:

- **Paper Trading Mode**: Test strategies without real money
- **Risk Limits**: Configurable position and trade limits
- **Time-Based Rules**: Control when trades can be executed
- **Error Handling**: Robust error handling and reporting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Trading involves risk. This software is for educational and informational purposes only. It is not intended as financial advice or a recommendation to trade. Use at your own risk.

## Disclaimer and Risk Warning

### Financial Disclaimer
This software is provided strictly for educational and informational purposes only and is not financial advice.

**IMPORTANT NOTICE:**
- Trading options, futures, stocks, and other financial instruments involves substantial risk of loss and is not suitable for all investors.
- Past performance is not indicative of future results. No representation is being made that any account will or is likely to achieve profits or losses similar to those discussed within this software or its documentation.
- You should never trade with money you cannot afford to lose.
- The author(s) and contributor(s) to this project are not registered investment advisors, brokers/dealers, financial analysts, financial advisors, or securities professionals.
- The information provided in this software is not a substitute for professional financial advice.
- Before engaging in any trading activity of any kind, you should consult with a licensed broker, financial advisor, or financial professional to determine the suitability of any investment.

### Technical Requirements Disclaimer
This software combines multiple complex technologies and requires substantial technical expertise:

- **Programming Languages**: Requires proficiency in Python 3.8+, Go 1.20+, and understanding of asynchronous programming.
- **Infrastructure**: Requires knowledge of Docker, containerization, and potentially Kubernetes for production deployments.
- **Financial APIs**: Requires understanding of Interactive Brokers TWS API, market data formats, and order execution mechanics.
- **Financial Concepts**: Requires solid understanding of options trading, vertical spreads, and risk management principles.

It is strongly recommended that you consult with a developer who has expertise in these areas before attempting to deploy this system in any capacity beyond paper trading. Technical errors in implementation or deployment could result in unexpected behavior and financial loss.

### Regulatory Compliance
Users of this software are solely responsible for ensuring compliance with all applicable laws and regulations in their jurisdiction, including but not limited to:

- Securities regulations
- Tax laws
- Trading rules and restrictions
- Reporting requirements

### No Liability
The authors, contributors, and maintainers of this software expressly disclaim all liability for any direct, indirect, consequential, incidental, or special damages arising out of or in any way connected with the use of or inability to use this software.

BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THAT YOU HAVE READ THIS DISCLAIMER, UNDERSTAND IT, AND AGREE TO BE BOUND BY ITS TERMS.

## New Feature: TraderAdmin GUI

We've implemented a new Wails desktop GUI for managing the trading system configuration. The TraderAdmin tool provides a "pause → edit → unpause" workflow that lets you modify settings without disrupting TWS connections or restarting containers.

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Host OS (Windows / macOS)                              │
│                                                         │
│  • Trader Workstation (TWS) GUI  ← you still log in     │
│  • Wails "TraderAdmin" GUI  ← pause/edit/unpause cfg    │
│                                                         │
│  Docker Desktop (includes containerd + k8s)             │
│    ├─ Kubernetes control-plane                          │
│    │   └─ our namespace: trader-stack/                  │
│    │        • python-orchestrator   (Pod)               │
│    │        • go-scanner            (Pod)               │
│    │        • redis / postgres …    (Pods)              │
│    │        • config-volume (PVC)   ────┐               │
│    │                                    │ mounted RO    │
│    └─ docker engine (same socket)       │               │
│         ↳ visible to Wails via          │               │
│           //./pipe/docker_engine        │               │
└─────────────────────────────────────────┘
```

### Configuration and Reload Process

```
┌────────────────────────────┐
│  Wails GUI (Go+Svelte)     │
│  • Form → Config model     │
│  • Status panel (Docker)   │
└────────────┬───────────────┘
             │ 1. POST /save-config
             ▼
┌────────────────────────────┐
│  Wails backend (Go)        │
│  • Validate + persist TOML │
│  • docker-pause targets    │
│  • SIGUSR1 to reload cfg   │
│  • docker-unpause targets  │
└────────────┬───────────────┘
             │ 2. SIGHUP/USR1
             ▼
┌────────────────────────────┐
│  Python Orchestrator       │
│  • watchdog for SIGUSR1    │
│  • re-read config & resume │
└────────────────────────────┘
┌────────────────────────────┐
│  Go Scanner (gRPC)         │
│  • fsnotify on cfg mount   │
│  • atomic swap of params   │
└────────────────────────────┘
```

### Quick Start

1. **Start Docker Desktop** with Kubernetes enabled
2. **Deploy the trader stack**: `kubectl apply -k kubernetes/base/`
3. **Start Trader Workstation or IB Gateway** and log in
4. **Launch TraderAdmin** from the installer (or build from source)
5. Edit parameters as needed and click "Save & Restart"

Total interruption time is typically less than 500ms, so TWS never notices any disconnect.

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
