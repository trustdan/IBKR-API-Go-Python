# Save/Restart & Scheduling Workflow

This document explains how to use the Save/Restart functionality and Scheduling features of the TraderAdmin application.

## Save/Restart Functionality

The "Save & Restart" functionality allows you to safely modify configuration settings and apply them without disrupting active trades or causing inconsistent states. When you use this feature, the system:

1. Pauses all running services (orchestrator and scanner)
2. Backs up the current configuration
3. Saves the new configuration
4. Restarts the services with the new configuration

### How to Use Save & Restart

1. Navigate to any configuration tab (e.g., Options, Scheduling)
2. Make your desired changes
3. Click the "Save & Restart" button
4. Wait for the confirmation toast message

## Scheduling Features

The Scheduling tab allows you to configure when trading should automatically start and stop.

### Trading Hours

Set the specific times when trading should start and end each day:

- **Trading Start Time**: When trading should automatically begin (e.g., "09:30:00" for market open)
- **Trading End Time**: When trading should automatically stop (e.g., "16:00:00" for market close)
- **Timezone**: The timezone to use for these times (e.g., "America/New_York")

### Trading Days

Select which days of the week trading should be active:

- By default, trading is enabled Monday through Friday
- You can enable or disable trading for any day of the week

### Maintenance Window

Set a window for system maintenance:

- Format: "HH:MM:SS-HH:MM:SS" (e.g., "00:00:00-03:00:00" for midnight to 3 AM)
- During this window, automated maintenance tasks will run

## How It Works

### Backend Implementation

The TraderAdmin application uses several mechanisms to ensure safe configuration updates:

1. **Docker/Kubernetes Integration**: Services are paused using Docker or Kubernetes APIs
2. **Configuration Backup**: The current config is backed up before any changes
3. **Signal Handling**: Services respond to signals to reload configuration
4. **Trading Scheduler**: A Python scheduler manages the trading_enabled flag based on configured times

### Python Orchestrator

The Python orchestrator implements:

- **Signal Handling**: Listens for SIGUSR1 to reload configuration
- **Time-based Scheduler**: Automatically enables/disables trading based on configured times
- **State Management**: Maintains a trading_enabled flag that controls all trading operations

## Testing

The application includes:

- **Unit Tests**: Test individual components of the Save/Restart functionality
- **Gherkin/Cucumber Tests**: Behavioral tests for the Save/Restart and scheduling workflows

## Technical Details

- The scheduler uses the Python `schedule` library and `pytz` for timezone handling
- Configuration is stored in TOML format
- Docker/Kubernetes operations use their respective APIs

## Troubleshooting

- If changes don't apply, check the logs for errors during the restart process
- If scheduling doesn't work correctly, verify timezone settings
- For manual restarts, you can use the "Save & Restart" button at any time
