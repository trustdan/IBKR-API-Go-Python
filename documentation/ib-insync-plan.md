# IB Insync Implementation Plan

## Overview

This document outlines a plan to integrate the `ib_insync` library as a replacement for the current placeholder implementation in our IBKR trading application. The `ib_insync` library provides a more powerful, Pythonic interface to the Interactive Brokers API compared to the official IBAPI, with better support for async operations and event handling.

### Why ib_insync?

1. **Simplicity**: ib_insync wraps the official IB API with a more intuitive interface
2. **Event-driven architecture**: Simplifies handling of asynchronous events like trades, executions, and market data
3. **Built-in error handling**: Better error handling and connection management
4. **Request throttling**: Automatically handles API request rate limitations
5. **Pythonic approach**: Uses Python idioms and modern async patterns for cleaner code
6. **Active maintenance**: Regularly updated with frequent fixes and community support
7. **Comprehensive functionality**: Full support for options, spreads, and complex order types

## Current State

- The application has a placeholder `IBKRApi` class in `src/brokers/ibkr_api.py` with simulated behavior
- Current implementation mocks API interactions rather than making actual connections to IBKR
- The current structure uses a well-defined interface that should be preserved
- Existing methods include:
  - Connection management (`connect()`, `disconnect()`)
  - Order placement (`place_order()`)
  - Market data retrieval (`get_market_data()`)
  - Account information (`get_account_summary()`, `get_positions()`)
  - Order management (`get_order_status()`, `cancel_order()`)
  - Option chain retrieval (`get_option_chain()`)
- The application architecture is modular with good separation of concerns, making it suitable for this integration

## Implementation Goals

1. **Maintain API Compatibility**: Replace placeholder with `ib_insync`-based implementation while preserving the existing interface
2. **Real-time Capability**: Implement proper connection, subscription, and event handling for reliable real-time data
3. **Robust Error Handling**: Develop comprehensive error handling and recovery mechanisms for connection issues
4. **Transaction Support**: Implement accurate order execution and monitoring with proper fill handling
5. **Market Data Integration**: Support real-time option chain retrieval and market data functions
6. **Account Management**: Add proper account, position and portfolio tracking
7. **Testing Coverage**: Create comprehensive unit and integration tests for the implementation
8. **Documentation**: Update documentation with implementation details and usage guidelines
9. **Production Readiness**: Ensure reliability for both paper trading and live trading environments

## Behavior-Driven Development Approach

We'll use Behavior-Driven Development (BDD) with Cucumber/Gherkin scenarios to define the expected behavior of each component. This approach will:

1. **Define Clear Requirements**: Express functionality in plain language before implementation
2. **Guide Development**: Use scenarios as a roadmap for implementation
3. **Enable Validation**: Scenarios become automated acceptance tests
4. **Improve Communication**: Provide clear documentation for both technical and non-technical stakeholders

Each major component of the implementation will have:
- Gherkin scenarios defining expected behavior
- Unit tests verifying implementation
- Integration tests confirming real-world behavior

## Dependencies

```
# Core dependencies
ib_insync>=0.9.86
pytz>=2023.3

# Testing dependencies
pytest>=7.4.0
pytest-mock>=3.11.1
pytest-cov>=4.1.0
pytest-bdd>=7.0.0  # For Cucumber/Gherkin style tests
```

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.9"
ib_insync = "^0.9.86"
pytz = "^2023.3"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-mock = "^3.11.1"
pytest-cov = "^4.1.0"
pytest-bdd = "^7.0.0"
```

## Implementation Plan

### Phase 1: Basic Setup

**Gherkin Scenario - Connection Management:**
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

#### 1. Install Dependencies

```bash
pip install ib_insync>=0.9.86 pytz>=2023.3
pip install pytest>=7.4.0 pytest-mock>=3.11.1 pytest-cov>=4.1.0 pytest-bdd>=7.0.0
```

#### 2. Create IB Insync Wrapper Class

Create a new implementation that maintains the same interface:

```python
# src/brokers/ibkr_ib_insync.py
from typing import Any, Dict, List, Optional, Tuple
import threading
import time
from datetime import datetime, date

from ib_insync import IB, util
from ib_insync import Contract, Stock, Option as IBOption, ComboLeg, TagValue
from ib_insync import Order, LimitOrder, MarketOrder
from ib_insync import Ticker, Trade, Position as IBPosition
import pytz

from src.app.config import Config
from src.models.option import Option, OptionSpread
from src.utils.logger import log_debug, log_error, log_info, log_warning


class IBKRIBInsyncApi:
    """Implementation of IBKR API using ib_insync library."""
    
    def __init__(self, config: Config):
        """Initialize the IBKR API client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.connected = False
        
        # Connection details
        self.host = config.IBKR_HOST if hasattr(config, "IBKR_HOST") else "127.0.0.1"
        self.port = config.IBKR_PORT if hasattr(config, "IBKR_PORT") else 7497
        self.client_id = config.IBKR_CLIENT_ID if hasattr(config, "IBKR_CLIENT_ID") else 1
        self.account_id = config.IBKR_ACCOUNT_ID if hasattr(config, "IBKR_ACCOUNT_ID") else ""
        self.read_only = config.IBKR_READ_ONLY if hasattr(config, "IBKR_READ_ONLY") else False
        
        # Create IB instance
        self.ib = IB()
        
        # Order tracking
        self.next_order_id = 1
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, Dict[str, Any]] = {}

        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Setup event handlers
        self._setup_event_handlers()
    
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
                    "trades": []
                }
            
            self.positions[symbol]["quantity"] = position.position
            self.positions[symbol]["avg_price"] = position.avgCost
            
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

#### 3. Implement Connection Management

```python
def connect(self) -> bool:
    """Connect to the IBKR TWS/Gateway.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        log_info(f"Connecting to IBKR at {self.host}:{self.port} with client ID {self.client_id}")
        
        # Connect to IB with timeout
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
            
            # Initialize managed accounts
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

#### 4. Update Factory Method in `__init__.py`

```python
# src/brokers/__init__.py
"""
Brokers module for interacting with various trading platforms.
"""

from src.brokers.ibkr_api import IBKRApi
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi

def get_broker_api(config, use_ib_insync=True):
    """Factory method to get the appropriate broker API implementation.
    
    Args:
        config: Application configuration
        use_ib_insync: Whether to use the ib_insync implementation
        
    Returns:
        An instance of the appropriate broker API
    """
    if use_ib_insync:
        return IBKRIBInsyncApi(config)
    else:
        return IBKRApi(config)

__all__ = ["IBKRApi", "IBKRIBInsyncApi", "get_broker_api"]
```

#### 5. Create Basic Test Infrastructure

```python
# tests/features/connection.feature
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

Create the test implementation:

```python
# tests/test_ibkr_connection.py
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

@then("the connection should be terminated")
def connection_terminated(api):
    assert api.connected is False

@then("the system should handle the disconnection gracefully")
def disconnection_handled(api, mock_ib):
    # Check that disconnect was called
    mock_ib.disconnect.assert_called_once()
```

### Phase 2: Order Management Implementation

**Gherkin Scenario - Order Placement:**
```gherkin
Feature: IBKR Order Management
  As a trader
  I want to place, monitor, and cancel option spread orders
  So that I can execute my trading strategy effectively

  Background:
    Given I am connected to IBKR
    And I have a valid option spread for AAPL

  Scenario: Place a limit order for a bull call spread
    When I place a limit order for 1 contract
    Then the order should be submitted successfully
    And the order status should be tracked

  Scenario: Place a market order for a bear put spread
    When I place a market order for 2 contracts
    Then the order should be submitted successfully
    And the order should be filled at market price

  Scenario: Cancel an open order
    Given I have placed a limit order
    And the order is not yet filled
    When I cancel the order
    Then the order should be cancelled successfully

  Scenario: Handle order rejection
    Given the market is closed
    When I place a market order for 1 contract
    Then the order should be rejected
    And an appropriate error message should be logged
```

#### 1. Implement Order Management Methods

```python
def get_next_order_id(self) -> int:
    """Get the next available order ID.
    
    Returns:
        Next order ID
    """
    with self.lock:
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id

def place_order(
    self,
    symbol: str,
    direction: str,
    contracts: int,
    option_spread: OptionSpread,
    price_type: str = "LIMIT",
    limit_price: Optional[float] = None,
) -> str:
    """Place an option spread order.
    
    Args:
        symbol: Underlying symbol
        direction: Trade direction ("LONG" or "SHORT")
        contracts: Number of contracts to trade
        option_spread: The option spread to trade
        price_type: Order type ("MARKET" or "LIMIT")
        limit_price: Limit price if price_type is "LIMIT"
        
    Returns:
        Order ID string
        
    Raises:
        ValueError: If not connected or invalid parameters
        RuntimeError: If order placement fails
    """
    if not self.connected:
        raise ValueError("Not connected to IBKR")
    
    # Validate parameters
    if contracts <= 0:
        raise ValueError(f"Invalid number of contracts: {contracts}")
    
    if price_type == "LIMIT" and limit_price is None:
        raise ValueError("Limit price required for LIMIT orders")
    
    try:
        # Create contract objects for legs
        expiry = option_spread.expiration.strftime("%Y%m%d")
        
        # Create contracts based on spread type and direction
        if option_spread.spread_type == "BULL_CALL":
            # For bull call spread: Buy lower strike call, sell higher strike call
            long_option_type = 'C'
            short_option_type = 'C'
            long_strike = option_spread.long_leg.strike
            short_strike = option_spread.short_leg.strike
        elif option_spread.spread_type == "BEAR_PUT":
            # For bear put spread: Buy higher strike put, sell lower strike put
            long_option_type = 'P'
            short_option_type = 'P'
            long_strike = option_spread.long_leg.strike
            short_strike = option_spread.short_leg.strike
        else:
            raise ValueError(f"Unsupported spread type: {option_spread.spread_type}")
        
        # Create option contracts
        long_contract = IBOption(
            symbol, 
            expiry, 
            long_strike, 
            long_option_type,
            exchange='SMART', 
            currency='USD'
        )
        
        short_contract = IBOption(
            symbol, 
            expiry, 
            short_strike, 
            short_option_type,
            exchange='SMART', 
            currency='USD'
        )
        
        # Qualify the contracts to get their conIds
        try:
            qualified_long = self.ib.qualifyContracts(long_contract)[0]
            qualified_short = self.ib.qualifyContracts(short_contract)[0]
        except Exception as e:
            log_error(f"Failed to qualify option contracts: {str(e)}")
            raise ValueError("Invalid option contracts")
        
        # Create bag contract for the spread
        bag = Contract()
        bag.symbol = symbol
        bag.secType = 'BAG'
        bag.currency = 'USD'
        bag.exchange = 'SMART'
        
        # Define the legs
        leg1 = ComboLeg()
        leg1.conId = qualified_long.conId
        leg1.ratio = 1
        leg1.action = 'BUY' if direction == 'LONG' else 'SELL'
        leg1.exchange = 'SMART'
        
        leg2 = ComboLeg()
        leg2.conId = qualified_short.conId
        leg2.ratio = 1
        leg2.action = 'SELL' if direction == 'LONG' else 'BUY'
        leg2.exchange = 'SMART'
        
        bag.comboLegs = [leg1, leg2]
        
        # Create order
        if price_type == "LIMIT":
            order = LimitOrder(
                'BUY' if direction == 'LONG' else 'SELL',
                contracts,
                limit_price
            )
        else:  # MARKET
            order = MarketOrder(
                'BUY' if direction == 'LONG' else 'SELL',
                contracts
            )
        
        # Set order properties
        order.orderRef = f"{option_spread.spread_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        order.transmit = True  # Transmit order immediately
        
        # Place the order
        trade = self.ib.placeOrder(bag, order)
        order_id = str(trade.order.orderId)
        
        # Store the order details
        with self.lock:
            self.orders[order_id] = {
                "id": order_id,
                "symbol": symbol,
                "direction": direction,
                "contracts": contracts,
                "spread_type": option_spread.spread_type,
                "price_type": price_type,
                "limit_price": limit_price,
                "status": trade.orderStatus.status,
                "filled_price": None,
                "submit_time": datetime.now(),
                "fill_time": None,
                "trade": trade,
                "option_spread": {
                    "long_strike": long_strike,
                    "short_strike": short_strike,
                    "expiration": expiry,
                    "option_type": long_option_type if option_spread.spread_type == "BULL_CALL" else short_option_type
                }
            }
        
        log_info(
            f"Placed order #{order_id}: {symbol} {direction} {contracts} contracts "
            f"of {option_spread.spread_type} at {price_type} "
            f"price {'$' + str(limit_price) if limit_price else 'MARKET'}"
        )
        
        return order_id
    
    except Exception as e:
        log_error(f"Error placing order: {str(e)}")
        raise RuntimeError(f"Order placement failed: {str(e)}")

def get_order_status(self, order_id: str) -> Dict[str, Any]:
    """Get the status of an order.
    
    Args:
        order_id: Order ID to check
        
    Returns:
        Order status details or empty dict if not found
    """
    with self.lock:
        if order_id not in self.orders:
            return {}
        
        order_info = self.orders[order_id].copy()
        trade = order_info.get("trade")
        
        if trade:
            # Update status from trade object
            order_info["status"] = trade.orderStatus.status
            order_info["filled"] = trade.orderStatus.filled
            order_info["remaining"] = trade.orderStatus.remaining
            
            if trade.orderStatus.status == 'Filled':
                order_info["filled_price"] = trade.orderStatus.avgFillPrice
                if not order_info.get("fill_time"):
                    order_info["fill_time"] = datetime.now()
            
            # Don't return the trade object in the dict
            if "trade" in order_info:
                del order_info["trade"]
        
        return order_info

def cancel_order(self, order_id: str) -> bool:
    """Cancel an open order.
    
    Args:
        order_id: Order ID to cancel
        
    Returns:
        True if cancel successful, False otherwise
    """
    try:
        if not self.connected:
            log_warning("Not connected to IBKR when attempting to cancel order")
            return False
        
        with self.lock:
            if order_id not in self.orders:
                log_warning(f"Order {order_id} not found when attempting to cancel")
                return False
            
            order_info = self.orders[order_id]
            trade = order_info.get("trade")
            
            if not trade:
                log_warning(f"Trade object not found for order {order_id}")
                return False
            
            order_status = trade.orderStatus.status
            if order_status in ['Filled', 'Cancelled', 'ApiCancelled']:
                log_warning(f"Cannot cancel order {order_id} with status {order_status}")
                return False
            
            # Cancel the order
            self.ib.cancelOrder(trade.order)
            log_info(f"Cancellation request sent for order {order_id}")
            
            # Wait briefly for cancellation to process
            for _ in range(5):  # Try for up to 5 * 0.2 = 1 second
                self.ib.sleep(0.2)
                # Check if cancelled
                if trade.orderStatus.status in ['Cancelled', 'ApiCancelled']:
                    log_info(f"Order {order_id} successfully cancelled")
                    order_info["status"] = trade.orderStatus.status
                    return True
            
            # If we get here, we didn't see the cancellation confirmed
            log_warning(f"Order {order_id} cancellation request sent but not confirmed")
            return True  # Return true since we sent the request
        
    except Exception as e:
        log_error(f"Error cancelling order {order_id}: {str(e)}")
        return False
```

#### 2. Create Order Management Test Cases

```python
# tests/features/order_management.feature
Feature: IBKR Order Management
  As a trader
  I want to place, monitor, and cancel option spread orders
  So that I can execute my trading strategy effectively

  Background:
    Given I am connected to IBKR
    And I have a valid option spread for AAPL

  Scenario: Place a limit order for a bull call spread
    When I place a limit order for 1 contract
    Then the order should be submitted successfully
    And the order status should be tracked

  Scenario: Place a market order for a bear put spread
    When I place a market order for 2 contracts
    Then the order should be submitted successfully
    And the order should be filled at market price

  Scenario: Cancel an open order
    Given I have placed a limit order
    And the order is not yet filled
    When I cancel the order
    Then the order should be cancelled successfully

  Scenario: Handle order rejection
    Given the market is closed
    When I place a market order for 1 contract
    Then the order should be rejected
    And an appropriate error message should be logged
```

```python
# tests/test_ibkr_order_management.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timedelta

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.models.option import Option, OptionSpread

# Load scenarios from the feature file
scenarios('features/order_management.feature')

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
        
        # Mock order placement
        mock_trade = MagicMock()
        mock_trade.order.orderId = 123
        mock_trade.orderStatus.status = "Submitted"
        mock_ib_instance.placeOrder.return_value = mock_trade
        
        # Mock contract qualification
        mock_qualified_contract = MagicMock()
        mock_qualified_contract.conId = 12345
        mock_ib_instance.qualifyContracts.return_value = [mock_qualified_contract]
        
        yield mock_ib_instance

@pytest.fixture
def api(mock_config, mock_ib):
    api = IBKRIBInsyncApi(mock_config)
    api.connected = True
    api.account_id = "DU12345"
    return api

# Step definitions
@given("I am connected to IBKR")
def connected_to_ibkr(api):
    assert api.connected is True

@given("I have a valid option spread for AAPL")
def valid_option_spread(option_spread):
    assert option_spread.symbol == "AAPL"
    assert option_spread.spread_type == "BULL_CALL"

@given("I have placed a limit order")
def placed_limit_order(api, option_spread, mock_ib):
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Submitted"
    api.place_order("AAPL", "LONG", 1, option_spread, "LIMIT", 2.85)

@given("the order is not yet filled")
def order_not_filled(api, mock_ib):
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Submitted"
    mock_trade.orderStatus.filled = 0
    mock_trade.orderStatus.remaining = 1

@given("the market is closed")
def market_closed(mock_ib):
    # Mock that the market is closed by making placeOrder raise an exception
    mock_ib.placeOrder.side_effect = Exception("Market is closed")

@when(parsers.parse("I place a limit order for {quantity:d} contract"))
def place_limit_order(api, option_spread, quantity, mock_ib):
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Submitted"
    api.order_id = api.place_order("AAPL", "LONG", quantity, option_spread, "LIMIT", 2.85)

@when(parsers.parse("I place a market order for {quantity:d} contracts"))
def place_market_order(api, option_spread, quantity, mock_ib):
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Submitted"
    api.order_id = api.place_order("AAPL", "LONG", quantity, option_spread, "MARKET")

@when("I cancel the order")
def cancel_order(api, mock_ib):
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Cancelled"
    mock_trade.orderStatus.filled = 0
    mock_trade.orderStatus.remaining = 1
    api.cancelled = api.cancel_order(api.order_id)

@then("the order should be submitted successfully")
def order_submitted(api):
    assert api.order_id is not None
    order_status = api.get_order_status(api.order_id)
    assert order_status["status"] == "Submitted"

@then("the order status should be tracked")
def order_status_tracked(api):
    order_status = api.get_order_status(api.order_id)
    assert "status" in order_status
    assert "filled" in order_status
    assert "remaining" in order_status

@then("the order should be filled at market price")
def order_filled_market_price(api, mock_ib):
    # Simulate order being filled
    mock_trade = mock_ib.placeOrder.return_value
    mock_trade.orderStatus.status = "Filled"
    mock_trade.orderStatus.filled = 2
    mock_trade.orderStatus.remaining = 0
    mock_trade.orderStatus.avgFillPrice = 2.90
    
    # Check that the order was filled
    order_status = api.get_order_status(api.order_id)
    assert order_status["status"] == "Filled"
    assert order_status["filled"] == 2
    assert order_status["remaining"] == 0

@then("the order should be cancelled successfully")
def order_cancelled(api):
    assert api.cancelled is True
    order_status = api.get_order_status(api.order_id)
    assert order_status["status"] == "Cancelled"

@then("the order should be rejected")
def order_rejected(api, mock_ib):
    assert mock_ib.placeOrder.side_effect is not None
    with pytest.raises(RuntimeError):
        api.place_order("AAPL", "LONG", 1, option_spread, "MARKET")

@then("an appropriate error message should be logged")
def error_logged(caplog):
    # Check that an error was logged
    assert any("Error placing order" in record.message for record in caplog.records)
```

### Phase 3: Market Data Implementation

**Gherkin Scenario - Market Data:**
```gherkin
Feature: IBKR Market Data Retrieval
  As a trader
  I want to retrieve real-time market data and option chains
  So that I can make informed trading decisions

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve current market data for a stock
    When I request market data for "AAPL"
    Then I should receive the current price data
    And the data should include bid, ask, and last price

  Scenario: Handle market data for invalid symbol
    When I request market data for an invalid symbol "INVALID"
    Then I should receive an error response
    And an appropriate error message should be logged

  Scenario: Retrieve option chain for a stock
    When I request the option chain for "AAPL"
    Then I should receive a list of available options
    And the options should include calls and puts
    And each option should have price and Greek data

  Scenario: Handle option chain for invalid symbol
    When I request the option chain for an invalid symbol "INVALID"
    Then I should receive an empty list
    And an appropriate error message should be logged
```

#### 1. Implement Market Data Methods

```python
def get_market_data(self, symbol: str) -> Dict[str, Any]:
    """Get real-time market data for a symbol.
    
    Args:
        symbol: Symbol to get data for
        
    Returns:
        Market data dictionary
    """
    if not self.connected:
        log_warning("Not connected to IBKR when requesting market data")
        return {
            "symbol": symbol,
            "error": "Not connected"
        }
    
    try:
        # Create contract
        contract = Stock(symbol, 'SMART', 'USD')
        
        # Qualify contract
        try:
            qualified_contracts = self.ib.qualifyContracts(contract)
            if not qualified_contracts:
                log_error(f"Could not qualify contract for {symbol}")
                return {
                    "symbol": symbol,
                    "error": "Invalid symbol"
                }
            contract = qualified_contracts[0]
        except Exception as e:
            log_error(f"Error qualifying contract for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": f"Invalid symbol: {str(e)}"
            }
        
        # Request market data
        ticker = self.ib.reqMktData(contract)
        
        # Wait for data to arrive
        timeout = 3  # seconds
        for _ in range(timeout * 10):  # Check every 0.1 seconds
            self.ib.sleep(0.1)
            if not (util.isNan(ticker.last) and util.isNan(ticker.bid) and util.isNan(ticker.ask)):
                break
        
        # Gather data
        data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "last": ticker.last if not util.isNan(ticker.last) else None,
            "bid": ticker.bid if not util.isNan(ticker.bid) else None,
            "ask": ticker.ask if not util.isNan(ticker.ask) else None,
            "volume": ticker.volume if not util.isNan(ticker.volume) else None,
            "high": ticker.high if not util.isNan(ticker.high) else None,
            "low": ticker.low if not util.isNan(ticker.low) else None,
            "close": ticker.close if not util.isNan(ticker.close) else None,
        }
        
        # Cancel market data to conserve resources
        self.ib.cancelMktData(contract)
        
        return data
    
    except Exception as e:
        log_error(f"Error getting market data for {symbol}: {str(e)}")
        return {
            "symbol": symbol,
            "error": str(e)
        }

def get_option_chain(self, symbol: str) -> List[Option]:
    """Get the full option chain for a symbol.
    
    Args:
        symbol: Underlying symbol
        
    Returns:
        List of options
    """
    if not self.connected:
        log_error("Not connected to IBKR")
        return []
    
    try:
        # Create stock contract
        contract = Stock(symbol, 'SMART', 'USD')
        
        # Qualify contract
        try:
            qualified_contracts = self.ib.qualifyContracts(contract)
            if not qualified_contracts:
                log_error(f"Could not qualify contract for {symbol}")
                return []
            contract = qualified_contracts[0]
        except Exception as e:
            log_error(f"Error qualifying contract for {symbol}: {str(e)}")
            return []
        
        # Request contract details to get contract ID
        details = self.ib.reqContractDetails(contract)
        
        if not details:
            log_error(f"No contract details found for {symbol}")
            return []
        
        # Request option chain parameters
        chains = self.ib.reqSecDefOptParams(
            underlyingSymbol=symbol, 
            futFopExchange='', 
            underlyingSecType='STK', 
            underlyingConId=contract.conId
        )
        
        if not chains:
            log_error(f"No option chains found for {symbol}")
            return []
        
        # Get first chain (usually there's only one)
        chain = chains[0]
        
        # Get current price for determining which strikes to include
        market_data = self.get_market_data(symbol)
        current_price = market_data.get('last')
        if current_price is None:
            current_price = market_data.get('bid', 0)
            if current_price is None:
                current_price = market_data.get('ask', 100.0)
                if current_price is None:
                    current_price = 100.0  # Default if no price available
        
        # Create a list to store all options
        options = []
        
        # Define how many expirations and strikes to include
        max_expirations = 4  # Limit number of expirations to reduce API load
        max_strikes_per_expiry_and_type = 6  # Limit number of strikes per expiration and type
        
        # Request each expiration
        for expiration in chain.expirations[:max_expirations]:
            for right in ['C', 'P']:  # Calls and puts
                # Get strikes around ATM
                price_range = 0.3  # Get strikes within 30% of current price
                min_strike = current_price * (1 - price_range)
                max_strike = current_price * (1 + price_range)
                
                relevant_strikes = [
                    strike for strike in chain.strikes 
                    if min_strike <= strike <= max_strike
                ]
                
                # If we have too many strikes, select a subset centered around ATM
                if len(relevant_strikes) > max_strikes_per_expiry_and_type:
                    # Sort strikes
                    relevant_strikes.sort(key=lambda x: abs(x - current_price))
                    relevant_strikes = relevant_strikes[:max_strikes_per_expiry_and_type]
                    # Sort back to normal order
                    relevant_strikes.sort()
                
                # Process each strike
                for strike in relevant_strikes:
                    # Create option contract
                    option_contract = IBOption(
                        symbol=symbol,
                        lastTradeDateOrContractMonth=expiration,
                        strike=strike,
                        right=right,
                        exchange=chain.exchange
                    )
                    
                    try:
                        # Qualify the contract
                        qualified_options = self.ib.qualifyContracts(option_contract)
                        
                        if not qualified_options:
                            continue
                        
                        qualified_option = qualified_options[0]
                        
                        # Request market data
                        ticker = self.ib.reqMktData(qualified_option, '', False, False)
                        
                        # Wait for market data to arrive (with timeout)
                        timeout = 1  # seconds
                        for _ in range(timeout * 10):  # Check every 0.1 seconds
                            self.ib.sleep(0.1)
                            if not (util.isNan(ticker.last) and util.isNan(ticker.bid) and util.isNan(ticker.ask)):
                                break
                        
                        # Convert to our Option model
                        exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                        
                        # Extract implied volatility and greeks
                        implied_vol = ticker.impliedVolatility if hasattr(ticker, 'impliedVolatility') and not util.isNan(ticker.impliedVolatility) else 0.0
                        
                        # Get greeks from model or compute them
                        delta = gamma = theta = vega = rho = 0.0
                        
                        if hasattr(ticker, 'modelGreeks') and ticker.modelGreeks:
                            delta = ticker.modelGreeks.delta if not util.isNan(ticker.modelGreeks.delta) else 0.0
                            gamma = ticker.modelGreeks.gamma if not util.isNan(ticker.modelGreeks.gamma) else 0.0
                            theta = ticker.modelGreeks.theta if not util.isNan(ticker.modelGreeks.theta) else 0.0
                            vega = ticker.modelGreeks.vega if not util.isNan(ticker.modelGreeks.vega) else 0.0
                            rho = ticker.modelGreeks.rho if not util.isNan(ticker.modelGreeks.rho) else 0.0
                        
                        option = Option(
                            symbol=qualified_option.localSymbol,
                            underlying=symbol,
                            option_type="call" if right == 'C' else "put",
                            strike=strike,
                            expiration=exp_date,
                            bid=ticker.bid if not util.isNan(ticker.bid) else 0.0,
                            ask=ticker.ask if not util.isNan(ticker.ask) else 0.0,
                            last=ticker.last if not util.isNan(ticker.last) else 0.0,
                            volume=int(ticker.volume) if not util.isNan(ticker.volume) else 0,
                            open_interest=int(ticker.openInterest) if hasattr(ticker, 'openInterest') and not util.isNan(ticker.openInterest) else 0,
                            implied_volatility=implied_vol,
                            delta=delta,
                            gamma=gamma,
                            theta=theta,
                            vega=vega,
                            rho=rho
                        )
                        
                        options.append(option)
                        
                        # Cancel market data to conserve resources
                        self.ib.cancelMktData(qualified_option)
                    
                    except Exception as e:
                        log_warning(f"Error processing option {symbol} {expiration} {right} {strike}: {str(e)}")
                        continue
        
        log_info(f"Retrieved {len(options)} options for {symbol}")
        return options
    
    except Exception as e:
        log_error(f"Error getting option chain for {symbol}: {str(e)}")
        return []
```

#### 2. Create Market Data Test Cases

```python
# tests/features/market_data.feature
Feature: IBKR Market Data Retrieval
  As a trader
  I want to retrieve real-time market data and option chains
  So that I can make informed trading decisions

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve current market data for a stock
    When I request market data for "AAPL"
    Then I should receive the current price data
    And the data should include bid, ask, and last price

  Scenario: Handle market data for invalid symbol
    When I request market data for an invalid symbol "INVALID"
    Then I should receive an error response
    And an appropriate error message should be logged

  Scenario: Retrieve option chain for a stock
    When I request the option chain for "AAPL"
    Then I should receive a list of available options
    And the options should include calls and puts
    And each option should have price and Greek data

  Scenario: Handle option chain for invalid symbol
    When I request the option chain for an invalid symbol "INVALID"
    Then I should receive an empty list
    And an appropriate error message should be logged
```

```python
# tests/test_ibkr_market_data.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import MagicMock, patch, ANY
from datetime import date, datetime, timedelta

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.models.option import Option

# Load scenarios from the feature file
scenarios('features/market_data.feature')

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
        
        # Mock ticker
        mock_ticker = MagicMock()
        mock_ticker.last = 150.25
        mock_ticker.bid = 150.20
        mock_ticker.ask = 150.30
        mock_ticker.volume = 1000000
        mock_ticker.high = 151.50
        mock_ticker.low = 149.75
        mock_ticker.close = 150.00
        
        # Mock option ticker
        mock_option_ticker = MagicMock()
        mock_option_ticker.last = 5.25
        mock_option_ticker.bid = 5.20
        mock_option_ticker.ask = 5.30
        mock_option_ticker.volume = 1500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.modelGreeks = MagicMock()
        mock_option_ticker.modelGreeks.delta = 0.60
        mock_option_ticker.modelGreeks.gamma = 0.05
        mock_option_ticker.modelGreeks.theta = -0.10
        mock_option_ticker.modelGreeks.vega = 0.15
        mock_option_ticker.modelGreeks.rho = 0.03
        
        # Mock contract qualification
        mock_qualified_contract = MagicMock()
        mock_qualified_contract.conId = 12345
        mock_qualified_contract.localSymbol = "AAPL"
        mock_ib_instance.qualifyContracts.return_value = [mock_qualified_contract]
        
        # Mock market data request
        mock_ib_instance.reqMktData.return_value = mock_ticker
        
        # Mock contract details
        mock_details = [MagicMock()]
        mock_ib_instance.reqContractDetails.return_value = mock_details
        
        # Mock option chain
        mock_chain = MagicMock()
        expiry_date = date.today() + timedelta(days=30)
        mock_chain.expirations = [expiry_date.strftime("%Y%m%d")]
        mock_chain.strikes = [145.0, 150.0, 155.0]
        mock_chain.exchange = "SMART"
        mock_ib_instance.reqSecDefOptParams.return_value = [mock_chain]
        
        yield mock_ib_instance

@pytest.fixture
def api(mock_config, mock_ib):
    api = IBKRIBInsyncApi(mock_config)
    api.connected = True
    api.account_id = "DU12345"
    return api

# Step definitions
@given("I am connected to IBKR")
def connected_to_ibkr(api):
    assert api.connected is True

@when(parsers.parse("I request market data for {symbol}"))
def request_market_data(api, symbol, mock_ib):
    api.market_data = api.get_market_data(symbol)

@when(parsers.parse("I request market data for an invalid symbol {symbol}"))
def request_invalid_market_data(api, symbol, mock_ib):
    # Mock that the symbol is invalid
    mock_ib.qualifyContracts.side_effect = Exception("Invalid symbol")
    api.market_data = api.get_market_data(symbol)

@when(parsers.parse("I request the option chain for {symbol}"))
def request_option_chain(api, symbol, mock_ib):
    # Setup mock for option market data
    mock_option_ticker = MagicMock()
    mock_option_ticker.last = 5.25
    mock_option_ticker.bid = 5.20
    mock_option_ticker.ask = 5.30
    mock_option_ticker.volume = 1500
    mock_option_ticker.impliedVolatility = 0.25
    mock_option_ticker.modelGreeks = MagicMock()
    mock_option_ticker.modelGreeks.delta = 0.60
    mock_option_ticker.modelGreeks.gamma = 0.05
    mock_option_ticker.modelGreeks.theta = -0.10
    mock_option_ticker.modelGreeks.vega = 0.15
    mock_option_ticker.modelGreeks.rho = 0.03
    
    # When qualifyContracts is called with an option contract, return a different mock
    def qualify_side_effect(contract):
        if hasattr(contract, 'right'):
            mock_qualified_option = MagicMock()
            mock_qualified_option.conId = 67890
            mock_qualified_option.localSymbol = f"AAPL {contract.right} {contract.strike}"
            return [mock_qualified_option]
        else:
            mock_qualified_stock = MagicMock()
            mock_qualified_stock.conId = 12345
            mock_qualified_stock.localSymbol = "AAPL"
            return [mock_qualified_stock]
    
    mock_ib.qualifyContracts.side_effect = qualify_side_effect
    
    # Use the option ticker for option market data
    mock_ib.reqMktData.return_value = mock_option_ticker
    
    api.options = api.get_option_chain(symbol)

@when(parsers.parse("I request the option chain for an invalid symbol {symbol}"))
def request_invalid_option_chain(api, symbol, mock_ib):
    # Mock that the symbol is invalid
    mock_ib.qualifyContracts.side_effect = Exception("Invalid symbol")
    api.options = api.get_option_chain(symbol)

@then("I should receive the current price data")
def receive_price_data(api):
    assert api.market_data is not None
    assert api.market_data["symbol"] == "AAPL"
    assert "error" not in api.market_data

@then("the data should include bid, ask, and last price")
def data_includes_prices(api):
    assert "bid" in api.market_data
    assert "ask" in api.market_data
    assert "last" in api.market_data
    assert api.market_data["bid"] == 150.20
    assert api.market_data["ask"] == 150.30
    assert api.market_data["last"] == 150.25

@then("I should receive an error response")
def receive_error_response(api):
    assert "error" in api.market_data

@then("I should receive a list of available options")
def receive_option_list(api):
    assert isinstance(api.options, list)
    assert len(api.options) > 0

@then("the options should include calls and puts")
def options_include_calls_and_puts(api, mock_ib):
    # Since we mocked the chain to get only a few strikes/expiries,
    # we can just check that our mock side effect was called correctly
    assert mock_ib.qualifyContracts.call_count >= 6  # At least 6 calls (3 strikes * 2 types)

@then("each option should have price and Greek data")
def options_have_price_and_greeks(api):
    for option in api.options:
        assert option.bid >= 0
        assert option.ask >= 0
        assert option.delta != 0
        assert option.gamma != 0
        assert option.theta != 0
        assert option.vega != 0

@then("I should receive an empty list")
def receive_empty_list(api):
    assert isinstance(api.options, list)
    assert len(api.options) == 0

@then("an appropriate error message should be logged")
def error_logged(caplog):
    # Check that an error was logged
    assert any("Error" in record.message for record in caplog.records)
```

### Phase 4: Account and Position Management

**Gherkin Scenario - Account Management:**
```gherkin
Feature: IBKR Account Management
  As a trader
  I want to retrieve account and position information
  So that I can monitor my portfolio and risk

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve account summary
    When I request the account summary
    Then I should receive the account values
    And the summary should include cash balance and equity values

  Scenario: Retrieve current positions
    When I request my current positions
    Then I should receive a list of positions
    And each position should include symbol, quantity, and average cost

  Scenario: Handle position update events
    Given I have an open position in "AAPL"
    When a position update event occurs
    Then my position data should be updated accordingly
    And the update should be logged
```

#### 1. Implement Account and Position Methods

```python
def get_account_summary(self) -> Dict[str, Any]:
    """Get account summary data.
    
    Returns:
        Account summary information
    """
    if not self.connected:
        return {
            "error": "Not connected to IBKR",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Get account values
        account_values = self.ib.accountValues()
        
        # Extract the values we want
        summary = {
            "timestamp": datetime.now().isoformat(),
            "account_id": self.account_id
        }
        
        # Map of tag names to our key names
        account_fields = {
            "CashBalance": "cash_balance",
            "NetLiquidation": "net_liquidation",
            "EquityWithLoanValue": "equity_with_loan",
            "InitMarginReq": "initial_margin_req",
            "MaintMarginReq": "maintenance_margin_req",
            "AvailableFunds": "available_funds",
            "ExcessLiquidity": "excess_liquidity",
            "BuyingPower": "buying_power",
            "DayTradesRemaining": "day_trades_remaining",
            "GrossPositionValue": "gross_position_value",
            "TotalCashValue": "total_cash_value",
        }
        
        # Initialize with None values
        for value in account_fields.values():
            summary[value] = None
            
        # Fill in the values we have
        for value in account_values:
            # Only use USD values for now
            if value.currency != "USD":
                continue
                
            # Map the tag to our field name
            if value.tag in account_fields:
                field_name = account_fields[value.tag]
                
                # Try to convert to float if possible
                try:
                    summary[field_name] = float(value.value)
                except ValueError:
                    summary[field_name] = value.value
        
        return summary
    except Exception as e:
        log_error(f"Error getting account summary: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_positions(self) -> Dict[str, Dict[str, Any]]:
    """Get current positions.
    
    Returns:
        Dictionary of positions by symbol
    """
    with self.lock:
        if not self.connected:
            return {}
            
        # If we already have positions, return what we have
        if self.positions:
            return self.positions.copy()
        
        try:
            # Request positions from TWS
            ib_positions = self.ib.positions()
            positions = {}
            
            # Convert IB positions to our format
            for pos in ib_positions:
                symbol = pos.contract.symbol
                
                if symbol not in positions:
                    positions[symbol] = {
                        "symbol": symbol,
                        "quantity": 0,
                        "avg_price": 0,
                        "market_price": 0,
                        "market_value": 0,
                        "unrealized_pnl": 0,
                        "realized_pnl": 0,
                        "account": pos.account,
                        "trades": []
                    }
                
                # Update position
                positions[symbol]["quantity"] += pos.position
                positions[symbol]["avg_price"] = pos.avgCost
                
                # Try to get market price and value
                if hasattr(pos, 'marketPrice') and not util.isNan(pos.marketPrice):
                    positions[symbol]["market_price"] = pos.marketPrice
                    
                if hasattr(pos, 'marketValue') and not util.isNan(pos.marketValue):
                    positions[symbol]["market_value"] = pos.marketValue
                
            # Store for future use
            self.positions = positions
            
            return positions.copy()
        
        except Exception as e:
            log_error(f"Error getting positions: {str(e)}")
            return {}
```

#### 2. Create Account Test Cases

```python
# tests/features/account_management.feature
Feature: IBKR Account Management
  As a trader
  I want to retrieve account and position information
  So that I can monitor my portfolio and risk

  Background:
    Given I am connected to IBKR

  Scenario: Retrieve account summary
    When I request the account summary
    Then I should receive the account values
    And the summary should include cash balance and equity values

  Scenario: Retrieve current positions
    When I request my current positions
    Then I should receive a list of positions
    And each position should include symbol, quantity, and average cost

  Scenario: Handle position update events
    Given I have an open position in "AAPL"
    When a position update event occurs
    Then my position data should be updated accordingly
    And the update should be logged
```

```python
# tests/test_ibkr_account.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.models.option import Option

# Load scenarios from the feature file
scenarios('features/account_management.feature')

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
        
        # Mock account values
        mock_account_value_cash = MagicMock()
        mock_account_value_cash.tag = "CashBalance"
        mock_account_value_cash.value = "100000.00"
        mock_account_value_cash.currency = "USD"
        
        mock_account_value_equity = MagicMock()
        mock_account_value_equity.tag = "EquityWithLoanValue"
        mock_account_value_equity.value = "150000.00"
        mock_account_value_equity.currency = "USD"
        
        mock_account_value_buying_power = MagicMock()
        mock_account_value_buying_power.tag = "BuyingPower"
        mock_account_value_buying_power.value = "300000.00"
        mock_account_value_buying_power.currency = "USD"
        
        mock_ib_instance.accountValues.return_value = [
            mock_account_value_cash,
            mock_account_value_equity,
            mock_account_value_buying_power
        ]
        
        # Mock positions
        mock_position_aapl = MagicMock()
        mock_position_aapl.account = "DU12345"
        mock_position_aapl.contract = MagicMock()
        mock_position_aapl.contract.symbol = "AAPL"
        mock_position_aapl.position = 100
        mock_position_aapl.avgCost = 150.25
        
        mock_position_msft = MagicMock()
        mock_position_msft.account = "DU12345"
        mock_position_msft.contract = MagicMock()
        mock_position_msft.contract.symbol = "MSFT"
        mock_position_msft.position = 50
        mock_position_msft.avgCost = 220.75
        
        mock_ib_instance.positions.return_value = [mock_position_aapl, mock_position_msft]
        
        yield mock_ib_instance

@pytest.fixture
def api(mock_config, mock_ib):
    api = IBKRIBInsyncApi(mock_config)
    api.connected = True
    api.account_id = "DU12345"
    return api

# Step definitions
@given("I am connected to IBKR")
def connected_to_ibkr(api):
    assert api.connected is True

@given(parsers.parse("I have an open position in {symbol}"))
def have_open_position(api, symbol, mock_ib):
    # Make sure the position exists
    api.positions = {}  # Clear any existing positions
    mock_position = MagicMock()
    mock_position.account = "DU12345"
    mock_position.contract = MagicMock()
    mock_position.contract.symbol = symbol
    mock_position.position = 100
    mock_position.avgCost = 150.25
    api.positions[symbol] = {
        "symbol": symbol,
        "quantity": 100,
        "avg_price": 150.25,
        "market_price": 155.50,
        "market_value": 15550.00,
        "unrealized_pnl": 525.00,
        "realized_pnl": 0.00,
        "account": "DU12345",
        "trades": []
    }

@when("I request the account summary")
def request_account_summary(api):
    api.account_summary = api.get_account_summary()

@when("I request my current positions")
def request_positions(api):
    api.position_data = api.get_positions()

@when("a position update event occurs")
def position_update_event(api, mock_ib):
    # Simulate a position update event
    mock_position = MagicMock()
    mock_position.account = "DU12345"
    mock_position.contract = MagicMock()
    mock_position.contract.symbol = "AAPL"
    mock_position.position = 120  # Increased position
    mock_position.avgCost = 152.30  # New average cost
    
    # Trigger the position event handler
    api._on_position(mock_position)

@then("I should receive the account values")
def receive_account_values(api):
    assert api.account_summary is not None
    assert "error" not in api.account_summary
    assert "timestamp" in api.account_summary
    assert api.account_summary["account_id"] == "DU12345"

@then("the summary should include cash balance and equity values")
def summary_includes_values(api):
    assert "cash_balance" in api.account_summary
    assert "equity_with_loan" in api.account_summary
    assert "buying_power" in api.account_summary
    assert api.account_summary["cash_balance"] == 100000.00
    assert api.account_summary["equity_with_loan"] == 150000.00
    assert api.account_summary["buying_power"] == 300000.00

@then("I should receive a list of positions")
def receive_position_list(api):
    assert isinstance(api.position_data, dict)
    assert len(api.position_data) == 2
    assert "AAPL" in api.position_data
    assert "MSFT" in api.position_data

@then("each position should include symbol, quantity, and average cost")
def positions_include_details(api):
    for symbol, position in api.position_data.items():
        assert "symbol" in position
        assert "quantity" in position
        assert "avg_price" in position
        assert position["symbol"] == symbol
    
    assert api.position_data["AAPL"]["quantity"] == 100
    assert api.position_data["AAPL"]["avg_price"] == 150.25
    assert api.position_data["MSFT"]["quantity"] == 50
    assert api.position_data["MSFT"]["avg_price"] == 220.75

@then("my position data should be updated accordingly")
def position_data_updated(api):
    assert "AAPL" in api.positions
    assert api.positions["AAPL"]["quantity"] == 120  # Updated quantity
    assert api.positions["AAPL"]["avg_price"] == 152.30  # Updated price

@then("the update should be logged")
def update_logged(caplog):
    # Check that a position update log message exists
    assert any("Position update" in record.message for record in caplog.records)
```

### Phase 5: Integration and Configuration

#### 1. Update Config Schema

Update `config.yaml` with new ib_insync specific settings:

```yaml
# IBKR API Connection
ibkr:
  host: "127.0.0.1"
  port: 7497  # TWS: 7497, IB Gateway: 4001
  client_id: 1
  read_only: false
  account: ""  # Set your account ID or leave blank to use active account
  use_ib_insync: true  # Use new implementation instead of placeholder
  timeout: 20  # Connection timeout in seconds
  auto_reconnect: true  # Automatically try to reconnect on disconnection
  max_rate: 45  # Maximum API requests per second (IB's limit is 50)
```

#### 2. Update the Trader Class

Modify the initialization in `src/app/trader.py` to use the factory method:

```python
def __init__(self, config_file: str = "config.yaml"):
    """Initialize the trader.

    Args:
        config_file: Path to configuration file
    """
    # Load configuration
    self.config = Config.from_yaml(config_file)
    log_info(f"Initialized trader with {self.config.TRADING_MODE} mode")
    
    # Check if we should use ib_insync
    use_ib_insync = getattr(self.config, "USE_IB_INSYNC", True)
    
    # Connect to IBKR using the appropriate implementation
    from src.brokers import get_broker_api
    self.broker_api = get_broker_api(self.config, use_ib_insync=use_ib_insync)
    
    # Attempt to connect
    connected = self.broker_api.connect()
    if not connected:
        log_error("Failed to connect to IBKR, some functionality may be limited")
    
    # Initialize components with the broker API
    self.scanner = ScannerClient(self.config.SCANNER_HOST, self.config.SCANNER_PORT)
    self.option_selector = OptionSelector(self.config)
    self.risk_manager = RiskManager(self.config, self.broker_api)
    self.trade_executor = TradeExecutor(self.config, self.broker_api)

    # Signal processing queue
    self.signal_queue = queue.Queue()
    self.processing = False
    self.processing_thread = None
```

#### 3. Handle Periodic Callbacks

Add periodic callback handling to ensure IB messages are processed:

```python
def _process_signals_thread(self) -> None:
    """Background thread for processing signals from the queue."""
    while self.processing:
        try:
            # Process any queued signals with a timeout
            try:
                signal = self.signal_queue.get(timeout=1.0)
                status, result = self.process_signal(signal)
                log_debug(f"Signal processing result: {status} - {result}")
                self.signal_queue.task_done()
            except queue.Empty:
                # No signals to process
                pass
                
            # Process IB callbacks to keep connection alive
            if self.broker_api and hasattr(self.broker_api, 'handle_callbacks'):
                self.broker_api.handle_callbacks()
                
            # Periodically update positions from broker
            self.risk_manager.update_positions_from_broker()

            # Process any queued trades
            self.trade_executor.process_queued_trades()
                
            # Sleep to avoid excessive CPU usage
            time.sleep(0.1)
        except Exception as e:
            log_error(f"Error in signal processing thread: {str(e)}")
```

## Testing Strategy

### 1. Unit Tests

Unit tests should verify the behavior of individual methods in isolation, with mocked dependencies. All tests should use pytest and pytest-bdd.

```bash
# Run unit tests for the IBKR implementation
pytest tests/test_ibkr_*.py

# Run tests with coverage
pytest tests/test_ibkr_*.py --cov=src.brokers

# Generate coverage report
pytest tests/test_ibkr_*.py --cov=src.brokers --cov-report=html
```

### 2. Integration Tests

Integration tests should verify correct interaction with the TWS/Gateway application. These tests require a running instance of TWS/Gateway with an active paper trading account.

```python
# tests/test_ibkr_integration.py
import os
import unittest
from datetime import date

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.models.option import Option, OptionSpread

@unittest.skipIf(os.environ.get("SKIP_IB_TESTS", "1") == "1", 
                 "Skipping IB tests. Set SKIP_IB_TESTS=0 to run")
class TestIBKRIBInsyncApiIntegration(unittest.TestCase):
    def setUp(self):
        # Load config from file for integration test
        self.config = Config.from_yaml("tests/test_config.yaml")
        
        # Create real instance
        self.api = IBKRIBInsyncApi(self.config)
        connected = self.api.connect()
        self.assertTrue(connected, "Failed to connect to IB")
        
    def tearDown(self):
        self.api.disconnect()
        
    def test_get_market_data(self):
        data = self.api.get_market_data("SPY")
        self.assertEqual(data["symbol"], "SPY")
        self.assertIsNotNone(data["last"])
        
    # Add more tests...
```

### 3. Automation

Automate all tests with GitHub Actions workflow:

```yaml
# .github/workflows/ibkr_tests.yml
name: IBKR API Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov pytest-bdd
        pip install -r requirements.txt
    
    - name: Run unit tests
      run: |
        pytest tests/test_ibkr_*.py --cov=src.brokers --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## Migration Strategy

### 1. Phased Implementation

1. **Phase A: Development**
   - Implement the ib_insync wrapper
   - Write unit tests
   - Verify basic functionality

2. **Phase B: Paper Trading Testing**
   - Enable for paper trading environments only
   - Test with real TWS/Gateway but paper accounts
   - Verify all trade execution paths
   - Collect and fix issues

3. **Phase C: Parallel Implementation**
   - Run both implementations side by side with configuration toggle
   - Compare results for consistency
   - Verify backtesting compatibility

4. **Phase D: Production Rollout**
   - Enable for live trading
   - Monitor closely for any issues
   - Maintain fallback capability

### 2. Rollback Plan

- Keep the original implementation available with configuration toggle
- Add toggle to `config.yaml` for easy switching
- Maintain clear separation between implementations
- Document issues and workarounds

## Conclusion

Implementing the `ib_insync` library will provide a more robust and maintainable interface to Interactive Brokers for our trading application. The systematic approach outlined in this document ensures that we:

1. Maintain compatibility with the existing codebase
2. Validate every aspect of the implementation with tests
3. Add powerful new capabilities for real-time market data and trading
4. Have a clear path to migrate safely and with minimal disruption

Following this implementation plan will result in a production-quality interface to IBKR that can be the foundation for more sophisticated trading strategies.
