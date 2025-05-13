#!/usr/bin/env python3
"""
Interactive Brokers TWS API Connection Diagnostic Tool

This utility checks for TWS API connectivity and diagnoses common connection issues.
It helps troubleshoot problems with connecting to the Interactive Brokers API.
"""

import socket
import subprocess
import sys
import time
import os
from datetime import datetime

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def print_section(message):
    """Print a section header."""
    print(f"\n--- {message} ---")

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

def check_port(host, port, timeout=3):
    """Check if a port is open on the given host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        start_time = time.time()
        result = sock.connect_ex((host, port))
        duration = time.time() - start_time
        
        if result == 0:
            print_success(f"Port {port} is OPEN on {host} (connected in {duration:.2f}s)")
            return True
        else:
            print_error(f"Port {port} is CLOSED on {host} (error code: {result})")
            return False
    except socket.error as e:
        print_error(f"Error checking port {port}: {e}")
        return False
    finally:
        sock.close()

def check_tws_ports():
    """Check common TWS API ports."""
    print_section("TWS API Port Check")
    
    host = "127.0.0.1"
    ports = {
        7497: "TWS Paper Trading (default)",
        7496: "TWS Live Trading (default)",
        4001: "IB Gateway Paper Trading (default)",
        4002: "IB Gateway Live Trading (default)",
        5000: "Custom port (sometimes used)",
    }
    
    open_ports = []
    for port, description in ports.items():
        print(f"Testing port {port} ({description})...")
        if check_port(host, port):
            open_ports.append(port)
    
    return open_ports

def check_windows_firewall():
    """Check if Windows Firewall might be blocking TWS API connections."""
    print_section("Windows Firewall Check")
    
    if os.name != 'nt':
        print_warning("Not running on Windows - skipping Windows Firewall check.")
        return
    
    try:
        # Check if Windows Firewall is enabled
        firewall_output = subprocess.check_output(
            ["netsh", "advfirewall", "show", "allprofiles"], 
            universal_newlines=True
        )
        
        firewall_status = "unknown"
        for line in firewall_output.splitlines():
            if "State" in line and "ON" in line:
                firewall_status = "ON"
                break
            elif "State" in line and "OFF" in line:
                firewall_status = "OFF"
                break
        
        if firewall_status == "ON":
            print_info("Windows Firewall is ENABLED.")
            print_info("If you're having connection issues, try adding firewall exceptions for TWS and the API ports.")
            print("    1. Run Windows Defender Firewall with Advanced Security as administrator")
            print("    2. Select 'Inbound Rules' > 'New Rule'")
            print("    3. Choose 'Port' > 'TCP' > Enter the TWS API port (7497, etc.)")
            print("    4. Allow the connection > Apply to all profiles > Name it 'TWS API'")
        elif firewall_status == "OFF":
            print_success("Windows Firewall is DISABLED. This should not block TWS API connections.")
        else:
            print_warning("Could not determine Windows Firewall status.")
    
    except subprocess.CalledProcessError as e:
        print_error(f"Error checking Windows Firewall: {e}")
    except Exception as e:
        print_error(f"Error checking Windows Firewall: {e}")

def check_tws_running():
    """Check if TWS or IB Gateway appears to be running."""
    print_section("TWS Process Check")
    
    tws_process_names = ["tws.exe", "ibgateway.exe", "javaw.exe"]
    
    if os.name == 'nt':  # Windows
        try:
            tasklist_output = subprocess.check_output(
                ["tasklist"], universal_newlines=True
            )
            
            tws_processes = []
            for process in tws_process_names:
                if process.lower() in tasklist_output.lower():
                    tws_processes.append(process)
            
            if tws_processes:
                print_success(f"TWS or IB Gateway appears to be running: {', '.join(tws_processes)}")
                return True
            else:
                print_error("No TWS or IB Gateway processes found. TWS must be running for API connections.")
                return False
                
        except Exception as e:
            print_error(f"Error checking for TWS processes: {e}")
            return False
    else:
        print_warning("Process check only supported on Windows. Please verify TWS is running manually.")
        return None

def suggest_solutions(open_ports, tws_running):
    """Based on diagnostics, suggest troubleshooting steps."""
    print_header("Diagnosis & Recommendations")
    
    if open_ports and tws_running:
        print_success("DIAGNOSIS: TWS is running and listening on API ports. Connection should be possible.")
        print("\nRecommended settings for your config.yaml:")
        for port in open_ports:
            print(f"""
ibkr:
  host: "127.0.0.1"
  port: {port}
  client_id: 1    # Try different values (e.g., 10, 123) if conflicts occur
  read_only: false
  account: ""     # Enter your account ID from TWS
  use_ib_insync: true
  timeout: 20
  auto_reconnect: true
  max_rate: 45
""")
        
    elif tws_running and not open_ports:
        print_error("DIAGNOSIS: TWS is running but no API ports are open.")
        print("\nLikely issues and solutions:")
        print("  1. TWS API not enabled - Go to Edit > Global Configuration > API > Settings")
        print("  2. Check 'Enable ActiveX and Socket Clients' is selected")
        print("  3. Verify Socket Port (default 7497 for paper trading)")
        print("  4. Click Apply, then restart TWS completely")
        print("  5. Windows Firewall may be blocking connection - Add exception for TWS API port")
        
    elif not tws_running:
        print_error("DIAGNOSIS: TWS or IB Gateway does not appear to be running.")
        print("\nSolutions:")
        print("  1. Start TWS or IB Gateway and log in")
        print("  2. Allow it to fully initialize (may take 2-3 minutes)")
        print("  3. Enable API access in TWS settings")
        print("  4. Run this diagnostic tool again")
    
    print("\nAdditional troubleshooting steps:")
    print("  • Start TWS/Gateway first, then start your application")
    print("  • Run both TWS and your application as Administrator")
    print("  • Try different client IDs if you have connection conflicts")
    print("  • Restart TWS completely after changing API settings")
    print("  • Check TWS logs for API-related errors")
    print("  • Verify your account has API access permissions")
    print("  • For paper accounts, ensure paper trading API access is enabled")

def main():
    """Main function to run TWS API connection diagnostics."""
    print_header("Interactive Brokers TWS API Connection Diagnostic Tool")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Computer name: {socket.gethostname()}")
    print(f"Operating system: {os.name}")
    
    try:
        tws_running = check_tws_running()
        open_ports = check_tws_ports()
        check_windows_firewall()
        suggest_solutions(open_ports, tws_running)
        
        print_header("Diagnostics complete")
        print("If problems persist, please check the documentation or contact support.")
        
        return 0
    except Exception as e:
        print_error(f"Unexpected error during diagnosis: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 