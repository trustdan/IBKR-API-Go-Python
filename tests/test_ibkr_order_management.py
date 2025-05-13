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
        last=5.25,
        volume=100,
        open_interest=1000,
        implied_volatility=0.3,
        delta=0.55,
        gamma=0.02,
        theta=-0.05,
        vega=0.1,
        rho=0.01
    )
    
    short_leg = Option(
        symbol="AAPL_C_155",
        underlying="AAPL",
        option_type="call",
        strike=155.0,
        expiration=exp_date,
        bid=3.20,
        ask=3.30,
        last=3.25,
        volume=75,
        open_interest=800,
        implied_volatility=0.28,
        delta=0.45,
        gamma=0.02,
        theta=-0.04,
        vega=0.09,
        rho=0.01
    )
    
    return OptionSpread(
        symbol="AAPL",
        spread_type="BULL_CALL",
        expiration=exp_date,
        long_leg=long_leg,
        short_leg=short_leg,
        cost=2.0,
        max_profit=3.0,
        max_loss=2.0,
        delta=0.1
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
def order_rejected(api, mock_ib, option_spread):
    assert mock_ib.placeOrder.side_effect is not None
    with pytest.raises(RuntimeError):
        api.place_order("AAPL", "LONG", 1, option_spread, "MARKET")

@then("an appropriate error message should be logged")
def error_logged(caplog):
    # Check that an error was logged
    assert any("Error placing order" in record.message for record in caplog.records) 