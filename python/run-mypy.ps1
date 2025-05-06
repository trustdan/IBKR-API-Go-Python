# PowerShell script to run mypy with proper configuration
# This script bypasses the issue with duplicate module names

# Clear PYTHONPATH to avoid any path conflicts
$env:PYTHONPATH = ""

# First, remove any cached files that might cause issues
Write-Host "Cleaning up mypy cache..." -ForegroundColor Yellow
if (Test-Path .mypy_cache) {
    Remove-Item -Recurse -Force .mypy_cache
}

# Run mypy with specific configuration overrides
Write-Host "Running mypy with custom configuration..." -ForegroundColor Green
mypy --no-namespace-packages --no-implicit-reexport --ignore-missing-imports src

# Exit with the mypy exit code
exit $LASTEXITCODE
