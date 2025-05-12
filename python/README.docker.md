# Auto Vertical Spread Trader - Python Orchestrator

This is the Python orchestrator component of the Auto Vertical Spread Trader system, designed to work in conjunction with the [Go scanner component](https://hub.docker.com/r/trustdan/auto-vertical-spread-go).

## About This Component

The Python orchestrator handles:
- Trading strategy implementation
- Option selection logic
- Risk management
- Trade execution through IBKR API
- Backtesting capabilities

## Important: Component Dependency

**Note:** This container is designed to work together with the Go scanner component. The full system requires both containers to function properly.

## Quick Start

```bash
# Pull both components
docker pull trustdan/auto-vertical-spread-python
docker pull trustdan/auto-vertical-spread-go

# Run both containers (see full instructions in the GitHub README)
```

## Complete Documentation

For complete documentation, configuration options, and setup instructions, please refer to the [GitHub repository](https://github.com/trustdan/ibkr-trader).

## License

MIT License

