# Enhanced README for Auto Vertical Spread Trader

This document provides clear guidance for setting up and operating the Auto Vertical Spread Trader, focusing on practical integration with Interactive Brokers (IBKR) Trader Workstation (TWS) or IB Gateway.

## Prerequisites

* **Interactive Brokers Account**:

  * IBKR Pro account (live or paper trading)
  * Latest stable release of TWS or IB Gateway
  * Ensure Java is installed as both TWS and IB Gateway are Java applications
* **Software Requirements**:

  * Docker Desktop (preferred) or manual setup using Python 3.8+ and Go 1.20+

## Step-by-Step Setup and Operation

### Step 1: Install and Configure TWS or IB Gateway

1. **Download Software**:

   * [Trader Workstation (TWS)](https://www.interactivebrokers.com/en/trading/tws.php)
   * [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)

2. **Run Application**:

   * Launch TWS or IB Gateway. You'll need to log in manually.

3. **Configure API Access**:

   * Navigate to **Edit > Global Configuration > API > Settings**:

     * Check **"Enable ActiveX and Socket Clients"**.
     * Uncheck **"Read-Only API"**.
     * Note the **Socket Port** (default: 7497 for paper, 7496 for live).

4. **Security and Stability**:

   * Navigate to **Lock and Exit** settings:

     * Set **"Never Lock Trader Workstation"** and **"Auto restart"** to ensure uninterrupted connection.
   * Navigate to **API > Precautions** and enable bypass options relevant to your use case.

### Step 2: Clone and Configure the Trading Application

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/trustdan/auto-vertical-spread-trader.git
   cd auto-vertical-spread-trader
   ```

2. **Configure Application**:

   * Copy `config.yaml.example` to `config.yaml`.
   * Set your IBKR socket port and other strategy parameters in `config.yaml`.

Example configuration snippet:

```yaml
IBKR:
  host: 127.0.0.1
  port: 7497  # Paper trading port
  clientId: 1
```

### Step 3: Run the Trading Application

#### Using Docker (Recommended)

* **Run Docker containers**:

  ```bash
  ./run-local.sh
  ```

* Services are accessible at:

  * Go scanner: [http://localhost:50051](http://localhost:50051)
  * Python orchestrator: [http://localhost:8000](http://localhost:8000)

#### Manual Installation

* **Install Python and Go dependencies**:

```bash
# Python dependencies
cd python
poetry install  # or pip install -r requirements.txt

# Go dependencies
cd ../go
go mod download
```

* **Run Python orchestrator**:

  ```bash
  cd python
  python src/run_trader.py trade --symbols symbols.txt --config config.yaml
  ```

* **Run Go scanner**:

  ```bash
  cd ../go
  go run cmd/scanner/main.go
  ```

### Step 4: Operating Instructions

* **Ensure TWS/IB Gateway is running before launching your trader.**
* Verify connectivity using the logs or interface provided by the orchestrator.
* Adjust strategies and risk parameters dynamically via the configuration file (`config.yaml`). Restart your trader to apply changes.

### Step 5: Monitoring and Logging

* View Docker logs:

  ```bash
  docker logs vertical-spread-go -f
  docker logs vertical-spread-python -f
  ```

* Monitor trades and system status via orchestrator UI (`http://localhost:8000`) or logs if running manually.

### Additional Notes

* Restart TWS or IB Gateway weekly or enable auto-restart settings to prevent downtime.
* Use pre-commit hooks (`pre-commit run --all-files`) to maintain code quality.

## Conclusion

By following these steps, you can seamlessly integrate the Auto Vertical Spread Trader with IBKR's TWS or IB Gateway for efficient and automated vertical spread trading.
