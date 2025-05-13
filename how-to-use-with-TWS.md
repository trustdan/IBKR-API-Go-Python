# Enhanced Setup Guide for TraderAdmin with Interactive Brokers

This document provides comprehensive guidance for setting up and operating the TraderAdmin application with Interactive Brokers (IBKR) Trader Workstation (TWS) or IB Gateway.

## Prerequisites

* **Interactive Brokers Account**:
  * IBKR Pro account (live or paper trading)
  * Latest stable release of TWS or IB Gateway
  * Ensure Java is installed as both TWS and IB Gateway are Java applications
* **Software Requirements**:
  * Docker Desktop (preferred) or manual setup using Python 3.8+ and Go 1.20+

## Step-by-Step Setup and Operation

### Step 1: Install and Configure TWS or IB Gateway (CRITICAL)

1. **Download Software**:
   * [Trader Workstation (TWS)](https://www.interactivebrokers.com/en/trading/tws.php)
   * [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)

2. **Run Application**:
   * Launch TWS or IB Gateway. You'll need to log in manually.

3. **Configure API Access (Essential Settings)**:
   * Navigate to **Edit > Global Configuration > API > Settings**:
     * Check **"Enable ActiveX and Socket Clients"**.
     * Uncheck **"Read-Only API"** unless you only want read-only functionality.
     * Set the **Socket Port** (default: 7497 for paper, 7496 for live).
     * **Critical:** Enter "1" in the **Master API client ID** field (or match this with client_id_trading in config).
     * Check **"Allow connections from localhost only"** if running locally.
     * Click **Apply** then **OK**

4. **Configure API Precautions**:
   * Navigate to **API > Precautions**:
     * Check **"Bypass Order Precautions for API Orders"** to avoid confirmation dialogs.
     * Click **Apply** then **OK**

5. **Restart TWS After Configuration**:
   * Close TWS completely
   * Restart TWS and log in again to ensure all settings take effect

### Step 2: Set Up the TraderAdmin Application

1. **Create Configuration File**:
   * Copy the template configuration file:
   ```bash
   cp config/config.template.toml config/config.toml
   ```

2. **Edit Configuration**:
   * Open config/config.toml and update the following:
   ```toml
   [ibkr_connection]
     host = "127.0.0.1"
     port = 7497  # Must match the port in TWS settings
     client_id_trading = 1  # Must match Master API client ID in TWS
     client_id_data = 2
     account_code = "YOUR_ACCOUNT_CODE"  # Replace with your actual IBKR account code
   ```

3. **Finding Your Account Code**:
   * Look at the top of your TWS window for your account code
   * Paper trading accounts typically start with "DU" (e.g., "DUE722383")
   * Live accounts typically start with "U"
   * Use this exact account code in your configuration

### Step 3: Start the Docker Services

1. **Ensure Docker is Running**:
   ```powershell
   docker info
   ```

2. **Create Docker Network (First Time Only)**:
   ```powershell
   docker network create vertical-spread-network
   ```

3. **Clean Up Any Existing Containers**:
   ```powershell
   docker rm -f vertical-spread-go vertical-spread-python 2>$null
   ```

4. **Start Services**:
   ```powershell
   .\run-local.ps1
   ```

5. **Verify Services**:
   ```powershell
   docker ps
   ```
   You should see two containers running:
   - vertical-spread-go
   - vertical-spread-python

### Step 4: Launch the TraderAdmin Application

1. **Launch the Application**:
   ```powershell
   Start-Process "C:\Users\<username>\IBKR-trader\build\bin\TraderAdmin-dev.exe"
   ```

2. **Connect to TWS**:
   * In the TraderAdmin application, go to the Connection tab
   * Verify all settings match your config file:
     - Host: 127.0.0.1
     - Port: 7497
     - Account Code: Your account code (e.g., DUE722383)
     - Client IDs: 1 and 2 (or whatever values you set)
   * Click "Connect to Interactive Brokers TWS/Gateway"

### Troubleshooting Connection Issues

If you experience connection problems:

1. **TWS API Settings**:
   * Make sure the Master API client ID is not blank (set to 1 or another number)
   * Ensure "Enable ActiveX and Socket Clients" is checked
   * Verify the port number matches your configuration (typically 7497)

2. **Account Code**:
   * Double-check that your account code in config.toml exactly matches your IBKR account

3. **Complete Restart Sequence**:
   * Close TraderAdmin
   * Close TWS/Gateway
   * Start TWS/Gateway and log in completely
   * Start TraderAdmin again
   * Try connecting

4. **Client ID Conflicts**:
   * If standard client IDs (1 and 2) don't work, try different values (e.g., 123 and 124)
   * Update both TWS settings and your config.toml file
   * Restart both applications

5. **Check TWS Message Center**:
   * Look for API connection messages or errors
   * Check if your connection is being rejected for any reason

### Additional Notes

* Restart TWS or IB Gateway weekly or enable auto-restart settings to prevent downtime.
* Always ensure TWS is fully started before launching TraderAdmin.
* The Docker containers provide essential market data services for the application.
* For paper trading, ensure your IBKR account has market data subscriptions.

## Conclusion

By following these steps, you can seamlessly integrate the TraderAdmin application with IBKR's TWS or IB Gateway for automated trading operations.
