# TraderAdmin Installer Guide

This guide explains how to build and use the NSIS installer for the TraderAdmin application.

## Building the Installer

### Prerequisites

1. **NSIS (Nullsoft Scriptable Install System)**
   - Download and install NSIS from [nsis.sourceforge.io](https://nsis.sourceforge.io/Download)
   - Add NSIS to your system PATH

2. **Wails**
   - Ensure Wails is installed and available in your PATH
   - Wails is used to build the TraderAdmin application before packaging

### Build Process

1. Navigate to the `trader-admin` directory:
   ```
   cd trader-admin
   ```

2. Run the build script:
   ```
   .\build-installer.bat
   ```

3. The installer will be created as `TraderAdmin-Setup-1.0.0.exe` in the same directory.

## Installation Process

### System Checks

The installer performs several system checks to ensure a proper environment:

1. **Windows Version**: Verifies Windows 10 or newer
2. **Docker Desktop**: Checks if Docker Desktop is running
3. **Kubernetes**: Checks if Kubernetes is enabled in Docker Desktop
4. **TWS/IB Gateway**: Checks if Interactive Brokers Trader Workstation or Gateway is running

If any required services are not running, the installer will display warnings and recommendations.

### Installation Options

1. **Installation Directory**: Default is `C:\Program Files\IBKR Auto Trader\TraderAdmin`
2. **Start Menu Shortcuts**: Created in the IBKR Auto Trader folder
3. **Desktop Shortcut**: Created by default

## Post-Installation

After installation, the TraderAdmin application will:

1. Perform startup checks for Docker, Kubernetes, and TWS/IB Gateway
2. Display the service status in the System tab
3. Automatically copy configuration files if found

## Troubleshooting

### Common Issues

1. **"Docker Desktop not available" warning**
   - Ensure Docker Desktop is installed and running
   - Start Docker Desktop and restart TraderAdmin

2. **"Kubernetes not available" warning**
   - Open Docker Desktop settings
   - Enable Kubernetes and wait for it to start
   - Restart TraderAdmin

3. **Missing trader-stack namespace**
   - Run `kubectl apply -k kubernetes/base/` to deploy the trading stack
   - Restart TraderAdmin to refresh status

### Uninstallation

To uninstall TraderAdmin:

1. Use Windows Control Panel > Programs and Features
2. Find "TraderAdmin" and select "Uninstall"
3. Choose whether to keep or remove configuration files

## Advanced

The installer includes these advanced features:

1. **Configuration Backup**: Before making changes, configurations are backed up
2. **Custom Components**: Creates necessary directories and registry entries
3. **System Integration**: Properly registers the application with Windows
