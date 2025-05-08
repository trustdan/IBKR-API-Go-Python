# IBKR Trader Administration GUI

A Wails-based desktop GUI for managing the IBKR Auto Vertical Spread Trader with a "pause → edit → unpause" workflow that preserves TWS connections during configuration changes.

![TraderAdmin GUI](https://i.imgur.com/placeholder.png)

## Quick Start

1. **Start Docker Desktop** with Kubernetes enabled
2. **Deploy the trader stack**: `kubectl apply -k kubernetes/base/`
3. **Run TWS or IB Gateway** and log in
4. **Launch TraderAdmin** and edit parameters
5. **Click "Save & Restart"** to apply changes without service interruption

## Key Components

### Backend
- **Python & Go signal handlers** for live configuration reloading
- **Docker SDK integration** for container control
- **TOML configuration** with thread-safe access
- **Kubernetes PVC** for shared configuration

### Frontend
- **Four configuration tabs**: Trading, Strategy, Options, System
- **Real-time container status** monitoring
- **Intuitive interface** for editing all parameters
- **One-click save and restart** with intelligent error handling

## Daily Workflow

The TraderAdmin dashboard simplifies daily management:

1. Make configuration changes in any tab
2. Click "Save & Restart"
3. The system will:
   - Pause containers (< 500ms interruption)
   - Save the config to shared volume
   - Unpause containers
   - Signal reloading via SIGUSR1

## Documentation

- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Complete usage instructions
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Technical details
- [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md) - Windows installer guide
- [CI-CD.md](CI-CD.md) - Continuous Integration/Deployment details
- [TraderAdmin/README.md](TraderAdmin/README.md) - Tool documentation

## Installation

### Windows Installer

Download the latest installer from the [Releases](https://github.com/trustdan/ibkr-trader/releases) page:

```
TraderAdmin-Setup-1.0.0.exe
```

The installer checks system requirements and sets up desktop/start menu shortcuts.

### Automatic Builds

The installer is automatically built by our GitHub Actions workflow on commits to the main branch. See [CI-CD.md](CI-CD.md) for details on the build process.

## Building from Source

### Manual Build

```bash
cd TraderAdmin
wails build
```

### Building the Installer

```bash
cd trader-admin
.\build-installer.bat
```
