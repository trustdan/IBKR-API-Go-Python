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