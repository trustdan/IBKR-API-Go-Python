#!/usr/bin/env python3
"""
Direct config test script for IBKR connection

This script extracts config settings directly from config.yaml and attempts to connect.
"""

import sys
import time
import yaml
from datetime import datetime

# Import ib_insync
try:
    from ib_insync import IB, util
    print("Successfully imported ib_insync")
except ImportError:
    print("Error: ib_insync not installed. Please install with: pip install ib_insync")
    sys.exit(1)

def main():
    """Test IBKR connection using settings from config.yaml."""
    print(f"Starting direct config IBKR connection test at {datetime.now()}")
    
    # Load config file
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("Successfully loaded config.yaml")
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return 1
    
    # Extract IBKR settings
    ibkr_config = config.get('ibkr', {})
    host = ibkr_config.get('host', '127.0.0.1')
    port = ibkr_config.get('port', 7497)
    client_id = ibkr_config.get('client_id', 1)
    read_only = ibkr_config.get('read_only', False)
    account = ibkr_config.get('account', '')
    timeout = ibkr_config.get('timeout', 20)
    
    print(f"Using config settings: host={host}, port={port}, client_id={client_id}, read_only={read_only}")
    
    # Create IB instance and try to connect
    ib = IB()
    
    try:
        print(f"Connecting to IBKR at {host}:{port} with client ID {client_id}...")
        ib.connect(host, port, clientId=client_id, readonly=read_only, timeout=timeout)
        
        if not ib.isConnected():
            print("Connection failed - IB reports not connected")
            return 1
        
        print(f"SUCCESS! Connected to IBKR")
        
        # Verify connection by getting managed accounts
        managed_accounts = ib.managedAccounts()
        print(f"Managed accounts: {', '.join(managed_accounts) if managed_accounts else 'None'}")
        
        # Use first account or specified account
        active_account = account if account else (managed_accounts[0] if managed_accounts else None)
        if not active_account:
            print("No account available")
            ib.disconnect()
            return 1
        
        print(f"Using account: {active_account}")
        
        # Get account summary
        print("Requesting account summary...")
        account_values = ib.accountValues(active_account)
        
        # Print key account values
        key_tags = ['NetLiquidation', 'EquityWithLoanValue', 'AvailableFunds', 'BuyingPower']
        print("\nKey Account Values:")
        for tag in key_tags:
            values = [val.value for val in account_values 
                     if val.tag == tag and val.currency == 'USD']
            if values:
                print(f"{tag}: ${values[0]}")
        
        # Retrieve current positions
        print("\nRetrieving positions...")
        positions = ib.positions(active_account)
        if positions:
            print(f"Found {len(positions)} positions:")
            for pos in positions:
                print(f"{pos.contract.symbol}: {pos.position} shares @ ${pos.avgCost:.2f}")
        else:
            print("No positions found")
        
        # Disconnect
        ib.disconnect()
        print("Test completed successfully. Connection works!")
        return 0
        
    except Exception as e:
        print(f"Connection error: {str(e)}")
        
        if ib.isConnected():
            ib.disconnect()
            
        print("\nTroubleshooting steps:")
        print("1. Verify TWS/Gateway is running and fully initialized")
        print("2. In TWS, go to Edit > Global Configuration > API > Settings")
        print("   - Make sure 'Enable ActiveX and Socket Clients' is checked")
        print("   - Confirm port number matches your config.yaml (port 7497)")
        print("3. Try restarting TWS completely")
        print("4. Check Windows Firewall settings")
        print("5. Make sure your TWS client has API access permissions")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 