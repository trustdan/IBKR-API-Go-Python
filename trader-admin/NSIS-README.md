# TraderAdmin NSIS Installer Implementation

This document describes the implementation of the NSIS installer for the TraderAdmin application.

## Files Created

1. **TraderAdmin-Installer.nsi**
   - Main NSIS script that defines the installer behavior
   - Includes system checks for Docker, Kubernetes, and TWS
   - Creates shortcuts, registry entries, and uninstallation support

2. **build-installer.bat**
   - Windows batch script to automate the build process
   - Checks for required tools (NSIS, Wails)
   - Builds the TraderAdmin application and then the installer

3. **launcher.go**
   - Go code that implements runtime service checks
   - Shows warnings if required services are not available
   - Provides real-time status information in the UI

4. **SystemStatus.svelte**
   - Svelte component that displays service status in the UI
   - Shows Docker, Kubernetes, and TWS availability
   - Provides visual indicators and helpful messages

5. **INSTALLER_GUIDE.md**
   - User guide for building and using the installer
   - Includes troubleshooting instructions

## Implementation Features

### System Checks

The installer performs checks at two key points:

1. **Installation Time**
   - Detects if Docker Desktop is running
   - Checks if Kubernetes is enabled
   - Verifies if TWS/IB Gateway is running
   - Provides warnings and recommendations based on findings

2. **Runtime (Application Startup)**
   - Performs the same checks when the application starts
   - Shows a dialog if critical services are missing
   - Displays real-time status in the System tab

### User Experience

- **Modern UI**: Uses NSIS Modern UI for a clean installer experience
- **Informative Dialogs**: Clear explanations for requirements
- **Progress Indicators**: Visual feedback for long operations
- **Configurability**: Options to customize installation

### Integration with TraderAdmin

- **Config Management**: Preserves user configuration during uninstallation (optional)
- **Default Settings**: Sets up proper defaults for first-time users
- **Registry Integration**: Proper Windows registration
- **Shortcuts**: Desktop and Start Menu shortcuts

## Technical Details

### Dependencies

- **NSIS 3.0+**: Required for building the installer
- **Wails**: Required for building the TraderAdmin application
- **Go 1.20+**: Required for compiling the application
- **Windows 10+**: Required for running the application

### Building

1. Ensure prerequisites are installed
2. Run `build-installer.bat` from the trader-admin directory
3. The installer will be created as `TraderAdmin-Setup-1.0.0.exe`

## Maintenance

To update the installer for new versions:

1. Update the VERSION constant in TraderAdmin-Installer.nsi
2. Add any new files to the installer script if needed
3. Update registry entries if needed
4. Rebuild using the build script
