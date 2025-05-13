# IB Insync Implementation: Step 4 - Order Management

## Introduction

This guide covers implementing order management functionality for the IB Insync API wrapper. We'll implement placing, monitoring, and canceling orders for options and option spreads.

## Order Management Methods

Add the following methods to the `IBKRIBInsyncApi` class:

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

## Testing Order Management Functionality

Create a file `tests/features/order_management.feature` with Gherkin scenarios:

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

Create a test implementation at `tests/test_ibkr_order_management.py`:

```python
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

@pytest.fixture
def option_spread():
    # Create a bull call spread for AAPL
    exp_date = date.today() + timedelta(days=30)
    
    long_leg = Option(
        symbol="AAPL_C_150",
        underlying="AAPL",
        option_type="call",
        strike=150.0,
        expiration=exp_date,
        bid=5.20,
        ask=5.30,
        last=5.25
    )
    
    short_leg = Option(
        symbol="AAPL_C_155",
        underlying="AAPL",
        option_type="call",
        strike=155.0,
        expiration=exp_date,
        bid=3.20,
        ask=3.30,
        last=3.25
    )
    
    return OptionSpread(
        symbol="AAPL",
        spread_type="BULL_CALL",
        expiration=exp_date,
        long_leg=long_leg,
        short_leg=short_leg
    )

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

## Testing

Run the tests using pytest:

```bash
pytest tests/test_ibkr_order_management.py -v
```

## Next Steps

After implementing order management functionality, proceed to [Step 5](ib-insync-step5-account-management.md) to implement account and position management functionality. 