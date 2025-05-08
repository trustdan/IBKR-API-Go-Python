@echo off
SETLOCAL EnableDelayedExpansion

echo ===========================================
echo TraderAdmin Installer Build Script
echo ===========================================

REM Check if NSIS is installed and in PATH
where /q makensis.exe
if %ERRORLEVEL% neq 0 (
    echo NSIS is not found in your PATH. Please install NSIS and make sure it's in your PATH.
    echo You can download NSIS from https://nsis.sourceforge.io/Download
    goto :error
)

REM Check if Wails executable is available
where /q wails.exe
if %ERRORLEVEL% neq 0 (
    echo Wails is not found in your PATH.
    echo Please install Wails first: https://wails.io/docs/gettingstarted/installation
    goto :error
)

REM Check if LICENSE.txt exists
if not exist LICENSE.txt (
    echo Creating blank LICENSE.txt file...
    echo TraderAdmin - IBKR Auto Trader > LICENSE.txt
    echo MIT License >> LICENSE.txt
)

REM First, build the TraderAdmin app using Wails
echo Building TraderAdmin application...
cd TraderAdmin
wails build -trimpath -o TraderAdmin.exe
if %ERRORLEVEL% neq 0 (
    echo Error building TraderAdmin application.
    goto :error
)
cd ..

REM Build the installer
echo Building NSIS installer...
makensis.exe TraderAdmin-Installer.nsi
if %ERRORLEVEL% neq 0 (
    echo Error building NSIS installer.
    goto :error
)

echo Installer successfully built!
echo File created: TraderAdmin-Setup-1.0.0.exe
goto :end

:error
echo Build failed!
exit /b 1

:end
echo Done!
