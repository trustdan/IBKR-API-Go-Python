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

## System Components

The system is structured into the following components:

1. **Scanner**: Identifies trading opportunities based on technical patterns
2. **Strategy Engine**: Implements multiple technical trading strategies
3. **Option Selector**: Selects the optimal vertical spread for a given trade signal
4. **Trade Executor**: Handles trade execution timing and order management
5. **Risk Manager**: Controls position sizing and overall risk exposure
6. **IBKR Integration**: Connects to Interactive Brokers for data and trading
7. **Alerting System**: Provides notifications for trade and system events
8. **Performance Monitor**: Tracks system performance metrics

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
   - Custom hook ensures all text files end with exactly one newline
   - Works in conjunction with the standard end-of-file-fixer
   - Automatically fixes any incorrect file endings

2. **Code Quality**:
   - Removes trailing whitespace (preserving Markdown line breaks)
   - Formats Python code using Black
   - Sorts imports using isort
   - Runs mypy type checking on core modules

To manually run all pre-commit hooks on all files:
```bash
pre-commit run --all-files
```

To run a specific hook:
```bash
pre-commit run end-of-file-fixer --all-files
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
