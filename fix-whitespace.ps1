#!/usr/bin/env pwsh

$textExtensions = @(
    ".py", ".go", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss",
    ".md", ".txt", ".yml", ".yaml", ".json", ".toml", ".xml", ".sh",
    ".bat", ".ps1", ".nsi", ".sql", ".cfg", ".conf", ".ini"
)

$excludeDirs = @(
    ".git", "node_modules", "venv", "env", "__pycache__",
    "dist", "build", "bin", "obj", "target", "Debug", "Release"
)

function Should-ProcessFile {
    param (
        [string]$filePath
    )

    $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
    if ($textExtensions -notcontains $extension) {
        return $false
    }

    foreach ($dir in $excludeDirs) {
        if ($filePath -match [regex]::Escape($dir)) {
            return $false
        }
    }

    return $true
}

function Fix-FileEndings {
    param (
        [string]$filePath
    )

    try {
        $content = Get-Content -Path $filePath -Raw
        if ($null -eq $content) {
            return $false
        }

        # Fix line endings to LF and remove trailing whitespace
        $newContent = $content -replace "`r`n", "`n"
        $newContent = $newContent -replace "[ `t]+`n", "`n"
        $newContent = $newContent.TrimEnd() + "`n"

        if ($content -ne $newContent) {
            [System.IO.File]::WriteAllText($filePath, $newContent)
            Write-Host "Fixed: $filePath"
            return $true
        }

        return $false
    }
    catch {
        Write-Error "Error processing $filePath`: $_"
        return $false
    }
}

$modifiedCount = 0
$examinedCount = 0

Get-ChildItem -Path . -Recurse -File | ForEach-Object {
    $filePath = $_.FullName
    if (Should-ProcessFile $filePath) {
        $examinedCount++
        if (Fix-FileEndings $filePath) {
            $modifiedCount++
        }
    }
}

Write-Host "`nExamined $examinedCount files"
Write-Host "Modified $modifiedCount files"
