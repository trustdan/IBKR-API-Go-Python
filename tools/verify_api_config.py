#!/usr/bin/env python3
"""
Interactive Brokers API Configuration Verification Tool

This utility verifies the configuration settings for connecting to Interactive Brokers API,
checking for common issues and suggesting improvements.
"""

import os
import sys
import yaml
import socket
from pathlib import Path

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

def find_config_file():
    """Find the configuration file in common locations."""
    possible_locations = [
        "config.yaml",
        "config/config.yaml",
        "../config.yaml",
        "../config/config.yaml",
        "config.yml",
        "config/config.yml"
    ]
    
    for location in possible_locations:
        path = Path(location)
        if path.is_file():
            return str(path.absolute())
    
    return None

def load_config(file_path=None):
    """Load the configuration file."""
    if file_path is None:
        file_path = find_config_file()
        
    if file_path is None or not os.path.exists(file_path):
        print_error(f"Configuration file not found. Checked common locations.")
        return None
    
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        print_success(f"Loaded configuration from {file_path}")
        return config
    except Exception as e:
        print_error(f"Error loading configuration: {str(e)}")
        return None

def check_ibkr_config(config):
    """Check the IBKR configuration section for common issues."""
    if config is None:
        return False
    
    print_header("IBKR API Configuration Check")
    
    # Check if IBKR section exists
    if 'ibkr' not in config:
        print_error("Missing 'ibkr' section in configuration")
        print_info("Your config.yaml should have an 'ibkr' section with connection details.")
        return False
    
    ibkr_config = config['ibkr']
    issues_found = False
    
    # Required fields
    required_fields = ['host', 'port', 'client_id']
    for field in required_fields:
        if field not in ibkr_config:
            print_error(f"Missing required field: '{field}'")
            issues_found = True
    
    # Host check
    if 'host' in ibkr_config:
        host = ibkr_config['host']
        if host not in ['127.0.0.1', 'localhost']:
            print_warning(f"Host is set to '{host}'. For local TWS, use '127.0.0.1' or 'localhost'")
            issues_found = True
        else:
            print_success(f"Host is properly set to '{host}'")
    
    # Port check
    if 'port' in ibkr_config:
        port = ibkr_config['port']
        if port not in [7497, 7496, 4001, 4002]:
            print_warning(f"Port is set to non-standard value: {port}")
            print_info("Standard ports: 7497 (Paper TWS), 7496 (Live TWS), 4001 (Paper Gateway), 4002 (Live Gateway)")
        else:
            port_descriptions = {
                7497: "TWS Paper Trading (default)",
                7496: "TWS Live Trading (default)",
                4001: "IB Gateway Paper Trading (default)",
                4002: "IB Gateway Live Trading (default)"
            }
            print_success(f"Port is set to {port} - {port_descriptions.get(port)}")
            
            # Check if port is actually open
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    print_success(f"Port {port} is OPEN - TWS API is accessible")
                else:
                    print_error(f"Port {port} is CLOSED - TWS may not be running or API not enabled")
                    issues_found = True
                sock.close()
            except Exception as e:
                print_error(f"Error checking port {port}: {str(e)}")
                issues_found = True
    
    # Client ID check
    if 'client_id' in ibkr_config:
        client_id = ibkr_config['client_id']
        if client_id == 0:
            print_warning("Client ID is set to 0, which may cause issues with some TWS versions")
            issues_found = True
        elif client_id < 0:
            print_error(f"Client ID is negative: {client_id}. Must be a positive integer.")
            issues_found = True
        else:
            print_success(f"Client ID is set to {client_id}")
    
    # Account check
    if 'account' in ibkr_config:
        account = ibkr_config['account']
        if account and not (account.startswith('U') or account.startswith('DU')):
            print_warning(f"Account ID format looks unusual: '{account}'")
            print_info("IBKR account IDs typically start with 'U' (live) or 'DU' (paper)")
            issues_found = True
        elif not account:
            print_info("Account ID is empty. System will use the first account available in TWS.")
        else:
            print_success(f"Account ID is set to '{account}'")
    else:
        print_warning("No 'account' field found. System will use the first account available in TWS.")
    
    # Timeout check
    if 'timeout' in ibkr_config:
        timeout = ibkr_config['timeout']
        if timeout < 10:
            print_warning(f"Timeout is set to {timeout} seconds, which may be too short")
            print_info("Recommended timeout: 20-30 seconds")
            issues_found = True
        elif timeout > 60:
            print_warning(f"Timeout is set to {timeout} seconds, which may be unnecessarily long")
            issues_found = True
        else:
            print_success(f"Timeout is set to {timeout} seconds")
    else:
        print_warning("No 'timeout' specified. Will use default value.")
    
    # Auto reconnect check
    if 'auto_reconnect' in ibkr_config:
        if ibkr_config['auto_reconnect']:
            print_success("Auto reconnect is enabled")
        else:
            print_warning("Auto reconnect is disabled. Enable for more robust connections.")
            issues_found = True
    else:
        print_warning("No 'auto_reconnect' setting found. Recommend adding 'auto_reconnect: true'")
        issues_found = True
    
    # Read-only check
    if 'read_only' in ibkr_config:
        if ibkr_config['read_only']:
            print_warning("API is in read-only mode. Trading will not be possible.")
        else:
            print_success("API is in trading mode (not read-only)")
    
    if not issues_found:
        print_success("Configuration looks good! No issues detected.")
    
    return not issues_found

def check_config_files():
    """Check for existence of all necessary configuration files."""
    print_header("Configuration Files Check")
    
    config_files = {
        "config.yaml": "Main configuration file",
        "config.toml": "Alternative configuration file",
    }
    
    found_files = []
    for file_name, description in config_files.items():
        if os.path.exists(file_name):
            print_success(f"Found {file_name} - {description}")
            found_files.append(file_name)
        else:
            print_warning(f"Missing {file_name} - {description}")
    
    if not found_files:
        print_error("No configuration files found in current directory.")
        print_info("Create a configuration file based on the templates in the documentation.")
        return False
    
    return True

def suggest_improvements(config):
    """Suggest improvements to the configuration."""
    if config is None or 'ibkr' not in config:
        return
    
    print_header("Configuration Improvement Suggestions")
    
    ibkr_config = config['ibkr']
    suggestions = []
    
    # Suggest read-only mode for initial testing
    if 'read_only' not in ibkr_config or not ibkr_config.get('read_only', False):
        suggestions.append(
            "During initial setup and testing, consider using read-only mode:\n"
            "ibkr:\n"
            "  read_only: true"
        )
    
    # Suggest higher timeout for slow connections
    if 'timeout' not in ibkr_config or ibkr_config.get('timeout', 0) < 20:
        suggestions.append(
            "For slow or unstable connections, increase the timeout value:\n"
            "ibkr:\n"
            "  timeout: 30"
        )
    
    # Suggest enabling auto reconnection
    if 'auto_reconnect' not in ibkr_config or not ibkr_config.get('auto_reconnect', False):
        suggestions.append(
            "Enable automatic reconnection for better reliability:\n"
            "ibkr:\n"
            "  auto_reconnect: true"
        )
    
    # Suggest API rate limit
    if 'max_rate' not in ibkr_config:
        suggestions.append(
            "Specify API request rate limit to prevent throttling:\n"
            "ibkr:\n"
            "  max_rate: 45  # Maximum API requests per second (IB's limit is 50)"
        )
    
    if suggestions:
        print_info("Consider the following improvements to your configuration:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n--- Suggestion {i} ---")
            print(suggestion)
    else:
        print_success("Your configuration already includes all recommended settings!")

def main():
    """Main function to check TWS API configuration."""
    print_header("Interactive Brokers API Configuration Verification Tool")
    
    # Get config file path from command line argument, or find automatically
    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    check_config_files()
    config = load_config(config_file)
    check_ibkr_config(config)
    suggest_improvements(config)
    
    print_header("Verification Complete")
    print("For detailed connection troubleshooting, run: python tools/check_tws_connection.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 