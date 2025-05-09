# Version Management for TraderAdmin

This document explains how version management works in the TraderAdmin application.

## Version File

The central version information is stored in `TraderAdmin/version.go`. This file defines:

- `Version`: The application version (e.g., "1.0.2")
- `BuildDate`: When the application was built
- `CommitHash`: The git commit hash at build time

## Updating the Version

To update the version number:

### Windows
```powershell
# From the trader-admin directory
.\update-version.ps1 1.0.3
```

### Linux/macOS
```bash
# From the trader-admin directory
chmod +x update-version.sh  # First time only
./update-version.sh 1.0.3
```

## Building with the New Version

After updating the version, build the installer:

```
.\build-installer.bat
```

This will:
1. Extract the version from `version.go`
2. Build the TraderAdmin executable
3. Create an installer named `TraderAdmin-Setup-x.y.z.exe` (where x.y.z is your version)

## Where Version Information is Used

The version number is displayed in:

1. The application window title
2. The footer of the application
3. The installer filename
4. Windows registry entries

## Version Format

We follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 1.0.2)
- Increment MAJOR when making incompatible API changes
- Increment MINOR when adding functionality in a backward compatible manner
- Increment PATCH when making backward compatible bug fixes 