#!/usr/bin/env pwsh
# Script to update the version number across the project

param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion
)

# Get build date and commit hash
$BuildDate = Get-Date -Format "yyyy-MM-dd"
$CommitHash = & git rev-parse --short HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    $CommitHash = "dev"
}

# Update version.go
Write-Host "Updating version.go..."
$VersionContent = @"
package main

// Version information
var (
	// Version is the application version
	Version = "$NewVersion"
	
	// BuildDate is the date when the application was built
	BuildDate = "$BuildDate"
	
	// CommitHash is the git commit hash at build time
	CommitHash = "$CommitHash"
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
"@

# Write to version.go
Set-Content -Path "TraderAdmin/version.go" -Value $VersionContent

Write-Host "Version updated to $NewVersion"
Write-Host "Build date set to $BuildDate"
Write-Host "Commit hash set to $CommitHash"

Write-Host "Done! Now you can build the installer with: .\build-installer.bat" 