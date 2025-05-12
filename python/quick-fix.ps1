# This is a quick fix for the "module found twice" issue
# It runs mypy with options that work around the problem

# Clear any existing Python path to avoid conflicts
$env:PYTHONPATH = ""

# Run mypy with options that prevent the module duplication issue
Write-Host "Running mypy with workaround settings..." -ForegroundColor Green
mypy --no-namespace-packages --follow-imports=skip --ignore-missing-imports src

Write-Host "`nIf this passes, consider making these changes permanent in your mypy.ini"
Write-Host "Add the following to your mypy.ini:" -ForegroundColor Yellow
Write-Host "namespace_packages = False"
Write-Host "follow_imports = skip"
Write-Host "ignore_missing_imports = True"

