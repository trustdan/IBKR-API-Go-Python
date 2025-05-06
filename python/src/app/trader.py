import queue
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from src.app.config import Config
from src.app.scanner_client import ScannerClient
from src.brokers.ibkr_api import IBKRApi
from src.trading.option_selector import OptionSelector
from src.trading.risk_manager import RiskManager
from src.trading.trade_executor import TradeExecutor
from src.utils.logger import log_debug, log_error, log_info, log_warning


class Trader:
    """Main trader class that orchestrates the entire trading process."""

    config: Any
    broker_api: Optional[IBKRApi]
    scanner: ScannerClient
    option_selector: OptionSelector
    risk_manager: RiskManager
    trade_executor: TradeExecutor
    signal_queue: queue.Queue
    processing: bool
    processing_thread: Optional[threading.Thread]

    def __init__(self, config_file: str = "config.yaml"):
        """Initialize the trader.

        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = Config.from_yaml(config_file)
        log_info(f"Initialized trader with {self.config.TRADING_MODE} mode")

        # Connect to IBKR
        self.broker_api = IBKRApi(self.config)
        connected = self.broker_api.connect()
        if not connected:
            log_error("Failed to connect to IBKR, some functionality may be limited")

        # Initialize components
        self.scanner = ScannerClient(self.config.SCANNER_HOST, self.config.SCANNER_PORT)
        self.option_selector = OptionSelector(self.config)
        self.risk_manager = RiskManager(self.config, self.broker_api)
        self.trade_executor = TradeExecutor(self.config, self.broker_api)

        # Signal processing queue
        self.signal_queue = queue.Queue()
        self.processing = False
        self.processing_thread = None

    def start(self) -> None:
        """Start the trader."""
        log_info("Starting trader...")

        # Start the signal processing thread
        self.processing = True
        self.processing_thread = threading.Thread(target=self._process_signals_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()

        log_info("Trader started successfully")

    def stop(self) -> None:
        """Stop the trader."""
        log_info("Stopping trader...")

        # Stop the processing thread
        self.processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)

        # Disconnect from broker
        if self.broker_api:
            self.broker_api.disconnect()

        log_info("Trader stopped")

    def scan_for_signals(
        self, symbols: List[str], strategies: List[str]
    ) -> Dict[str, List[str]]:
        """Scan for trading signals.

        Args:
            symbols: List of symbols to scan
            strategies: List of strategies to apply

        Returns:
            Dictionary mapping symbols to signal types
        """
        try:
            log_info(
                f"Scanning {len(symbols)} symbols with {len(strategies)} strategies"
            )

            # Call the scanner service
            signals = self.scanner.scan(symbols, strategies)

            # Queue signals for processing
            signal_count = 0
            for symbol, signal_types in signals.items():
                for signal_type in signal_types:
                    self.signal_queue.put(
                        {
                            "symbol": symbol,
                            "direction": signal_type,
                            "timestamp": datetime.now(),
                        }
                    )
                    signal_count += 1

            log_info(f"Scan completed, queued {signal_count} signals for processing")
            return signals
        except Exception as e:
            log_error(f"Error scanning for signals: {str(e)}")
            return {}

    def process_signal(self, signal: Dict[str, Any]) -> Tuple[str, Any]:
        """Process a single trading signal.

        Args:
            signal: Trading signal dictionary

        Returns:
            Tuple of (status, result)
        """
        try:
            symbol = signal["symbol"]
            direction = signal["direction"]

            log_info(f"Processing signal: {symbol} {direction}")

            # Check risk management constraints
            can_trade, reason = self.risk_manager.can_enter_trade(symbol, direction)
            if not can_trade:
                log_warning(f"Trade rejected by risk manager: {reason}")
                return "REJECTED", reason

            # Fetch current price
            if self.broker_api:
                market_data = self.broker_api.get_market_data(symbol)
                current_price = market_data.get("last", 100.0)  # Default for demo
            else:
                # For demo/development
                current_price = 100.0

            # Select option spread
            option_spread = self.option_selector.select_vertical_spread(
                symbol, direction, current_price
            )

            if not option_spread:
                return "REJECTED", "No suitable option spread found"

            # Calculate position size
            account_value = self.risk_manager.get_account_value()
            position_size = self.risk_manager.calculate_position_size(
                account_value, option_spread.cost
            )

            if position_size <= 0:
                return (
                    "REJECTED",
                    "Position size calculation resulted in zero contracts",
                )

            # Execute the trade
            status, result = self.trade_executor.execute_trade(
                signal, option_spread, position_size
            )

            # Record trade if executed
            if status == "EXECUTED":
                self.risk_manager.record_trade(
                    symbol, direction, position_size, option_spread
                )

            return status, result
        except Exception as e:
            log_error(f"Error processing signal: {str(e)}")
            return "ERROR", str(e)

    def _process_signals_thread(self) -> None:
        """Background thread for processing signals from the queue."""
        while self.processing:
            try:
                # Process any queued signals with a timeout
                try:
                    signal = self.signal_queue.get(timeout=1.0)
                    status, result = self.process_signal(signal)
                    log_debug(f"Signal processing result: {status} - {result}")
                    self.signal_queue.task_done()
                except queue.Empty:
                    # No signals to process, check queued trades
                    self.trade_executor.process_queued_trades()

                # Periodically update positions from broker
                self.risk_manager.update_positions_from_broker()

                # Sleep to avoid excessive CPU usage
                time.sleep(0.1)
            except Exception as e:
                log_error(f"Error in signal processing thread: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Get current trader status.

        Returns:
            Status dictionary
        """
        try:
            # Get status from each component
            risk_metrics = self.risk_manager.get_metrics()
            execution_metrics = self.trade_executor.get_metrics()

            # Get account data if available
            account_data = {}
            if self.broker_api and self.broker_api.connected:
                account_data = self.broker_api.get_account_summary()

            return {
                "mode": self.config.TRADING_MODE,
                "active": self.processing,
                "queued_signals": self.signal_queue.qsize(),
                "risk": risk_metrics,
                "execution": execution_metrics,
                "account": account_data,
            }
        except Exception as e:
            log_error(f"Error getting status: {str(e)}")
            return {"error": str(e)}

    def run_scan_cycle(
        self, symbols: List[str], strategies: List[str]
    ) -> Dict[str, Any]:
        """Run a complete scan and trade cycle.

        Args:
            symbols: List of symbols to scan
            strategies: List of strategies to apply

        Returns:
            Status information
        """
        start_time = time.time()

        # Run the scan
        signals = self.scan_for_signals(symbols, strategies)

        # Wait for all signals to be processed
        while (
            not self.signal_queue.empty() and (time.time() - start_time) < 300
        ):  # 5-minute timeout
            time.sleep(1.0)

        # Collect results
        scan_time = time.time() - start_time
        status = self.get_status()

        return {
            "scan_time": scan_time,
            "symbols_scanned": len(symbols),
            "signals_found": sum(
                len(signal_types) for signal_types in signals.values()
            ),
            "status": status,
        }
