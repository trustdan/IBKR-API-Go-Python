#!/usr/bin/env pwsh
# version-extract.ps1
# This script extracts the version from version.go and returns it in a format usable by the NSIS installer

$versionFile = Join-Path $PSScriptRoot "TraderAdmin/version.go"

if (-not (Test-Path $versionFile)) {
    Write-Error "Version file not found: $versionFile"
    exit 1
}

# Extract version from version.go
$versionContent = Get-Content $versionFile
$versionMatch = $versionContent | Select-String -Pattern 'Version\s*=\s*"([^"]+)"'

if ($versionMatch) {
    $version = $versionMatch.Matches.Groups[1].Value
    Write-Output $version
    exit 0
} else {
    Write-Error "Version not found in $versionFile"
    exit 1
} 