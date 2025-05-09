"""
Main entry point for IBKR Auto Vertical Spread Trader.
"""

import argparse
import datetime
import os
import signal
import sys
import threading
import time
from pathlib import Path

from src.app.scanner_client import ScannerClient
from src.config import config
from src.data import DataManager
from src.options import SpreadManager
from src.utils.logger import log_error, log_info, log_warning, setup_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="IBKR Auto Vertical Spread Trader")
    parser.add_argument(
        "--config", type=str, help="Path to configuration file", default=None
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        default=None,
    )
    parser.add_argument(
        "--clear-cache",
        type=str,
        choices=["all", "universe", "minute", "options"],
        help="Clear specific cache data",
        default=None,
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start trading immediately, ignoring schedule",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop trading immediately",
    )
    return parser.parse_args()


def handle_sigusr1(signum, frame):
    """Handle SIGUSR1 signal for config reload."""
    log_info("Received SIGUSR1 signal, reloading configuration...")

    # Reload the configuration
    config._load_config()

    # Reload SpreadManager if it exists in the global context
    if "spread_manager" in globals():
        log_info("Reloading SpreadManager with new configuration")
        spread_manager.reload_config()

    log_info("Configuration reloaded successfully")


def is_trading_time() -> bool:
    """Check if current time is within scheduled trading time."""
    # Get schedule settings from config
    auto_start_enabled = config.get("schedule.auto_start_enabled", False)
    auto_stop_enabled = config.get("schedule.auto_stop_enabled", False)

    # If neither is enabled, always return True (always trade)
    if not auto_start_enabled and not auto_stop_enabled:
        return True

    # Get current time (assuming US Eastern Time as market time)
    now = datetime.datetime.now()
    current_time = now.time()

    # Parse schedule times
    start_time_str = config.get("schedule.start_time", "09:30")
    stop_time_str = config.get("schedule.stop_time", "16:00")

    try:
        start_hours, start_minutes = map(int, start_time_str.split(":"))
        stop_hours, stop_minutes = map(int, stop_time_str.split(":"))

        start_time = datetime.time(start_hours, start_minutes)
        stop_time = datetime.time(stop_hours, stop_minutes)

        # Check if current time is within trading hours
        if auto_start_enabled and auto_stop_enabled:
            return start_time <= current_time <= stop_time
        elif auto_start_enabled:
            return start_time <= current_time
        elif auto_stop_enabled:
            return current_time <= stop_time

    except ValueError:
        log_warning(
            f"Invalid time format in schedule: {start_time_str} or {stop_time_str}"
        )

    # Default to True if parsing fails
    return True


def scheduler_thread(data_manager, should_run_event):
    """Run a scheduler thread to control trading hours."""
    log_info("Scheduler thread started")

    # Keep track of trading status
    trading_status = True

    while True:
        # Check if trading should occur based on schedule
        should_trade = is_trading_time()

        # Update the thread event based on schedule
        if should_trade and not trading_status:
            log_info("Scheduled trading start")
            should_run_event.set()
            trading_status = True
        elif not should_trade and trading_status:
            log_info("Scheduled trading stop")
            should_run_event.clear()
            trading_status = False

        # Check for expired cache and clean up
        data_manager.clear_expired_cache()

        # Sleep for a minute before next check
        time.sleep(60)


def process_trading(data_manager, spread_manager):
    """
    Process trading logic using the SpreadManager.

    Args:
        data_manager: DataManager instance for market data
        spread_manager: SpreadManager instance for spread filtering
    """
    try:
        log_info("Starting trading cycle...")

        # Get list of symbols from universe
        universe = config.get("trading.symbols", [])
        if not universe:
            log_warning("No symbols in trading universe")
            return

        log_info(f"Processing {len(universe)} symbols in universe")

        # Process each symbol
        for symbol in universe:
            # Get underlying data
            underlying_data = get_underlying_data(data_manager, symbol)
            if not underlying_data:
                continue

            # Get option chains
            option_chains = get_option_chains(data_manager, symbol)
            if not option_chains:
                continue

            # Find the best spread
            best_spread = spread_manager.get_best_spread(
                symbol, option_chains, underlying_data
            )
            if best_spread:
                log_info(
                    f"Found valid spread for {symbol}: {best_spread['type']} with reward/risk {best_spread['reward_risk']:.2f}"
                )
                # In a real implementation, execute the trade here
            else:
                log_info(f"No valid spreads found for {symbol}")

    except Exception as e:
        log_error(f"Error in trading process: {str(e)}")


def get_underlying_data(data_manager, symbol):
    """
    Get underlying stock data including price, IV, and event dates.

    Args:
        data_manager: DataManager instance
        symbol: Stock symbol

    Returns:
        Dictionary with underlying data or None on error
    """
    try:
        # Get daily data for the symbol
        daily_data = data_manager.get_data(symbol, timeframe="1 day", duration="1 Y")
        if daily_data is None or daily_data.empty:
            log_warning(f"No daily data available for {symbol}")
            return None

        # Get current price (last close)
        current_price = daily_data.iloc[-1]["close"]

        # Calculate ATR
        atr = calculate_atr(daily_data, period=14)

        # Get IV data (this would be from IBKR in a real implementation)
        iv_rank = 0.5  # Placeholder (should be calculated from historical IV)
        iv_percentile = 0.5  # Placeholder
        call_put_skew = 0.02  # Placeholder (positive means calls more expensive)

        # Get expected move (simple approximation based on ATR)
        expected_move = atr * 1.5

        # Get earnings and dividend dates (placeholders)
        earnings_date = ""  # Would come from fundamental data
        ex_dividend_date = ""  # Would come from fundamental data

        return {
            "symbol": symbol,
            "price": current_price,
            "atr": atr,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "call_put_skew": call_put_skew,
            "expected_move": expected_move,
            "earnings_date": earnings_date,
            "ex_dividend_date": ex_dividend_date,
        }

    except Exception as e:
        log_error(f"Error getting underlying data for {symbol}: {str(e)}")
        return None


def get_option_chains(data_manager, symbol):
    """
    Get option chains for a symbol.

    Args:
        data_manager: DataManager instance
        symbol: Stock symbol

    Returns:
        Dictionary with calls and puts option chains or None on error
    """
    try:
        # In a real implementation, this would fetch from IBKR
        # For now, we return a simple placeholder
        return {
            "calls": [],  # Would be a list of option contracts
            "puts": [],  # Would be a list of option contracts
        }

    except Exception as e:
        log_error(f"Error getting option chains for {symbol}: {str(e)}")
        return None


def calculate_atr(data, period=14):
    """
    Calculate Average True Range.

    Args:
        data: DataFrame with OHLC data
        period: Period for ATR calculation

    Returns:
        ATR value (float)
    """
    try:
        # Simple placeholder implementation
        # In a real implementation, use proper ATR calculation
        return (data["high"] - data["low"]).mean()

    except Exception as e:
        log_error(f"Error calculating ATR: {str(e)}")
        return 1.0  # Fallback default value


def main() -> int:
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

    # Register signal handler for SIGUSR1
    signal.signal(signal.SIGUSR1, handle_sigusr1)
    log_info("Registered SIGUSR1 handler for config reloading")

    try:
        # Initialize DataManager
        data_manager = DataManager()
        log_info("Data manager initialized")

        # Initialize the SpreadManager
        global spread_manager
        spread_manager = SpreadManager()
        log_info("SpreadManager initialized")

        # Handle cache clearing if requested
        if args.clear_cache:
            count = data_manager.clear_cache(args.clear_cache)
            log_info(f"Cleared {count} items from {args.clear_cache} cache")
            return 0  # Exit after clearing cache if that was the only command

        # Initialize Scanner Client
        scanner_host = config.get("scanner.host", "localhost")
        scanner_port = config.get("scanner.port", 50051)
        scanner_client = ScannerClient(scanner_host, scanner_port)
        log_info(
            f"Scanner client initialized, connecting to {scanner_host}:{scanner_port}"
        )

        # Test connection to Go scanner service
        metrics = scanner_client.get_metrics()
        log_info(f"Connected to scanner service, current metrics: {metrics}")

        # Set scanner client in data manager for bulk fetch operations
        data_manager.set_scanner_client(scanner_client)

        # Create a threading event to control trading
        should_run_event = threading.Event()

        # Start with status based on command line or schedule
        if args.start:
            log_info("Starting trading immediately (command line override)")
            should_run_event.set()
        elif args.stop:
            log_info("Stopping trading immediately (command line override)")
            should_run_event.clear()
        else:
            # Set initial state based on schedule
            should_run_event.set() if is_trading_time() else should_run_event.clear()
            log_info(
                f"Setting initial trading state to: {'running' if should_run_event.is_set() else 'paused'}"
            )

        # Start scheduler thread to control trading hours
        scheduler = threading.Thread(
            target=scheduler_thread, args=(data_manager, should_run_event)
        )
        scheduler.daemon = True
        scheduler.start()

        # Main application loop
        log_info("Entering main application loop")
        last_trading_cycle = 0
        TRADING_CYCLE_INTERVAL = 15 * 60  # 15 minutes in seconds

        while True:
            try:
                current_time = time.time()

                # Only perform trading operations if scheduler allows and it's time for a new cycle
                if should_run_event.is_set():
                    # Check if it's time for a new trading cycle
                    if current_time - last_trading_cycle >= TRADING_CYCLE_INTERVAL:
                        process_trading(data_manager, spread_manager)
                        last_trading_cycle = current_time
                    else:
                        log_info(
                            f"Waiting for next trading cycle. {int((TRADING_CYCLE_INTERVAL - (current_time - last_trading_cycle)) / 60)} minutes remaining."
                        )
                else:
                    log_info("Trading operations paused by schedule")

                # Sleep for a minute
                time.sleep(60)
            except Exception as e:
                log_error(f"Unexpected error in main loop: {str(e)}")
                # Sleep a bit before continuing to avoid tight error loops
                time.sleep(5)

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
