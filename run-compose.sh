#!/bin/bash
# Bash script to run auto-vertical-spread services using docker-compose

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
  echo -e "${RED}Error: docker-compose is not available. Please install Docker with docker-compose.${NC}"
  exit 1
fi

# Ensure config directories exist
mkdir -p go
mkdir -p python/config

# Create default config file for Go if it doesn't exist
if [ ! -f "go/config.json" ]; then
  echo -e "${CYAN}Creating default Go config...${NC}"
  cat > go/config.json << EOF
{
  "log_level": "info",
  "grpc_port": 50051,
  "metrics_port": 2112
}
EOF
fi

# Check if config.yaml exists and create a default one if needed
if [ ! -f "python/config/config.yaml" ]; then
  echo -e "${CYAN}Creating default Python config...${NC}"

  # Try to copy from example if it exists
  if [ -f "python/config/config.yaml.example" ]; then
    cp python/config/config.yaml.example python/config/config.yaml
  else
    # Create a basic one
    cat > python/config/config.yaml << EOF
# IBKR Auto Vertical Spread Trader Configuration
ibkr:
  host: "127.0.0.1"
  port: 7497
  client_id: 1
  read_only: false
  account: ""

# Scanner Configuration
scanner:
  host: "go-scanner"
  port: 50051
  max_concurrency: 50

# Trading
trading:
  mode: "PAPER"
  max_positions: 5
  max_daily_trades: 3
  risk_per_trade: 0.02
  price_improvement_factor: 0.4
  allow_late_day_entry: true
EOF
  fi
fi

# Determine which docker-compose file to use
COMPOSE_FILE="docker-compose.prod.yml"
if [ "$1" == "dev" ]; then
  COMPOSE_FILE="docker-compose.yml"
fi

echo -e "${GREEN}Starting services using $COMPOSE_FILE...${NC}"

# Run docker-compose
docker-compose -f $COMPOSE_FILE up -d

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${CYAN}Go service running at: http://localhost:50051${NC}"
echo -e "${CYAN}Go metrics at: http://localhost:2112${NC}"
echo -e "${CYAN}Python service running at: http://localhost:8000${NC}"
echo ""
echo -e "${CYAN}To view logs, run:${NC}"
echo "docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo -e "${CYAN}To stop all services, run:${NC}"
echo "docker-compose -f $COMPOSE_FILE down"

