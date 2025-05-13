#!/usr/bin/env python3
"""
Interactive Brokers Account Permissions Validation Tool

This utility checks if your IBKR account has the necessary permissions for API trading,
including options trading, data subscriptions, and API access.
"""

import sys
import yaml
import os
from datetime import datetime

try:
    from ib_insync import IB, util, ContractDetails
    print("Successfully imported ib_insync")
except ImportError:
    print("Error: ib_insync not installed. Please install with: pip install ib_insync")
    sys.exit(1)

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_warning(message):
    """Print a warning message."""
    print(f"⚠️ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print an informational message."""
    print(f"ℹ️ {message}")

def load_config():
    """Load the IBKR configuration from config file."""
    try:
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                
            if 'ibkr' in config:
                ibkr_config = config['ibkr']
                return {
                    'host': ibkr_config.get('host', '127.0.0.1'),
                    'port': ibkr_config.get('port', 7497),
                    'client_id': ibkr_config.get('client_id', 1),
                    'account': ibkr_config.get('account', ''),
                    'timeout': ibkr_config.get('timeout', 20)
                }
        return {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'account': '',
            'timeout': 20
        }
    except Exception as e:
        print_error(f"Error loading config: {str(e)}")
        return {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'account': '',
            'timeout': 20
        }

def connect_to_tws(config):
    """Connect to TWS/Gateway using the configuration."""
    ib = IB()
    print_info(f"Connecting to TWS at {config['host']}:{config['port']} (client ID: {config['client_id']})...")
    
    try:
        ib.connect(
            host=config['host'],
            port=config['port'],
            clientId=config['client_id'],
            readonly=True,  # Use read-only mode for validation
            timeout=config['timeout']
        )
        
        if ib.isConnected():
            print_success("Successfully connected to TWS/Gateway")
            return ib
        else:
            print_error("Connection to TWS/Gateway failed")
            return None
    except Exception as e:
        print_error(f"Error connecting to TWS/Gateway: {str(e)}")
        print_info("Make sure TWS is running and API connections are enabled")
        return None

def validate_account_permissions(ib, config):
    """Validate account permissions for API trading."""
    if not ib or not ib.isConnected():
        return False
    
    print_header("Account Permissions Validation")
    
    # Check managed accounts
    managed_accounts = ib.managedAccounts()
    if not managed_accounts:
        print_error("No managed accounts found")
        return False
    
    print_success(f"Found {len(managed_accounts)} managed account(s): {', '.join(managed_accounts)}")
    
    # Use configured account or first available
    account = config['account'] if config['account'] else managed_accounts[0]
    print_info(f"Using account: {account}")
    
    # Check if account is paper or live
    is_paper = account.startswith('DU')
    account_type = 'Paper Trading' if is_paper else 'Live Trading'
    print_info(f"Account type: {account_type}")
    
    # Get account summary
    try:
        account_values = ib.accountValues(account)
        if not account_values:
            print_error("No account data received")
            return False
        
        print_success(f"Retrieved {len(account_values)} account values")
        
        # Check for specific permissions and values
        permissions = {}
        trading_type = None
        
        for value in account_values:
            # Check Trading Type
            if value.tag == 'AccountType' and value.value:
                trading_type = value.value
            
            # Check specific permissions
            if value.tag == 'OptionTradingLevel' and value.value:
                permissions['options'] = int(value.value) if value.value.isdigit() else value.value
            
            # Check for API connection permission 
            if value.tag == 'TradingPermissions' and value.value:
                perms = value.value.split(',')
                permissions['api'] = 'API' in perms
        
        # Display trading type
        if trading_type:
            print_success(f"Account trading type: {trading_type}")
        else:
            print_warning("Could not determine account trading type")
        
        # Display options permissions
        if 'options' in permissions:
            option_levels = {
                '1': 'Covered Calls/Puts, Buy Calls/Puts',
                '2': 'Level 1 + Spreads',
                '3': 'Level 2 + Naked Shorts',
                '4': 'Level 3 + Advanced Options'
            }
            opt_level = permissions['options']
            if isinstance(opt_level, int) or opt_level.isdigit():
                level_desc = option_levels.get(str(opt_level), 'Unknown')
                print_success(f"Options trading level: {opt_level} - {level_desc}")
                
                # Check if option spread trading is allowed
                if int(opt_level) >= 2:
                    print_success("Account has permission for option spreads (Level ≥ 2)")
                else:
                    print_error("Account lacks permission for option spreads (requires Level 2+)")
            else:
                print_warning(f"Options trading level: {opt_level}")
        else:
            print_warning("Could not determine options trading permissions")
            
        # Display API permissions
        if 'api' in permissions:
            if permissions['api']:
                print_success("Account has API trading permission")
            else:
                print_error("Account does NOT have API trading permission")
        else:
            print_warning("Could not determine API trading permissions")
        
        # Check market data
        try:
            print_info("Checking market data permissions...")
            # Try to get snapshot data for SPY to check market data
            from ib_insync import Stock
            contract = Stock('SPY', 'SMART', 'USD')
            qualified = ib.qualifyContracts(contract)
            if qualified:
                ticker = ib.reqMktData(qualified[0])
                
                # Wait briefly for data
                for _ in range(10):
                    ib.sleep(0.2)
                    if not util.isNan(ticker.last) or not util.isNan(ticker.bid) or not util.isNan(ticker.ask):
                        break
                
                if (not util.isNan(ticker.last) and ticker.last > 0) or \
                   (not util.isNan(ticker.bid) and ticker.bid > 0) or \
                   (not util.isNan(ticker.ask) and ticker.ask > 0):
                    print_success("Market data permissions verified")
                else:
                    print_warning("Market data might be delayed or unavailable")
                
                # Cancel to clean up
                ib.cancelMktData(qualified[0])
            else:
                print_warning("Could not verify market data permissions")
        except Exception as e:
            print_warning(f"Error checking market data permissions: {str(e)}")
        
        # Check options data
        try:
            print_info("Checking options data permissions...")
            from ib_insync import Option
            # Try a generic SPY option - just for checking permissions
            next_month = util.getNextOptionExpiry()
            option = Option('SPY', next_month, 400, 'C', 'SMART')
            qualified = ib.qualifyContracts(option)
            
            if qualified:
                print_success("Options data permissions verified")
            else:
                print_warning("Could not verify options data permissions")
        except Exception as e:
            print_warning(f"Error checking options data permissions: {str(e)}")
        
        return True
        
    except Exception as e:
        print_error(f"Error validating account permissions: {str(e)}")
        return False

def check_trading_hours(ib):
    """Check current trading hours status."""
    print_header("Trading Hours Check")
    
    if not ib or not ib.isConnected():
        return
    
    try:
        from ib_insync import Stock, ContractDetails
        
        # Try to check SPY for trading hours
        contract = Stock('SPY', 'SMART', 'USD')
        qualified = ib.qualifyContracts(contract)
        
        if qualified:
            details = ib.reqContractDetails(qualified[0])
            
            if details and isinstance(details[0], ContractDetails):
                detail = details[0]
                trading_hours = detail.tradingHours if hasattr(detail, 'tradingHours') else None
                liquid_hours = detail.liquidHours if hasattr(detail, 'liquidHours') else None
                
                print_info("Trading hours information:")
                if trading_hours:
                    zones = trading_hours.split(';')
                    for zone in zones:
                        if zone and '-' in zone:
                            print(f"  {zone}")
                
                # Try to determine if market is open
                try:
                    now = datetime.now()
                    is_open = False
                    
                    if liquid_hours:
                        # Format is typically: 20230512:0930-1600;20230515:0930-1600
                        today = now.strftime("%Y%m%d")
                        for schedule in liquid_hours.split(';'):
                            if today in schedule:
                                times = schedule.split(':')[1].split('-')
                                open_time = datetime.strptime(f"{today}{times[0]}", "%Y%m%d%H%M")
                                close_time = datetime.strptime(f"{today}{times[1]}", "%Y%m%d%H%M")
                                
                                if open_time <= now <= close_time:
                                    is_open = True
                                    break
                        
                        if is_open:
                            print_success("Market is currently OPEN for trading")
                        else:
                            print_warning("Market is currently CLOSED for trading")
                    else:
                        print_warning("Could not determine if market is open")
                except Exception as e:
                    print_warning(f"Error determining market hours: {str(e)}")
            else:
                print_warning("Could not get trading hours information")
        else:
            print_warning("Could not get trading hours information")
            
    except Exception as e:
        print_error(f"Error checking trading hours: {str(e)}")

def main():
    """Main function to validate IBKR account permissions."""
    print_header("Interactive Brokers Account Permissions Validation Tool")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    config = load_config()
    
    # Connect to TWS
    ib = connect_to_tws(config)
    if not ib:
        print_error("Could not connect to TWS. Cannot validate account permissions.")
        return 1
    
    try:
        # Validate account permissions
        validate_account_permissions(ib, config)
        
        # Check trading hours
        check_trading_hours(ib)
        
        # Disconnect from TWS
        ib.disconnect()
        print_success("Disconnected from TWS")
        
        print_header("Validation Complete")
        print("For connection troubleshooting, run: python tools/check_tws_connection.py")
        print("For configuration verification, run: python tools/verify_api_config.py")
        
        return 0
    except Exception as e:
        print_error(f"Unexpected error during validation: {str(e)}")
        if ib and ib.isConnected():
            ib.disconnect()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 