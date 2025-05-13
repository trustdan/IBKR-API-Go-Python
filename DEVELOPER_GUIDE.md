# TraderAdmin Developer Guide

This document provides technical information for developers working on the TraderAdmin project.

## Project Structure

```
TraderAdmin/
├── backend/              # Go code for Wails backend
│   ├── models/           # Data structures (e.g., metrics)
│   └── ...               # Other backend modules
├── frontend/             # Svelte/TS frontend for Wails GUI
│   ├── src/
│   │   ├── components/   # Reusable UI elements
│   │   ├── tabs/         # Main application tabs
│   │   ├── stores/       # Svelte stores
│   │   └── wailsjs/      # Generated Wails JS bindings
│   └── ...               # Frontend build configuration
├── config/               # Configuration files
├── deploy/               # Kubernetes deployment files
├── app.go                # Main Wails app implementation
├── main.go               # Application entry point
└── ...                   # Other project files
```

## Technology Stack

- **GUI Framework**: [Wails](https://wails.io/) - Go backend with web frontend
- **Frontend**: Svelte with TypeScript
- **Backend**: Go (for the Wails application)
- **Trading Orchestration**: Python
- **Deployment**: Docker and Kubernetes
- **Configuration**: TOML

## Development Setup

### Prerequisites

1. Go 1.23+ installed
2. Node.js 18+ and npm
3. Wails CLI installed
4. Docker and Kubernetes (for backend services)
5. Python 3.10+ (for orchestrator)

### Installing Wails

```bash
go install github.com/wailsapp/wails/v2/cmd/wails@latest
```

### Setting Up for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/IBKR-trader.git
   cd IBKR-trader
   ```

2. Install Go dependencies:
   ```bash
   go mod download
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Start the application in development mode:
   ```bash
   wails dev
   ```

## Application Architecture

### Go Backend

The Go backend serves as both the Wails application backend and the coordinator for Kubernetes-deployed services.

Key components:
- `app.go`: Contains the main `App` struct with Wails-exposed methods
- `backend/models`: Contains data structures shared between Go and frontend

#### Important Wails-Exposed Functions

These functions are exposed to the frontend and can be called from Svelte components:

- `GetConfigSchema()`: Returns a JSON schema for the configuration
- `LoadConfig()`: Loads the current configuration
- `SaveConfigurationAndRestart(config)`: Saves configuration and restarts services
- `GetStatus()`: Gets the current system status
- `GetLatestMetrics()`: Retrieves monitoring metrics
- `TestAlertNotification(channelType, message)`: Tests alert notifications
- `PauseTradingServices()`: Pauses trading services
- `ResumeTradingServices()`: Resumes trading services

### Frontend Structure

The Svelte frontend is organized as follows:

- **Components**: Reusable UI elements in `frontend/src/components/`
  - `NavTabs.svelte`: Navigation sidebar
  - `StatusBar.svelte`: Status bar showing service states
  - `DynamicForm.svelte`: Dynamic form generator based on JSON schema

- **Tabs**: Main application content areas in `frontend/src/tabs/`
  - `OverviewTab.svelte`: Dashboard and summary
  - `ConnectionTab.svelte`: IBKR connection settings
  - `TradingRiskTab.svelte`: Risk management settings
  - `OptionsTab.svelte`: Options trading settings
  - `SchedulingTab.svelte`: Trading schedule configuration
  - `MonitoringTab.svelte`: Real-time metrics display
  - `AlertsConfigurationTab.svelte`: Alert settings

- **Stores**: State management in `frontend/src/stores/`
  - `activeTab.ts`: Currently active tab
  - `configStore.ts`: Configuration data
  - `schemaStore.ts`: JSON schema for configuration
  - `statusStore.ts`: System status information
  - `metricsStore.ts`: Trading metrics data

### Data Flow

1. The frontend loads and initializes stores
2. Backend data is fetched via Wails-exposed functions
3. User interactions update store states
4. Configuration changes are applied via `SaveConfigurationAndRestart`
5. Status and metrics are periodically refreshed

## Testing

### Running Backend Tests

```bash
cd /path/to/project
go test ./...
```

### Running Frontend Tests

```bash
cd frontend
npm run test
```

### Adding New Tests

- **Backend**: Add test files with `_test.go` suffix
- **Frontend**: Create `.test.ts` or `.spec.ts` files for components and stores

## Building for Production

To build a production version:

```bash
wails build
```

This creates executables in the `build/bin` directory.

## Contributing

1. Create a feature branch from the main branch
2. Make your changes
3. Add appropriate tests
4. Submit a pull request

## Troubleshooting

### Common Issues

- **Wails Development Server Not Starting**: Check for port conflicts or try reinstalling Wails CLI
- **Go Module Issues**: Run `go mod tidy` to resolve dependency conflicts
- **Frontend Hot Reload Not Working**: Check the Wails development server logs for errors

### Debugging

- Use `LogDebug`, `LogInfo`, etc. in Go code for logging
- Use Chrome DevTools in Wails development mode for frontend debugging
- Check application logs in the terminal running `wails dev` 