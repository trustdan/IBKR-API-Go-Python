import unittest
from unittest.mock import MagicMock, patch
import time

from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from ib_insync import Trade, OrderStatus, Execution, CommissionReport

class TestIBKRConnection(unittest.TestCase):
    
    def setUp(self):
        # Mock the config
        self.config = MagicMock()
        self.config.IBKR_HOST = "127.0.0.1"
        self.config.IBKR_PORT = 7497
        self.config.IBKR_CLIENT_ID = 1
        
        # Set up patches
        self.ib_patcher = patch('src.brokers.ibkr_ib_insync.IB')
        self.mock_ib_class = self.ib_patcher.start()
        self.mock_ib = self.mock_ib_class.return_value
        
        # Create the API instance
        self.api = IBKRIBInsyncApi(self.config)
        
        # Configure mock IB behavior
        self.mock_ib.isConnected.return_value = True
        self.mock_ib.managedAccounts.return_value = ["DU12345"]
        self.mock_ib.client.getReqId.return_value = 10
    
    def tearDown(self):
        self.ib_patcher.stop()
    
    def test_connect_success(self):
        # Test successful connection
        result = self.api.connect()
        
        # Verify results
        self.assertTrue(result)
        self.assertTrue(self.api.connected)
        self.mock_ib.connect.assert_called_once_with(
            host="127.0.0.1",
            port=7497,
            clientId=1,
            readonly=False,
            account="",
            timeout=20
        )
    
    def test_connect_failure(self):
        # Set up failure scenario
        self.mock_ib.isConnected.return_value = False
        
        # Test connection
        result = self.api.connect()
        
        # Verify results
        self.assertFalse(result)
        self.assertFalse(self.api.connected)
    
    def test_connect_exception(self):
        # Set up exception scenario
        self.mock_ib.connect.side_effect = Exception("Connection refused")
        
        # Test connection
        result = self.api.connect()
        
        # Verify results
        self.assertFalse(result)
        self.assertFalse(self.api.connected)
    
    def test_disconnect(self):
        # Set up initial state
        self.api.connected = True
        
        # Call disconnect
        self.api.disconnect()
        
        # Verify results
        self.assertFalse(self.api.connected)
        self.mock_ib.disconnect.assert_called_once()
    
    def test_event_handlers(self):
        # Connect and verify event handlers were added
        self.api.connect()
        
        # Verify event handlers were set up
        handlers = [
            self.mock_ib.connectedEvent.__iadd__,
            self.mock_ib.disconnectedEvent.__iadd__,
            self.mock_ib.orderStatusEvent.__iadd__,
            self.mock_ib.execDetailsEvent.__iadd__,
            self.mock_ib.commissionReportEvent.__iadd__,
            self.mock_ib.positionEvent.__iadd__,
            self.mock_ib.errorEvent.__iadd__
        ]
        
        for handler in handlers:
            self.assertEqual(handler.call_count, 1)
    
    def test_on_error_handling(self):
        # Test various error codes
        test_cases = [
            {"code": 502, "expected_connected": False, "description": "Connection issue"},
            {"code": 1100, "expected_connected": False, "description": "Connection lost"},
            {"code": 2104, "expected_connected": True, "description": "Market data warning"},
            {"code": 9999, "expected_connected": True, "description": "Other error"}
        ]
        
        for case in test_cases:
            # Reset the state
            self.api.connected = True
            
            # Call the error handler
            self.api._on_error(1, case["code"], case["description"], None)
            
            # Verify the connected state
            self.assertEqual(self.api.connected, case["expected_connected"], 
                            f"Failed for error code {case['code']}")
    
    def test_handle_callbacks(self):
        # Set up test
        self.api.connected = True
        
        # Call the method
        self.api.handle_callbacks()
        
        # Verify ib.sleep was called
        self.mock_ib.sleep.assert_called_once_with(0)
        
        # Test exception case
        self.mock_ib.sleep.side_effect = Exception("Test error")
        self.api.handle_callbacks()  # Should not raise an exception
        
        # Test not connected case
        self.api.connected = False
        self.mock_ib.sleep.reset_mock()
        self.api.handle_callbacks()
        self.mock_ib.sleep.assert_not_called()

if __name__ == '__main__':
    unittest.main() 