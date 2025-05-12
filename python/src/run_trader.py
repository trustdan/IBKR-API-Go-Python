#!/usr/bin/env python
"""
Auto Vertical Spread Trader runner script.
This script is the main entry point for the trading system.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, cast

from src.app.trader import Trader
from src.utils.logger import log_error, log_info, setup_logger


def load_symbol_list(filename: str) -> List[str]:
    """Load symbols from a file.

    Args:
        filename: Path to file containing symbols

    Returns:
        List of symbols
    """
    if not os.path.exists(filename):
        log_error(f"Symbol file not found: {filename}")
        return []

    with open(filename, "r") as f:
        symbols = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

    return symbols


def main() -> int:
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Auto Vertical Spread Trader")

    # Setup subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for trade signals")
    scan_parser.add_argument(
        "--symbols", required=True, help="File containing symbols to scan"
    )
    scan_parser.add_argument(
        "--strategies",
        nargs="+",
        choices=["HIGH_BASE", "LOW_BASE", "BULL_PULLBACK", "BEAR_RALLY"],
        default=["HIGH_BASE", "LOW_BASE", "BULL_PULLBACK", "BEAR_RALLY"],
        help="Strategies to use for scanning",
    )
    scan_parser.add_argument(
        "--config", default="config.yaml", help="Path to config file"
    )
    scan_parser.add_argument("--output", help="Output file for scan results (JSON)")

    # Trade command
    trade_parser = subparsers.add_parser(
        "trade", help="Run the trader with scanning and execution"
    )
    trade_parser.add_argument(
        "--symbols", required=True, help="File containing symbols to trade"
    )
    trade_parser.add_argument(
        "--strategies",
        nargs="+",
        choices=["HIGH_BASE", "LOW_BASE", "BULL_PULLBACK", "BEAR_RALLY"],
        default=["HIGH_BASE", "LOW_BASE", "BULL_PULLBACK", "BEAR_RALLY"],
        help="Strategies to use for trading",
    )
    trade_parser.add_argument(
        "--config", default="config.yaml", help="Path to config file"
    )
    trade_parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Scanning interval in seconds (default: 3600)",
    )
    trade_parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of scan cycles to run (default: 1, 0 for infinite)",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Check trader status")
    status_parser.add_argument(
        "--config", default="config.yaml", help="Path to config file"
    )

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    setup_logger()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "scan":
            # Load symbols
            symbols = load_symbol_list(args.symbols)
            if not symbols:
                log_error(f"No symbols found in {args.symbols}")
                return 1

            log_info(
                f"Running scan with {len(symbols)} symbols and strategies: {args.strategies}"
            )

            # Initialize trader
            trader = Trader(config_file=args.config)

            # Run scan
            results = trader.scan_for_signals(symbols, args.strategies)

            # Print results
            signal_count = sum(len(signals) for signals in results.values())
            log_info(
                f"Scan completed, found {signal_count} signals across {len(results)} symbols"
            )

            for symbol, signals in results.items():
                log_info(f"  {symbol}: {', '.join(signals)}")

            # Save results if output file specified
            if args.output:
                output_data = {
                    "timestamp": datetime.now().isoformat(),
                    "symbols_scanned": len(symbols),
                    "signals_found": signal_count,
                    "results": results,
                }

                with open(args.output, "w") as f:
                    json.dump(output_data, f, indent=2)
                log_info(f"Scan results saved to {args.output}")

        elif args.command == "trade":
            # Load symbols
            symbols = load_symbol_list(args.symbols)
            if not symbols:
                log_error(f"No symbols found in {args.symbols}")
                return 1

            log_info(
                f"Starting trader with {len(symbols)} symbols and strategies: {args.strategies}"
            )

            # Initialize trader
            trader = Trader(config_file=args.config)
            trader.start()

            try:
                # Run scan cycles
                cycle = 1
                max_cycles = args.cycles

                while max_cycles == 0 or cycle <= max_cycles:
                    log_info(f"Starting scan cycle {cycle}")

                    # Run scan cycle
                    results: Dict[str, Any] = trader.run_scan_cycle(
                        symbols, args.strategies
                    )

                    log_info(
                        f"Scan cycle {cycle} completed in {results.get('scan_time', 0.0):.2f}s, "
                        f"found {results.get('signals_found', 0)} signals"
                    )

                    # Print trader status
                    status = cast(Dict[str, Any], results.get("status", {}))
                    risk_info = cast(Dict[str, Any], status.get("risk", {}))

                    log_info(
                        f"Trader status: Mode={status.get('mode', 'unknown')}, "
                        f"Positions={risk_info.get('active_positions', 0)}/{risk_info.get('max_positions', 0)}, "
                        f"Daily trades={risk_info.get('daily_trades', 0)}/{risk_info.get('max_daily_trades', 0)}"
                    )

                    # Wait for next cycle if not the last one
                    if max_cycles == 0 or cycle < max_cycles:
                        log_info(
                            f"Waiting {args.interval} seconds until next scan cycle"
                        )
                        time.sleep(args.interval)
                        cycle += 1
                    else:
                        break

                log_info("All scan cycles completed")
            finally:
                # Make sure to stop the trader
                trader.stop()

        elif args.command == "status":
            # Initialize trader
            trader = Trader(config_file=args.config)

            # Get status
            status = trader.get_status()

            # Print status
            log_info(f"Trader status: Mode={status['mode']}")
            log_info(f"Risk metrics: {json.dumps(status['risk'], indent=2)}")
            log_info(f"Execution metrics: {json.dumps(status['execution'], indent=2)}")

            if "account" in status and status["account"]:
                log_info(f"Account data: {json.dumps(status['account'], indent=2)}")
            else:
                log_info("No account data available")

        return 0
    except KeyboardInterrupt:
        log_info("Operation interrupted by user")
        return 130
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
