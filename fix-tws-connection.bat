@echo off
:: ===========================================================================
:: Interactive Brokers TWS API Connection Fix Tool
:: 
:: This batch file runs the sequence of troubleshooting tools to 
:: diagnose and fix TWS API connectivity issues.
:: ===========================================================================

echo.
echo ===================================================================
echo   INTERACTIVE BROKERS TWS API CONNECTION TROUBLESHOOTER
echo ===================================================================
echo.
echo This tool will help fix connectivity issues between your app and TWS
echo.
echo Prerequisites:
echo - Make sure TWS or IB Gateway is running and logged in
echo - You might need to run this script as Administrator 
echo   (for firewall rule changes)
echo.
echo Press any key to start the diagnosis...
pause > nul

:: Create tools directory if it doesn't exist
if not exist tools mkdir tools

:: Check if we're running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: This script is NOT running as Administrator
    echo          Some fixes may not be applied
    echo.
    echo Press any key to continue anyway, or CTRL+C to stop and restart as admin...
    pause > nul
)

:: Step 1: Basic connection check
echo.
echo ===================================================================
echo STEP 1: Checking TWS API Connection
echo ===================================================================
python tools\check_tws_connection.py
echo.
echo Press any key to continue to the next step...
pause > nul

:: Step 2: TWS Connectivity Fix (Windows firewall rules)
echo.
echo ===================================================================
echo STEP 2: Fixing Windows Firewall Rules
echo ===================================================================
python tools\tws_connectivity_fix.py --apply
echo.
echo Press any key to continue to the next step...
pause > nul

:: Step 3: Try to connect directly with ib_insync
echo.
echo ===================================================================
echo STEP 3: Testing Direct Connection
echo ===================================================================
echo This may take a few minutes as we try multiple configurations...
echo.
python tools\test_ibinsync_direct.py --try-all
set CONNECTION_RESULT=%errorlevel%

:: Step 4: Verify config settings
echo.
echo ===================================================================
echo STEP 4: Verifying Configuration Settings
echo ===================================================================
python tools\verify_api_config.py
echo.

:: Final summary
echo.
echo ===================================================================
echo TROUBLESHOOTING COMPLETE
echo ===================================================================
echo.
if %CONNECTION_RESULT% equ 0 (
    echo SUCCESS! A working connection configuration was found.
    echo.
    echo Please update your config.yaml with the recommended settings
    echo shown above and restart your application.
) else (
    echo No working connection configuration was found.
    echo.
    echo Additional troubleshooting steps:
    echo 1. Make sure TWS is fully started and the API is enabled
    echo 2. Try restarting your computer
    echo 3. Check your TWS API settings again:
    echo    - Edit ^> Global Configuration ^> API ^> Settings
    echo    - Make sure "Enable ActiveX and Socket Clients" is checked
    echo 4. Consider reinstalling TWS/IB Gateway
    echo 5. Contact Interactive Brokers support if problems persist
)
echo.
echo Press any key to exit...
pause > nul 