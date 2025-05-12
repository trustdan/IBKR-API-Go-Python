# Test script for config hot-reload in PowerShell

# Ensure the config directory exists
if (-not (Test-Path -Path "config")) {
    New-Item -ItemType Directory -Path "config"
}

# Create or update config.toml with test values
$configContent = @"
[ibkr]
host = "localhost"
port = 7497
client_id = 0
read_only = false

[trading]
mode = "PAPER"
max_positions = 5
risk_per_trade_pct = 1.0
max_loss_pct = 5.0
"@

Set-Content -Path "config/config.toml" -Value $configContent

Write-Host "Created initial config.toml"
Write-Host "Starting Go config watcher example..."

# Start the Go watcher in a new window (only if the binary exists)
Start-Process -NoNewWindow -FilePath "go" -ArgumentList "run", "go_examples/config_watcher.go"

# Wait a bit
Start-Sleep -Seconds 5

# Modify the config file
$updatedConfig = @"
[ibkr]
host = "localhost"
port = 7497
client_id = 0
read_only = false

[trading]
mode = "PAPER"
max_positions = 10  # Changed from 5 to 10
risk_per_trade_pct = 2.0  # Changed from 1.0 to 2.0
max_loss_pct = 5.0
"@

Write-Host "Updating config file with new values..."
Set-Content -Path "config/config.toml" -Value $updatedConfig

Write-Host "Config file updated. Check the Go process output to see if it detected the change."
