# PowerShell script to fix whitespace and end-of-file issues

# Function to fix trailing whitespace in a file
function Fix-TrailingWhitespace {
    param([string]$filePath)

    Write-Host "Fixing trailing whitespace in $filePath"

    # Read all lines from the file
    $content = Get-Content -Path $filePath -Raw

    # Replace trailing whitespace with nothing and normalize line endings to LF
    $newContent = $content -replace '[ \t]+$', '' -replace '\r\n', "`n"

    # Write the content back to the file with LF line endings
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($filePath, $newContent, $utf8NoBom)
}

# Function to fix end-of-file issues (ensure there's exactly one newline at the end)
function Fix-EndOfFile {
    param([string]$filePath)

    Write-Host "Fixing end-of-file in $filePath"

    # Read all lines from the file
    $content = Get-Content -Path $filePath -Raw

    # Normalize line endings to LF
    $content = $content -replace '\r\n', "`n"

    # Ensure there's exactly one newline at the end
    $content = $content -replace '[\s\r\n]*$', "`n"

    # Write the content back to the file with LF line endings
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
}

# Find all text files in the repository, excluding binary files and certain directories
$files = Get-ChildItem -Recurse -File | Where-Object {
    # Check file extensions
    $_.Extension -match '\.(md|yaml|yml|json|ps1|sh|py|go|js|jsx|ts|tsx|css|scss|html|htm|xml|txt|conf|cfg|ini|toml|sql)$' -and
    # Exclude certain directories
    $_.FullName -notmatch '(\\node_modules\\|\\\.git\\|\\build\\|\\dist\\|\\venv\\)'
}

$fixedCount = 0

foreach ($file in $files) {
    # Skip binary files
    if ((Get-Item $file.FullName).Length -gt 1MB) {
        Write-Host "Skipping large file: $($file.FullName)"
        continue
    }

    try {
        # Check if file is binary by trying to read it as text
        $null = Get-Content -Path $file.FullName -Raw -ErrorAction Stop

        # Fix whitespace issues
        Fix-TrailingWhitespace -filePath $file.FullName
        Fix-EndOfFile -filePath $file.FullName
        $fixedCount++
    }
    catch {
        Write-Host "Skipping binary file: $($file.FullName)"
    }
}

Write-Host "Fixed $fixedCount files!"
