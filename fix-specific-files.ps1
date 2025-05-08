#!/usr/bin/env pwsh

$filesToFix = @(
    "trader-admin\TraderAdmin-Installer.nsi",
    "trader-admin\TraderAdmin\frontend\src\components\SystemStatus.svelte",
    ".github\workflows\ci.yml",
    "trader-admin\LICENSE.txt",
    "trader-admin\TraderAdmin\frontend\package.json.md5",
    "trader-admin\TraderAdmin\frontend\wailsjs\runtime\runtime.js",
    "trader-admin\TraderAdmin\frontend\wailsjs\runtime\runtime.d.ts",
    "trader-admin\TraderAdmin\frontend\src\App.svelte",
    "trader-admin\TraderAdmin\frontend\wailsjs\go\models.ts"
)

function Fix-FileEndings {
    param (
        [string]$filePath
    )

    try {
        Write-Host "Processing: $filePath"

        # Read file content as bytes to preserve encoding
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $content = [System.Text.Encoding]::UTF8.GetString($bytes)

        if ($null -eq $content) {
            Write-Host "Empty file: $filePath"
            return $false
        }

        # Fix line endings to LF and remove trailing whitespace
        $newContent = $content -replace "`r`n", "`n"  # Convert CRLF to LF
        $newContent = $newContent -replace "`r", "`n"  # Convert any remaining CR to LF

        # Split into lines, trim trailing whitespace, and rejoin
        $lines = $newContent -split "`n"
        $lines = $lines | ForEach-Object { $_.TrimEnd() }
        $newContent = [String]::Join("`n", $lines)

        # Ensure single newline at end
        $newContent = $newContent.TrimEnd() + "`n"

        if ($content -ne $newContent) {
            # Write content back as UTF-8 without BOM
            $utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($filePath, $newContent, $utf8NoBomEncoding)
            Write-Host "Fixed: $filePath"
            return $true
        }

        Write-Host "No changes needed: $filePath"
        return $false
    }
    catch {
        Write-Error "Error processing $filePath`: $_"
        return $false
    }
}

$modifiedCount = 0

foreach ($file in $filesToFix) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        if (Fix-FileEndings $fullPath) {
            $modifiedCount++
        }
    } else {
        Write-Warning "File not found: $fullPath"
    }
}

Write-Host "`nModified $modifiedCount files"
