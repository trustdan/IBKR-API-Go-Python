# TraderAdmin Usage Guide

This guide shows you how to use the TraderAdmin tool to manage your IBKR Trader configuration.

## Prerequisites

- Docker Desktop with Kubernetes enabled
- Interactive Brokers Trader Workstation (TWS) or IB Gateway
- The trader-stack deployed in Kubernetes

## Getting Started

### Installation

1. Clone this repository
2. Navigate to the `trader-admin/TraderAdmin` directory
3. Run the application:
   - Windows: Double-click `TraderAdmin.exe`
   - macOS: Open `TraderAdmin.app`
   - Linux: Run `./TraderAdmin`

Alternatively, build from source:
```bash
cd trader-admin/TraderAdmin
wails build
```

### First Time Setup

1. Ensure your configuration is in the correct format:
   ```bash
   cd python
   python scripts/yaml_to_toml.py config/config.yaml -o config/config.toml
   ```
2. Deploy the Kubernetes resources:
   ```bash
   kubectl apply -k kubernetes/base/
   ```
3. Start TWS or IB Gateway and log in
4. Launch TraderAdmin

## Using the Interface

The TraderAdmin interface is organized into tabs for different configuration areas:

### Trading Tab

![Trading Tab](https://i.imgur.com/placeholder.png)

- **Trading Mode**: Switch between PAPER and LIVE trading
- **Max Positions**: Maximum concurrent positions
- **Max Daily Trades**: Maximum trades per day
- **Risk Per Trade**: Percentage of account to risk per trade
- **Price Improvement Factor**: Order placement strategy
- **Allow Late Day Entry**: Enable/disable late day trading

### Strategy Tab

![Strategy Tab](https://i.imgur.com/placeholder.png)

Contains parameters for different strategy types:
- **High Base**: Max ATR Ratio, Min RSI
- **Low Base**: Min ATR Ratio, Max RSI
- **Bull Pullback**: RSI Threshold
- **Bear Rally**: RSI Threshold

### Options Tab

![Options Tab](https://i.imgur.com/placeholder.png)

- **DTE Range**: Min/Max days to expiration
- **Delta Range**: Min/Max delta values
- **Max Spread Cost**: Maximum cost per spread
- **Min Reward/Risk**: Minimum reward-to-risk ratio

### System Tab

![System Tab](https://i.imgur.com/placeholder.png)

- View running containers and their status
- Pause/Unpause all containers

## Workflow

1. Make changes to settings in the appropriate tabs
2. Click "Save & Restart" button
3. The system will:
   - Pause all trading containers
   - Save your configuration
   - Unpause the containers
   - Signal them to reload the new configuration

## Troubleshooting

### Common Issues

1. **No containers shown**
   - Ensure Docker Desktop is running
   - Check that Kubernetes is enabled
   - Verify that `kubectl apply -k kubernetes/base/` was run

2. **Configuration not saving**
   - Check file permissions on the config directory
   - Ensure the `trader-config` persistent volume is properly mounted

3. **Changes not taking effect**
   - Verify that containers are receiving the SIGUSR1 signal
   - Check container logs for configuration reload messages

### Viewing Logs

To check if configuration changes were properly applied:

```bash
# Python orchestrator logs
kubectl logs deployment/python-orchestrator -n trader-stack

# Go scanner logs
kubectl logs deployment/go-scanner -n trader-stack
```

Look for lines like "Configuration reloaded successfully" that indicate the changes were applied.

## Advanced Usage

### Backup and Restore

TraderAdmin automatically creates a backup of your configuration before making changes. To restore:

1. Stop all containers:
   ```bash
   kubectl scale deployment python-orchestrator go-scanner --replicas=0 -n trader-stack
   ```
2. Restore the backup:
   ```bash
   cp trader-admin/TraderAdmin/config/config.toml.bak trader-admin/TraderAdmin/config/config.toml
   ```
3. Restart containers:
   ```bash
   kubectl scale deployment python-orchestrator go-scanner --replicas=1 -n trader-stack
   ```
