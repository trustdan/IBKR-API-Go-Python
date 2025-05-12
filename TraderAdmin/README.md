# TraderAdmin

A robust trading platform GUI for IBKR Trader built with Wails (Go & Svelte).

## Features

- Centralized configuration management
- Docker and Kubernetes integration
- Live configuration reloading
- Advanced trading strategy configuration
- Real-time monitoring and alerts

## Development Setup

### Prerequisites

- Go 1.21+
- Node.js 16+
- Wails CLI (`go install github.com/wailsapp/wails/v2/cmd/wails@latest`)
- Docker Desktop with Kubernetes enabled

### Getting Started

1. Clone the repository
2. Run `wails dev` to start the development server
3. Make changes to the code and see them update in real-time

### Configuration

All configuration is managed through `config/config.toml`. The file is monitored for changes and will automatically reload when changes are detected.

### Deployment

The application can be packaged for distribution using:

```bash
wails build
```

## Docker & Kubernetes

### Kubernetes Setup

```bash
# Create the namespace and resources
kubectl apply -f deploy/namespace.yaml
kubectl apply -f deploy/config-pvc.yaml
kubectl apply -f deploy/orchestrator-deployment.yaml
kubectl apply -f deploy/scanner-deployment.yaml
```

## Project Structure

- `frontend/` - Svelte frontend application
- `app.go` - Main Go application code
- `config/` - Configuration files
- `deploy/` - Kubernetes deployment files

## License

MIT
