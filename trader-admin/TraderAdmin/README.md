# TraderAdmin - IBKR Trader Control Panel

TraderAdmin is a desktop application built with Wails that provides a GUI for managing and configuring the IBKR Auto Vertical Spread Trader system. It allows you to pause, edit configuration, and unpause trading containers without interrupting the TWS connection.

## Features

- **Live Container Status**: Monitor running containers in real-time.
- **Edit Configuration**: Modify trading parameters through an intuitive GUI.
- **Pause/Unpause Stack**: Temporarily halt trading while making changes.
- **Hot Reload**: Apply configuration changes without restarting containers.

## Prerequisites

- Docker Desktop with Kubernetes enabled
- IBKR Trader Workstation (TWS) or IB Gateway running
- Windows, macOS, or Linux operating system

## Getting Started

### Startup Sequence

1. **Start Docker Desktop** (ensures both Docker and the local k8s cluster are up)
2. **Apply Kubernetes resources**: `kubectl apply -k kubernetes/base/`
3. **Start Trader Workstation or IB Gateway** and log in
4. **Launch TraderAdmin**

### Editing Configuration

1. Make changes to parameters in the appropriate tab (Trading, Strategy, Options)
2. Click "Save & Restart"
3. The app will:
   - Pause all trading containers
   - Write the updated configuration
   - Unpause the containers
   - Signal them to reload the configuration

Total interruption time is typically less than 500ms, so TWS never notices any disconnect.

## Building from Source

```bash
# Install dependencies
go get github.com/docker/docker/client
go get github.com/BurntSushi/toml

# Build the application
wails build
```

## Development

```bash
# Start the development server
wails dev
```

## Configuration Details

The configuration is stored in TOML format and includes settings for:

- **Trading**: Mode, position limits, risk parameters
- **Strategy**: ATR ratios, RSI thresholds for various strategies
- **Options**: DTE ranges, delta parameters, spread cost limits
- **System**: Scanner connection settings, logging

## Architecture

- **Wails** (Go + Svelte): Provides the desktop GUI
- **Docker SDK**: Manages containers (pause/unpause)
- **TOML Config**: Central configuration shared with Python and Go services
- **Signal Handling**: Services respond to SIGUSR1 to reload configuration

## Troubleshooting

- Check Docker and Kubernetes status if containers aren't visible
- Ensure proper file permissions on the config volume
- Verify that TWS is running and accessible on the expected port

## License

This project is licensed under the MIT License - see the LICENSE file for details.
