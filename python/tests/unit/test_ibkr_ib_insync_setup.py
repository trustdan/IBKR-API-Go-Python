import unittest
from unittest.mock import MagicMock, patch

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi


class TestIBKRIBInsyncSetup(unittest.TestCase):
    """Test the initial setup of the IBKRIBInsyncApi class."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_config = MagicMock(spec=Config)
        self.mock_config.IBKR_HOST = "127.0.0.1"
        self.mock_config.IBKR_PORT = 7497
        self.mock_config.IBKR_CLIENT_ID = 1
        self.mock_config.IBKR_ACCOUNT_ID = "DU12345"
        self.mock_config.IBKR_READ_ONLY = False

    def test_init(self):
        """Test initialization of the API class."""
        # Patch the IB class to avoid actual connection attempts
        with patch('src.brokers.ibkr_ib_insync.IB') as mock_ib:
            api = IBKRIBInsyncApi(self.mock_config)
            
            # Check initialization of instance variables
            self.assertEqual(api.host, "127.0.0.1")
            self.assertEqual(api.port, 7497)
            self.assertEqual(api.client_id, 1)
            self.assertEqual(api.account_id, "DU12345")
            self.assertEqual(api.read_only, False)
            self.assertFalse(api.connected)
            
            # Check that IB instance was created
            mock_ib.assert_called_once()
            
            # Check initial state of orders and positions
            self.assertEqual(api.orders, {})
            self.assertEqual(api.positions, {})

    def test_factory_method(self):
        """Test that the factory method returns the correct implementation."""
        from src.brokers import get_broker_api
        from src.brokers.ibkr_api import IBKRApi
        
        # Test with use_ib_insync=True
        with patch('src.brokers.IBKRIBInsyncApi') as mock_insync_api:
            api = get_broker_api(self.mock_config, use_ib_insync=True)
            mock_insync_api.assert_called_once_with(self.mock_config)
        
        # Test with use_ib_insync=False
        with patch('src.brokers.IBKRApi') as mock_api:
            api = get_broker_api(self.mock_config, use_ib_insync=False)
            mock_api.assert_called_once_with(self.mock_config)


if __name__ == '__main__':
    unittest.main() 