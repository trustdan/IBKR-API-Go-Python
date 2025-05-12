#!/bin/bash

set -e

# Build the Docker image locally
echo "Building Go Scanner Docker image locally..."
docker build -t local/auto-vertical-spread-go:latest -f Dockerfile .

echo "Build completed successfully!"
echo "To run the image locally: docker run -p 50051:50051 -p 2112:2112 -v $(pwd)/config.json:/root/config.json local/auto-vertical-spread-go:latest"
