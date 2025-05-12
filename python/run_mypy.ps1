# PowerShell script to run mypy only on core modules with crucial runtime checks
# This ignores documentation-style errors and focuses on catching bugs

$ErrorActionPreference = "Continue"

# Specify modules to check
$modules = @(
    "python/src/app/trader.py",
    "python/src/app/scanner.py",
    "python/src/app/scanner_client.py",
    "python/src/data/data_manager.py"
)

# Use a temporary .ini file that only has essential settings
$tempConfig = @"
[mypy]
python_version = 3.8
ignore_missing_imports = True
check_untyped_defs = True
disallow_untyped_defs = False
disallow_subclassing_any = False
disallow_incomplete_defs = False
disallow_untyped_calls = False
disallow_untyped_decorators = False
no_implicit_optional = False
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_return_any = False
warn_unreachable = True
"@

# Write to temp file
$tempConfig | Out-File -FilePath "python/temp-mypy.ini"

Write-Host "Running mypy focused on runtime errors only..."

# Run mypy on each module separately to avoid module conflicts
foreach ($module in $modules) {
    Write-Host "`nChecking $module..."
    mypy --config-file=python/temp-mypy.ini $module
}

# Clean up
Remove-Item -Force "python/temp-mypy.ini"

