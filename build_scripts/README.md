# TraderAdmin Build Scripts

This directory contains scripts used for building and packaging the TraderAdmin application.

## Windows

### windows_installer.nsi

NSIS script for creating the Windows installer. Requires NSIS to be installed.

### build_windows.bat

Batch script to:
1. Build the Wails application for Windows
2. Create the Windows installer using NSIS

Usage:
```
.\build_windows.bat
```

## Unix-like Systems (Linux/macOS)

### build_unix.sh

Shell script to:
1. Build the Wails application for Linux or macOS
2. Create a distribution package (.tar.gz for Linux, .dmg or .zip for macOS)

Usage:
```bash
# Make sure the script is executable
chmod +x build_unix.sh

# Run the script
./build_unix.sh
```

## Requirements

- **Windows**:
  - Wails CLI
  - NSIS (Nullsoft Scriptable Install System)

- **macOS**:
  - Wails CLI
  - Optional: create-dmg tool for creating DMG files

- **Linux**:
  - Wails CLI
  - Standard Unix utilities (tar, gzip)

## Manual Building

If you prefer to build manually without using these scripts:

1. Build the Wails application:
   ```
   wails build -trimpath -ldflags="-s -w"
   ```

2. For Windows, compile the NSIS script:
   ```
   makensis build_scripts\windows_installer.nsi
   ``` 