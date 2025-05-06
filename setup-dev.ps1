# PowerShell script to set up the development environment

# Navigate to the python directory
cd python

# Install the package in development mode
pip install -e .

# Install type stubs for mypy
pip install types-PyYAML types-requests types-psutil pandas-stubs

Write-Host "Development environment set up successfully."
Write-Host "You can now run mypy with proper import resolution."
