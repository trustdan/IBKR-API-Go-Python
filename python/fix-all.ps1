# PowerShell script to fix all import issues and set up the proper environment

Write-Host "===== IBKR-Trader Project Fix Script =====" -ForegroundColor Green

# First, install the package in development mode
Write-Host "`nStep 1: Installing package in development mode..." -ForegroundColor Cyan
cd $PSScriptRoot
pip install -e .

# Install type stubs for mypy
Write-Host "`nStep 2: Installing type stubs for mypy..." -ForegroundColor Cyan
pip install types-PyYAML types-requests types-psutil pandas-stubs

# Run the import fixer script
Write-Host "`nStep 3: Fixing relative imports in Python files..." -ForegroundColor Cyan
python fix-imports.py src

# Update PYTHONPATH environment variable for development
Write-Host "`nStep 4: Setting up PYTHONPATH environment variable..." -ForegroundColor Cyan
$env:PYTHONPATH = "$PSScriptRoot"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH"

# Test imports
Write-Host "`nStep 5: Testing imports..." -ForegroundColor Cyan
python test_imports.py

# Provide instructions for proper PYTHONPATH setup
Write-Host "`n===== Setup Complete =====" -ForegroundColor Green
Write-Host "`nTo permanently set PYTHONPATH for your project, add the following to your PowerShell profile:"
Write-Host '$env:PYTHONPATH += ";C:\Users\Dan\IBKR-trader\python"' -ForegroundColor Yellow

Write-Host "`nYou can now run mypy with:"
Write-Host "mypy src" -ForegroundColor Yellow

Write-Host "`nOr for Python files outside the src directory:"
Write-Host "mypy path/to/your/file.py" -ForegroundColor Yellow

