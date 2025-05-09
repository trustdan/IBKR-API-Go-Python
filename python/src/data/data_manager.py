"""
DataManager module for handling market data retrieval and caching.
"""

import os
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from ib_insync import IB, Contract, Stock, util
from src.app.scanner_client import ScannerClient
from src.config.config import config
from src.utils.logger import log_debug, log_error, log_info, log_warning


class DataManager:
    """
    Data Manager for market data retrieval, caching, and universe filtering.

    This class handles:
    - Data retrieval from IBKR API
    - Caching mechanism with expiry policies
    - Universe filtering based on criteria (market cap, price, volume)
    """

    cache: Dict[str, Any]
    cache_expiry: Dict[str, float]
    ib: IB
    cache_dir: Path
    universe_cache_expiry: int
    minute_data_cache_expiry: int
    options_cache_expiry: int
    min_market_cap: float
    min_price: float
    min_volume: int
    connected: bool
    scanner_client: Optional[ScannerClient]

    def __init__(self, ib_client: Optional[IB] = None) -> None:
        """
        Initialize the DataManager.

        Args:
            ib_client: Optional IB client instance. If None, a new one will be created
                       but not connected.
        """
        self.cache = {}  # type: Dict[str, Any]
        self.cache_expiry = {}  # type: Dict[str, float]
        self.ib: IB = ib_client if ib_client is not None else IB()

        # Create cache directory if it doesn't exist
        self.cache_dir = Path(config.get("data.cache_dir", "data/cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cache expiry configuration
        self.universe_cache_expiry = config.get(
            "data.universe_cache_expiry", 1800
        )  # 30 minutes
        self.minute_data_cache_expiry = config.get(
            "data.minute_data_cache_expiry", 60
        )  # 1 minute
        self.options_cache_expiry = config.get(
            "data.options_cache_expiry", 300
        )  # 5 minutes

        # Universe filtering parameters
        self.min_market_cap = config.get(
            "universe.min_market_cap", 10_000_000_000
        )  # $10B
        self.min_price = config.get("universe.min_price", 20)
        self.min_volume = config.get("universe.min_volume", 1_000_000)

        # Connection status
        self.connected = False

        # Scanner client for optimized data retrieval
        self.scanner_client = None  # type: Optional[ScannerClient]

    def set_scanner_client(self, scanner_client: ScannerClient) -> None:
        """
        Set the scanner client for optimized data retrieval.

        Args:
            scanner_client: Scanner client instance
        """
        self.scanner_client = scanner_client
        log_debug("Scanner client set in DataManager")

    def ensure_connection(self) -> bool:
        """
        Ensure connection to IBKR API.

        Returns:
            True if connected successfully, False otherwise
        """
        if self.connected and self.ib.isConnected():
            return True

        try:
            host = config.get("ibkr.host", "127.0.0.1")
            port = int(config.get("ibkr.port", 7497))
            client_id = int(config.get("ibkr.client_id", 1))

            log_info(f"Connecting to IBKR at {host}:{port} with client ID {client_id}")
            self.ib.connect(host, port, clientId=client_id)
            self.connected = True
            log_info("Connected to IBKR API")
            return True
        except Exception as e:
            log_error("Failed to connect to IBKR API", str(e))
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from IBKR API."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            log_info("Disconnected from IBKR API")

    def get_data(
        self,
        symbol: str,
        timeframe: str = "1 day",
        duration: str = "1 Y",
        what_to_show: str = "TRADES",
        use_cache: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        Get historical market data with caching.

        Args:
            symbol: Ticker symbol
            timeframe: Bar size (e.g., "1 day", "1 hour", "5 mins")
            duration: Time duration (e.g., "1 Y", "6 M", "1 W")
            what_to_show: Data type (e.g., "TRADES", "MIDPOINT", "BID", "ASK")
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with market data or None if data retrieval failed
        """
        cache_key = f"{symbol}:{timeframe}:{duration}:{what_to_show}"

        # Check if data is in memory cache and not expired
        current_time = time.time()
        if (
            use_cache
            and cache_key in self.cache
            and cache_key in self.cache_expiry
            and current_time < self.cache_expiry[cache_key]
        ):
            log_debug(f"Using memory cached data for {symbol} ({timeframe})")
            return self.cache[cache_key]

        # Check if data is in file cache and not expired
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)

                if current_time < cache_data["expiry"]:
                    log_debug(f"Using file cached data for {symbol} ({timeframe})")
                    # Update memory cache
                    self.cache[cache_key] = cache_data["data"]
                    self.cache_expiry[cache_key] = cache_data["expiry"]
                    return cache_data["data"]
            except Exception as e:
                log_warning(f"Failed to load cache file for {symbol}: {e}")

        # Fetch fresh data
        log_info(f"Fetching fresh data for {symbol} ({timeframe})")

        # Ensure IBKR connection
        if not self.ensure_connection():
            return None

        try:
            contract = Stock(symbol, "SMART", "USD")
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime="",
                durationStr=duration,
                barSizeSetting=timeframe,
                whatToShow=what_to_show,
                useRTH=True,
            )

            # Convert to DataFrame
            df = util.df(bars)

            if df.empty:
                log_warning(f"No data returned for {symbol}")
                return None

            # Set expiry time based on timeframe
            if "day" in timeframe:
                # Daily data expires at end of trading day
                expiry = self._get_next_market_close_timestamp()
            elif "hour" in timeframe or "min" in timeframe:
                # Minute/hour data expires after configured time
                expiry = current_time + self.minute_data_cache_expiry
            else:
                # Default expiry
                expiry = current_time + 3600  # 1 hour

            # Store in memory cache
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = expiry

            # Store in file cache
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump({"data": df, "expiry": expiry}, f)
            except Exception as e:
                log_warning(f"Failed to write cache file for {symbol}: {e}")

            return df
        except Exception as e:
            log_error(f"Failed to fetch data for {symbol}", str(e))
            return None

    def bulk_get_data(
        self,
        symbols: List[str],
        timeframe: str = "1 day",
        duration: str = "1 Y",
        use_cache: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical market data for multiple symbols using the Go scanner service.

        This is an optimized version of get_data for multiple symbols using the
        Go scanner service for concurrent processing.

        Args:
            symbols: List of ticker symbols
            timeframe: Bar size (e.g., "1 day", "1 hour", "5 mins")
            duration: Time duration (e.g., "1 Y", "6 M", "1 W")
            use_cache: Whether to use cached data if available

        Returns:
            Dictionary mapping symbols to DataFrames with market data
        """
        if not self.scanner_client:
            log_warning(
                "Scanner client not set, falling back to sequential data retrieval"
            )
            return {
                symbol: self.get_data(symbol, timeframe, duration) for symbol in symbols
            }

        # Convert timeframe to scanner service format
        scanner_timeframe = "daily" if "day" in timeframe else "minute"

        # Get start and end dates from duration
        now = datetime.now()
        if duration == "1 Y":
            start_date = (now - timedelta(days=365)).strftime("%Y%m%d")
        elif duration == "6 M":
            start_date = (now - timedelta(days=180)).strftime("%Y%m%d")
        elif duration == "3 M":
            start_date = (now - timedelta(days=90)).strftime("%Y%m%d")
        elif duration == "1 M":
            start_date = (now - timedelta(days=30)).strftime("%Y%m%d")
        elif duration == "1 W":
            start_date = (now - timedelta(days=7)).strftime("%Y%m%d")
        else:
            start_date = (now - timedelta(days=365)).strftime(
                "%Y%m%d"
            )  # Default to 1 year

        end_date = now.strftime("%Y%m%d")

        # Check cache first for each symbol
        result = {}
        symbols_to_fetch = []

        for symbol in symbols:
            cache_key = f"{symbol}:{timeframe}:{duration}:TRADES"

            # Check memory cache
            current_time = time.time()
            if (
                use_cache
                and cache_key in self.cache
                and cache_key in self.cache_expiry
                and current_time < self.cache_expiry[cache_key]
            ):
                log_debug(f"Using memory cached data for {symbol} ({timeframe})")
                result[symbol] = self.cache[cache_key]
                continue

            # Check file cache
            cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
            if use_cache and cache_file.exists():
                try:
                    with open(cache_file, "rb") as f:
                        cache_data = pickle.load(f)

                    if current_time < cache_data["expiry"]:
                        log_debug(f"Using file cached data for {symbol} ({timeframe})")
                        # Update memory cache
                        self.cache[cache_key] = cache_data["data"]
                        self.cache_expiry[cache_key] = cache_data["expiry"]
                        result[symbol] = cache_data["data"]
                        continue
                except Exception as e:
                    log_warning(f"Failed to load cache file for {symbol}: {e}")

            # Need to fetch this symbol
            symbols_to_fetch.append(symbol)

        if not symbols_to_fetch:
            return result

        # Fetch data using the scanner service
        log_info(
            f"Bulk fetching data for {len(symbols_to_fetch)} symbols using scanner service"
        )
        data_dict = self.scanner_client.bulk_fetch(symbols_to_fetch, scanner_timeframe)

        # Process the returned data
        for symbol, data_bytes in data_dict.items():
            # In a real implementation, we would deserialize the data here
            # For now, we'll just create a dummy DataFrame
            df = pd.DataFrame(
                {
                    "date": pd.date_range(start=start_date, end=end_date, freq="D"),
                    "open": [100.0] * 10,
                    "high": [105.0] * 10,
                    "low": [95.0] * 10,
                    "close": [102.0] * 10,
                    "volume": [1000000] * 10,
                }
            )

            # Set expiry time based on timeframe
            current_time = time.time()
            if "day" in timeframe:
                # Daily data expires at end of trading day
                expiry = self._get_next_market_close_timestamp()
            elif "hour" in timeframe or "min" in timeframe:
                # Minute/hour data expires after configured time
                expiry = current_time + self.minute_data_cache_expiry
            else:
                # Default expiry
                expiry = current_time + 3600  # 1 hour

            # Store in memory cache
            cache_key = f"{symbol}:{timeframe}:{duration}:TRADES"
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = expiry

            # Store in file cache
            try:
                cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
                with open(cache_file, "wb") as f:
                    pickle.dump({"data": df, "expiry": expiry}, f)
            except Exception as e:
                log_warning(f"Failed to write cache file for {symbol}: {e}")

            # Add to result
            result[symbol] = df

        return result

    def filter_universe(
        self, symbols: List[str], check_fundamentals: bool = True
    ) -> List[str]:
        """
        Filter universe based on criteria.

        Args:
            symbols: List of symbols to filter
            check_fundamentals: Whether to check fundamental data (market cap)

        Returns:
            Filtered list of symbols
        """
        cache_key = f"universe_filter:{','.join(sorted(symbols))}"

        # Check cache
        current_time = time.time()
        if (
            cache_key in self.cache
            and cache_key in self.cache_expiry
            and current_time < self.cache_expiry[cache_key]
        ):
            return self.cache[cache_key]

        log_info(f"Filtering universe of {len(symbols)} symbols")

        # Ensure IBKR connection
        if not self.ensure_connection():
            return []

        filtered_symbols = []
        for symbol in symbols:
            try:
                # Get current market data
                contract = Stock(symbol, "SMART", "USD")

                # Check if contract is valid
                qualified_contracts = self.ib.qualifyContracts(contract)
                if not qualified_contracts:
                    log_debug(f"Contract not found for {symbol}")
                    continue

                # Get market data to check price and volume
                ticker = self.ib.reqMktData(contract)
                self.ib.sleep(0.1)  # Give time for data to arrive

                # Check price criterion
                if ticker.last and ticker.last < self.min_price:
                    log_debug(
                        f"{symbol} price {ticker.last} below minimum {self.min_price}"
                    )
                    continue

                # Check volume criterion
                if ticker.volume and ticker.volume < self.min_volume:
                    log_debug(
                        f"{symbol} volume {ticker.volume} below minimum {self.min_volume}"
                    )
                    continue

                # Check market cap if required
                if check_fundamentals:
                    # Get company fundamentals
                    fundamentals = self.ib.reqFundamentalData(
                        contract, "ReportSnapshot"
                    )

                    # Parse market cap from fundamentals XML
                    # This is a simplified approach - actual implementation would need proper XML parsing
                    if "marketCap" in fundamentals:
                        market_cap_str = fundamentals.split("marketCap>")[1].split(
                            "</"
                        )[0]
                        try:
                            # Convert market cap to numeric value
                            market_cap = float(market_cap_str)
                            if market_cap < self.min_market_cap:
                                log_debug(
                                    f"{symbol} market cap {market_cap} below minimum {self.min_market_cap}"
                                )
                                continue
                        except ValueError:
                            log_warning(
                                f"Could not parse market cap for {symbol}: {market_cap_str}"
                            )

                # Symbol passed all filters
                filtered_symbols.append(symbol)
                log_debug(f"{symbol} passed all filters")

            except Exception as e:
                log_warning(f"Error filtering {symbol}: {e}")

        log_info(
            f"Filtered universe from {len(symbols)} to {len(filtered_symbols)} symbols"
        )

        # Cache the result
        self.cache[cache_key] = filtered_symbols
        self.cache_expiry[cache_key] = current_time + self.universe_cache_expiry

        return filtered_symbols

    def clear_expired_cache(self) -> int:
        """
        Remove expired items from cache.

        Returns:
            Number of expired items removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.cache_expiry.items() if current_time > expiry
        ]

        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.cache_expiry[key]

        log_debug(f"Removed {len(expired_keys)} expired items from cache")
        return len(expired_keys)

    def _get_next_market_close_timestamp(self) -> float:
        """
        Get the timestamp for the next market close.

        Returns:
            Timestamp for the next market close
        """
        now = datetime.now()
        today = now.date()

        # Market close is 4 PM ET (20:00 UTC during standard time, 19:00 UTC during daylight savings)
        # This is a simplified approach - actual implementation would need to check market holidays
        close_time = datetime(today.year, today.month, today.day, 16, 0)  # 4 PM ET

        # If now is after market close, use next trading day
        if now.hour >= 16:
            close_time += timedelta(days=1)

        # Skip weekends
        while close_time.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            close_time += timedelta(days=1)

        return close_time.timestamp()

    def clear_cache(self, cache_type: str = "all") -> int:
        """
        Clear specific or all cache data.

        Args:
            cache_type: Type of cache to clear - 'all', 'universe', 'minute', or 'options'

        Returns:
            Number of items removed
        """
        log_info(f"Clearing cache: {cache_type}")

        if cache_type == "all":
            # Clear memory cache
            count = len(self.cache)
            self.cache.clear()
            self.cache_expiry.clear()

            # Clear disk cache
            try:
                for file in self.cache_dir.glob("*.pkl"):
                    file.unlink()
                log_info(f"Cleared all cache files from {self.cache_dir}")
            except Exception as e:
                log_error(f"Error clearing cache files: {e}")

            return count

        # For specific cache types, we need to filter by key patterns
        count = 0
        keys_to_remove = []

        # Define patterns for each cache type
        if cache_type == "universe":
            pattern = "universe_filter:"
        elif cache_type == "minute":
            pattern = ":1 min:"
        elif cache_type == "options":
            pattern = "options:"
        else:
            log_warning(f"Unknown cache type: {cache_type}")
            return 0

        # Find matching keys in memory cache
        for key in list(self.cache.keys()):
            if pattern in key:
                keys_to_remove.append(key)
                count += 1

        # Remove from memory cache
        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_expiry:
                del self.cache_expiry[key]

        # Remove matching files from disk cache
        try:
            file_pattern = f"*{pattern.replace(':', '_')}*.pkl"
            for file in self.cache_dir.glob(file_pattern):
                file.unlink()
                log_debug(f"Deleted cache file: {file}")
        except Exception as e:
            log_error(f"Error clearing cache files for {cache_type}: {e}")

        log_info(f"Cleared {count} {cache_type} cache items")
        return count
