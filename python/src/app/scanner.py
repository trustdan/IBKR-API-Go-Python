import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from src.app.scanner_client import ScannerClient
from src.data.data_manager import DataManager
from src.strategies.strategy_factory import StrategyFactory
from src.utils.logger import log_debug, log_error, log_info


class Scanner:
    """
    Scanner class that manages the process of evaluating market data against trading strategies.
    It can use either local processing or delegate to the Go scanner service for high-performance scanning.
    """

    config: Dict[str, Any]
    data_manager: Optional[DataManager]
    strategy_factory: StrategyFactory
    go_client: Optional[ScannerClient]

    def __init__(
        self, config: Dict[str, Any], data_manager: Optional[DataManager] = None
    ) -> None:
        """
        Initialize the scanner with configuration and dependencies.

        Args:
            config: Configuration dictionary
            data_manager: Optional DataManager instance for fetching market data
        """
        self.config = config
        self.data_manager = data_manager
        self.strategy_factory = StrategyFactory(config)

        # Initialize Go scanner client if configured
        use_go_scanner = config.get("USE_GO_SCANNER", True)
        if use_go_scanner:
            host = config.get("GO_SCANNER_HOST", "localhost")
            port = config.get("GO_SCANNER_PORT", 50051)
            self.go_client = ScannerClient(host, port)
        else:
            self.go_client = None

    def scan(
        self, symbols: List[str], strategies: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Scan a list of symbols for trading signals using the specified strategies.

        Args:
            symbols: List of symbols to scan
            strategies: List of strategy identifiers to apply (if None, use all)

        Returns:
            Dictionary mapping symbols to lists of signal types ("LONG", "SHORT")
        """
        start_time = time.time()
        log_info(f"Scanning {len(symbols)} symbols")

        # Determine which strategies to use
        if strategies is None:
            strategies = self.strategy_factory.get_strategy_ids()

        log_debug(f"Using strategies: {strategies}")

        # Choose scanning method based on configuration
        if self.go_client is not None:
            # Use Go scanner service for high-performance scanning
            signals = self.scan_with_go_service(symbols, strategies)
        else:
            # Use local processing
            signals = self.scan_locally(symbols, strategies)

        scan_time = time.time() - start_time
        log_info(
            f"Scan completed in {scan_time:.2f} seconds. Found signals for {len(signals)} symbols"
        )

        return signals

    def scan_with_go_service(
        self, symbols: List[str], strategies: List[str]
    ) -> Dict[str, List[str]]:
        """
        Scan using the Go scanner service via gRPC.

        Args:
            symbols: List of symbols to scan
            strategies: List of strategy identifiers to apply

        Returns:
            Dictionary mapping symbols to lists of signal types
        """
        try:
            # Call the Go scanner service
            return self.go_client.scan(symbols, strategies)
        except Exception as e:
            log_error(f"Error using Go scanner service: {str(e)}")
            # Fallback to local scanning if Go service fails
            log_info("Falling back to local scanning")
            return self.scan_locally(symbols, strategies)

    def scan_locally(
        self, symbols: List[str], strategy_ids: List[str]
    ) -> Dict[str, List[str]]:
        """
        Scan using local Python processing.

        Args:
            symbols: List of symbols to scan
            strategy_ids: List of strategy identifiers to apply

        Returns:
            Dictionary mapping symbols to lists of signal types
        """
        if self.data_manager is None:
            log_error("Cannot scan locally without a DataManager")
            return {}

        signals = {}

        # Get strategy instances
        strategies = []
        for strategy_id in strategy_ids:
            strategy = self.strategy_factory.get_strategy(strategy_id)
            if strategy:
                strategies.append(strategy)

        # Check if we have any valid strategies
        if not strategies:
            log_error("No valid strategies found for scanning")
            return {}

        # Process each symbol
        current_time = datetime.now()
        for symbol in symbols:
            # Only process if within execution window (optional)
            if not self._should_execute_now(current_time):
                continue

            try:
                # Get market data for the symbol
                data = self.data_manager.get_data(
                    symbol,
                    "daily",  # Use daily timeframe by default
                    None,  # Use default date ranges
                    None,
                )

                if data is None or data.empty:
                    log_debug(f"No data available for {symbol}")
                    continue

                # Add symbol column if not present
                if "symbol" not in data.columns:
                    data["symbol"] = symbol

                # Apply all strategies and collect signals
                symbol_signals = []
                for strategy in strategies:
                    # Compute indicators first
                    data_with_indicators = strategy.compute_indicators(data)

                    # Generate signals
                    strategy_signals = strategy.generate_signals(data_with_indicators)

                    # Extract signal types
                    for signal_type, signal_symbol in strategy_signals:
                        if (
                            signal_symbol == symbol
                            and signal_type not in symbol_signals
                        ):
                            symbol_signals.append(signal_type)

                # Add to results if any signals found
                if symbol_signals:
                    signals[symbol] = symbol_signals

            except Exception as e:
                log_error(f"Error processing {symbol}: {str(e)}")

        return signals

    def _should_execute_now(self, current_time: datetime) -> bool:
        """
        Check if we should execute strategies at the current time.

        Args:
            current_time: Current datetime

        Returns:
            Boolean indicating whether to execute
        """
        # Check if any strategy wants to execute
        # In practice, they all share the same execution timing logic
        # so we just use the first strategy
        if self.strategy_factory.get_strategy_ids():
            strategy = self.strategy_factory.get_strategy(
                self.strategy_factory.get_strategy_ids()[0]
            )
            if strategy:
                return strategy.should_execute(current_time)

        # Default behavior if no strategies found
        return True

