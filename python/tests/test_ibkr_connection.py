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