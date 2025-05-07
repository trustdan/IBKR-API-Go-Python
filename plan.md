Here's a robust, structured implementation plan for your **Auto Vertical Spread Trader** project, aligning your original intentions (behavior, parameters, architecture) and recent decision to pivot towards a Python and Go hybrid system. We'll integrate your provided roadmap and add specific Cucumber/Gherkin scenarios and detailed pseudocode to clearly guide implementation.

---

## Comprehensive Implementation Plan (with Cucumber & Pseudocode)

### **1. Objectives & Refined Architecture**

* Python orchestrator for business logic, config, and API interactions.
* Go service for high-performance scanning using concurrent routines.
* API Contract defined clearly via gRPC/Protobuf.

```plaintext
[ Market Data/API ] Ã¢â€ â€ [ Python Orchestrator ] Ã¢â€ ÂgRPCÃ¢â€ â€™ [ Go Scanner Service ]
                                Ã¢â€ â€œ
                         [ IBKR API / Order Management ]
```

---

### **2. Greenfield Python Orchestrator (Phase 1)**

#### Repo & Setup

* Initialize Git repo
* Setup with Poetry (`pyproject.toml`)
* CI with pytest, black, mypy

#### Cucumber Example for Initial Setup:

```gherkin
Feature: Python Orchestrator Initialization
  Scenario: Clean repo setup
    Given a fresh Python repository
    When I run poetry install
    Then all dependencies are installed without errors
    And black and mypy pass without warnings
```

#### Pseudocode (StrategyEngine):

```python
class StrategyEngine:
    def __init__(self, config):
        self.config = config

    def compute_indicators(self, df):
        df['ATR14'] = df.ta.atr(length=14)
        df['RSI14'] = df.ta.rsi(length=14)
        return df

    def generate_signals(self, df):
        signals = []
        for row in df.itertuples():
            if row.close > row.ATR14 * self.config.HIGH_BASE_MAX_ATR_RATIO:
                signals.append(('LONG', row.symbol))
        return signals
```

---

### **3. API Contract & IDL (Phase 2)**

#### Protobuf IDL Definition:

```proto
syntax = "proto3";

service ScannerService {
  rpc Scan (ScanRequest) returns (ScanResponse);
}

message DateRange {
  string start_date = 1;
  string end_date = 2;
}

message ScanRequest {
  repeated string symbols = 1;
  DateRange date_range = 2;
}

message ScanResponse {
  map<string, SignalList> signals = 1;
}

message SignalList {
  repeated string signal_types = 1; // ["LONG", "SHORT"]
}
```

---

### **4. Go Scanner Implementation (Phase 3)**

#### Cucumber for Go Scanner:

```gherkin
Feature: Concurrent Go Scanner
  Scenario: Scan multiple symbols concurrently
    Given I have a running Go scanner service
    When I send symbols ["AAPL", "MSFT", "TSLA"]
    Then the response includes signals for all symbols within 2 seconds
```

#### Go Pseudocode (Concurrent Scanner Logic):

```go
func (s *ScannerService) Scan(req *scannerpb.ScanRequest) (*scannerpb.ScanResponse, error) {
	var wg sync.WaitGroup
	signals := make(map[string]*scannerpb.SignalList)
	var mu sync.Mutex

	for _, symbol := range req.Symbols {
		wg.Add(1)
		go func(sym string) {
			defer wg.Done()
			data := LoadMarketData(sym)
			signalTypes := EvaluateStrategies(data)
			mu.Lock()
			signals[sym] = &scannerpb.SignalList{SignalTypes: signalTypes}
			mu.Unlock()
		}(symbol)
	}

	wg.Wait()
	return &scannerpb.ScanResponse{Signals: signals}, nil
}
```

---

### **5. Integration: Python Ã¢â€ â€ Go (Phase 4)**

#### Python gRPC Client Stub Pseudocode:

```python
class ScannerClient:
    def __init__(self, channel):
        self.stub = ScannerServiceStub(channel)

    def scan(self, symbols, date_range):
        request = ScanRequest(symbols=symbols, date_range=date_range)
        response = self.stub.Scan(request)
        return response.signals
```

---

### **6. Universe Management & Filtering**

#### Cucumber scenario:

```gherkin
Feature: Universe Filtering
  Scenario: Select tradable stocks
    Given the S&P 500 universe data
    When I filter by MIN_MARKET_CAP, MIN_PRICE, MIN_VOLUME
    Then all returned stocks have cap Ã¢â€°Â¥ $10B, price > $20, volume Ã¢â€°Â¥ 1M
```

#### Pseudocode (Universe Filter):

```python
def filter_universe(stocks, config):
    filtered = []
    for stock in stocks:
        if stock.market_cap >= config.MIN_MARKET_CAP and \
           stock.price > config.MIN_PRICE and \
           stock.daily_volume >= config.MIN_VOLUME and \
           stock.is_optionable:
            filtered.append(stock)
    return filtered
```

---

### **7. Trade Execution & Risk Management**

#### Cucumber scenario:

```gherkin
Feature: ATR-based Risk Management
  Scenario: Stop-loss triggered
    Given an open vertical spread on AAPL
    And an ATR-based stop-loss at 2 Ãƒâ€” ATR
    When price reaches the stop-loss level
    Then the system exits the trade automatically
    And sends a notification alerting me
```

#### Pseudocode (Risk Management):

```python
def monitor_stop_loss(position, market_data, config):
    atr_stop_loss = position.entry_price - (market_data.ATR14 * config.STOP_LOSS_ATR_MULT)
    if market_data.current_price <= atr_stop_loss:
        exit_trade(position)
        send_alert(f"Stop-loss triggered for {position.symbol}")
```

---

### **8. Deployment & CI/CD (Phase 6)**

* GitHub Actions for automatic build/test/deploy:

  * Run unit tests
  * Integration tests with Docker Compose
  * Publish Docker images

---

### **9. Monitoring, Logging & Observability (Phase 7)**

* Structured JSON logging (Python and Go)
* Prometheus metrics for performance and availability
* Health-check endpoints (`/health`)

---

### **10. Rollout Roadmap (Detailed)**

* **Weeks 1-2**:

  * Repo setup, Python orchestrator base, API definition
* **Weeks 3-4**:

  * Go scanner MVP, concurrency
  * Docker Compose local integration
* **Weeks 5-6**:

  * Full risk management integration
  * CI/CD pipeline in place
* **Weeks 7-8**:

  * Monitoring/logging observability
  * Production readiness & final tests

---

### **11. Future Extensions (Next Steps)**

* Performance optimizations (parallel scanning, caching)
* Expand strategies (momentum, earnings-based volatility)
* Enhanced reporting dashboards, SMS/Slack notifications
* Comprehensive backtesting framework

---

### **Key Technical Choices Reaffirmed**:

* pandas-ta (no C/C++ dependencies)
* Go (for concurrency and performance)
* Protobuf/gRPC (robust typed interfaces)

---

This structured approach sets clear expectations, enabling your development team to build maintainable, robust software aligned with your original intentions and recent decisions. Let me know if you'd like further detail on any phase!
