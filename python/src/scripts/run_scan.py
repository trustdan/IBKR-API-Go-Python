#!/usr/bin/env python
"""
Script to run a scan of the market using our trading strategies.
"""

import argparse
import json
from datetime import datetime
import yaml
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.app.scanner import Scanner
from src.data.data_manager import DataManager
from src.utils.logger import setup_logger, log_info, log_error


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run a market scan using trading strategies')
    
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--symbols', type=str, nargs='+',
                        help='List of symbols to scan')
    parser.add_argument('--strategies', type=str, nargs='+',
                        help='List of strategies to apply')
    parser.add_argument('--use-go-scanner', action='store_true',
                        help='Use the Go scanner service')
    parser.add_argument('--output', type=str,
                        help='Output file for scan results')
    
    return parser.parse_args()


def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        log_error(f"Error loading config from {config_path}: {str(e)}")
        return {}


def save_results(results, output_file):
    """Save scan results to a file."""
    try:
        # Convert results to a more JSON-friendly format
        serializable_results = {}
        for symbol, signals in results.items():
            serializable_results[symbol] = list(signals)
            
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
            
        log_info(f"Results saved to {output_file}")
    except Exception as e:
        log_error(f"Error saving results to {output_file}: {str(e)}")


def main():
    """Main function to run the scan."""
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.use_go_scanner:
        config['USE_GO_SCANNER'] = True
    
    # Setup logger
    setup_logger(config.get('LOGGING', {}))
    
    # Set default symbols if not provided
    if not args.symbols:
        args.symbols = config.get('SCAN_SYMBOLS', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'])
        
    # Initialize data manager
    data_manager = DataManager(config)
    
    # Initialize scanner
    scanner = Scanner(config, data_manager)
    
    log_info(f"Starting scan for {len(args.symbols)} symbols")
    
    # Run scan
    results = scanner.scan(args.symbols, args.strategies)
    
    # Output results
    print("\nScan Results:")
    for symbol, signals in results.items():
        print(f"{symbol}: {', '.join(signals)}")
    
    print(f"\nFound signals for {len(results)} out of {len(args.symbols)} symbols.")
    
    # Save results if output file specified
    if args.output:
        save_results(results, args.output)


if __name__ == '__main__':
    main() 