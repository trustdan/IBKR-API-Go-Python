# PowerShell script to fix whitespace and end-of-file issues

Write-Host "Starting whitespace fixing script..."

# Get Git's autocrlf setting to determine how to handle line endings
function Get-GitAutoCrLf {
    $gitConfig = git config --get core.autocrlf 2>$null
    if ($LASTEXITCODE -eq 0) {
        return $gitConfig.Trim()
    }
    return "false" # Default to false if not set
}

# Function to fix trailing whitespace in a file
function Fix-TrailingWhitespace {
    param(
        [string]$filePath,
        [string]$autoCrLf
    )

    # Read all lines from the file
    $content = Get-Content -Path $filePath -Raw
    $originalContent = $content

    # Replace trailing whitespace with nothing
    $content = $content -replace '[ \t]+$', ''

    # Handle line endings based on Git's autocrlf setting
    if ($autoCrLf -eq "true") {
        # Convert to CRLF for Windows
        $content = $content -replace '\r?\n', "`r`n"
    }
    elseif ($autoCrLf -eq "input") {
        # Keep line endings as they were, just fix trailing whitespace
    }
    else {
        # Convert to LF for cross-platform
        $content = $content -replace '\r\n', "`n"
    }

    # Ensure there's exactly one newline at the end
    if ($autoCrLf -eq "true") {
        $content = $content -replace '[\s\r\n]*$', "`r`n"
    } else {
        $content = $content -replace '[\s\r\n]*$', "`n"
    }

    # Only write back if content changed
    if ($content -ne $originalContent) {
        Write-Host "Fixing whitespace in $filePath"

        # Use appropriate encoding based on autocrlf
        if ($autoCrLf -eq "true") {
            [System.IO.File]::WriteAllText($filePath, $content)
        } else {
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
        }
        return $true
    }

    return $false
}

# Get Git's autocrlf setting
$autoCrLf = Get-GitAutoCrLf
Write-Host "Git autocrlf setting: $autoCrLf"

# Check if running as pre-commit hook
$preCommit = $args -contains "--pre-commit"
Write-Host "Running as pre-commit hook: $preCommit"

# Get the list of files to process
$filesToProcess = @()

if ($preCommit) {
    # Get only staged files
    Write-Host "Getting staged files from git..."
    $stagedFiles = git diff --name-only --cached --diff-filter=ACMR
    Write-Host "Found $($stagedFiles.Count) staged files"
    foreach ($file in $stagedFiles) {
        if (Test-Path $file) {
            $filesToProcess += $file
        }
    }
} else {
    # Find all relevant text files, excluding specified directories and extensions
    Write-Host "Scanning for text files..."
    $excludeDirs = @(
        '\\node_modules\\',
        '\\\.git\\',
        '\\build\\',
        '\\dist\\',
        '\\venv\\',
        '\\\.venv\\',
        '\\\.pytest_cache\\',
        '\\\.mypy_cache\\',
        '\\__pycache__\\',
        '\\\.idea\\',
        '\\\.vs\\',
        '\\\.vscode\\'
    ) -join '|'

    $includeExts = @(
        'md', 'yaml', 'yml', 'json', 'ps1', 'sh', 'py', 'go',
        'js', 'jsx', 'ts', 'tsx', 'css', 'scss', 'html', 'htm',
        'xml', 'txt', 'conf', 'cfg', 'ini', 'toml', 'sql'
    )

    $extPattern = ($includeExts | ForEach-Object { "\.$_`$" }) -join '|'

    Write-Host "Searching for files with extensions: $extPattern"
    Write-Host "Excluding directories matching: $excludeDirs"

    $filesToProcess = Get-ChildItem -Recurse -File | Where-Object {
        $_.Extension -match $extPattern -and
        $_.FullName -notmatch $excludeDirs -and
        $_.Length -lt 1MB
    } | Select-Object -ExpandProperty FullName

    Write-Host "Found $($filesToProcess.Count) files to process"
}

$fixedCount = 0

Write-Host "Processing files..."
foreach ($file in $filesToProcess) {
    try {
        # Skip binary files by examining the first few bytes
        $bytes = Get-Content -Path $file -Encoding Byte -ReadCount 1 -TotalCount 1000
        $isBinary = $false

        # Simple heuristic: if there are null bytes or many non-printable chars, it's likely binary
        $nonTextCount = ($bytes | Where-Object { $_ -eq 0 -or ($_ -lt 32 -and $_ -ne 9 -and $_ -ne 10 -and $_ -ne 13) }).Count
        if ($nonTextCount -gt 5) {
            $isBinary = $true
        }

        if (-not $isBinary) {
            $wasFixed = Fix-TrailingWhitespace -filePath $file -autoCrLf $autoCrLf
            if ($wasFixed) {
                $fixedCount++

                # If running as pre-commit, re-add the fixed file
                if ($preCommit) {
                    git add $file
                }
            }
        } else {
            Write-Host "Skipping binary file: $file"
        }
    }
    catch {
        Write-Host "Error processing file $file`: $_"
    }
}

if ($fixedCount -gt 0) {
    Write-Host "Fixed whitespace in $fixedCount file(s)"
} else {
    Write-Host "No files needed fixing"
}

Write-Host "Whitespace fixing complete!"

# Exit with correct status code for pre-commit
if ($preCommit -and $fixedCount -gt 0) {
    exit 1  # Signal to pre-commit that files were modified
} else {
    exit 0  # Success
}
