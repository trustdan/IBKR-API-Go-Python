# PowerShell script to run auto-vertical-spread services using docker-compose

# Check if Docker is running
try {
    $null = docker info
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    $null = docker-compose --version
} catch {
    Write-Host "Error: docker-compose is not available. Please install Docker Desktop with docker-compose." -ForegroundColor Red
    exit 1
}

# Ensure config directories exist
$GoConfigDir = Join-Path $PWD "go"
$PythonConfigDir = Join-Path $PWD "python/config"
if (-not (Test-Path $GoConfigDir)) { New-Item -Path $GoConfigDir -ItemType Directory -Force }
if (-not (Test-Path $PythonConfigDir)) { New-Item -Path $PythonConfigDir -ItemType Directory -Force }

# Create default config file for Go if it doesn't exist
$GoConfigFile = Join-Path $GoConfigDir "config.json"
if (-not (Test-Path $GoConfigFile)) {
    Write-Host "Creating default Go config..." -ForegroundColor Cyan
    @"
{
  "log_level": "info",
  "grpc_port": 50051,
  "metrics_port": 2112
}
"@ | Out-File -FilePath $GoConfigFile -Encoding utf8
}

# Check if config.yaml exists and create a default one if needed
$PythonConfigFile = Join-Path $PythonConfigDir "config.yaml"
if (-not (Test-Path $PythonConfigFile)) {
    Write-Host "Creating default Python config..." -ForegroundColor Cyan
    Copy-Item -Path (Join-Path $PWD "python/config/config.yaml.example") -Destination $PythonConfigFile -ErrorAction SilentlyContinue

    # If no example file exists, create a basic one
    if (-not (Test-Path $PythonConfigFile)) {
        @"
# IBKR Auto Vertical Spread Trader Configuration
ibkr:
  host: "127.0.0.1"
  port: 7497
  client_id: 1
  read_only: false
  account: ""

# Scanner Configuration
scanner:
  host: "go-scanner"
  port: 50051
  max_concurrency: 50

# Trading
trading:
  mode: "PAPER"
  max_positions: 5
  max_daily_trades: 3
  risk_per_trade: 0.02
  price_improvement_factor: 0.4
  allow_late_day_entry: true
"@ | Out-File -FilePath $PythonConfigFile -Encoding utf8
    }
}

# Determine which docker-compose file to use
$ComposeFile = "docker-compose.prod.yml"
if ($args[0] -eq "dev") {
    $ComposeFile = "docker-compose.yml"
}

Write-Host "Starting services using $ComposeFile..." -ForegroundColor Green

# Run docker-compose
docker-compose -f $ComposeFile up -d

Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "Go service running at: http://localhost:50051" -ForegroundColor Cyan
Write-Host "Go metrics at: http://localhost:2112" -ForegroundColor Cyan
Write-Host "Python service running at: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs, run:" -ForegroundColor Cyan
Write-Host "docker-compose -f $ComposeFile logs -f"
Write-Host ""
Write-Host "To stop all services, run:" -ForegroundColor Cyan
Write-Host "docker-compose -f $ComposeFile down"

