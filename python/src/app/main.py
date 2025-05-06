"""
Main entry point for IBKR Auto Vertical Spread Trader.
"""

import argparse
import sys
import time
from pathlib import Path

from ..config import config
from ..data import DataManager
from ..utils.logger import log_error, log_info, setup_logger
from .scanner_client import ScannerClient


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="IBKR Auto Vertical Spread Trader")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        default=None
    )
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_args()
    
    # Initialize configuration if path provided
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            log_error(f"Configuration file not found: {args.config}")
            sys.exit(1)
    
    # Setup logging
    log_level = args.log_level or config.get("logging.level", "INFO")
    logger = setup_logger(log_level=log_level)
    log_info("Starting IBKR Auto Vertical Spread Trader")
    
    try:
        # Initialize DataManager
        data_manager = DataManager()
        log_info("Data manager initialized")
        
        # Initialize Scanner Client
        scanner_host = config.get("scanner.host", "localhost")
        scanner_port = config.get("scanner.port", 50051)
        scanner_client = ScannerClient(scanner_host, scanner_port)
        log_info(f"Scanner client initialized, connecting to {scanner_host}:{scanner_port}")
        
        # Test connection to Go scanner service
        metrics = scanner_client.get_metrics()
        log_info(f"Connected to scanner service, current metrics: {metrics}")
        
        # Set scanner client in data manager for bulk fetch operations
        data_manager.set_scanner_client(scanner_client)
        
        # Main application loop
        log_info("Entering main application loop")
        while True:
            # Just a placeholder for now
            time.sleep(60)
            log_info("Application running...")
            
    except KeyboardInterrupt:
        log_info("Application stopped by user")
    except Exception as e:
        log_error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        log_info("Shutting down IBKR Auto Vertical Spread Trader")
        # Cleanup resources if needed
        
    return 0


if __name__ == "__main__":
    sys.exit(main()) 