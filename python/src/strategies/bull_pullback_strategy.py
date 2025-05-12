from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from src.strategies.base_strategy import BaseStrategy
from src.utils.logger import log_debug, log_info


class BullPullbackStrategy(BaseStrategy):
    """
    Bull Pullback Strategy: Looks for stocks in an established uptrend that have pulled
    back temporarily, creating an opportunity to enter before the trend resumes.

    This strategy identifies potential long entries by finding uptrends with a
    temporary pullback in price or momentum.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Bull Pullback Strategy.

        Args:
            config: Dictionary containing strategy parameters
        """
        super().__init__(config)
        # Extract strategy-specific parameters
        self.rsi_threshold = config.get("BULL_PULLBACK_RSI_THRESHOLD", 45)
        self.recovery_periods = config.get("BULL_PULLBACK_RECOVERY_PERIODS", 2)
        self.uptrend_periods = config.get("BULL_PULLBACK_UPTREND_PERIODS", 20)

    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Generate trading signals based on bull pullback criteria.

        Args:
            df: DataFrame with price data and indicators

        Returns:
            List of (signal_type, symbol) tuples
        """
        signals: List[Tuple[str, str]] = []

        # Need at least 20 rows of data (to confirm uptrend)
        if len(df) < self.uptrend_periods:
            return signals

        # Get the most recent data and symbol
        latest = df.iloc[-1]
        symbol = latest.get("symbol", "UNKNOWN")

        log_debug(f"Evaluating Bull Pullback Strategy for {symbol}")

        # Check for required indicators
        required_columns = ["RSI14", "SMA50", "SMA200", "close"]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            log_info(f"Missing required indicators for {symbol}: {missing}")
            return signals

        # Strategy logic:
        # 1. Confirm uptrend (MA50 > MA200 and price was trending up)
        # 2. Check for pullback (RSI dips below threshold)
        # 3. Look for recovery (RSI starts rising or price starts rising)

        # 1. Confirm uptrend
        uptrend_condition = (
            # MA50 > MA200 (Golden Cross)
            df["SMA50"].iloc[-1] > df["SMA200"].iloc[-1]
            and
            # Price has been trending up over the uptrend period
            df["close"].iloc[-self.uptrend_periods :].mean()
            < df["close"].iloc[-10:].mean()
        )

        if not uptrend_condition:
            return signals

        # 2. Check for pullback and recovery
        # Get recent RSI values
        recent_rsi = df["RSI14"].iloc[-self.recovery_periods - 5 :]

        # Check if RSI dipped below threshold and then started to recover
        pullback_occurred = any(rsi < self.rsi_threshold for rsi in recent_rsi)

        if pullback_occurred:
            # Check if RSI is starting to recover
            rsi_recovering = df["RSI14"].iloc[-1] > df["RSI14"].iloc[-2]

            # Check if price is recovering (closing above short-term moving average)
            recent_closes = df["close"].iloc[-3:]
            price_recovering = recent_closes.iloc[-1] > recent_closes.iloc[-3]

            # Only generate signal if we're seeing recovery
            if rsi_recovering and price_recovering:
                log_info(
                    f"Bull Pullback signal generated for {symbol}. "
                    f"RSI: {df['RSI14'].iloc[-1]:.2f}, "
                    f"RSI trend: {df['RSI14'].iloc[-2]:.2f} -> {df['RSI14'].iloc[-1]:.2f}"
                )
                signals.append(("LONG", symbol))

        return signals

