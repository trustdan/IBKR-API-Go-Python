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

## Installation

### Prerequisites

- Python 3.8+
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
├── src/
│   ├── app/              # Application-level code
│   ├── brokers/          # Broker integration code
│   ├── models/           # Data models and classes
│   ├── strategies/       # Trading strategy implementations
│   ├── trading/          # Core trading components
│   └── utils/            # Utility functions
└── config.yaml           # Configuration file
```

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
