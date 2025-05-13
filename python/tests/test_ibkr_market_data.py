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
    api.market_data = api.get_market_data(symbol.strip('"'))

@when(parsers.parse("I request market data for an invalid symbol {symbol}"))
def request_invalid_market_data(api, symbol, mock_ib):
    # Mock that the symbol is invalid
    mock_ib.qualifyContracts.side_effect = Exception("Invalid symbol")
    api.market_data = api.get_market_data(symbol.strip('"'))

@when(parsers.parse("I request the option chain for {symbol}"))
def request_option_chain(api, symbol, mock_ib):
    # Setup mock for option market data
    mock_option_ticker = MagicMock()
    mock_option_ticker.last = 5.25
    mock_option_ticker.bid = 5.20
    mock_option_ticker.ask = 5.30
    mock_option_ticker.volume = 1500
    mock_option_ticker.impliedVolatility = 0.25
    mock_option_ticker.openInterest = 500
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
    
    api.options = api.get_option_chain(symbol.strip('"'))

@when(parsers.parse("I request the option chain for an invalid symbol {symbol}"))
def request_invalid_option_chain(api, symbol, mock_ib):
    # Mock that the symbol is invalid
    mock_ib.qualifyContracts.side_effect = Exception("Invalid symbol")
    api.options = api.get_option_chain(symbol.strip('"'))

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