#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Set default tag to use
TAG=${1:-latest}

echo -e "${BLUE}Starting auto-vertical-spread services with tag: ${TAG}${NC}"

# Pull the latest images
echo -e "${BLUE}Pulling Docker images...${NC}"
docker pull trustdan/auto-vertical-spread-go:${TAG} || {
  echo -e "${RED}Failed to pull Go image. Using local image if available.${NC}"
}
docker pull trustdan/auto-vertical-spread-python:${TAG} || {
  echo -e "${RED}Failed to pull Python image. Using local image if available.${NC}"
}

# Create network if it doesn't exist
docker network inspect vertical-spread-network > /dev/null 2>&1 || {
  echo -e "${BLUE}Creating Docker network...${NC}"
  docker network create vertical-spread-network
}

# Check if containers are already running and stop them
if docker ps -a | grep -q vertical-spread-go; then
  echo -e "${BLUE}Stopping and removing existing Go container...${NC}"
  docker stop vertical-spread-go || true
  docker rm vertical-spread-go || true
fi

if docker ps -a | grep -q vertical-spread-python; then
  echo -e "${BLUE}Stopping and removing existing Python container...${NC}"
  docker stop vertical-spread-python || true
  docker rm vertical-spread-python || true
fi

# Make sure config directories exist
mkdir -p "${PWD}/go/config"
mkdir -p "${PWD}/python/config"

# Create default config file for Go if it doesn't exist
if [ ! -f "${PWD}/go/config.json" ]; then
  echo -e "${BLUE}Creating default Go config...${NC}"
  cat > "${PWD}/go/config.json" << EOF
{
  "log_level": "info",
  "grpc_port": 50051,
  "metrics_port": 2112
}
EOF
fi

# Start Go scanner
echo -e "${BLUE}Starting Go scanner...${NC}"
docker run -d --name vertical-spread-go \
  --network vertical-spread-network \
  -p 50051:50051 -p 2112:2112 \
  -v "${PWD}/go/config.json:/root/config.json" \
  trustdan/auto-vertical-spread-go:${TAG} || {
    echo -e "${RED}Failed to start Go container. Trying to use local image...${NC}"
    docker run -d --name vertical-spread-go \
      --network vertical-spread-network \
      -p 50051:50051 -p 2112:2112 \
      -v "${PWD}/go/config.json:/root/config.json" \
      local/auto-vertical-spread-go:latest || {
        echo -e "${RED}Failed to start Go container with local image as well. Exiting.${NC}"
        exit 1
      }
  }

# Start Python orchestrator
echo -e "${BLUE}Starting Python orchestrator...${NC}"
docker run -d --name vertical-spread-python \
  --network vertical-spread-network \
  -p 8000:8000 \
  -v "${PWD}/python/config:/app/config" \
  -e "SCANNER_HOST=vertical-spread-go" \
  -e "SCANNER_PORT=50051" \
  trustdan/auto-vertical-spread-python:${TAG} || {
    echo -e "${RED}Failed to start Python container. Trying to use local image...${NC}"
    docker run -d --name vertical-spread-python \
      --network vertical-spread-network \
      -p 8000:8000 \
      -v "${PWD}/python/config:/app/config" \
      -e "SCANNER_HOST=vertical-spread-go" \
      -e "SCANNER_PORT=50051" \
      local/auto-vertical-spread-python:latest || {
        echo -e "${RED}Failed to start Python container with local image as well.${NC}"
        echo -e "${RED}Stopping Go container and exiting.${NC}"
        docker stop vertical-spread-go || true
        exit 1
      }
  }

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${BLUE}Go service running at: http://localhost:50051${NC}"
echo -e "${BLUE}Go metrics at: http://localhost:2112${NC}"
echo -e "${BLUE}Python service running at: http://localhost:8000${NC}"
echo ""
echo -e "${BLUE}To stop all services, run:${NC} docker stop vertical-spread-go vertical-spread-python"
echo -e "${BLUE}To view logs, run:${NC} docker logs vertical-spread-go -f"

