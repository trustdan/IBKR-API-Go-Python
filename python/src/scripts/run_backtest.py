#!/usr/bin/env python
"""
Script to run a backtest of the trading strategies.
"""

import argparse
import json
from datetime import datetime, timedelta
import yaml
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.app.backtest_engine import BacktestEngine
from src.data.data_manager import DataManager
from src.utils.logger import setup_logger, log_info, log_error


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run a backtest of trading strategies')
    
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--symbols', type=str, nargs='+',
                        help='List of symbols to backtest')
    parser.add_argument('--strategies', type=str, nargs='+',
                        help='List of strategies to backtest')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=180,
                        help='Number of days to backtest if start/end dates not provided')
    parser.add_argument('--equity', type=float, default=100000,
                        help='Initial equity')
    parser.add_argument('--output', type=str,
                        help='Output file for backtest report')
    
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


def main():
    """Main function to run the backtest."""
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logger
    setup_logger(config.get('LOGGING', {}))
    
    # Set default symbols if not provided
    if not args.symbols:
        args.symbols = config.get('BACKTEST_SYMBOLS', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'])
        
    # Set default dates if not provided
    end_date = args.end_date
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        
    start_date = args.start_date
    if not start_date:
        start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        
    # Initialize data manager
    data_manager = DataManager(config)
    
    # Initialize backtest engine
    backtest_engine = BacktestEngine(config, data_manager)
    
    log_info(f"Starting backtest for {len(args.symbols)} symbols "
             f"from {start_date} to {end_date}")
    
    # Run backtest
    results = backtest_engine.run_backtest(
        symbols=args.symbols,
        start_date=start_date,
        end_date=end_date,
        strategy_ids=args.strategies,
        initial_equity=args.equity
    )
    
    # Generate report
    report = backtest_engine.generate_report(args.output)
    print(report)
    
    # Output summary to console
    if results and 'overall' in results:
        overall = results['overall']
        print("\nSummary:")
        print(f"Total trades: {overall['total_trades']}")
        print(f"Win rate: {overall['win_rate']*100:.2f}%")
        print(f"Profit factor: {overall['profit_factor']:.2f}")
        print(f"Final equity: ${overall['final_equity']:.2f}")
        print(f"Total profit: ${overall['total_profit']:.2f} ({overall['total_profit']/overall['initial_equity']*100:.2f}%)")
        print(f"Max drawdown: {overall['max_drawdown']*100:.2f}%")


if __name__ == '__main__':
    main() 