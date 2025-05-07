# Auto Vertical Spread Trader

An automated trading system that implements vertical spread trading strategies using Interactive Brokers (IBKR) API. The system scans for specific technical patterns, selects optimal option spreads, and handles trade execution for equity options.

## Features

- **Automated Technical Analysis**: Scans for specific patterns using custom-built strategies
- **Option Chain Analysis**: Analyzes option chains to find optimal vertical spread opportunities
- **Risk Management**: Implements position sizing and risk controls
- **Trade Execution**: Interfaces with Interactive Brokers for automated or semi-automated trading
- **Performance Tracking**: Tracks and reports on system performance

## System Components

The system is structured into the following components:

1. **Scanner**: Identifies trading opportunities based on technical patterns
2. **Strategy Engine**: Implements multiple technical trading strategies
3. **Option Selector**: Selects the optimal vertical spread for a given trade signal
4. **Trade Executor**: Handles trade execution timing and order management
5. **Risk Manager**: Controls position sizing and overall risk exposure
6. **IBKR Integration**: Connects to Interactive Brokers for data and trading

## Quick Start with Docker

The easiest way to run the system is using Docker:

### Prerequisites

- Docker Desktop installed and running
- Internet connection to pull images

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
- Go 1.23+
- Interactive Brokers account and TWS/Gateway installed
- Either IBKR Paper Trading or Live Trading account

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto-vertical-spread-trader.git
   cd auto-vertical-spread-trader
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install and set up pre-commit hooks:
   ```
   pip install pre-commit
   pre-commit install
   ```

4. Configure your system:
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

### Configuration

The system is highly configurable through the `config.yaml` file. Key configuration areas include:

- **Trading Mode**: Switch between paper and live trading
- **Strategy Parameters**: Customize technical indicators and thresholds
- **Risk Parameters**: Set max positions, trade size, and other risk controls
- **Option Selection Criteria**: Configure option spread selection criteria
- **IBKR Connection**: Set connection parameters for TWS/Gateway

## Trading Strategies

The system implements four primary technical strategies:

1. **High Base Strategy**: Identifies stocks trading near resistance with strong momentum
2. **Low Base Strategy**: Identifies stocks trading near support with weak momentum
3. **Bull Pullback Strategy**: Identifies uptrends with temporary pullbacks
4. **Bear Rally Strategy**: Identifies downtrends with temporary rallies

## Architecture

The system follows a modular architecture designed for flexibility and extensibility:

```
python/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ src/
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ app/              # Application-level code
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ brokers/          # Broker integration code
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ models/           # Data models and classes
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ strategies/       # Trading strategy implementations
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ trading/          # Core trading components
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ utils/            # Utility functions
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ config.yaml           # Configuration file

go/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ cmd/
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ scanner/          # Go scanner application
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ pkg/                  # Shared Go packages
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ config.json           # Go scanner configuration
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

### Kubernetes Deployment

For production deployments, Kubernetes manifests are available in the `kubernetes/` directory. However, this is optional and not required for local usage.

## Safety Features

The system includes multiple safety mechanisms:

- **Paper Trading Mode**: Test strategies without real money
- **Risk Limits**: Configurable position and trade limits
- **Time-Based Rules**: Control when trades can be executed
- **Error Handling**: Robust error handling and reporting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Trading involves risk. This software is for educational and informational purposes only. It is not intended as financial advice or a recommendation to trade. Use at your own risk.
