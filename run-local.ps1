# PowerShell script to run the auto-vertical-spread services locally

# Colors for output
$Green = [System.ConsoleColor]::Green
$Blue = [System.ConsoleColor]::Cyan
$Red = [System.ConsoleColor]::Red
$Reset = [System.ConsoleColor]::White

# Function to write colored output
function Write-Color($Color, $Message) {
    $CurrentForeground = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $Host.UI.RawUI.ForegroundColor = $Reset
}

# Check if Docker is running
try {
    $null = docker info
} catch {
    Write-Color $Red "Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Set default tag to use
$Tag = if ($args[0]) { $args[0] } else { "latest" }

Write-Color $Blue "Starting auto-vertical-spread services with tag: $Tag"

# Pull the latest images
Write-Color $Blue "Pulling Docker images..."
try {
    docker pull "trustdan/auto-vertical-spread-go:$Tag"
} catch {
    Write-Color $Red "Failed to pull Go image. Using local image if available."
}

try {
    docker pull "trustdan/auto-vertical-spread-python:$Tag"
} catch {
    Write-Color $Red "Failed to pull Python image. Using local image if available."
}

# Create network if it doesn't exist
try {
    $null = docker network inspect vertical-spread-network
} catch {
    Write-Color $Blue "Creating Docker network..."
    docker network create vertical-spread-network
}

# Check if containers are already running and stop them
if (docker ps -a | Select-String -Pattern "vertical-spread-go") {
    Write-Color $Blue "Stopping and removing existing Go container..."
    docker stop vertical-spread-go -ErrorAction SilentlyContinue
    docker rm vertical-spread-go -ErrorAction SilentlyContinue
}

if (docker ps -a | Select-String -Pattern "vertical-spread-python") {
    Write-Color $Blue "Stopping and removing existing Python container..."
    docker stop vertical-spread-python -ErrorAction SilentlyContinue
    docker rm vertical-spread-python -ErrorAction SilentlyContinue
}

# Make sure config directories exist
$GoConfigDir = Join-Path $PWD "go"
$PythonConfigDir = Join-Path $PWD "python/config"
if (-not (Test-Path $GoConfigDir)) { New-Item -Path $GoConfigDir -ItemType Directory -Force }
if (-not (Test-Path $PythonConfigDir)) { New-Item -Path $PythonConfigDir -ItemType Directory -Force }

# Create default config file for Go if it doesn't exist
$GoConfigFile = Join-Path $GoConfigDir "config.json"
if (-not (Test-Path $GoConfigFile)) {
    Write-Color $Blue "Creating default Go config..."
    @"
{
  "log_level": "info",
  "grpc_port": 50051,
  "metrics_port": 2112
}
"@ | Out-File -FilePath $GoConfigFile -Encoding utf8
}

# Convert Windows paths to Docker paths
$GoConfigMountPath = $GoConfigFile.Replace('\', '/').Replace('C:', '/c')
$PythonConfigMountPath = $PythonConfigDir.Replace('\', '/').Replace('C:', '/c')

# Start Go scanner
Write-Color $Blue "Starting Go scanner..."
try {
    docker run -d --name vertical-spread-go `
        --network vertical-spread-network `
        -p 50051:50051 -p 2112:2112 `
        -v "${GoConfigMountPath}:/root/config.json" `
        "trustdan/auto-vertical-spread-go:$Tag"
} catch {
    Write-Color $Red "Failed to start Go container. Trying to use local image..."
    try {
        docker run -d --name vertical-spread-go `
            --network vertical-spread-network `
            -p 50051:50051 -p 2112:2112 `
            -v "${GoConfigMountPath}:/root/config.json" `
            "local/auto-vertical-spread-go:latest"
    } catch {
        Write-Color $Red "Failed to start Go container with local image as well. Exiting."
        exit 1
    }
}

# Start Python orchestrator
Write-Color $Blue "Starting Python orchestrator..."
try {
    docker run -d --name vertical-spread-python `
        --network vertical-spread-network `
        -p 8000:8000 `
        -v "${PythonConfigMountPath}:/app/config" `
        -e "SCANNER_HOST=vertical-spread-go" `
        -e "SCANNER_PORT=50051" `
        "trustdan/auto-vertical-spread-python:$Tag"
} catch {
    Write-Color $Red "Failed to start Python container. Trying to use local image..."
    try {
        docker run -d --name vertical-spread-python `
            --network vertical-spread-network `
            -p 8000:8000 `
            -v "${PythonConfigMountPath}:/app/config" `
            -e "SCANNER_HOST=vertical-spread-go" `
            -e "SCANNER_PORT=50051" `
            "local/auto-vertical-spread-python:latest"
    } catch {
        Write-Color $Red "Failed to start Python container with local image as well."
        Write-Color $Red "Stopping Go container and exiting."
        docker stop vertical-spread-go -ErrorAction SilentlyContinue
        exit 1
    }
}

Write-Color $Green "All services started successfully!"
Write-Color $Blue "Go service running at: http://localhost:50051"
Write-Color $Blue "Go metrics at: http://localhost:2112"
Write-Color $Blue "Python service running at: http://localhost:8000"
Write-Output ""
Write-Color $Blue "To stop all services, run:"
Write-Output "docker stop vertical-spread-go vertical-spread-python"
Write-Color $Blue "To view logs, run:"
Write-Output "docker logs vertical-spread-go -f"
