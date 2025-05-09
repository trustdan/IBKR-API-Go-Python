@echo off
REM Build script for TraderAdmin installer

echo.
echo Building TraderAdmin installer...
echo.

REM Ensure we have the latest version
powershell -ExecutionPolicy Bypass -File "%~dp0version-extract.ps1" > "%TEMP%\version.txt"
set /p VERSION=<"%TEMP%\version.txt"
echo Using version: %VERSION%

REM Check if NSIS is installed
where makensis >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo NSIS not found. Please install NSIS and make sure it's in your PATH.
    exit /b 1
)

REM Check if Wails is installed
where wails >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Wails not found. Please install Wails and make sure it's in your PATH.
    exit /b 1
)

REM Build the TraderAdmin application
echo Building TraderAdmin with Wails...
cd /d "%~dp0TraderAdmin"
wails build -trimpath -o TraderAdmin.exe
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build TraderAdmin.
    exit /b 1
)
cd /d "%~dp0"

REM Check if LICENSE.txt exists, create it if not
if not exist "LICENSE.txt" (
    echo Creating blank LICENSE.txt file...
    echo TraderAdmin - IBKR Auto Trader > LICENSE.txt
    echo MIT License >> LICENSE.txt
)

REM Build the NSIS installer
echo Building NSIS installer...
makensis TraderAdmin-Installer.nsi
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build NSIS installer.
    exit /b 1
)

echo.
echo Build completed successfully! 
echo Installer: TraderAdmin-Setup-%VERSION%.exe
echo.

exit /b 0
