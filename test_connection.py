#!/usr/bin/env python3
"""
Simple Test script for IBKR connection using ib_insync directly

This script connects to IBKR and retrieves account information directly.
"""

import sys
import time
from datetime import datetime

# Import ib_insync
try:
    from ib_insync import IB, util
    print("Successfully imported ib_insync")
except ImportError:
    print("Error: ib_insync not installed. Please install with: pip install ib_insync")
    sys.exit(1)

def main():
    """Test connection to IBKR using ib_insync directly."""
    print(f"Starting IBKR connection test at {datetime.now()}")
    
    # Configuration - Try paper trading port 7497
    host = "127.0.0.1"
    port = 7497  # Updated to paper trading port
    account_id = "DUE722383"  # Your paper trading account ID from the screenshot
    
    # Try with different client IDs
    for client_id in [0, 1, 2, 3, 4, 5]:
        # Create new IB instance for each attempt
        ib = IB()
        
        try:
            print(f"\nAttempting to connect to IBKR at {host}:{port} with client ID {client_id}...")
            ib.connect(host, port, clientId=client_id, timeout=10, readonly=True)
            
            if ib.isConnected():
                print(f"SUCCESS! Connected to IBKR using client ID {client_id}")
                
                # Get account information
                print("\nGetting account information...")
                
                # List managed accounts
                managed_accounts = ib.managedAccounts()
                if managed_accounts:
                    print(f"Managed accounts: {', '.join(managed_accounts)}")
                    account = managed_accounts[0]
                else:
                    print("No managed accounts found")
                    account = None
                
                # Get account summary
                if account:
                    try:
                        # Get account summary
                        account_values = ib.accountValues(account)
                        
                        # Focus on key account values
                        key_tags = ['NetLiquidation', 'EquityWithLoanValue', 'AvailableFunds', 'BuyingPower']
                        print("\nKey Account Values:")
                        for tag in key_tags:
                            values = [val.value for val in account_values 
                                    if val.tag == tag and val.currency == 'USD']
                            if values:
                                print(f"{tag}: ${values[0]}")
                        
                        # Get portfolio
                        portfolio = ib.portfolio()
                        print(f"\nPortfolio ({len(portfolio)} positions):")
                        for item in portfolio:
                            print(f"{item.contract.symbol}: {item.position} shares @ ${item.averageCost:.2f}")
                    
                    except Exception as e:
                        print(f"Error getting account data: {str(e)}")
                
                # Disconnect and return success
                ib.disconnect()
                print(f"Disconnected from IBKR")
                return 0
                
        except Exception as e:
            print(f"Connection attempt with client ID {client_id} failed: {str(e)}")
            if ib.isConnected():
                ib.disconnect()
    
    # If we get here, all connection attempts failed
    print("\nFailed to connect to IBKR with any client ID")
    print("\nTroubleshooting tips:")
    print("1. Make sure TWS is running and API connections are enabled")
    print("2. In TWS, go to Edit > Global Configuration > API > Settings")
    print("   - Ensure 'Enable ActiveX and Socket Clients' is checked")
    print("   - 'Allow connections from localhost only' should be checked")
    print("   - Check that Socket Port is set to 7497 for paper trading")
    print("   - Make sure your client ID doesn't conflict with other connections")
    print("3. Try restarting TWS after changing settings")
    print("4. Make sure any firewalls or security software are not blocking the connection")
    print("5. Check if 'Trusted IPs' needs to be configured")
    
    return 1

if __name__ == "__main__":
    sys.exit(main()) 