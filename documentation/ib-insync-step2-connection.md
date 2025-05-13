# IB Insync Implementation: Step 2 - Connection Management

## Introduction

This guide covers implementing connection management for the IB Insync API wrapper. We'll implement connection initialization, event handling, and proper disconnection.

## Event Handlers Setup

Add the following methods to `IBKRIBInsyncApi` class to handle events from TWS/Gateway:

```python
def _setup_event_handlers(self):
    """Set up event handlers for IB events."""
    
    # Handle connection status
    self.ib.connectedEvent += self._on_connected
    self.ib.disconnectedEvent += self._on_disconnected
    
    # Handle order status changes
    self.ib.orderStatusEvent += self._on_order_status
    
    # Handle execution details (fills)
    self.ib.execDetailsEvent += self._on_execution
    self.ib.commissionReportEvent += self._on_commission_report
    
    # Handle position updates
    self.ib.positionEvent += self._on_position
    
    # Error handling
    self.ib.errorEvent += self._on_error

def _on_connected(self):
    """Handle connection event."""
    self.connected = True
    log_info("Connection to IBKR established")

def _on_disconnected(self):
    """Handle disconnection events."""
    self.connected = False
    log_warning("Disconnected from IBKR")

def _on_order_status(self, trade):
    """Handle order status updates."""
    order_id = str(trade.order.orderId)
    
    with self.lock:
        if order_id in self.orders:
            order_info = self.orders[order_id]
            order_info["status"] = trade.orderStatus.status
            order_info["filled"] = trade.orderStatus.filled
            order_info["remaining"] = trade.orderStatus.remaining
            
            log_debug(f"Order {order_id} status: {trade.orderStatus.status}")

def _on_execution(self, trade, fill):
    """Handle order executions (fills)."""
    order_id = str(trade.order.orderId)
    
    with self.lock:
        if order_id in self.orders:
            order_info = self.orders[order_id]
            order_info["status"] = trade.orderStatus.status
            
            # Track the execution
            if "executions" not in order_info:
                order_info["executions"] = []
            
            order_info["executions"].append({
                "time": fill.execution.time,
                "shares": fill.execution.shares,
                "price": fill.execution.price,
                "execution_id": fill.execution.execId
            })
            
            log_info(f"Order {order_id} fill: {fill.execution.shares} shares at ${fill.execution.price:.2f}")

def _on_commission_report(self, trade, fill, report):
    """Handle commission reports."""
    order_id = str(trade.order.orderId)
    
    with self.lock:
        if order_id in self.orders:
            order_info = self.orders[order_id]
            
            # Update commission info
            if "commissions" not in order_info:
                order_info["commissions"] = []
            
            order_info["commissions"].append({
                "execution_id": report.execId,
                "commission": report.commission,
                "currency": report.currency,
                "realized_pnl": report.realizedPNL
            })

def _on_position(self, position):
    """Handle position updates."""
    with self.lock:
        symbol = position.contract.symbol
        
        if symbol not in self.positions:
            self.positions[symbol] = {
                "quantity": 0,
                "avg_price": 0,
                "market_price": 0,
                "market_value": 0,
                "unrealized_pnl": 0,
                "realized_pnl": 0,
                "account": position.account,
                "trades": []
            }
        
        # Update position
        self.positions[symbol]["quantity"] = position.position
        self.positions[symbol]["avg_price"] = position.avgCost
        
        # Try to get market price and value if available
        if hasattr(position, 'marketPrice') and not util.isNan(position.marketPrice):
            self.positions[symbol]["market_price"] = position.marketPrice
        
        if hasattr(position, 'marketValue') and not util.isNan(position.marketValue):
            self.positions[symbol]["market_value"] = position.marketValue
        
        log_debug(f"Position update: {symbol}, {position.position} shares, avg cost ${position.avgCost:.2f}")

def _on_error(self, reqId, errorCode, errorString, contract):
    """Handle error events."""
    if errorCode in (502, 504):  # Connection issues
        log_error(f"IBKR connection error: {errorString}")
        self.connected = False
    elif errorCode == 2104 or errorCode == 2106:  # Market data farm connection
        log_warning(f"IBKR market data warning: {errorString}")
    elif errorCode == 1100:  # Connection lost
        log_error("IBKR connection lost")
        self.connected = False
    elif errorCode == 1300:  # TWS or Gateway not running
        log_error("IBKR TWS/Gateway not running")
        self.connected = False
    else:
        log_error(f"IBKR error {errorCode}: {errorString}, reqId: {reqId}")
```

## Implement Connection and Disconnection

Add these methods to handle connection and disconnection:

```python
def connect(self) -> bool:
    """Connect to the IBKR TWS/Gateway.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        log_info(f"Connecting to IBKR at {self.host}:{self.port} with client ID {self.client_id}")
        
        # Connect to IB with timeout and retry logic
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                self.ib.connect(
                    host=self.host,
                    port=self.port,
                    clientId=self.client_id,
                    readonly=self.read_only,
                    account=self.account_id,
                    timeout=20  # 20 second timeout
                )
                break  # Connection successful
            except Exception as e:
                if attempt < max_attempts:
                    log_warning(f"Connection attempt {attempt} failed: {str(e)}. Retrying...")
                    time.sleep(2)  # Wait before retrying
                else:
                    raise  # Re-raise the exception if all attempts failed
        
        # Check if really connected
        if self.ib.isConnected():
            self.connected = True
            log_info("Successfully connected to IBKR")
            
            # Request account updates
            if self.account_id:
                self.ib.reqAccountUpdates(True, self.account_id)
            
            # Initialize managed accounts if account not specified
            if not self.account_id and self.ib.managedAccounts():
                self.account_id = self.ib.managedAccounts()[0]
                log_info(f"Using account: {self.account_id}")
            
            # Get the next valid order ID
            self.next_order_id = self.ib.client.getReqId()
            
            return True
        else:
            log_error("Failed to connect to IBKR")
            return False
    except Exception as e:
        log_error(f"Failed to connect to IBKR: {str(e)}")
        self.connected = False
        return False

def disconnect(self) -> None:
    """Disconnect from the IBKR TWS/Gateway."""
    try:
        if self.connected:
            # Cancel any subscriptions if needed
            # self.ib.cancelPositions()
            # self.ib.cancelAccountUpdates()
            
            self.ib.disconnect()
            log_info("Disconnected from IBKR")
            self.connected = False
    except Exception as e:
        log_error(f"Error disconnecting from IBKR: {str(e)}")
        self.connected = False

def handle_callbacks(self) -> None:
    """Process IB API callbacks.
    
    This should be called periodically to ensure the IB API works properly.
    """
    if self.connected:
        try:
            self.ib.sleep(0)  # Allow IB to process messages
        except Exception as e:
            log_error(f"Error handling callbacks: {str(e)}")
```

## Testing Connection Management

Create a file `tests/features/connection.feature` with Gherkin scenarios:

```gherkin
Feature: IBKR Connection Management
  As a trader
  I want to connect to IBKR TWS/Gateway
  So that I can interact with the trading platform

  Background:
    Given the IBKR TWS/Gateway is running
    And I have valid connection parameters

  Scenario: Successful connection to IBKR
    When I connect to IBKR
    Then the connection should be established
    And account information should be available

  Scenario: Failed connection to IBKR
    Given the IBKR TWS/Gateway is not running
    When I attempt to connect to IBKR
    Then the connection should fail
    And an appropriate error message should be logged

  Scenario: Disconnection from IBKR
    Given I am connected to IBKR
    When I disconnect from IBKR
    Then the connection should be terminated
    And the system should handle the disconnection gracefully
```

Create a test implementation at `tests/test_ibkr_connection.py`:

```python
import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import MagicMock, patch

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi

# Load scenarios from the feature file
scenarios('features/connection.feature')

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.IBKR_HOST = "127.0.0.1"
    config.IBKR_PORT = 7497
    config.IBKR_CLIENT_ID = 1
    return config

@pytest.fixture
def mock_ib():
    with patch('src.brokers.ibkr_ib_insync.IB') as mock_ib_class:
        mock_ib_instance = mock_ib_class.return_value
        mock_ib_instance.isConnected.return_value = True
        mock_ib_instance.managedAccounts.return_value = ["DU12345"]
        yield mock_ib_instance

@pytest.fixture
def api(mock_config, mock_ib):
    return IBKRIBInsyncApi(mock_config)

# Step definitions
@given("the IBKR TWS/Gateway is running")
def ibkr_running(mock_ib):
    mock_ib.isConnected.return_value = True

@given("the IBKR TWS/Gateway is not running")
def ibkr_not_running(mock_ib):
    mock_ib.connect.side_effect = Exception("Connection refused")
    mock_ib.isConnected.return_value = False

@given("I have valid connection parameters")
def valid_connection_parameters(mock_config):
    # Already set up in the mock_config fixture
    pass

@given("I am connected to IBKR")
def connected_to_ibkr(api, mock_ib):
    api.connected = True

@when("I connect to IBKR")
def connect_to_ibkr(api):
    api.connect()

@when("I attempt to connect to IBKR")
def attempt_connect(api):
    api.connect()

@when("I disconnect from IBKR")
def disconnect_from_ibkr(api):
    api.disconnect()

@then("the connection should be established")
def connection_established(api):
    assert api.connected is True

@then("account information should be available")
def account_info_available(api, mock_ib):
    assert api.account_id != ""

@then("the connection should fail")
def connection_failed(api):
    assert api.connected is False

@then("an appropriate error message should be logged")
def error_logged(caplog):
    # Check that an error was logged
    assert any("Failed to connect to IBKR" in record.message for record in caplog.records)

@then("the connection should be terminated")
def connection_terminated(api):
    assert api.connected is False

@then("the system should handle the disconnection gracefully")
def disconnection_handled(api, mock_ib):
    # Check that disconnect was called
    mock_ib.disconnect.assert_called_once()
```

## Testing

Run the tests using pytest:

```bash
pytest tests/test_ibkr_connection.py -v
```

## Next Steps

After implementing connection management, proceed to [Step 3](ib-insync-step3-market-data.md) to implement market data retrieval functionality. 