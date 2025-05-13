#!/usr/bin/env python3
"""
Test script for IBKR account connection

This script tests the connection to IBKR and retrieves account and position information
to help diagnose connectivity issues.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.config import Config
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi
from src.utils.logger import log_debug, log_error, log_info, log_warning

def main():
    """Main function to test IBKR connection."""
    log_info("Starting IBKR account connection test")
    
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        config = Config.from_yaml(config_file)
        log_info(f"Loaded configuration from {config_file}")
        
        # Create IBKR API client
        api = IBKRIBInsyncApi(config)
        log_info(f"Connecting to IBKR at {api.host}:{api.port} with client ID {api.client_id}")
        
        # Connect to IBKR
        start_time = datetime.now()
        connected = api.connect()
        connect_duration = (datetime.now() - start_time).total_seconds()
        
        if not connected:
            log_error("Failed to connect to IBKR")
            return 1
        
        log_info(f"Successfully connected to IBKR in {connect_duration:.2f} seconds")
        
        # Process callbacks for a few seconds
        log_info("Processing callbacks...")
        for _ in range(5):
            api.handle_callbacks()
            time.sleep(0.5)
        
        # Get account summary
        log_info("Retrieving account summary...")
        account_summary = api.get_account_summary()
        
        # Print account summary
        print("\n=== Account Summary ===")
        if "error" in account_summary:
            print(f"Error: {account_summary['error']}")
        else:
            for key, value in sorted(account_summary.items()):
                if key in ['timestamp', 'account_id']:
                    print(f"{key}: {value}")
                elif isinstance(value, (int, float)) and key not in ['timestamp']:
                    print(f"{key}: ${value:,.2f}")
                elif value is not None:
                    print(f"{key}: {value}")
        
        # Get positions
        log_info("Retrieving positions...")
        positions = api.get_positions()
        
        # Print positions
        print("\n=== Positions ===")
        if not positions:
            print("No positions found")
        else:
            for symbol, position in sorted(positions.items()):
                print(f"{symbol}: {position['quantity']} shares @ ${position.get('avg_price', 0):.2f}")
                
                # Print additional position details
                for key, value in sorted(position.items()):
                    if key not in ['symbol', 'quantity', 'avg_price']:
                        if isinstance(value, (int, float)) and key not in ['timestamp']:
                            print(f"  {key}: ${value:,.2f}")
                        elif value is not None:
                            print(f"  {key}: {value}")
        
        # Save results to file
        output = {
            "timestamp": datetime.now().isoformat(),
            "connected": api.connected,
            "connection_details": {
                "host": api.host,
                "port": api.port,
                "client_id": api.client_id,
                "account_id": api.account_id
            },
            "account_summary": account_summary,
            "positions": positions
        }
        
        output_file = os.path.join(os.path.dirname(__file__), 'account_test_results.json')
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        log_info(f"Results saved to {output_file}")
        
        # Disconnect
        api.disconnect()
        log_info("Disconnected from IBKR")
        
        return 0
        
    except Exception as e:
        log_error(f"Error testing IBKR connection: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 