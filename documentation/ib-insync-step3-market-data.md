# IB Insync Implementation: Step 3 - Market Data Retrieval

## Introduction

This guide covers implementing market data retrieval functionality for the IB Insync API wrapper. We'll implement real-time market data for stocks and option chains.

## Market Data Methods

Add the following methods to the `IBKRIBInsyncApi` class:

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

## Testing Market Data Functionality

Create a file `tests/features/market_data.feature` with Gherkin scenarios:

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

Create a test implementation at `tests/test_ibkr_market_data.py`:

```python
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

## Testing

Run the tests using pytest:

```bash
pytest tests/test_ibkr_market_data.py -v
```

## Next Steps

After implementing market data functionality, proceed to [Step 4](ib-insync-step4-order-management.md) to implement order management functionality. 