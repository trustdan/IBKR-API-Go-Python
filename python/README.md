# IBKR Auto Vertical Spread Trader - Python

This is the Python component of the Auto Vertical Spread Trader system. It serves as the orchestrator that handles trading strategies, option selection, and order execution through the Interactive Brokers API.

## Features

- Multiple trading strategies (High Base, Low Base, Bull Pullback, Bear Rally)
- Robust option selection algorithm
- Risk management controls
- Alert system with multiple notification channels
- Backtesting framework
- API integration with high-performance Go scanner

## Development

This project uses Poetry for dependency management. To install dependencies:

```bash
cd python
poetry install
```

To run tests:

```bash
poetry run pytest
```
