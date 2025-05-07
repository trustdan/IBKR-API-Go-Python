# PowerShell script to fix whitespace and end-of-file issues

# Function to fix trailing whitespace in a file
function Fix-TrailingWhitespace {
    param([string]$filePath)

    Write-Host "Fixing trailing whitespace in $filePath"

    # Read all lines from the file
    $content = Get-Content -Path $filePath -Raw

    # Replace trailing whitespace with nothing
    $newContent = $content -replace '[ \t]+$', '' -replace '\r\n', "`n"

    # Write the content back to the file with proper line endings
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($filePath, $newContent, $utf8NoBom)
}

# Function to fix end-of-file issues (ensure there's exactly one newline at the end)
function Fix-EndOfFile {
    param([string]$filePath)

    Write-Host "Fixing end-of-file in $filePath"

    # Read all lines from the file
    $content = Get-Content -Path $filePath -Raw

    # Ensure there's exactly one newline at the end
    $content = $content -replace '[^\S\r\n]*$', ''
    if (-not $content.EndsWith("`n")) {
        $content += "`n"
    }

    # Write the content back to the file with proper line endings
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
}

# Find all text files in the repository
$files = Get-ChildItem -Recurse -File | Where-Object {
    $_.Extension -match '\.(md|yaml|yml|json|ps1|sh|py|go|js|jsx|ts|tsx|css|scss|html|htm|xml|txt|conf|cfg|ini|toml|sql)$'
}

foreach ($file in $files) {
    Fix-TrailingWhitespace -filePath $file.FullName
    Fix-EndOfFile -filePath $file.FullName
}

Write-Host "All files fixed!"
