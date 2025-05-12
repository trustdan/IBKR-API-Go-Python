# PowerShell script to fix PYTHONPATH for mypy

# Clear previous PYTHONPATH environment variable
$env:PYTHONPATH = ""

# Set PYTHONPATH to point ONLY to the python directory
$env:PYTHONPATH = "$PSScriptRoot"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH"

# Now you can run mypy with this command:
Write-Host "`nRun mypy with:"
Write-Host "mypy src" -ForegroundColor Green

