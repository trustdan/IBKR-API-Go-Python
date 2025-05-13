# TraderAdmin Deployment Guide

This guide details the deployment process for both the TraderAdmin desktop application and its server-side components.

## Table of Contents

- [Desktop Application Deployment](#desktop-application-deployment)
  - [Windows Installer](#windows-installer)
  - [Manual Installation](#manual-installation)
- [Server-Side Deployment](#server-side-deployment)
  - [Prerequisites](#prerequisites)
  - [Docker Images](#docker-images)
  - [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
  - [Health Checks](#health-checks)
  - [Logs](#logs)
  - [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)

## Desktop Application Deployment

### Windows Installer

The easiest way to install TraderAdmin on Windows is to use the provided installer:

1. Download the latest `TraderAdmin_Setup.exe` from the releases page.
2. Double-click the installer and follow the on-screen instructions.
3. The installer will create shortcuts in the Start Menu and on the Desktop.
4. Configuration files will be stored in the installation directory under the `config` folder.

### Manual Installation

If you prefer not to use the installer, you can manually install the application:

1. Download the appropriate binary for your platform from the releases page.
2. Extract the archive to a location of your choice.
3. Create a `config` directory in the same location as the executable.
4. Copy the example configuration file to the `config` directory and rename it to `config.toml`.

## Server-Side Deployment

### Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl (configured to access your cluster)
- Docker (for building and pushing images)

### Docker Images

Build and push the Docker images for the server-side components:

```bash
# Build images
docker build -t traderadmin/orchestrator:latest ./python/orchestrator

# Push images to your registry
docker push traderadmin/orchestrator:latest
```

Alternatively, use the provided build scripts:

```bash
# Windows
powershell -File .\run-compose.ps1 -build

# Linux/macOS
bash ./run-compose.sh -build
```

### Kubernetes Deployment

1. Create the TraderAdmin namespace:

```bash
kubectl apply -f deploy/namespace.yaml
```

2. Create the config PVC:

```bash
kubectl apply -f deploy/config-pvc.yaml
```

3. Deploy the orchestrator:

```bash
kubectl apply -f deploy/orchestrator-deployment.yaml
```

4. Verify the deployment:

```bash
kubectl get pods -n traderadmin
```

## Configuration

The primary configuration file is `config.toml`, which should be placed:

- **Desktop app**: In the `config` directory within the installation directory
- **Server-side**: In the Kubernetes PVC mounted at `/app/config`

You can copy the example configuration and modify it as needed:

```bash
# For Kubernetes deployment
kubectl cp config.toml.example traderadmin/$(kubectl get pod -n traderadmin -l app=traderadmin-orchestrator -o jsonpath='{.items[0].metadata.name}'):/app/config/config.toml
```

## Monitoring and Maintenance

### Health Checks

All server-side components expose health endpoints:

- Orchestrator: `/healthz` on port 8080

You can check the health status using kubectl:

```bash
# Get orchestrator pod name
ORCHESTRATOR_POD=$(kubectl get pod -n traderadmin -l app=traderadmin-orchestrator -o jsonpath='{.items[0].metadata.name}')

# Check health status
kubectl exec -n traderadmin $ORCHESTRATOR_POD -- curl http://localhost:8080/healthz
```

### Logs

View logs for the server-side components:

```bash
kubectl logs -n traderadmin -l app=traderadmin-orchestrator
```

For the desktop application, logs are stored in:
- Windows: `%APPDATA%\TraderAdmin\logs`

### Backup and Restore

To backup your configuration:

```bash
kubectl cp traderadmin/$(kubectl get pod -n traderadmin -l app=traderadmin-orchestrator -o jsonpath='{.items[0].metadata.name}'):/app/config/config.toml ./config.toml.backup
```

To restore from backup:

```bash
kubectl cp ./config.toml.backup traderadmin/$(kubectl get pod -n traderadmin -l app=traderadmin-orchestrator -o jsonpath='{.items[0].metadata.name}'):/app/config/config.toml
```

## Troubleshooting

### Desktop Application

- Ensure your system meets the minimum requirements
- Check the logs for errors
- Verify you have the correct configuration

### Server-Side Components

- Check pod status: `kubectl get pods -n traderadmin`
- Check pod details: `kubectl describe pod -n traderadmin $POD_NAME`
- Check logs: `kubectl logs -n traderadmin $POD_NAME`
- Verify the PVC is correctly mounted: `kubectl describe pod -n traderadmin $POD_NAME | grep -A 5 "Volumes:"` 