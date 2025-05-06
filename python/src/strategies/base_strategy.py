from abc import ABC, abstractmethod
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

from ..utils.logger import log_debug


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy with configuration parameters.
        
        Args:
            config: Dictionary containing strategy parameters
        """
        self.config = config
        self.name = self.__class__.__name__
        
    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute common indicators used by all strategies.
        
        Args:
            df: DataFrame with OHLCV price data
            
        Returns:
            DataFrame with added indicators
        """
        log_debug(f"Computing common indicators for {self.name}")
        
        # Verify we have the required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"DataFrame missing required columns: {missing}")
        
        # Compute common indicators
        # ATR - Average True Range (volatility)
        df['ATR14'] = df.ta.atr(length=14)
        
        # RSI - Relative Strength Index (momentum)
        df['RSI14'] = df.ta.rsi(length=14)
        
        # Moving Averages
        df['SMA20'] = df.ta.sma(length=20)
        df['SMA50'] = df.ta.sma(length=50)
        df['SMA200'] = df.ta.sma(length=200)
        
        # MACD - Moving Average Convergence Divergence
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        df = pd.concat([df, macd], axis=1)
        
        # Bollinger Bands
        bbands = df.ta.bbands(length=20)
        df = pd.concat([df, bbands], axis=1)
        
        return df
        
    def should_execute(self, current_time: datetime) -> bool:
        """
        Determine if strategy should execute based on time of day.
        
        Args:
            current_time: Current datetime
            
        Returns:
            Boolean indicating whether the strategy should execute
        """
        # Convert to ET for US markets
        from ..utils.time_utils import convert_to_eastern
        et_time = convert_to_eastern(current_time)
        
        # Implementation of "after 3 PM ET" rule (and other time-based rules)
        return et_time.hour >= 15  # Only execute after 3 PM ET
        
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Generate trading signals based on market data.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            List of (signal_type, symbol) tuples where signal_type is "LONG" or "SHORT"
        """
        pass 