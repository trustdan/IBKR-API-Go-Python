#!/usr/bin/env python3
"""
Interactive Brokers TWS Connectivity Fix Tool

This tool performs a comprehensive diagnosis and attempts to fix common TWS API connectivity issues,
with a focus on Windows firewall rules and network configuration.

Usage: python tools/tws_connectivity_fix.py [--apply]
  --apply: Apply recommended fixes automatically (requires admin privileges)
"""

import os
import sys
import socket
import subprocess
import time
import ctypes
import argparse
from datetime import datetime
import platform

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # For non-Windows platforms, check if UID is 0 (root)
            return os.geteuid() == 0
    except:
        return False

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
    }
    
    open_ports = []
    for port, description in ports.items():
        print(f"Testing port {port} ({description})...")
        if check_port(host, port):
            open_ports.append(port)
    
    return open_ports

def check_windows_firewall_status():
    """Check if Windows Firewall is enabled and return its status."""
    if platform.system() != 'Windows':
        return None, "Not running on Windows"
    
    try:
        # Check if Windows Firewall is enabled
        firewall_output = subprocess.check_output(
            ["netsh", "advfirewall", "show", "allprofiles"], 
            universal_newlines=True
        )
        
        profiles = {}
        current_profile = None
        
        for line in firewall_output.splitlines():
            line = line.strip()
            
            # Detect profile change
            if line.startswith("Domain Profile") or line.startswith("Private Profile") or line.startswith("Public Profile"):
                current_profile = line.split(" Profile")[0].lower()
                profiles[current_profile] = {}
                
            # Get state for current profile
            if current_profile and "State" in line:
                state_parts = line.split()
                if len(state_parts) >= 2:
                    state = state_parts[-1].upper()  # Last part should be ON/OFF
                    profiles[current_profile]["state"] = state
        
        # Check if any profile is ON
        any_enabled = any(profile.get("state") == "ON" for profile in profiles.values())
        
        return any_enabled, profiles
    
    except subprocess.CalledProcessError as e:
        return None, f"Error checking Windows Firewall: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def check_existing_firewall_rules():
    """Check for existing TWS firewall rules."""
    if platform.system() != 'Windows':
        return []
    
    try:
        # Get all inbound rules
        rules_output = subprocess.check_output(
            ["netsh", "advfirewall", "firewall", "show", "rule", "name=all", "dir=in"],
            universal_newlines=True
        )
        
        # Look for rules that might be for TWS
        tws_rules = []
        current_rule = {}
        
        for line in rules_output.splitlines():
            line = line.strip()
            
            # New rule begins with Rule Name
            if line.startswith("Rule Name:"):
                if current_rule and ("TWS" in current_rule.get("name", "") or 
                                     "IB" in current_rule.get("name", "") or 
                                     "Interactive Brokers" in current_rule.get("name", "")):
                    tws_rules.append(current_rule)
                
                current_rule = {"name": line.split(":", 1)[1].strip()}
            
            # Get enabled status
            elif line.startswith("Enabled:"):
                current_rule["enabled"] = line.split(":", 1)[1].strip()
            
            # Get direction
            elif line.startswith("Direction:"):
                current_rule["direction"] = line.split(":", 1)[1].strip()
            
            # Get profiles
            elif line.startswith("Profiles:"):
                current_rule["profiles"] = line.split(":", 1)[1].strip()
            
            # Get local ports
            elif line.startswith("LocalPort:"):
                current_rule["local_port"] = line.split(":", 1)[1].strip()
        
        # Check for the last rule
        if current_rule and ("TWS" in current_rule.get("name", "") or 
                             "IB" in current_rule.get("name", "") or 
                             "Interactive Brokers" in current_rule.get("name", "")):
            tws_rules.append(current_rule)
        
        # Also check for rules with typical TWS ports
        port_rules = []
        current_rule = {}
        
        for line in rules_output.splitlines():
            line = line.strip()
            
            # New rule begins with Rule Name
            if line.startswith("Rule Name:"):
                if current_rule and current_rule.get("local_port") in ["7496", "7497", "4001", "4002"]:
                    port_rules.append(current_rule)
                
                current_rule = {"name": line.split(":", 1)[1].strip()}
            
            # Get enabled status
            elif line.startswith("Enabled:"):
                current_rule["enabled"] = line.split(":", 1)[1].strip()
            
            # Get local ports
            elif line.startswith("LocalPort:"):
                current_rule["local_port"] = line.split(":", 1)[1].strip()
        
        # Check for the last rule
        if current_rule and current_rule.get("local_port") in ["7496", "7497", "4001", "4002"]:
            port_rules.append(current_rule)
        
        # Add unique port rules
        for rule in port_rules:
            if rule not in tws_rules:
                tws_rules.append(rule)
        
        return tws_rules
    
    except subprocess.CalledProcessError as e:
        print_error(f"Error checking firewall rules: {e}")
        return []
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return []

def create_firewall_rule(port, protocol="TCP", apply=False):
    """Create a Windows Firewall rule for the specified port."""
    if platform.system() != 'Windows':
        print_warning("Firewall rule creation only supported on Windows.")
        return False
    
    rule_name = f"IBKR TWS API Port {port}"
    
    if not apply:
        print_info(f"Would create firewall rule: {rule_name} for port {port}/{protocol}")
        print_info("Run with --apply to create this rule")
        return False
    
    if not is_admin():
        print_error("Administrator privileges required to create firewall rules.")
        print_info("Please restart this script as Administrator.")
        return False
    
    try:
        print_info(f"Creating firewall rule: {rule_name}")
        
        # Create the rule
        cmd = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}",
            "dir=in",
            "action=allow",
            f"protocol={protocol}",
            f"localport={port}",
            "profile=domain,private,public",
            f"description=Allow IBKR TWS API connections on port {port}"
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_success(f"Successfully created firewall rule for port {port}")
        return True
    
    except subprocess.CalledProcessError as e:
        print_error(f"Error creating firewall rule: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"Output: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def check_tws_process():
    """Check if TWS or IB Gateway is running."""
    print_section("TWS Process Check")
    
    if platform.system() == 'Windows':
        try:
            # Use tasklist to check for running processes
            tasklist_output = subprocess.check_output(
                ["tasklist"], universal_newlines=True
            )
            
            tws_processes = []
            process_names = ["tws.exe", "ibgateway.exe", "javaw.exe"]
            
            for process in process_names:
                if process.lower() in tasklist_output.lower():
                    tws_processes.append(process)
            
            if tws_processes:
                print_success(f"TWS or IB Gateway appears to be running: {', '.join(tws_processes)}")
                return True
            else:
                print_error("No TWS or IB Gateway processes found. Please start TWS or IB Gateway.")
                return False
        
        except Exception as e:
            print_error(f"Error checking TWS processes: {e}")
            return None
    else:
        # For non-Windows platforms
        try:
            ps_output = subprocess.check_output(
                ["ps", "aux"], universal_newlines=True
            )
            
            if "tws" in ps_output.lower() or "ibgateway" in ps_output.lower() or "java" in ps_output.lower():
                print_success("TWS or IB Gateway appears to be running")
                return True
            else:
                print_error("No TWS or IB Gateway processes found. Please start TWS or IB Gateway.")
                return False
        except Exception as e:
            print_error(f"Error checking TWS processes: {e}")
            return None

def create_port_connectivity_test(port):
    """Create a simple test script to continuously check port connectivity."""
    filename = f"test_port_{port}_connection.py"
    
    script_content = f'''#!/usr/bin/env python3
"""
TWS API Port {port} Connection Test
This script continuously tests connection to TWS API port {port}.
"""

import socket
import time
from datetime import datetime

def check_port(port, host="127.0.0.1"):
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            return True, "SUCCESS"
        else:
            return False, f"FAILED (error code: {{result}})"
    except socket.error as e:
        return False, f"ERROR: {{e}}"
    finally:
        sock.close()

def main():
    """Run continuous port test."""
    port = {port}
    print(f"Starting continuous connection test to port {{port}}...")
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success, message = check_port(port)
            status = "OPEN" if success else "CLOSED"
            print(f"[{{now}}] Port {{port}}: {{status}} - {{message}}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\\nTest stopped by user")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(filename, 'w') as f:
            f.write(script_content)
        print_success(f"Created port test script: {filename}")
        print_info(f"Run with: python {filename}")
        return True
    except Exception as e:
        print_error(f"Error creating test script: {e}")
        return False

def analyze_and_fix(args):
    """Analyze the system and fix any issues found."""
    # Check if TWS is running
    tws_running = check_tws_process()
    
    # Check which ports are open
    open_ports = check_tws_ports()
    
    # Check Windows Firewall status
    if platform.system() == 'Windows':
        firewall_enabled, profiles = check_windows_firewall_status()
        
        if isinstance(profiles, dict):
            print_section("Windows Firewall Status")
            for profile, settings in profiles.items():
                state = settings.get("state", "UNKNOWN")
                if state == "ON":
                    print_warning(f"{profile.capitalize()} Profile: {state} (may block connections)")
                else:
                    print_success(f"{profile.capitalize()} Profile: {state}")
        
        # Check existing firewall rules
        existing_rules = check_existing_firewall_rules()
        if existing_rules:
            print_section("Existing TWS Firewall Rules")
            for rule in existing_rules:
                name = rule.get("name", "Unknown Rule")
                enabled = rule.get("enabled", "Unknown")
                port = rule.get("local_port", "Unknown")
                
                if enabled == "Yes":
                    print_success(f"Rule '{name}' is enabled for port {port}")
                else:
                    print_warning(f"Rule '{name}' is disabled for port {port}")
        else:
            print_warning("No TWS-related firewall rules found")
    
    # Suggest fixes
    print_header("Diagnosis & Recommendations")
    
    ports_to_fix = [7497, 7496, 4001, 4002]
    ports_needing_rules = []
    
    for port in ports_to_fix:
        if port not in open_ports:
            ports_needing_rules.append(port)
    
    if not tws_running:
        print_error("TWS or IB Gateway is not running.")
        print_info("Please start TWS or IB Gateway and log in.")
    
    if platform.system() == 'Windows' and firewall_enabled and ports_needing_rules:
        print_warning("Windows Firewall is enabled and may be blocking TWS API connections.")
        
        # Create firewall rules if requested
        if args.apply:
            print_info("Creating firewall rules for TWS API ports...")
            for port in ports_needing_rules:
                create_firewall_rule(port, apply=True)
        else:
            print_info("The following firewall rules are recommended:")
            for port in ports_needing_rules:
                print(f"  - Allow inbound TCP traffic on port {port}")
            print_info("Run this script with --apply to create these rules automatically.")
    
    # Create test script for the most likely port
    target_port = 7497  # Default paper trading port
    if open_ports:
        target_port = open_ports[0]
    elif ports_needing_rules:
        target_port = ports_needing_rules[0]
    
    create_port_connectivity_test(target_port)
    
    # Final recommendations
    print_header("Next Steps")
    print_info("1. If you applied firewall rules, RESTART BOTH TWS AND YOUR APPLICATION")
    print_info("2. Make sure TWS API settings are properly configured:")
    print_info("   - Open TWS > Edit > Global Configuration > API > Settings")
    print_info("   - Enable 'ActiveX and Socket Clients'")
    print_info("   - Set Socket Port to 7497 (paper) or 7496 (live)")
    print_info("   - Set Master API client ID to match your application (typically 1)")
    print_info("   - Check 'Allow connections from localhost only' if running locally")
    print_info("3. After changing TWS settings, RESTART TWS COMPLETELY")
    print_info("4. Run the port test script to verify connection:")
    print_info(f"   python test_port_{target_port}_connection.py")
    print_info("5. Update your application config to match the working port")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="TWS API Connectivity Fix Tool")
    parser.add_argument("--apply", action="store_true", help="Apply recommended fixes automatically")
    args = parser.parse_args()
    
    print_header("Interactive Brokers TWS API Connectivity Fix Tool")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Administrator mode: {'Yes' if is_admin() else 'No'}")
    
    if args.apply and not is_admin() and platform.system() == 'Windows':
        print_warning("Administrator privileges required to apply fixes!")
        print_info("Please restart the script as Administrator.")
        return 1
    
    try:
        analyze_and_fix(args)
        return 0
    except Exception as e:
        print_error(f"Error during execution: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 