#!/usr/bin/env python3
"""
Direct Interactive Brokers API Connection Test using ib_insync

This script attempts to connect directly to TWS or IB Gateway using ib_insync
with multiple configurations to help diagnose connectivity issues.
"""

import sys
import time
import socket
import argparse
from datetime import datetime

try:
    from ib_insync import IB, util
    print("Successfully imported ib_insync")
except ImportError:
    print("Error: ib_insync not installed.")
    print("Please install with: pip install ib_insync")
    sys.exit(1)

def check_port_open(host, port, timeout=2):
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def try_connection(host, port, client_id, timeout=20, read_only=False, account=""):
    """Try to connect to TWS/Gateway with the given parameters."""
    print(f"\n{'='*80}")
    print(f" ATTEMPTING CONNECTION: {host}:{port} (Client ID: {client_id}, Timeout: {timeout}s)")
    print(f"{'='*80}")
    
    # First check if port is even open
    if not check_port_open(host, port):
        print(f"❌ Port {port} is CLOSED on {host}. TWS API not available at this port.")
        return False
    
    print(f"✅ Port {port} is OPEN on {host}")
    
    # Create new IB instance
    ib = IB()
    
    try:
        # Attempt connection
        print(f"Connecting to {host}:{port} with client ID {client_id}...")
        start_time = time.time()
        ib.connect(host, port, clientId=client_id, timeout=timeout, readonly=read_only)
        connect_time = time.time() - start_time
        
        if ib.isConnected():
            print(f"✅ CONNECTION SUCCESSFUL in {connect_time:.2f}s!")
            
            # Get TWS version
            print(f"TWS API Version: {ib.client.serverVersion()}")
            
            # Get client info
            client_id = ib.client.clientId
            print(f"Connected with Client ID: {client_id}")
            
            # Get account info
            managed_accounts = ib.managedAccounts()
            if managed_accounts:
                print(f"Available accounts: {', '.join(managed_accounts)}")
                
                # Try to get account summary for first account
                target_account = account or managed_accounts[0]
                print(f"\nGetting account summary for {target_account}...")
                
                try:
                    # Request account summary
                    account_values = ib.accountValues(target_account)
                    
                    # Print key account values
                    key_values = ['NetLiquidation', 'TotalCashValue', 'AvailableFunds']
                    print("\nKey Account Values:")
                    for tag in key_values:
                        values = [val.value for val in account_values if val.tag == tag and val.currency == 'USD']
                        if values:
                            print(f"  {tag}: ${values[0]}")
                    
                    # Try to get positions
                    portfolio = ib.portfolio()
                    if portfolio:
                        print(f"\nPortfolio: {len(portfolio)} positions")
                        for position in portfolio[:5]:  # Show up to 5 positions
                            print(f"  {position.contract.symbol}: {position.position} shares")
                        if len(portfolio) > 5:
                            print(f"  ... and {len(portfolio) - 5} more positions")
                    else:
                        print("\nNo positions found")
                    
                except Exception as e:
                    print(f"⚠️ Error getting account data: {str(e)}")
            else:
                print("❌ No managed accounts found")
            
            # Disconnect
            ib.disconnect()
            print("\nDisconnected from TWS")
            return True
        else:
            print("❌ Connection failed (isConnected() returned False)")
            return False
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        if ib.isConnected():
            ib.disconnect()
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        if ib.isConnected():
            ib.disconnect()
        return False

def connection_test_sequence():
    """Run a sequence of connection tests with various configurations."""
    # Configuration variations to try
    hosts = ["127.0.0.1", "localhost"]
    ports = [7497, 7496, 4001, 4002]
    client_ids = [1, 2, 5, 10]
    timeout_options = [10, 30]
    
    # Track successful configs
    successful_configs = []
    
    # First try user-provided values
    if args.host and args.port and args.client_id:
        print(f"\nTrying user-specified configuration:")
        success = try_connection(
            args.host,
            args.port, 
            args.client_id,
            timeout=args.timeout,
            read_only=args.readonly,
            account=args.account
        )
        if success:
            successful_configs.append({
                'host': args.host,
                'port': args.port,
                'client_id': args.client_id,
                'timeout': args.timeout,
                'read_only': args.readonly,
                'account': args.account
            })
            if not args.try_all:
                return successful_configs
    
    # Otherwise try common combinations
    print("\nTrying common configurations...")
    
    # Start with most common configurations
    common_configs = [
        {'host': '127.0.0.1', 'port': 7497, 'client_id': 1},  # Paper TWS
        {'host': '127.0.0.1', 'port': 7496, 'client_id': 1},  # Live TWS
        {'host': '127.0.0.1', 'port': 4001, 'client_id': 1},  # Paper Gateway
        {'host': '127.0.0.1', 'port': 4002, 'client_id': 1},  # Live Gateway
    ]
    
    for config in common_configs:
        success = try_connection(
            config['host'],
            config['port'],
            config['client_id'],
            timeout=args.timeout,
            read_only=args.readonly,
            account=args.account
        )
        if success:
            successful_configs.append({
                'host': config['host'],
                'port': config['port'],
                'client_id': config['client_id'],
                'timeout': args.timeout,
                'read_only': args.readonly,
                'account': args.account
            })
            if not args.try_all:
                return successful_configs
    
    # If still not successful and try_all is enabled, try more variations
    if args.try_all and not successful_configs:
        print("\nTrying additional configurations...")
        
        # Try alternative client IDs
        for port in ports:
            for client_id in client_ids[1:]:  # Skip client_id 1 as we already tried it
                success = try_connection(
                    "127.0.0.1",
                    port,
                    client_id,
                    timeout=args.timeout,
                    read_only=args.readonly,
                    account=args.account
                )
                if success:
                    successful_configs.append({
                        'host': "127.0.0.1",
                        'port': port,
                        'client_id': client_id,
                        'timeout': args.timeout,
                        'read_only': args.readonly,
                        'account': args.account
                    })
                    if not args.try_all:
                        return successful_configs
        
        # If still not successful, try with longer timeout
        if not successful_configs and args.timeout != timeout_options[1]:
            print("\nTrying with longer timeout...")
            for port in ports:
                success = try_connection(
                    "127.0.0.1",
                    port,
                    1,
                    timeout=timeout_options[1],
                    read_only=args.readonly,
                    account=args.account
                )
                if success:
                    successful_configs.append({
                        'host': "127.0.0.1",
                        'port': port,
                        'client_id': 1,
                        'timeout': timeout_options[1],
                        'read_only': args.readonly,
                        'account': args.account
                    })
                    if not args.try_all:
                        return successful_configs
    
    return successful_configs

def print_recommendations(successful_configs):
    """Print recommendations based on test results."""
    print("\n" + "="*80)
    print(" SUMMARY AND RECOMMENDATIONS")
    print("="*80)
    
    if successful_configs:
        print("\n✅ CONNECTION SUCCESSFUL!")
        print("\nWorking configuration(s):")
        
        for i, config in enumerate(successful_configs, 1):
            print(f"\nConfiguration {i}:")
            print(f"  Host: {config['host']}")
            print(f"  Port: {config['port']}")
            print(f"  Client ID: {config['client_id']}")
            print(f"  Timeout: {config['timeout']}s")
            print(f"  Read-only: {config['read_only']}")
            if config['account']:
                print(f"  Account: {config['account']}")
        
        print("\nUpdate your config.yaml file with the following:")
        
        # Use the first successful config for the recommendation
        config = successful_configs[0]
        print(f"""
ibkr:
  host: "{config['host']}"
  port: {config['port']}
  client_id: {config['client_id']}
  read_only: {str(config['read_only']).lower()}
  account: "{config['account']}"
  timeout: {config['timeout']}
  auto_reconnect: true
  max_rate: 45
""")
    else:
        print("\n❌ No successful connections found.")
        print("\nTroubleshooting steps:")
        print("1. Make sure TWS or IB Gateway is running and logged in")
        print("2. Check API settings in TWS:")
        print("   - Edit > Global Configuration > API > Settings")
        print("   - Enable 'ActiveX and Socket Clients'")
        print("   - Verify the Socket Port (7497 for paper, 7496 for live)")
        print("3. Check if Windows Firewall is blocking connections")
        print("   - Run tools/tws_connectivity_fix.py --apply")
        print("4. Restart TWS/Gateway completely after changing settings")
        print("5. Make sure you have the right account permissions")
        print("\nRun this script with --try-all to attempt all possible combinations.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test connection to Interactive Brokers API")
    parser.add_argument("--host", type=str, default="", help="API host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=0, help="API port (default: 7497)")
    parser.add_argument("--client-id", type=int, default=0, help="Client ID (default: 1)")
    parser.add_argument("--timeout", type=int, default=10, help="Connection timeout in seconds (default: 10)")
    parser.add_argument("--readonly", action="store_true", help="Connect in read-only mode")
    parser.add_argument("--account", type=str, default="", help="Account ID to use (default: first available)")
    parser.add_argument("--try-all", action="store_true", help="Try all possible configurations")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(" INTERACTIVE BROKERS API CONNECTION TEST")
    print("="*80)
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ib_insync version: {util.version()}")
    
    try:
        successful_configs = connection_test_sequence()
        print_recommendations(successful_configs)
        
        if successful_configs:
            sys.exit(0)
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1) 