#!/bin/bash
# Script to update the version number across the project

# Check if a version number was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <new_version>"
  echo "Example: $0 1.0.3"
  exit 1
fi

NEW_VERSION="$1"
BUILD_DATE=$(date +"%Y-%m-%d")
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")

# Update version.go
echo "Updating version.go..."
cat > "TraderAdmin/version.go" << EOF
package main

// Version information
var (
	// Version is the application version
	Version = "$NEW_VERSION"
	
	// BuildDate is the date when the application was built
	BuildDate = "$BUILD_DATE"
	
	// CommitHash is the git commit hash at build time
	CommitHash = "$COMMIT_HASH"
)

// GetVersionInfo returns a formatted version string
func GetVersionInfo() string {
	return Version
}

// GetFullVersionInfo returns detailed version information
func GetFullVersionInfo() map[string]string {
	return map[string]string{
		"version":    Version,
		"buildDate":  BuildDate,
		"commitHash": CommitHash,
	}
}
EOF

echo "Version updated to $NEW_VERSION"
echo "Build date set to $BUILD_DATE"
echo "Commit hash set to $COMMIT_HASH"

echo "Done! Now you can build the installer with: ./build-installer.bat" 