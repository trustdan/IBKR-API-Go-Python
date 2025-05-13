@echo off
echo Building TraderAdmin for Windows...

:: Store current directory and move to project root
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%\..

:: Build Wails application
echo Building Wails application...
wails build -trimpath -ldflags="-s -w" -nsis

:: Check if build was successful
if not exist ".\build\bin\TraderAdmin.exe" (
    echo ERROR: Wails build failed! TraderAdmin.exe not found.
    exit /b 1
)

:: Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: NSIS not found! Please install NSIS to build the installer.
    echo You can download NSIS from https://nsis.sourceforge.io/Download
    exit /b 1
)

:: Create the installer using NSIS
echo Creating Windows installer...
makensis %SCRIPT_DIR%\windows_installer.nsi

:: Check if installer was created - NSIS outputs to script directory
if not exist "%SCRIPT_DIR%\TraderAdmin_Setup.exe" (
    echo ERROR: Installer creation failed! TraderAdmin_Setup.exe not found.
    exit /b 1
)

:: Move installer to project root
echo Moving installer to project root...
move "%SCRIPT_DIR%\TraderAdmin_Setup.exe" .\TraderAdmin_Setup.exe

:: Check if installer was moved successfully
if not exist "TraderAdmin_Setup.exe" (
    echo ERROR: Failed to move installer to project root.
    exit /b 1
)

echo Success! TraderAdmin Windows installer created at TraderAdmin_Setup.exe
echo You can now distribute this installer to users.
exit /b 0
