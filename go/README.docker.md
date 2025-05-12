# Auto Vertical Spread Trader - Go Scanner

This is the Go scanner component of the Auto Vertical Spread Trader system, designed to work in conjunction with the [Python orchestrator component](https://hub.docker.com/r/trustdan/auto-vertical-spread-python).

## About This Component

The Go scanner provides:
- High-performance market data scanning
- Concurrent processing of technical patterns
- gRPC API for communication with the Python orchestrator
- Optimized for speed and resource efficiency

## Important: Component Dependency

**Note:** This container is designed to work together with the Python orchestrator component. The full system requires both containers to function properly.

## Quick Start

```bash
# Pull both components
docker pull trustdan/auto-vertical-spread-go
docker pull trustdan/auto-vertical-spread-python

# Run both containers (see full instructions in the GitHub README)
```

## Complete Documentation

For complete documentation, configuration options, and setup instructions, please refer to the [GitHub repository](https://github.com/trustdan/ibkr-trader).

## License

MIT License

