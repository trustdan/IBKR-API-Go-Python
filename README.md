# Auto Vertical Spread Trader

A hybrid Python-Go architecture for automated vertical spread trading with Interactive Brokers.

## Architecture

- **Python Orchestrator**: Handles business logic, API interactions, and strategy implementation
- **Go Scanner Service**: High-performance concurrent market scanning
- **gRPC Communication**: Strong typing and efficient communication between services

## Components

1. **Data Management**: Data retrieval, caching, and universe filtering
2. **Strategy Implementation**: Multiple trading strategies with customizable parameters
3. **Option Selection**: Vertical spread selection based on specific criteria
4. **Trade Execution**: IBKR API integration with dual execution modes
5. **Backtesting**: Framework for historical simulation and parameter optimization

## Development

### Prerequisites

- Python 3.8+
- Go 1.19+
- Poetry for Python dependency management
- Docker & Docker Compose for local development
- Interactive Brokers TWS or IB Gateway

### Setup

1. Clone the repository
2. Configure environment variables in `.env`
3. Run `poetry install` in the `python` directory
4. Run `go mod download` in the `go` directory
5. Use docker-compose for local development: `docker-compose up`

## Testing

- Python: `poetry run pytest`
- Go: `go test ./...`

## License

Proprietary - All rights reserved 