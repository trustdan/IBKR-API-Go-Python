from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from src.strategies.base_strategy import BaseStrategy
from src.utils.logger import log_debug, log_info


class BearRallyStrategy(BaseStrategy):
    """
    Bear Rally Strategy: Looks for stocks in an established downtrend that have
    temporarily rallied, creating an opportunity to enter a short position before
    the downtrend resumes.

    This strategy identifies potential short entries by finding downtrends with a
    temporary rally in price or momentum.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Bear Rally Strategy.

        Args:
            config: Dictionary containing strategy parameters
        """
        super().__init__(config)
        # Extract strategy-specific parameters
        self.rsi_threshold = config.get("BEAR_RALLY_RSI_THRESHOLD", 55)
        self.reversal_periods = config.get("BEAR_RALLY_REVERSAL_PERIODS", 2)
        self.downtrend_periods = config.get("BEAR_RALLY_DOWNTREND_PERIODS", 20)

    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Generate trading signals based on bear rally criteria.

        Args:
            df: DataFrame with price data and indicators

        Returns:
            List of (signal_type, symbol) tuples
        """
        signals: List[Tuple[str, str]] = []

        # Need at least 20 rows of data (to confirm downtrend)
        if len(df) < self.downtrend_periods:
            return signals

        # Get the most recent data and symbol
        latest = df.iloc[-1]
        symbol = latest.get("symbol", "UNKNOWN")

        log_debug(f"Evaluating Bear Rally Strategy for {symbol}")

        # Check for required indicators
        required_columns = ["RSI14", "SMA50", "SMA200", "close"]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            log_info(f"Missing required indicators for {symbol}: {missing}")
            return signals

        # Strategy logic:
        # 1. Confirm downtrend (MA50 < MA200 and price was trending down)
        # 2. Check for rally (RSI rises above threshold)
        # 3. Look for reversal (RSI starts falling or price starts falling)

        # 1. Confirm downtrend
        downtrend_condition = (
            # MA50 < MA200 (Death Cross)
            df["SMA50"].iloc[-1] < df["SMA200"].iloc[-1]
            and
            # Price has been trending down over the downtrend period
            df["close"].iloc[-self.downtrend_periods :].mean()
            > df["close"].iloc[-10:].mean()
        )

        if not downtrend_condition:
            return signals

        # 2. Check for rally and reversal
        # Get recent RSI values
        recent_rsi = df["RSI14"].iloc[-self.reversal_periods - 5 :]

        # Check if RSI rose above threshold and then started to drop
        rally_occurred = any(rsi > self.rsi_threshold for rsi in recent_rsi)

        if rally_occurred:
            # Check if RSI is starting to fall
            rsi_reversing = df["RSI14"].iloc[-1] < df["RSI14"].iloc[-2]

            # Check if price is starting to fall
            recent_closes = df["close"].iloc[-3:]
            price_reversing = recent_closes.iloc[-1] < recent_closes.iloc[-3]

            # Only generate signal if we're seeing reversal
            if rsi_reversing and price_reversing:
                log_info(
                    f"Bear Rally signal generated for {symbol}. "
                    f"RSI: {df['RSI14'].iloc[-1]:.2f}, "
                    f"RSI trend: {df['RSI14'].iloc[-2]:.2f} -> {df['RSI14'].iloc[-1]:.2f}"
                )
                signals.append(("SHORT", symbol))

        return signals
