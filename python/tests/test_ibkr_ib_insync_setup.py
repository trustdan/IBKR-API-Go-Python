import pytest
from pytest_bdd import given, when, then, scenarios
from unittest.mock import MagicMock, patch

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.brokers import get_broker_api

# Load scenarios from the feature file
scenarios('features/setup.feature')

# Fixtures
@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=Config)
    # Default parameters
    config.IBKR_HOST = "127.0.0.1"
    config.IBKR_PORT = 7497
    config.IBKR_CLIENT_ID = 1
    config.IBKR_ACCOUNT_ID = ""
    config.IBKR_READ_ONLY = False
    return config

@pytest.fixture
def mock_custom_config():
    """Create a mock configuration with custom values."""
    config = MagicMock(spec=Config)
    # Custom parameters
    config.IBKR_HOST = "192.168.1.1"
    config.IBKR_PORT = 4001
    config.IBKR_CLIENT_ID = 5
    config.IBKR_ACCOUNT_ID = "DU12345"
    config.IBKR_READ_ONLY = True
    return config

# Step definitions for default parameters
@given("configuration with default connection parameters")
def config_with_defaults(mock_config):
    return mock_config

@when("I create an IB Insync API instance")
def create_api_instance(mock_config):
    with patch('src.brokers.ibkr_ib_insync.IB'):
        return IBKRIBInsyncApi(mock_config)

@then("the API should be initialized with default values")
def check_default_initialization(create_api_instance):
    api = create_api_instance
    assert api.host == "127.0.0.1"
    assert api.port == 7497
    assert api.client_id == 1
    assert api.account_id == ""
    assert api.read_only == False
    assert api.connected == False
    assert api.orders == {}
    assert api.positions == {}

# Step definitions for custom parameters
@given("configuration with custom connection parameters")
def config_with_custom_params(mock_custom_config):
    return mock_custom_config

@then("the API should be initialized with custom values")
def check_custom_initialization(mock_custom_config):
    with patch('src.brokers.ibkr_ib_insync.IB'):
        api = IBKRIBInsyncApi(mock_custom_config)
        assert api.host == "192.168.1.1"
        assert api.port == 4001
        assert api.client_id == 5
        assert api.account_id == "DU12345"
        assert api.read_only == True
        assert api.connected == False

# Step definitions for factory method test
@given("I need a broker API instance")
def need_broker_api(mock_config):
    return mock_config

@when("I call the factory method with use_ib_insync=True")
def call_factory_method(mock_config):
    with patch('src.brokers.IBKRIBInsyncApi') as mock_insync_api:
        mock_insync_api.return_value = "IB_INSYNC_INSTANCE"
        return get_broker_api(mock_config, use_ib_insync=True)

@then("it should return an IB Insync API instance")
def check_factory_returns_insync(call_factory_method):
    assert call_factory_method == "IB_INSYNC_INSTANCE" 