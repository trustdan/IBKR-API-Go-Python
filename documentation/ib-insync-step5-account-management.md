# IB Insync Implementation: Step 5 - Account and Position Management

## Introduction

This guide covers implementing account and position management functionality for the IB Insync API wrapper. We'll implement retrieving account information and tracking positions.

## Account and Position Methods

Add the following methods to the `IBKRIBInsyncApi` class:

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

## Testing Account Management Functionality

Create a file `tests/features/account_management.feature` with Gherkin scenarios:

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

Create a test implementation at `tests/test_ibkr_account.py`:

```python
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

## Testing

Run the tests using pytest:

```bash
pytest tests/test_ibkr_account.py -v
```

## Integration: Updating the Trader Class

Now that we have implemented all components of the `IBKRIBInsyncApi` class, we need to update the `Trader` class to use our new implementation:

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

And update the signal processing thread to handle periodic callbacks:

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

## Conclusion

This completes our implementation of the IB Insync API wrapper for our trading application. We have successfully:

1. Set up the initial structure and dependencies
2. Implemented connection management
3. Added market data and option chain retrieval
4. Implemented order placement and management
5. Added account and position tracking

The implementation provides a much more powerful and reliable way to interact with Interactive Brokers compared to the previous placeholder implementation.

## Next Steps

Here are some additional improvements that could be considered:

1. **Error Handling**: Add more robust error handling and recovery mechanisms
2. **Reconnection Logic**: Implement automatic reconnection when connection is lost
3. **Request Throttling**: Add rate limiting to avoid exceeding API limits
4. **Extended Order Types**: Support for additional order types like stop orders, trailing stops, etc.
5. **Performance Optimization**: Optimize data retrieval for frequently used operations
6. **Logging Enhancements**: Add more detailed logging for debugging and monitoring

To use this implementation in production:

1. Enable in your configuration:
   ```yaml
   ibkr:
     use_ib_insync: true
   ```

2. Ensure the Interactive Brokers TWS or Gateway is running and configured to allow API connections
3. Start with paper trading to verify all functionality works as expected
4. Gradually transition to live trading while monitoring closely 